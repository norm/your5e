# Break

When Markdown description is formatted closely enough to a directive that
the parser would be confused, use the `Break` directive to tell it not to
continue looking for directives until the next header.

It takes no arguments.


## Valid examples

### Hit Points
- Break

- **Hit Dice:** 1d12 per barbarian level
- **Hit Points at 1st Level:** 12 + your Constitution modifier
- **Hit Points at Higher Levels:** 1d12 (or 7) + your Constitution modifier per barbarian level after 1st


### Supports universal arguments
- Break
    - _comment_ hit points look like directives


## Working, but invalid examples

Extra unknown arguments are ignored by definition, so this will trigger
break, but the "why" arguments are not stored.

### Has no special arguments
- Break _why_ formatting
- Break
    - _why_ formatting
