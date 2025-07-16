rules parsing
=============

Rules, as understood both by players and GMs, and by the tools, will be
implemented in Markdown. This makes it easy to use and to edit.

Whilst being in Markdown, there will be constraints on the formatting so
that the tools can understand and use them too.


## Directives

Directives are instructions to the tools rather than to human beings. They
control how class features and interactables (such as basic equipment,
weapons, and magic items) are understood by the `your5e` tools.

They look like:

```markdown
# Fighter, Level 1

- Hit Die
    - _die_ d10
    - _value_ 10

At first level, …
```

The directives will **only** be understood by `your5e` at the first thing in a
file, or directly after a heading. Anywhere else, they will be assumed to be
a normal Markdown list. This would not be seen as a directive:

```markdown
# Fighter, Level 1

Fighters get a d10 hit die.

- Hit Die
    - *Die* d10
````

Directives can be separated by blank lines for visual spacing, but any textual
content will end a directive block.


### Available Directives

- [Hit Die](directives/hit_die.md)
