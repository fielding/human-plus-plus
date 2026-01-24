# Human++ Markdown Test

Markdown doesn't have traditional comments, but HTML comments work:

<!-- !! This HTML comment marker SHOULD highlight -->
<!-- ?? Is this the right approach for markdown? -->
<!-- >> Decision: support HTML comments in markdown files -->

## Regular content

> Blockquote with *italic* and **bold** and a [link](https://example.com).

- List item with `inline code`
- Another item with `!!` in backticks (should NOT highlight - it's code)

## Code blocks

Code blocks should NOT have markers highlighted (they're not comments):

```ts
// !! This is inside a code block - extension won't see it as a real comment
const x = foo ?? bar;  // ?? also won't highlight
```

```python
# !! Same here - code block content is just text to markdown
def foo():
    pass
```

## Inline HTML

<span>Regular HTML tag</span>

<!--
!! Multi-line HTML comment
?? Does this work?
>> Testing directive in HTML comment
-->
