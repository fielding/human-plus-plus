import * as vscode from 'vscode';

// Marker types and their colors
type MarkerType = 'intervention' | 'uncertainty' | 'directive';

interface MarkerDef {
  pattern: string;
  configKey: string;
  background: string;
  foreground: string;
}

const MARKERS: Record<MarkerType, MarkerDef> = {
  intervention: {
    pattern: '!!',
    configKey: 'markers.intervention.enable',
    background: '#bbff00',      // Lime (base0F) - attention/critical
    foreground: '#1a1c22',      // Dark text on bright background (base00)
  },
  uncertainty: {
    pattern: '??',
    configKey: 'markers.uncertainty.enable',
    background: '#9871fe',      // Purple (base0E) - uncertainty
    foreground: '#f8f6f2',      // Light text on dark background (base07)
  },
  directive: {
    pattern: '>>',
    configKey: 'markers.directive.enable',
    background: '#1ad0d6',      // Cyan (base0C) - directive/reference
    foreground: '#1a1c22',      // Dark text on bright background (base00)
  },
};

// Diagnostic colors (for inline error/warning badges)
type DiagnosticLevel = 'error' | 'warning' | 'info' | 'hint';

interface DiagnosticStyle {
  background: string;
  foreground: string;
}

const DIAGNOSTIC_COLORS: Record<DiagnosticLevel, DiagnosticStyle> = {
  error: {
    background: '#e7349c',      // Pink (base08)
    foreground: '#1a1c22',      // Dark text on bright background (base00)
  },
  warning: {
    background: '#f26c33',      // Orange (base09)
    foreground: '#1a1c22',      // Dark text on bright background (base00)
  },
  info: {
    background: '#1ad0d6',      // Cyan (base0C)
    foreground: '#1a1c22',      // Dark text on bright background (base00)
  },
  hint: {
    background: '#5e84b6',      // Quiet blue (base15)
    foreground: '#f8f6f2',      // Light text on dark background (base07)
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

interface MarkerMatch {
  type: MarkerType;
  lineNum: number;
  startChar: number;      // Start of comment (including leading whitespace for padding)
  endChar: number;        // End of line text
}

// ============================================================================
// Marker Decoration Manager (left-aligned comment badges)
// ============================================================================

class MarkerDecorationManager {
  private decorations: Map<MarkerType, vscode.TextEditorDecorationType> = new Map();

  constructor() {
    this.createDecorationTypes();
  }

  createDecorationTypes(): void {
    this.dispose();

    for (const [type, def] of Object.entries(MARKERS) as [MarkerType, MarkerDef][]) {
      this.decorations.set(type, vscode.window.createTextEditorDecorationType({
        backgroundColor: def.background,
        color: def.foreground,
        fontWeight: 'bold',
        fontStyle: 'normal',      // Override italic from comment styling
        borderRadius: '4px',
        overviewRulerColor: def.background,
        overviewRulerLane: vscode.OverviewRulerLane.Right,
        textDecoration: '; font-size: 0.9em;',
      }));
    }
  }

  getDecoration(type: MarkerType): vscode.TextEditorDecorationType | undefined {
    return this.decorations.get(type);
  }

  getAllTypes(): MarkerType[] {
    return Object.keys(MARKERS) as MarkerType[];
  }

  dispose(): void {
    for (const dec of this.decorations.values()) {
      dec.dispose();
    }
    this.decorations.clear();
  }
}

// ============================================================================
// Marker Scanner
// ============================================================================

class MarkerScanner {
  scan(document: vscode.TextDocument): MarkerMatch[] {
    const config = vscode.workspace.getConfiguration('human-plus-plus');
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
      return matches;
    }

    for (let lineNum = 0; lineNum < lines.length; lineNum++) {
      const line = lines[lineNum];

      // Try to match a comment pattern
      for (const commentPattern of COMMENT_PATTERNS) {
        const commentMatch = commentPattern.exec(line);
        if (!commentMatch) {
          continue;
        }

        const leadingWhitespace = commentMatch[1].length;
        const prefixEnd = commentMatch[0].length;
        const commentText = line.slice(prefixEnd);

        // Check for each marker type
        for (const [type, def] of enabledMarkers) {
          const markerRegex = new RegExp(`^\\s*(${def.pattern.replace(/\?/g, '\\?')})(?=\\s|$)`);
          if (markerRegex.test(commentText)) {
            // Find end of actual text (trim trailing whitespace)
            const trimmedEnd = line.trimEnd().length;
            matches.push({
              type,
              lineNum,
              startChar: leadingWhitespace,  // Start from the comment symbol
              endChar: trimmedEnd,
            });
            break;
          }
        }

        break; // Only check first comment pattern per line
      }
    }

    return matches;
  }
}

// ============================================================================
// Diagnostic Decoration Manager (right-aligned inline badges)
// ============================================================================

class DiagnosticDecorationManager {
  // One decoration type per severity level (reused)
  private decorationTypes: Map<DiagnosticLevel, vscode.TextEditorDecorationType> = new Map();

  constructor() {
    this.createDecorationTypes();
  }

  createDecorationTypes(): void {
    this.dispose();

    for (const [level, style] of Object.entries(DIAGNOSTIC_COLORS) as [DiagnosticLevel, DiagnosticStyle][]) {
      this.decorationTypes.set(level, vscode.window.createTextEditorDecorationType({
        after: {
          // contentText will be overridden per-range via renderOptions
          backgroundColor: style.background,
          color: style.foreground,
          margin: '0 0 0 3em',
          textDecoration: '; border-radius: 4px;',
        },
        rangeBehavior: vscode.DecorationRangeBehavior.ClosedClosed,
      }));
    }
  }

  updateDiagnostics(editor: vscode.TextEditor): void {
    const config = vscode.workspace.getConfiguration('human-plus-plus');

    // Clear all decorations first (but don't dispose types)
    for (const decType of this.decorationTypes.values()) {
      editor.setDecorations(decType, []);
    }

    if (!config.get('diagnostics.enable', true)) {
      return;
    }

    const document = editor.document;
    const diagnostics = vscode.languages.getDiagnostics(document.uri);

    // Group diagnostics by line (only show first per line to avoid clutter)
    const diagnosticsByLine: Map<number, vscode.Diagnostic> = new Map();

    for (const diagnostic of diagnostics) {
      const line = diagnostic.range.start.line;
      if (!diagnosticsByLine.has(line)) {
        diagnosticsByLine.set(line, diagnostic);
      } else {
        // Prefer higher severity (lower number = higher severity)
        const existing = diagnosticsByLine.get(line)!;
        if (diagnostic.severity < existing.severity) {
          diagnosticsByLine.set(line, diagnostic);
        }
      }
    }

    // Group by severity level for batch application
    const decorationsByLevel: Map<DiagnosticLevel, vscode.DecorationOptions[]> = new Map();
    for (const level of this.decorationTypes.keys()) {
      decorationsByLevel.set(level, []);
    }

    for (const [lineNum, diagnostic] of diagnosticsByLine) {
      const level = this.severityToLevel(diagnostic.severity);

      // Check if this level is enabled
      if (!config.get(`diagnostics.${level}.enable`, true)) {
        continue;
      }

      const line = document.lineAt(lineNum);
      const truncatedMessage = diagnostic.message.length > 50
        ? diagnostic.message.slice(0, 47) + '...'
        : diagnostic.message;

      // Create decoration option with custom message via renderOptions
      const style = DIAGNOSTIC_COLORS[level];
      const decorationOption: vscode.DecorationOptions = {
        range: new vscode.Range(
          lineNum, line.text.trimEnd().length,
          lineNum, line.text.trimEnd().length
        ),
        renderOptions: {
          after: {
            contentText: `  ${truncatedMessage}  `,
            backgroundColor: style.background,
            color: style.foreground,
          },
        },
      };

      decorationsByLevel.get(level)?.push(decorationOption);
    }

    // Apply decorations by level
    for (const [level, options] of decorationsByLevel) {
      const decType = this.decorationTypes.get(level);
      if (decType) {
        editor.setDecorations(decType, options);
      }
    }
  }

  private severityToLevel(severity: vscode.DiagnosticSeverity): DiagnosticLevel {
    switch (severity) {
      case vscode.DiagnosticSeverity.Error:
        return 'error';
      case vscode.DiagnosticSeverity.Warning:
        return 'warning';
      case vscode.DiagnosticSeverity.Information:
        return 'info';
      case vscode.DiagnosticSeverity.Hint:
        return 'hint';
      default:
        return 'info';
    }
  }

  dispose(): void {
    for (const dec of this.decorationTypes.values()) {
      dec.dispose();
    }
    this.decorationTypes.clear();
  }
}

// ============================================================================
// Main Highlighter
// ============================================================================

class HumanPlusPlusHighlighter {
  private markerDecorationManager: MarkerDecorationManager;
  private diagnosticDecorationManager: DiagnosticDecorationManager;
  private markerScanner: MarkerScanner;
  private debounceTimer: NodeJS.Timeout | undefined;
  private diagnosticDebounceTimer: NodeJS.Timeout | undefined;
  private enabled: boolean = true;

  constructor(private context: vscode.ExtensionContext) {
    this.markerDecorationManager = new MarkerDecorationManager();
    this.diagnosticDecorationManager = new DiagnosticDecorationManager();
    this.markerScanner = new MarkerScanner();
    this.enabled = vscode.workspace.getConfiguration('human-plus-plus').get('enable', true);
  }

  private getDebounceMs(): number {
    return vscode.workspace.getConfiguration('human-plus-plus').get('debounceMs', 200);
  }

  updateMarkerDecorations(editor: vscode.TextEditor | undefined): void {
    if (!editor || !this.enabled) {
      return;
    }

    const matches = this.markerScanner.scan(editor.document);

    // Group matches by marker type
    const ranges: Map<MarkerType, vscode.Range[]> = new Map();
    for (const type of this.markerDecorationManager.getAllTypes()) {
      ranges.set(type, []);
    }

    for (const match of matches) {
      const range = new vscode.Range(
        match.lineNum, match.startChar,
        match.lineNum, match.endChar
      );
      ranges.get(match.type)?.push(range);
    }

    // Apply decorations
    for (const type of this.markerDecorationManager.getAllTypes()) {
      const dec = this.markerDecorationManager.getDecoration(type);
      if (dec) {
        editor.setDecorations(dec, ranges.get(type) || []);
      }
    }
  }

  updateDiagnosticDecorations(editor: vscode.TextEditor | undefined): void {
    if (!editor || !this.enabled) {
      return;
    }

    this.diagnosticDecorationManager.updateDiagnostics(editor);
  }

  updateAllDecorations(editor: vscode.TextEditor | undefined): void {
    this.updateMarkerDecorations(editor);
    this.updateDiagnosticDecorations(editor);
  }

  clearDecorations(editor: vscode.TextEditor | undefined): void {
    if (!editor) {
      return;
    }

    for (const type of this.markerDecorationManager.getAllTypes()) {
      const dec = this.markerDecorationManager.getDecoration(type);
      if (dec) {
        editor.setDecorations(dec, []);
      }
    }

    this.diagnosticDecorationManager.dispose();
  }

  scheduleMarkerUpdate(editor: vscode.TextEditor | undefined): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }

    this.debounceTimer = setTimeout(() => {
      this.updateMarkerDecorations(editor);
    }, this.getDebounceMs());
  }

  scheduleDiagnosticUpdate(editor: vscode.TextEditor | undefined): void {
    if (this.diagnosticDebounceTimer) {
      clearTimeout(this.diagnosticDebounceTimer);
    }

    this.diagnosticDebounceTimer = setTimeout(() => {
      this.updateDiagnosticDecorations(editor);
    }, this.getDebounceMs());
  }

  toggle(): void {
    this.enabled = !this.enabled;
    vscode.workspace.getConfiguration('human-plus-plus').update('enable', this.enabled, true);

    const editor = vscode.window.activeTextEditor;
    if (this.enabled) {
      this.updateAllDecorations(editor);
      vscode.window.showInformationMessage('Human++ highlighting enabled');
    } else {
      this.clearDecorations(editor);
      vscode.window.showInformationMessage('Human++ highlighting disabled');
    }
  }

  refresh(): void {
    if (!this.enabled) {
      return;
    }
    this.updateAllDecorations(vscode.window.activeTextEditor);
  }

  onConfigurationChanged(): void {
    this.enabled = vscode.workspace.getConfiguration('human-plus-plus').get('enable', true);
    this.markerDecorationManager.createDecorationTypes();

    const editor = vscode.window.activeTextEditor;
    if (this.enabled) {
      this.updateAllDecorations(editor);
    } else {
      this.clearDecorations(editor);
    }
  }

  onDiagnosticsChanged(uri: vscode.Uri): void {
    const editor = vscode.window.activeTextEditor;
    if (editor && editor.document.uri.toString() === uri.toString()) {
      this.scheduleDiagnosticUpdate(editor);
    }
  }

  dispose(): void {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    if (this.diagnosticDebounceTimer) {
      clearTimeout(this.diagnosticDebounceTimer);
    }
    this.markerDecorationManager.dispose();
    this.diagnosticDecorationManager.dispose();
  }
}

