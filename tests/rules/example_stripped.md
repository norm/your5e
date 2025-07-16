# Hit Die

Hit Die are added to characters with the 'Hit Die' directive. It takes
three arguments:

- **Die** (mandatory), what size die to use
- **Value** (optional), the value to use; if no value is specified, the average rounded up is used
- **Name** (optional), the name of the die

## Valid examples

## Fighter, Level 1

## Barbarian, Level 3

## Wizard, Level 1


## Any non-directive lines terminate directive processing

The first level always takes the maximum value of a Hit Die.

- Hit Die
    - *Die* d10
    - *Value* 10


## Invalid examples

## Missing key, only value

## Keys are not differentiated with asterisks

## Values are invalid

## Indentation is significant
    - Hit Die
        - *Die* d6

## Unknown directive
