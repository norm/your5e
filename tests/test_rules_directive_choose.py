import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import Choose
from .utils import into_dicts


class TestChoose:
    def test_basic_choose_with_options(self):
        content = textwrap.dedent(
            """\
            - Choose _1_ First Equipment Choice
                - _Option_ chain mail
                    - Inventory _add_ Chain Mail
                - _Option_ leather armor
                    - Inventory _add_ Leather Armor
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "choose_1",
                "name": "First Equipment Choice",
                "comment": None,
                "count": 1,
                "description": None,
                "options": [
                    {
                        "name": "chain mail",
                        "directives": [
                            {
                                "id": "inventory_1",
                                "name": None,
                                "comment": None,
                                "action": "add",
                                "item": "Chain Mail",
                                "count": None,
                            }
                        ],
                    },
                    {
                        "name": "leather armor",
                        "directives": [
                            {
                                "id": "inventory_1",
                                "name": None,
                                "comment": None,
                                "action": "add",
                                "item": "Leather Armor",
                                "count": None,
                            }
                        ],
                    },
                ],
            },
        ]
        assert str(result[0]) == "Choose: First Equipment Choice (1 from 2 options)"
        assert errors == []

    def test_choose_with_description(self):
        content = textwrap.dedent(
            """\
            - Choose _2_ Class Languages
                - _Description_ Choose two more languages your character knows.
                - _Option_ Celestial
                    - Language _Celestial_
                - _Option_ Infernal
                    - Language _Infernal_
                - _Option_ Sylvan
                    - Language _Sylvan_
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "choose_1",
                "name": "Class Languages",
                "comment": None,
                "count": 2,
                "description": "Choose two more languages your character knows.",
                "options": [
                    {
                        "name": "Celestial",
                        "directives": [
                            {
                                "id": "language_1",
                                "name": "Celestial",
                                "comment": None,
                            }
                        ],
                    },
                    {
                        "name": "Infernal",
                        "directives": [
                            {
                                "id": "language_1",
                                "name": "Infernal",
                                "comment": None,
                            }
                        ],
                    },
                    {
                        "name": "Sylvan",
                        "directives": [
                            {
                                "id": "language_1",
                                "name": "Sylvan",
                                "comment": None,
                            }
                        ],
                    },
                ],
            },
        ]
        assert str(result[0]) == "Choose: Class Languages (2 from 3 options)"
        assert errors == []

    def test_choose_unnamed(self):
        content = textwrap.dedent(
            """\
            - Choose _1_
                - _Option_ a dungeoneer's pack
                    - Inventory _add_ Dungeoneer's Pack
                - _Option_ an explorer's pack
                    - Inventory _add_ Explorer's Pack
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "choose_1",
                "name": None,
                "comment": None,
                "count": 1,
                "description": None,
                "options": [
                    {
                        "name": "a dungeoneer's pack",
                        "directives": [
                            {
                                "id": "inventory_1",
                                "name": None,
                                "comment": None,
                                "action": "add",
                                "item": "Dungeoneer's Pack",
                                "count": None,
                            }
                        ],
                    },
                    {
                        "name": "an explorer's pack",
                        "directives": [
                            {
                                "id": "inventory_1",
                                "name": None,
                                "comment": None,
                                "action": "add",
                                "item": "Explorer's Pack",
                                "count": None,
                            }
                        ],
                    },
                ],
            },
        ]
        assert str(result[0]) == "Choose: (1 from 2 options)"
        assert errors == []

    def test_option_with_multiple_directives(self):
        content = textwrap.dedent(
            """\
            - Choose _1_ Equipment Choice
                - _Option_ bow and arrows
                    - Inventory _add_ Longbow
                    - Inventory
                        - _Action_ add
                        - _Item_ Arrow
                        - _Count_ 20
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "choose_1",
                "name": "Equipment Choice",
                "comment": None,
                "count": 1,
                "description": None,
                "options": [
                    {
                        "name": "bow and arrows",
                        "directives": [
                            {
                                "id": "inventory_1",
                                "name": None,
                                "comment": None,
                                "action": "add",
                                "item": "Longbow",
                                "count": None,
                            },
                            {
                                "id": "inventory_2",
                                "name": None,
                                "comment": None,
                                "action": "add",
                                "item": "Arrow",
                                "count": 20,
                            },
                        ],
                    },
                ],
            },
        ]
        assert str(result[0]) == "Choose: Equipment Choice (1 from 1 options)"
        assert errors == []

    def test_missing_count(self):
        content = textwrap.dedent(
            """\
            - Choose
                - _Option_ Sylvan
                    - Language _Sylvan_
                - _Option_ Undercommon
                    - Language _Undercommon_
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        # When count is missing, the main parser also generates "Argument has no key"
        # errors for nested content, so we check that count missing error is present
        assert any(
            error["text"] == 'Required "count" argument is missing.' for error in errors
        )
        assert len(errors) >= 1

    def test_not_enough_options(self):
        content = textwrap.dedent(
            """\
            - Choose _3_ Class Languages
                - _Option_ Sylvan
                    - Language _Sylvan_
                - _Option_ Undercommon
                    - Language _Undercommon_
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": "Not enough options to choose from.",
            },
        ]

    def test_options_without_directives(self):
        content = textwrap.dedent(
            """\
            - Choose _3_ Class Languages
                - _Option_ Celestial
                - _Option_ Giant
                - _Option_ Goblin
                - _Option_ Infernal
                - _Option_ Sylvan
                - _Option_ Undercommon
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 2,
                "text": "Option must contain at least one directive.",
            },
            {
                "line": 3,
                "text": "Option must contain at least one directive.",
            },
            {
                "line": 4,
                "text": "Option must contain at least one directive.",
            },
            {
                "line": 5,
                "text": "Option must contain at least one directive.",
            },
            {
                "line": 6,
                "text": "Option must contain at least one directive.",
            },
            {
                "line": 7,
                "text": "Option must contain at least one directive.",
            },
        ]

    def test_invalid_count(self):
        content = textwrap.dedent(
            """\
            - Choose _not_a_number_ Class Languages
                - _Option_ Sylvan
                    - Language _Sylvan_
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Count "not_a_number" should be a positive integer.',
            },
        ]

    def test_zero_count(self):
        content = textwrap.dedent(
            """\
            - Choose _0_ Class Languages
                - _Option_ Sylvan
                    - Language _Sylvan_
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Count "0" should be a positive integer.',
            },
        ]

    def test_description_against_reference_toml(self):
        result, errors = RuleParser().parse_rules_file(
            "docs/rules/directives/choose.md"
        )

        with open("tests/rules/directives/choose.toml", "r") as f:
            expected_data = toml.load(f)

        all_keys = {field.name for field in dataclasses.fields(Choose)}
        for item in expected_data.get("choose", []):
            for key in all_keys:
                if key not in item:
                    item[key] = None

            # Also fill in missing fields for nested directives
            if "options" in item and item["options"]:
                for option in item["options"]:
                    if "directives" in option and option["directives"]:
                        for directive in option["directives"]:
                            # Add common directive fields that might be missing
                            if "name" not in directive:
                                directive["name"] = None
                            if "comment" not in directive:
                                directive["comment"] = None
                            # Only add count for Inventory directives
                            if "action" in directive and "count" not in directive:
                                directive["count"] = None

        assert into_dicts(result) == expected_data["choose"]

        with open("tests/rules/directives/choose.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])

    def test_to_markdown(self):
        # Use existing test that parses full Choose objects from markdown
        # Avoids manually constructing complex nested structure
        result, errors = RuleParser().parse_rules_file(
            "docs/rules/directives/choose.md"
        )

        # Get successfully parsed Choose objects (ignore invalid examples)
        choose_objects = [obj for obj in result if isinstance(obj, Choose)]

        # Test first object (has name, no description - should use shorthand)
        expected_markdown_1 = textwrap.dedent(
            """\
            - Choose _1_ First Equipment Choice
                - _Option_ chain mail
                    - Inventory _add_ Chain Mail
                - _Option_ leather armor, longbow, and 20 arrows
                    - Inventory _add_ Leather Armor
                    - Inventory _add_ Longbow
                    - Inventory
                      - _action_ add
                      - _item_ Arrow
                      - _count_ 20
            """
        )
        assert choose_objects[0].to_markdown() == expected_markdown_1

        # Test second object (has name, no description - should use shorthand)
        expected_markdown_2 = textwrap.dedent(
            """\
            - Choose _1_ Second Equipment Choice
                - _Option_ a martial weapon and a shield
                    - Inventory _add_ Shield
                    - Inventory _add_ Martial Weapon
                - _Option_ two martial weapons
                    - Inventory _add_ Martial Weapon
                    - Inventory _add_ Martial Weapon
            """
        )
        assert choose_objects[1].to_markdown() == expected_markdown_2

        # Test third object (has name, no description - should use shorthand)
        expected_markdown_3 = textwrap.dedent(
            """\
            - Choose _1_ Third Equipment Choice
                - _Option_ a light crossbow and 20 bolts
                    - Inventory _add_ Light Crossbow
                    - Inventory
                      - _action_ add
                      - _item_ Crossbow Bolt
                      - _count_ 20
                - _Option_ two handaxes
                    - Inventory
                      - _action_ add
                      - _item_ Handaxe
                      - _count_ 2
            """
        )
        assert choose_objects[2].to_markdown() == expected_markdown_3

        # Test fourth object (no name, no description - should use special shorthand)
        expected_markdown_4 = textwrap.dedent(
            """\
            - Choose _1_
                - _Option_ a dungeoneer's pack
                    - Inventory _add_ Dungeoneer's Pack
                - _Option_ an explorer's pack
                    - Inventory _add_ Explorer's Pack
            """
        )
        assert choose_objects[3].to_markdown() == expected_markdown_4

        # Test fifth object (has name and description - should use full format)
        expected_markdown_5 = textwrap.dedent(
            """\
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
            """
        )
        assert choose_objects[4].to_markdown() == expected_markdown_5
