# Resource

Adding a resource type that can be used where actions are limited (eg. Ki
Points, charges in a magic staff) are added with the `Resource` directive.
It takes the following arguments and supports shorthand syntax:

- **Name** (mandatory), the name of the resource
- **Uses** (mandatory), how many times the resource can be used
- **Renew** (optional), when, if at all, the resource is renewed, values
  include:
    - rest, regained after a Short or Long Rest
    - long rest, regained only after a Long Rest
    - dawn, regained when the day starts
- **Regain** (optional), by how much the resource is renewed (defaults to all)

## Valid examples

### Second Wind
- Resource
    - _Name_ Second Wind
    - _Uses_ 1
    - _Renew_ rest

### Wand of Magic Missiles
- Resource
    - _Name_ Wand of Magic Missiles
    - _Uses_ 7
    - _Renew_ dawn
    - _Regain_ 1d6 + 1

### Charm of the Storm
- Resource _Charm of the Storm_ 3


## Invalid examples

### Missing keys
- Resource _Charm of the Storm_
- Resource
    - _Uses_ 7
    - _Renew_ long rest
