import * as vscode from 'vscode';

// Marker types and their default colors
type MarkerType = 'intervention' | 'uncertainty' | 'directive';

interface MarkerDef {
  pattern: string;
  regex: RegExp;
  configKey: string;
  color: string;        // LOUD color for badge
  colorDim: string;     // Low opacity for line background
  textColor: string;    // Text color on badge
}

const MARKERS: Record<MarkerType, MarkerDef> = {
  intervention: {
    pattern: '!!',
    regex: /!!/,
    configKey: 'markers.intervention.enable',
    color: '#bbff00',      // base0F lime
    colorDim: '#bbff0018', // ~10% opacity
    textColor: '#1b1d20',
  },
  uncertainty: {
    pattern: '??',
    regex: /\?\?/,
    configKey: 'markers.uncertainty.enable',
    color: '#8d57ff',      // base0E purple
    colorDim: '#8d57ff18',
    textColor: '#faf5ef',
  },
  directive: {
    pattern: '>>',
    regex: />>/,
    configKey: 'markers.directive.enable',
    color: '#1ad0d6',      // base0C cyan
    colorDim: '#1ad0d618',
    textColor: '#1b1d20',
  },
};

// Common comment prefix patterns
const COMMENT_PATTERNS: RegExp[] = [
  /^(\s*)(\/\/\/)/,        // /// doc comments
  /^(\s*)(\/\/)/,          // // C-style
  /^(\s*)(#)/,             // # Python/Shell/Ruby
  /^(\s*)(--)/,            // -- SQL/Lua/Haskell
  /^(\s*)(;)/,             // ; Lisp/Assembly
  /^(\s*)(\/\*+)/,         // /* block
  /^(\s*)(\*)/,            // * block continuation
  /^(\s*)(<!--)/,          // <!-- HTML/XML
  /^(\s*)(%)/,             // % LaTeX/Prolog
  /^(\s*)(rem\s)/i,        // REM Basic/Batch
];

type StyleMode = 'badge' | 'line' | 'both';

interface MarkerMatch {
  type: MarkerType;
  lineNum: number;
  markerStart: number;
  markerEnd: number;
  lineEnd: number;
}

interface ScanResult {
  matches: MarkerMatch[];
}

class DecorationManager {
  // Badge decorations (one per marker type)
  private badgeDecorations: Map<MarkerType, vscode.TextEditorDecorationType> = new Map();
  // Line background decorations (one per marker type)
  private lineDecorations: Map<MarkerType, vscode.TextEditorDecorationType> = new Map();

  constructor() {
    this.createDecorationTypes();
  }

  createDecorationTypes(): void {
    this.dispose();

    for (const [type, def] of Object.entries(MARKERS) as [MarkerType, MarkerDef][]) {
      // Badge decoration - bright background on marker
      this.badgeDecorations.set(type, vscode.window.createTextEditorDecorationType({
        backgroundColor: def.color,
        color: def.textColor,
        fontWeight: 'bold',
        borderRadius: '3px',
        overviewRulerColor: def.color,
        overviewRulerLane: vscode.OverviewRulerLane.Right,
      }));

      // Line decoration - subtle colored background
      this.lineDecorations.set(type, vscode.window.createTextEditorDecorationType({
        backgroundColor: def.colorDim,
        isWholeLine: true,
      }));
    }
  }

  getBadgeDecoration(type: MarkerType): vscode.TextEditorDecorationType | undefined {
    return this.badgeDecorations.get(type);
  }

  getLineDecoration(type: MarkerType): vscode.TextEditorDecorationType | undefined {
    return this.lineDecorations.get(type);
  }

  getAllTypes(): MarkerType[] {
    return Object.keys(MARKERS) as MarkerType[];
  }

  dispose(): void {
    for (const dec of this.badgeDecorations.values()) {
      dec.dispose();
    }
    for (const dec of this.lineDecorations.values()) {
      dec.dispose();
    }
    this.badgeDecorations.clear();
    this.lineDecorations.clear();
  }
}

class Scanner {
  scan(document: vscode.TextDocument): ScanResult {
    const config = vscode.workspace.getConfiguration('humanpp');
    const matches: MarkerMatch[] = [];

    const text = document.getText();
    const lines = text.split('\n');

    // Build list of enabled markers
    const enabledMarkers: [MarkerType, MarkerDef][] = [];
    for (const [type, def] of Object.entries(MARKERS) as [MarkerType, MarkerDef][]) {
      if (config.get(def.configKey, true)) {
        enabledMarkers.push([type, def]);
      }
    }

    if (enabledMarkers.length === 0) {
      return { matches };
    }

    for (let lineNum = 0; lineNum < lines.length; lineNum++) {
      const line = lines[lineNum];

      // Try to match a comment pattern
      for (const commentPattern of COMMENT_PATTERNS) {
        const commentMatch = commentPattern.exec(line);
        if (!commentMatch) {
          continue;
        }

        const prefixEnd = commentMatch[0].length;
        const commentText = line.slice(prefixEnd);

        // Check for each marker type
        for (const [type, def] of enabledMarkers) {
          // Match marker at start of comment (with optional whitespace)
          const markerRegex = new RegExp(`^(\\s*)(${def.pattern.replace(/\?/g, '\\?')})(?=\\s|$)`);
          const markerMatch = markerRegex.exec(commentText);

          if (markerMatch) {
            const wsBeforeMarker = markerMatch[1] || '';
            const marker = markerMatch[2];

            const markerStart = prefixEnd;
            const markerTokenEnd = prefixEnd + wsBeforeMarker.length + marker.length;
            const afterMarker = commentText.slice(wsBeforeMarker.length + marker.length);
            const trailingSpace = afterMarker.match(/^\s/) ? 1 : 0;
            const markerEnd = markerTokenEnd + trailingSpace;

            matches.push({
              type,
              lineNum,
              markerStart,
              markerEnd,
              lineEnd: line.length,
            });

            break; // Only one marker per line
          }
        }

        break; // Only check first comment pattern per line
      }
    }

    return { matches };
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

  private getStyleMode(): StyleMode {
    return vscode.workspace.getConfiguration('humanpp').get('style', 'both') as StyleMode;
  }

  updateDecorations(editor: vscode.TextEditor | undefined): void {
    if (!editor || !this.enabled) {
      return;
    }

    const { matches } = this.scanner.scan(editor.document);
    const style = this.getStyleMode();

    // Group matches by marker type
    const badgeRanges: Map<MarkerType, vscode.Range[]> = new Map();
    const lineRanges: Map<MarkerType, vscode.Range[]> = new Map();

    for (const type of this.decorationManager.getAllTypes()) {
      badgeRanges.set(type, []);
      lineRanges.set(type, []);
    }

    for (const match of matches) {
      // Badge range (just the marker)
      badgeRanges.get(match.type)?.push(new vscode.Range(
        new vscode.Position(match.lineNum, match.markerStart),
        new vscode.Position(match.lineNum, match.markerEnd)
      ));

      // Line range (whole line for background)
      lineRanges.get(match.type)?.push(new vscode.Range(
        new vscode.Position(match.lineNum, 0),
        new vscode.Position(match.lineNum, match.lineEnd)
      ));
    }

    // Apply decorations based on style mode
    for (const type of this.decorationManager.getAllTypes()) {
      const badgeDec = this.decorationManager.getBadgeDecoration(type);
      const lineDec = this.decorationManager.getLineDecoration(type);

      if (badgeDec) {
        const showBadge = style === 'badge' || style === 'both';
        editor.setDecorations(badgeDec, showBadge ? badgeRanges.get(type) || [] : []);
      }

      if (lineDec) {
        const showLine = style === 'line' || style === 'both';
        editor.setDecorations(lineDec, showLine ? lineRanges.get(type) || [] : []);
      }
    }
  }

  clearDecorations(editor: vscode.TextEditor | undefined): void {
    if (!editor) {
      return;
    }

    for (const type of this.decorationManager.getAllTypes()) {
      const badgeDec = this.decorationManager.getBadgeDecoration(type);
      const lineDec = this.decorationManager.getLineDecoration(type);

      if (badgeDec) {
        editor.setDecorations(badgeDec, []);
      }
      if (lineDec) {
        editor.setDecorations(lineDec, []);
      }
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
