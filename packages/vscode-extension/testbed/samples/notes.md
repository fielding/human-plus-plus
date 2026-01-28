# Human++ Markdown Comprehensive Test

This file tests all markdown elements for proper syntax highlighting.

---

## Headers (H1-H6)

# Heading Level 1
## Heading Level 2
### Heading Level 3
#### Heading Level 4
##### Heading Level 5
###### Heading Level 6

---

## Text Formatting

Regular paragraph text should use the base text color.

**Bold text** should stand out.
*Italic text* for emphasis.
***Bold and italic*** combined.
~~Strikethrough~~ for deleted content.
`inline code` should be distinct.

---

## Links and Images

[Regular link](https://example.com)
[Link with title](https://example.com "Example Title")
<https://autolink.example.com>
email@example.com

![Alt text for image](https://example.com/image.png)
![Image with title](https://example.com/image.png "Image Title")

Reference-style links: [reference link][ref1]
[ref1]: https://example.com "Reference"

---

## Lists

### Unordered Lists

- First item
- Second item
  - Nested item
  - Another nested
    - Deep nesting
- Back to top level

* Alternative bullet
+ Another alternative

### Ordered Lists

1. First numbered
2. Second numbered
   1. Nested numbered
   2. More nested
3. Back to top

### Task Lists

- [ ] Unchecked task
- [x] Completed task
- [ ] Another task with `code`

---

## Blockquotes

> Single line blockquote

> Multi-line blockquote
> continues here
> and here

> Nested blockquotes
>> Level 2
>>> Level 3

> Blockquote with **formatting** and `code`

---

## Code

### Inline Code

Use `const` for constants, `let` for variables.
The function `calculateTotal()` returns a `number`.

### Fenced Code Blocks

```typescript
// TypeScript with syntax highlighting
interface User {
  id: string;
  name: string;
}

async function getUser(id: string): Promise<User> {
  // !! Critical section
  return await fetch(`/api/users/${id}`);
}
```

```python
# Python example
def hello_world():
    """Docstring here"""
    print("Hello, World!")
    # TODO: Add more features
```

```rust
// Rust example
fn main() {
    let message = "Hello";
    println!("{}", message);
    // NOTE: Rust is memory safe
}
```

```json
{
  "name": "human-plus-plus",
  "version": "1.0.0",
  "colors": ["#bbff00", "#9871fe"]
}
```

```bash
# Shell script
echo "Hello World"
ls -la | grep ".md"
# FIXME: Handle errors
```

### Indented Code Block

    This is an indented code block
    Four spaces at the start
    Old-school markdown style

---

## Tables

| Header 1 | Header 2 | Header 3 |
|----------|:--------:|---------:|
| Left     | Center   | Right    |
| Cell     | Cell     | Cell     |
| **Bold** | *Italic* | `Code`   |

| Syntax | Description |
| --- | ----------- |
| Header | Title |
| Paragraph | Text |

---

## Horizontal Rules

Three ways to make them:

---

***

___

---

## HTML Comments (Marker Tests)

<!-- Regular HTML comment -->

<!-- !! ATTENTION: This should highlight lime -->
<!-- ?? UNCERTAINTY: This should highlight purple -->
<!-- >> REFERENCE: This should highlight cyan -->

<!-- TODO: Keyword alias test - should be purple -->
<!-- FIXME: Another keyword test - should be lime -->
<!-- NOTE: Reference keyword - should be cyan -->

<!--
Multi-line HTML comment
!! with markers
?? on different lines
>> should all work
-->

---

## Special Elements

### Footnotes

Here's a sentence with a footnote[^1].

[^1]: This is the footnote content.

### Definition Lists (if supported)

Term 1
: Definition 1

Term 2
: Definition 2a
: Definition 2b

### Abbreviations (if supported)

The HTML specification is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]: World Wide Web Consortium

---

## Escaping

\*Not italic\*
\`Not code\`
\# Not a header
\[Not a link\](url)

---

## Mixed Content

> A blockquote with a list:
> - Item 1
> - Item 2
>
> And some `code` and a [link](https://example.com)

1. List item with **bold** and *italic*
2. Item with `inline code` and ~~strikethrough~~
3. Item with [link](https://example.com) and ![image](img.png)

---

## Edge Cases

### Empty Elements

-
>
#####

### Special Characters

&amp; &lt; &gt; &quot; &copy; &reg; &trade;

### Unicode

Emoji: 🎨 🚀 ✨ 💻 🔥
International: 日本語 中文 한국어 العربية עברית

### Long Content

This is a very long paragraph that should wrap properly and maintain consistent styling throughout the entire length of the text without any issues or problems with the syntax highlighting breaking or becoming inconsistent as the line extends beyond the normal viewport width.

---

## Summary

Use this file to verify:
1. **Headers** - Should they use a distinct color? Which one?
2. **Bold/Italic** - Proper emphasis styling
3. **Links** - Clickable appearance
4. **Code** - Clear distinction from prose
5. **Lists** - Bullet/number visibility
6. **Blockquotes** - Quote styling
7. **Tables** - Header vs cell distinction
8. **HTML Comments** - Marker highlighting works
