# Inventory

To add or remove items from a character's inventory, use the `Inventory`
directive. It has three arguments, and supports shorthand syntax:

- **Action** (mandatory) either `add` or `remove`
- **Item** (mandatory) the name of the item to add/remove
- **Count** (optional) how many of the item to add/remove


## Valid examples

- Inventory _add_ Chain Mail

- Inventory
    - _Action_ add
    - _Item_ Arrow
    - _Count_ 20


## Invalid examples

### Arguments to shorthand
- Inventory _remove_ Gold Piece
    - _Count_ 500

### Missing action
- Inventory
    - _Item_ Chain Mail

### Missing item
- Inventory
    - _Action_ add
    - _Count_ 5gp
