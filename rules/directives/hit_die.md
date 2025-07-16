# Hit Die

Hit Die are added to characters with the 'Hit Die' directive. It takes
three arguments:

- **Die** (mandatory), what size die to use
- **Value** (optional), the value to use; if no value is specified, the average rounded up is used
- **Name** (optional), the name of the die

## Valid examples

## Fighter, Level 1
- Hit Die
    - *Die* d10
    - *Value* 10
    - *Comment* Always max for a character's first level

## Barbarian, Level 3
- hit die
    - *Die* d12

## Wizard, Level 1
- hit Die
    - *die* D6


## Invalid examples

## Missing key, only value
- Hit Die
    - d12

## Keys are not differentiated with asterisks
- Hit Die
    - die d6
    - value 3

## Values are invalid
- Hit Die
    - *Die* d40
- Hit Die
    - *Die* d6
    - *Value* 7
- Hit Die
    - *Die* d6
    - *Value* 0
- Hit Die
    - *Die* d6
    - *Value* six
- Hit Die
    - *Die* 8

## Indentation is significant
    - Hit Die
        - *Die* d6
