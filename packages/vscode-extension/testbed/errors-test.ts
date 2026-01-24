// Human++ Diagnostics Test File
// This file has INTENTIONAL errors and warnings to test diagnostic highlighting

interface User {
  id: string;
  name: string;
  email: string;
}

// ERROR: Type 'null' is not assignable to type 'string'
const user: User = {
  id: "123",
  name: null,  // <-- ERROR: should show pink squiggle + pink line tint
  email: "test@example.com"
};

// ERROR: Property 'age' does not exist on type 'User'
console.log(user.age);  // <-- ERROR: should show pink squiggle

// WARNING: 'unusedVariable' is declared but never used
const unusedVariable = "I'm not used";  // <-- WARNING: should show orange

// ERROR: Cannot assign to 'x' because it is a constant
const x = 10;
x = 20; 

// Type error
function greet(name: string): string {
  return name;
}
greet(123);  // <-- ERROR: number not assignable to string

// !! Human marker should still work alongside errors
// ?? This combines uncertainty with actual code issues
// >> See the theme file for diagnostic color definitions

// Unused parameter warning
function unused(param: string) {
  return "hello";
}

// Implicit any (if strict mode)
function noTypes(a, b) {  // <-- ERROR in strict: implicit any
  return a + b;
}
