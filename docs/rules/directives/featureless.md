# Featureless

When a character or class description is explanatory text rather than a
feature to include on a character sheet, it can be marked with the
'Featureless' directive, which causes that entire section to be skipped.

It takes no arguments.


## Valid examples

### Class Features
- Featureless

As a barbarian, you gain the following class features.

### Supports universal arguments
- Featureless
    - _comment_ unnecessary


## Working, but invalid examples

Extra unknown arguments are ignored by definition, so this will trigger
featureless, but the "why" arguments are not stored.

### Has no special arguments
- Featureless _why_ unnecessary
- Featureless
    - _why_ unnecessary
