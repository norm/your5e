# Ability Score

Ability Scores are set and adjusted with the 'Ability Score' directive. It
takes the following arguments and supports a shorthand syntax:

- **Ability** (mandatory), what ability to adjust
- **Value** (optional), what to set the ability to
    - `15` to set ability score to an absolute value
    - `+2 / -3` will increase or decrease the established score
- **Override** (optional), override the current score in some way:
    - `19` set the value
    - `minimum 19` increase the value if lower, but not decrease it
      if it is higher
    - `+2 / -3` will increase or decrease the score
    - `+2, maximum 20` will increase the score but not past 20

Override is typically used on temporary effects and magic items, so that the
"real" underlying ability score is not changed.

Although `value` and `override` are both optional, one must be present
(but not both).


## Valid examples

### Character Sheet
- Ability Score
    - *ability* Dexterity
    - *value* 15
    - *comment* standard array
- Ability Score *Strength* 8

### Dragonborn
- Ability Score
    - *ability* Strength
    - *value* +2
- Ability Score *charisma* +1

### Belt of Hill Giant Strength
- Ability Score
    - *ability* Strength
    - *override* 21

### Headband of Intellect
- Ability Score
    - *ability* Intelligence
    - *override* minimum 19

### Belt of Dwarvenkind
- Ability Score
    - *ability* Constitution
    - *override* +2, maximum 20


## Invalid examples

## Missing keys
- Ability Score
    - Wisdom
    - 15

## No score
- Ability Score *wisdom*

## Invalid values
- Ability Score
    - *ability* Charisma
    - *value* 21
- Ability Score
    - *ability* Intelligence
    - *value* 1
- Ability Score
    - *ability* Dexterity
    - *value* high

## Invalid Ability
- Ability Score
    - *ability* Finesse
    - *value* 15
- Ability Score *dancing* 18

## Needs one (only) of value or override
- Ability Score
    - *ability* Strength
- Ability Score
    - *ability* Constitution
    - *value* 18
    - *override* +2