// ============================================================================
// Extension Activation
// ============================================================================

let highlighter: HumanPlusPlusHighlighter | undefined;

export function activate(context: vscode.ExtensionContext): void {
  highlighter = new HumanPlusPlusHighlighter(context);

  context.subscriptions.push(
    vscode.commands.registerCommand('human-plus-plus.toggle', () => {
      highlighter?.toggle();
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('human-plus-plus.refresh', () => {
      highlighter?.refresh();
    })
  );

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor((editor) => {
      highlighter?.updateAllDecorations(editor);
    })
  );

  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument((event) => {
      const editor = vscode.window.activeTextEditor;
      if (editor && event.document === editor.document) {
        highlighter?.scheduleMarkerUpdate(editor);
      }
    })
  );

  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((event) => {
      if (event.affectsConfiguration('human-plus-plus')) {
        highlighter?.onConfigurationChanged();
      }
    })
  );

  // Listen for diagnostic changes
  context.subscriptions.push(
    vscode.languages.onDidChangeDiagnostics((event) => {
      for (const uri of event.uris) {
        highlighter?.onDiagnosticsChanged(uri);
      }
    })
  );

  if (vscode.window.activeTextEditor) {
    highlighter.updateAllDecorations(vscode.window.activeTextEditor);
  }
}

export function deactivate(): void {
  highlighter?.dispose();
}
