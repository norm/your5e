# Set

Some values are unique, such as a character's name. They are set with the 'Set' directive. It has only two arguments:

- **Key** (mandatory), what key to set
- **Value** (mandatory), what to set the key to


## Valid examples

### Character Sheet
- Set
    - *key* Name
    - *value* Shade of the Mountain
    - *comment* standard array
- Set
    - *key* Age
    - *value* 23

### Shorthand format
- Set *Name* Shade of the Mountain


## Invalid examples

### Missing arguments
- Set
- Set
    - *key* Name
- Set
    - *value* Shade of the Mountain
- Set
    - *Name* Shade of the Mountain
