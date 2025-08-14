# Proficiency

Character proficiencies are added with the `Proficiency` directive. It
takes the following arguments and supports shorthand syntax:

- **Type** (mandatory), what type of proficiency to gain, for example:
    - armor
    - weapon
    - skill
- **Value** (mandatory), within the type, what to become proficient in,
  for example:
    - Light Armor
    - Quarterstaff
    - Stealth


## Valid examples

### Fighter, Level 1
- Proficiency
    - _type_ weapon
    - _value_ Martial
    - _comment_ all Martial class weapons
- Proficiency _saving throw_ Strength
- Proficiency _saving throw_ Constitution


## Invalid examples

### Missing keys
- Proficiency
    - _type_ Weapons
- Proficiency
    - _value_ Stealth

### Invalid shorthand
- Proficiency _weapon_
- Proficiency _Stealth_
