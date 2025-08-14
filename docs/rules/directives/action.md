# Action

Actions a character can take are added with the `Action` directive. It takes
the following arguments:

- **Name** (mandatory), the name of the action to take
- **Description** (mandatory), a short reminder of what the action does
- **Uses** (optional), the [Resource](resource.md) the action uses, if any
- **Effect** (optional), the effect the action has, if any
- **Amount** (optional), how much `effect` the action produces, if any
- **Roll** (optional), if the action requires a roll, what to roll

There are three types of actions, which all take the same arguments:

- Action
- Bonus Action
- Reaction


## Valid examples

### Unarmed Strike
- Action
    - *name* Unarmed Strike
    - *description* Make a melee attack with your elbow, knee, etc.
    - *roll* d20
    - *effect* harm
    - *amount* 1 + {STRENGTH_MOD}

### Second Wind
- Bonus Action
    - *name* Second Wind
    - *description* Regain 1d10 + {FIGHTER} Hit Points between rests.
    - *uses* Second Wind
    - *effect* heal
    - *amount* 1d10 + {FIGHTER}

### Counterspell
- Reaction
    - *name* Counterspell
    - *description* Attempt to interrupt a creature casting a spell.
    - *uses* Spell Slot


## Invalid examples

### Shorthand not supported

- Action _Unarmed Strike_ 1+{STRENGTH_MOD}
- Reaction _Opportunity Attack_ When a creature leaves your reach.

### Name and description are mandatory

- Action
    - Uses _Ki_
    - Description _Spend 4 Ki to become invisible._
    - Uses _Ki, 4_

- Bonus Action
    - Name _Flurry of Blows_
    - Uses _Ki_
