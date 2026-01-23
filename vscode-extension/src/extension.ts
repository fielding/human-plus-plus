import * as vscode from 'vscode';

// Marker definitions (language-agnostic, detected inside comments only)
type MarkerType = 'intervention' | 'uncertainty' | 'directive';

const MARKER_CONFIG: Record<MarkerType, { pattern: string; configKey: string }> = {
  intervention: { pattern: '!!', configKey: 'markers.intervention.enable' },
  uncertainty: { pattern: '\\?\\?', configKey: 'markers.uncertainty.enable' },
  directive: { pattern: '>>', configKey: 'markers.directive.enable' },
};

// Combined marker regex: matches at start of comment text
// ^(\s*)(!!|\?\?|>>)(?=\s|$)
const MARKER_REGEX = /^(\s*)(!!|\?\?|>>)(?=\s|$)/;

// Common comment prefix patterns (language-agnostic detection)
// These identify where a comment starts - deliberately don't consume trailing space
// so the marker highlight can include the space before the marker
const COMMENT_PATTERNS: RegExp[] = [
  /^(\s*)(\/\/\/)/,        // /// doc comments (C#, Rust, etc) - check before //
  /^(\s*)(\/\/)/,          // // C-style
  /^(\s*)(#)/,             // # Python/Shell/Ruby
  /^(\s*)(--)/,            // -- SQL/Lua/Haskell
  /^(\s*)(;)/,             // ; Lisp/Assembly
  /^(\s*)(\/\*+)/,         // /* or /** C-style block
  /^(\s*)(\*)/,            // * block comment continuation
  /^(\s*)(<!--)/,          // <!-- HTML/XML
  /^(\s*)(%)/,             // % LaTeX/Prolog/Erlang
  /^(\s*)(rem\s)/i,        // REM Basic/Batch
  /^(\s*)(dnl\s)/,         // dnl m4
  /^(\s*)(@c\s)/,          // @c Texinfo
];

// Note: patterns are ordered by specificity (/// before //, etc.)

interface ScanResult {
  markerRanges: vscode.Range[];
  restOfLineRanges: vscode.Range[];
}

class DecorationManager {
  private markerDecorationType: vscode.TextEditorDecorationType | undefined;
  private restOfLineDecorationType: vscode.TextEditorDecorationType | undefined;

  constructor() {
    this.createDecorationTypes();
  }

  createDecorationTypes(): void {
    this.dispose();

    const config = vscode.workspace.getConfiguration('humanpp');

    // Marker token decoration - bright highlight
    this.markerDecorationType = vscode.window.createTextEditorDecorationType({
      backgroundColor: config.get('markerColor', '#bbff00'),
      color: config.get('markerTextColor', '#1b1d20'),
      fontWeight: 'bold',
      borderRadius: '2px',
      overviewRulerColor: config.get('markerColor', '#bbff00'),
      overviewRulerLane: vscode.OverviewRulerLane.Right,
    });

    // Rest of line decoration - subtle background (base02), light text
    this.restOfLineDecorationType = vscode.window.createTextEditorDecorationType({
      backgroundColor: config.get('restOfLineBackground', '#32343a'),
      color: config.get('restOfLineForeground', '#f2ebe4'),
    });
  }

  getMarkerDecorationType(): vscode.TextEditorDecorationType | undefined {
    return this.markerDecorationType;
  }

  getRestOfLineDecorationType(): vscode.TextEditorDecorationType | undefined {
    return this.restOfLineDecorationType;
  }

  dispose(): void {
    this.markerDecorationType?.dispose();
    this.restOfLineDecorationType?.dispose();
    this.markerDecorationType = undefined;
    this.restOfLineDecorationType = undefined;
  }
}

class Scanner {
  /**
   * Scans a document for Human++ markers inside comments.
   *
   * Strategy:
   * 1. For each line, detect if it's a comment using common patterns
   * 2. Extract the comment text (after the prefix)
   * 3. Check if comment text starts with a marker (!! | ?? | >>)
   * 4. Return ranges for the marker token and optionally rest of line
   */
  scan(document: vscode.TextDocument): ScanResult {
    const config = vscode.workspace.getConfiguration('humanpp');
    const highlightRestOfLine = config.get('highlightRestOfLine', false);

    const markerRanges: vscode.Range[] = [];
    const restOfLineRanges: vscode.Range[] = [];

    const text = document.getText();
    const lines = text.split('\n');

    // Build enabled marker pattern
    const enabledMarkers: string[] = [];
    for (const [type, { pattern, configKey }] of Object.entries(MARKER_CONFIG)) {
      if (config.get(configKey, true)) {
        enabledMarkers.push(pattern);
      }
    }

    if (enabledMarkers.length === 0) {
      return { markerRanges, restOfLineRanges };
    }

    // Dynamic regex based on enabled markers
    const markerRegex = new RegExp(`^(\\s*)(${enabledMarkers.join('|')})(?=\\s|$)`);

    for (let lineNum = 0; lineNum < lines.length; lineNum++) {
      const line = lines[lineNum];

      // Try to match a comment pattern
      for (const commentPattern of COMMENT_PATTERNS) {
        const commentMatch = commentPattern.exec(line);
        if (!commentMatch) {
          continue;
        }

        // commentMatch[1] = leading whitespace before comment
        // commentMatch[2] = the comment prefix (including its trailing space if any)
        const prefixEnd = commentMatch[0].length;
        const commentText = line.slice(prefixEnd);

        // Check if comment text starts with a marker
        const markerMatch = markerRegex.exec(commentText);
        if (markerMatch) {
          // markerMatch[1] = whitespace between prefix and marker (usually empty)
          // markerMatch[2] = the marker itself (!! | ?? | >>)
          const wsBeforeMarker = markerMatch[1] || '';
          const marker = markerMatch[2];

          // Include space before marker in highlight
          const markerStart = prefixEnd;
          const markerTokenEnd = prefixEnd + wsBeforeMarker.length + marker.length;

          // Include space after marker if present
          const afterMarker = commentText.slice(wsBeforeMarker.length + marker.length);
          const trailingSpace = afterMarker.match(/^\s/) ? 1 : 0;
          const markerEnd = markerTokenEnd + trailingSpace;

          // Highlight the marker token (with surrounding spaces)
          markerRanges.push(new vscode.Range(
            new vscode.Position(lineNum, markerStart),
            new vscode.Position(lineNum, markerEnd)
          ));

          // Optionally highlight rest of comment
          if (highlightRestOfLine && markerEnd < line.length) {
            restOfLineRanges.push(new vscode.Range(
              new vscode.Position(lineNum, markerEnd),
              new vscode.Position(lineNum, line.length)
            ));
          }
        }

        // Only match first comment pattern per line
        break;
      }
    }

    return { markerRanges, restOfLineRanges };
  }
}

class HumanPPHighlighter {
  private decorationManager: DecorationManager;
  private scanner: Scanner;
  private debounceTimer: NodeJS.Timeout | undefined;
  private enabled: boolean = true;

  constructor(private context: vscode.ExtensionContext) {
    this.decorationManager = new DecorationManager();
    this.scanner = new Scanner();
    this.enabled = vscode.workspace.getConfiguration('humanpp').get('enable', true);
  }

  private getDebounceMs(): number {
    return vscode.workspace.getConfiguration('humanpp').get('debounceMs', 200);
  }

  updateDecorations(editor: vscode.TextEditor | undefined): void {
    if (!editor || !this.enabled) {
      return;
    }

    const { markerRanges, restOfLineRanges } = this.scanner.scan(editor.document);

    const markerDecorationType = this.decorationManager.getMarkerDecorationType();
    const restOfLineDecorationType = this.decorationManager.getRestOfLineDecorationType();

    if (markerDecorationType) {
      editor.setDecorations(markerDecorationType, markerRanges);
    }

    if (restOfLineDecorationType) {
      const config = vscode.workspace.getConfiguration('humanpp');
      const highlightRestOfLine = config.get('highlightRestOfLine', false);
      editor.setDecorations(restOfLineDecorationType, highlightRestOfLine ? restOfLineRanges : []);
    }
  }

  clearDecorations(editor: vscode.TextEditor | undefined): void {
    if (!editor) {
      return;
    }

    const markerDecorationType = this.decorationManager.getMarkerDecorationType();
    const restOfLineDecorationType = this.decorationManager.getRestOfLineDecorationType();

    if (markerDecorationType) {
      editor.setDecorations(markerDecorationType, []);
    }
    if (restOfLineDecorationType) {
      editor.setDecorations(restOfLineDecorationType, []);
    }
  }

  scheduleUpdate(editor: vscode.TextEditor | undefined): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }

    this.debounceTimer = setTimeout(() => {
      this.updateDecorations(editor);
    }, this.getDebounceMs());
  }

  toggle(): void {
    this.enabled = !this.enabled;
    vscode.workspace.getConfiguration('humanpp').update('enable', this.enabled, true);

    const editor = vscode.window.activeTextEditor;
    if (this.enabled) {
      this.updateDecorations(editor);
      vscode.window.showInformationMessage('Human++ marker highlighting enabled');
    } else {
      this.clearDecorations(editor);
      vscode.window.showInformationMessage('Human++ marker highlighting disabled');
    }
  }

  refresh(): void {
    if (!this.enabled) {
      return;
    }
    this.updateDecorations(vscode.window.activeTextEditor);
  }

  onConfigurationChanged(): void {
    this.enabled = vscode.workspace.getConfiguration('humanpp').get('enable', true);
    this.decorationManager.createDecorationTypes();

    const editor = vscode.window.activeTextEditor;
    if (this.enabled) {
      this.updateDecorations(editor);
    } else {
      this.clearDecorations(editor);
    }
  }

  dispose(): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    this.decorationManager.dispose();
  }
}

let highlighter: HumanPPHighlighter | undefined;

export function activate(context: vscode.ExtensionContext): void {
  highlighter = new HumanPPHighlighter(context);

  context.subscriptions.push(
    vscode.commands.registerCommand('humanpp.toggle', () => {
      highlighter?.toggle();
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('humanpp.refresh', () => {
      highlighter?.refresh();
    })
  );

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor((editor) => {
      highlighter?.updateDecorations(editor);
    })
  );

  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument((event) => {
      const editor = vscode.window.activeTextEditor;
      if (editor && event.document === editor.document) {
        highlighter?.scheduleUpdate(editor);
      }
    })
  );

  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((event) => {
      if (event.affectsConfiguration('humanpp')) {
        highlighter?.onConfigurationChanged();
      }
    })
  );

  if (vscode.window.activeTextEditor) {
    highlighter.updateDecorations(vscode.window.activeTextEditor);
  }
}

export function deactivate(): void {
  highlighter?.dispose();
}
