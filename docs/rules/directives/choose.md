# Choose

Where a character must choose one (or more) from a set of options, use the
Choose directive. It takes the following arguments:

- **Name** (mandatory), the name of the choice to be made
- **Count** (mandatory), the number of options that can be selected
- **Description** (optional, defaults to "Choose _n_ from the following") a
  short description of the choice
- **Option** (mandatory, multiple), a number of options

The options have a name, and contain any number of directives that to be
applied if that option is chosen.


## Valid example

### Equipment
- Choose _1_ First Equipment Choice
    - _Option_ chain mail
        - Inventory _add_ Chain Mail
    - _Option_ leather armor, longbow, and 20 arrows
        - Inventory _add_ Leather Armor
        - Inventory _add_ Longbow
        - Inventory
            - _Action_ add
            - _Item_ Arrow
            - _Count_ 20
- Choose _1_ Second Equipment Choice
    - _Option_ a martial weapon and a shield
        - Inventory _add_ Shield
        - Inventory _add_ Martial Weapon
    - _Option_ two martial weapons
        - Inventory _add_ Martial Weapon
        - Inventory _add_ Martial Weapon
- Choose _1_ Third Equipment Choice
    - _Option_ a light crossbow and 20 bolts
        - Inventory _add_ Light Crossbow
        - Inventory
            - _Action_ add
            - _Item_ Crossbow Bolt
            - _Count_ 20
    - _Option_ two handaxes
        - Inventory
            - _Action_ add
            - _Item_ Handaxe
            - _Count_ 2
- Choose _1_
    - _Option_ a dungeoneer's pack
        - Inventory _add_ Dungeoneer's Pack
    - _Option_ an explorer's pack
        - Inventory _add_ Explorer's Pack

### Languages
- Choose
    - _Count_ 2
    - _Name_ Class Languages
    - _Description_ Choose two more languages your character knows.
    - _Option_ Celestial
        - Language _Celestial_
    - _Option_ Infernal
        - Language _Infernal_
    - _Option_ Sylvan
        - Language _Sylvan_
    - _Option_ Undercommon
        - Language _Undercommon_


## Invalid example

### No count
- Choose
    - _Option_ Sylvan
        - Language _Sylvan_
    - _Option_ Undercommon
        - Language _Undercommon_

### Not enough options
- Choose _3_ Class Languages
    - _Option_ Sylvan
        - Language _Sylvan_
    - _Option_ Undercommon
        - Language _Undercommon_

### No directives
- Choose _3_ Class Languages
    - _Option_ Celestial
    - _Option_ Giant
    - _Option_ Goblin
    - _Option_ Infernal
    - _Option_ Sylvan
    - _Option_ Undercommon

### Non-option after options
- Choose _2_ Class Languages
    - _Option_ Celestial
        - Language _Celestial_
    - Language _Common_
    - _Description_ Choose two more languages your character knows.
    - _Option_ Infernal
        - Language _Infernal_
    - _Option_ Sylvan
        - Language _Sylvan_
    - _Option_ Undercommon
        - Language _Undercommon_

### No options
- Choose _2_ Class Languages
