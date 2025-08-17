import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import Inventory
from tests.utils import into_dicts


class TestInventoryDirective:
    def test_basic_inventory_add_directive(self):
        content = textwrap.dedent(
            """\
            - Inventory
                - *Action* add
                - *Item* Chain Mail
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "inventory_1",
                "name": None,
                "comment": None,
                "action": "add",
                "item": "Chain Mail",
                "count": None,
            }
        ]
        assert str(result[0]) == "Inventory: add Chain Mail"
        assert errors == []

    def test_basic_inventory_remove_directive(self):
        content = textwrap.dedent(
            """\
            - Inventory
                - *Action* remove
                - *Item* Gold Piece
                - *Count* 500
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "inventory_1",
                "name": None,
                "comment": None,
                "action": "remove",
                "item": "Gold Piece",
                "count": 500,
            }
        ]
        assert str(result[0]) == "Inventory: remove Gold Piece (500)"
        assert errors == []

    def test_inventory_with_comment(self):
        content = textwrap.dedent(
            """\
            - Inventory
                - *Action* add
                - *Item* Arrow
                - *Count* 20
                - *comment* restocking ammunition
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "inventory_1",
                "name": None,
                "comment": "restocking ammunition",
                "action": "add",
                "item": "Arrow",
                "count": 20,
            }
        ]
        assert str(result[0]) == "Inventory: add Arrow (20)"
        assert errors == []

    def test_shorthand_format_add(self):
        content = textwrap.dedent(
            """\
            - Inventory *add* Chain Mail
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "inventory_1",
                "name": None,
                "comment": None,
                "action": "add",
                "item": "Chain Mail",
                "count": None,
            }
        ]
        assert str(result[0]) == "Inventory: add Chain Mail"
        assert errors == []

    def test_regular_format_with_count(self):
        content = textwrap.dedent(
            """\
            - Inventory
                - _Action_ remove
                - _Item_ Gold Piece
                - _Count_ 500
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "inventory_1",
                "name": None,
                "comment": None,
                "action": "remove",
                "item": "Gold Piece",
                "count": 500,
            }
        ]
        assert str(result[0]) == "Inventory: remove Gold Piece (500)"
        assert errors == []

    def test_missing_action(self):
        content = textwrap.dedent(
            """\
            - Inventory
                - *Item* Chain Mail
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "action" argument is missing.',
            }
        ]

    def test_missing_item(self):
        content = textwrap.dedent(
            """\
            - Inventory
                - *Action* add
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "item" argument is missing.',
            }
        ]

    def test_missing_both_required_arguments(self):
        content = textwrap.dedent(
            """\
            - Inventory
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "action" argument is missing.',
            },
            {
                "line": 1,
                "text": 'Required "item" argument is missing.',
            },
        ]

    def test_invalid_action(self):
        content = textwrap.dedent(
            """\
            - Inventory
                - *Action* steal
                - *Item* Gold Piece
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 2,
                "text": 'Action is either "add" or "remove".',
            }
        ]

    def test_empty_item(self):
        content = textwrap.dedent(
            """\
            - Inventory
                - *Action* add
                - *Item*
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "item" argument is missing.',
            }
        ]

    def test_invalid_count_not_number(self):
        content = textwrap.dedent(
            """\
            - Inventory
                - *Action* add
                - *Item* Arrow
                - *Count* many
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 4,
                "text": 'Count "many" should be a positive integer.',
            }
        ]

    def test_invalid_count_negative(self):
        content = textwrap.dedent(
            """\
            - Inventory
                - *Action* add
                - *Item* Arrow
                - *Count* -5
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 4,
                "text": 'Count "-5" should be a positive integer.',
            }
        ]

    def test_invalid_count_zero(self):
        content = textwrap.dedent(
            """\
            - Inventory
                - *Action* add
                - *Item* Arrow
                - *Count* 0
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 4,
                "text": 'Count "0" should be a positive integer.',
            }
        ]

    def test_description_against_reference_toml(self):
        result, errors = RuleParser().parse_rules_file(
            "docs/rules/directives/inventory.md"
        )

        with open("tests/rules/directives/inventory.toml", "r") as f:
            expected_data = toml.load(f)

        # TOML doesn't have a null type by design so this
        # won't be 100% accurate here; fill in the blanks
        all_keys = {field.name for field in dataclasses.fields(Inventory)}
        for item in expected_data.get("inventory", []):
            for key in all_keys:
                if key not in item:
                    item[key] = None

        assert into_dicts(result) == expected_data["inventory"]

        with open("tests/rules/directives/inventory.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])

    def test_to_markdown(self):
        # Create Inventory objects from TOML data
        with open("tests/rules/directives/inventory.toml", "r") as f:
            toml_data = toml.load(f)

        inventory_objects = []
        for item in toml_data["inventory"]:
            inventory_obj = Inventory(
                id=item["id"],
                name=item.get("name"),
                comment=item.get("comment"),
                action=item["action"],
                item=item["item"],
                count=item.get("count"),
            )
            inventory_objects.append(inventory_obj)

        # Test first object (no count - should use shorthand)
        expected_markdown_1 = textwrap.dedent(
            """\
            - Inventory _add_ Chain Mail
            """
        )
        assert inventory_objects[0].to_markdown() == expected_markdown_1

        # Test second object (with count - should use full format)
        expected_markdown_2 = textwrap.dedent(
            """\
            - Inventory
              - _action_ add
              - _item_ Arrow
              - _count_ 20
            """
        )
        assert inventory_objects[1].to_markdown() == expected_markdown_2
