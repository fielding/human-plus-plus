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
