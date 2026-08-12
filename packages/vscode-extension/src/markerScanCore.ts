export type MarkerType = 'intervention' | 'uncertainty' | 'directive';

export interface MarkerMatch {
  type: MarkerType;
  lineNum: number;
  startChar: number;
  endChar: number;
}

export interface EnabledMarkers {
  intervention: boolean;
  uncertainty: boolean;
  directive: boolean;
}

const MARKER_PATTERNS: Record<MarkerType, string> = {
  intervention: '!!',
  uncertainty: '??',
  directive: '>>',
};

// Keyword aliases for markers (case-insensitive matching)
// Strength order: intervention > uncertainty > directive
const MARKER_KEYWORDS: Record<MarkerType, string[]> = {
  intervention: ['FIXME', 'BUG', 'XXX'],
  uncertainty: ['TODO', 'HACK'],
  directive: ['NOTE', 'NB'],
};

// Priority order for conflict resolution (lower = stronger)
const MARKER_PRIORITY: Record<MarkerType, number> = {
  intervention: 1,
  uncertainty: 2,
  directive: 3,
};

const MARKER_ORDER: MarkerType[] = ['intervention', 'uncertainty', 'directive'];

interface CommentPrefix {
  index: number;
  length: number;
}

const LINE_START_COMMENT_PATTERNS: RegExp[] = [
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

const INLINE_COMMENT_TOKENS = ['///', '//', '#', '--', ';', '/*', '<!--', '%'];

export function scanMarkerLines(text: string, enabled: EnabledMarkers): MarkerMatch[] {
  const matches: MarkerMatch[] = [];
  const lines = text.split('\n');

  if (!MARKER_ORDER.some((type) => enabled[type])) {
    return matches;
  }

  for (let lineNum = 0; lineNum < lines.length; lineNum++) {
    const line = lines[lineNum];
    const prefix = findCommentPrefix(line);
    if (!prefix) {
      continue;
    }

    const commentText = line.slice(prefix.index + prefix.length);
    let foundType = findExplicitMarker(commentText, enabled);

    if (!foundType) {
      foundType = findKeywordMatch(commentText, enabled);
    }

    if (foundType) {
      matches.push({
        type: foundType,
        lineNum,
        startChar: prefix.index,
        endChar: line.trimEnd().length,
      });
    }
  }

  return matches;
}

function findCommentPrefix(line: string): CommentPrefix | null {
  for (const pattern of LINE_START_COMMENT_PATTERNS) {
    const match = pattern.exec(line);
    if (match) {
      return { index: match[1].length, length: match[2].length };
    }
  }

  return findInlineCommentPrefix(line);
}

function findInlineCommentPrefix(line: string): CommentPrefix | null {
  let quote: 'single' | 'double' | 'backtick' | null = null;
  let escaped = false;

  for (let index = 0; index < line.length; index++) {
    const char = line[index];

    if (escaped) {
      escaped = false;
      continue;
    }

    if (quote) {
      if (char === '\\') {
        escaped = true;
        continue;
      }

      if ((quote === 'single' && char === "'") ||
          (quote === 'double' && char === '"') ||
          (quote === 'backtick' && char === '`')) {
        quote = null;
      }
      continue;
    }

    if (char === "'") {
      quote = 'single';
      continue;
    }
    if (char === '"') {
      quote = 'double';
      continue;
    }
    if (char === '`') {
      quote = 'backtick';
      continue;
    }

    for (const token of INLINE_COMMENT_TOKENS) {
      if (line.startsWith(token, index) && isInlineCommentBoundary(line, index, token)) {
        return { index, length: token.length };
      }
    }
  }

  return null;
}

function isInlineCommentBoundary(line: string, index: number, token: string): boolean {
  const before = index === 0 ? '' : line[index - 1];
  const after = line[index + token.length] ?? '';

  if (index > 0 && !/\s/.test(before)) {
    return false;
  }

  if (token === '//' && after === '/') {
    return false;
  }

  // Avoid treating URLs and operators as comments; normal inline comments have
  // whitespace before the token and whitespace/end after it.
  return after === '' || /\s/.test(after);
}

function findExplicitMarker(commentText: string, enabled: EnabledMarkers): MarkerType | null {
  for (const type of MARKER_ORDER) {
    if (!enabled[type]) {
      continue;
    }

    const pattern = escapeRegex(MARKER_PATTERNS[type]);
    const markerRegex = new RegExp(`^\\s*(${pattern})(?=\\s|$)`);
    if (markerRegex.test(commentText)) {
      return type;
    }
  }

  return null;
}

function findKeywordMatch(commentText: string, enabled: EnabledMarkers): MarkerType | null {
  let bestMatch: MarkerType | null = null;
  let bestPriority = Infinity;

  for (const type of MARKER_ORDER) {
    if (!enabled[type]) {
      continue;
    }

    for (const keyword of MARKER_KEYWORDS[type]) {
      const keywordRegex = new RegExp(`\\b${escapeRegex(keyword)}\\b`, 'i');
      if (keywordRegex.test(commentText)) {
        const priority = MARKER_PRIORITY[type];
        if (priority < bestPriority) {
          bestMatch = type;
          bestPriority = priority;
        }
        break;
      }
    }
  }

  return bestMatch;
}

function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
