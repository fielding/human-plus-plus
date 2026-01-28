// Human++ Marker Test File
// Each marker type should have a DIFFERENT color

// Regular comment - should be muted (base03 coffee brown)

// !! ATTENTION - this should be LIME (#bbff00) badge + lime line tint
const criticalValue = 42;

// ?? UNCERTAINTY - this should be PURPLE (#8d57ff) badge + purple line tint
const maybeWrong = "not sure";

// >> REFERENCE - this should be CYAN (#1ad0d6) badge + cyan line tint
const seeOtherFile = true;

// Test all three in sequence:
// !! First marker - LIME
// ?? Second marker - PURPLE
// >> Third marker - CYAN

function example() {
  // !! Critical: don't change this without approval
  const x = 1;

  // ?? Not sure if this handles edge cases
  const y = x + 1;

  // >> See utils.ts for the implementation details
  return y;
}

// =============================================================================
// KEYWORD ALIAS TESTS
// These should highlight the same as their marker equivalents
// =============================================================================

// FIXME: This should be LIME (same as !!)
const fixmeExample = "broken";

// BUG: Known issue with edge case - should be LIME (same as !!)
const bugExample = null;

// XXX: Temporary workaround - should be LIME (same as !!)
const xxxExample = "hack";

// TODO: Implement this feature - should be PURPLE (same as ??)
const todoExample = undefined;

// HACK: This is a workaround - should be PURPLE (same as ??)
const hackExample = "temporary";

// NOTE: Important context - should be CYAN (same as >>)
const noteExample = "info";

// NB: Latin for "note well" - should be CYAN (same as >>)
const nbExample = "nota bene";

// =============================================================================
// PRECEDENCE TESTS
// Explicit markers should win over keywords
// =============================================================================

// ?? TODO: Explicit marker wins - should be PURPLE from ??
const explicitWins1 = true;

// !! FIXME: Explicit marker wins - should be LIME from !!
const explicitWins2 = true;

// TODO BUG: Multiple keywords - BUG is stronger, should be LIME
const multipleKeywords = true;

// =============================================================================
// CASE INSENSITIVITY TESTS
// =============================================================================

// todo: lowercase should work - PURPLE
const lowercaseTodo = 1;

// Todo: mixed case should work - PURPLE
const mixedCaseTodo = 2;

// fixme: lowercase should work - LIME
const lowercaseFixme = 3;

// Note: mixed case should work - CYAN
const mixedCaseNote = 4;
