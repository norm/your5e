# Register

To add a new feature, such as an ability score or skill to a character sheet,
use the `Register` directive. It has two arguments, and supports shorthand
syntax:

- **Type** (mandatory) the type of feature, which can be one of:
    - _Ability Score_, to add an ability score to the character sheet
    - _Roll_, to add a d20 based check the character can make
    - _Skill_, to add a skill to the skills list
- **Name** (mandatory) the name of the registered feature


## Valid examples

- Register _Ability Score_ Dexterity
- Register _Skill_ Acrobatics (Dexterity)
- Register
    - _type_ Roll
    - _name_ Initiative


## Invalid examples

### Missing arguments
- Register
- Register _Skill_
- Register
    - _name_ Initiative

### Unknown type
- Register _Armor Class_ 15
- Register _Inventory_ Bag of Holding

### Arguments to shorthand
- Register _Skill_ Stealth
    - _uses_ Dexterity
