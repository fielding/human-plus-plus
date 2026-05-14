const assert = require('node:assert/strict');
const { scanMarkerLines } = require('../out/markerScanCore.js');

function typesFor(text) {
  return scanMarkerLines(text, {
    intervention: true,
    uncertainty: true,
    directive: true,
  }).map((match) => match.type);
}

assert.deepEqual(
  typesFor("alias ls='eza -lhas name' # >> testme\n" +
           "alias lsc='eza -lhas created' # !! testme\n" +
           "alias lsr='eza -lhas name -R' # ?? testme"),
  ['directive', 'intervention', 'uncertainty'],
  'shell trailing comments should be scanned for Human++ markers'
);

assert.deepEqual(
  typesFor("const url = 'http://example.test';\n" +
           "const text = 'TODO inside a string is not a comment';"),
  [],
  'comment scanning should not treat URL or string contents as comments'
);

console.log('marker-scan-core tests passed');
