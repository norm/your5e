import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import Set
from tests.utils import into_dicts


class TestSetDirective:
    def test_basic_set_directive(self):
        content = textwrap.dedent(
            """\
            - Set
                - *key* Name
                - *value* Shade of the Mountain
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "set_1",
                "name": None,
                "comment": None,
                "key": "Name",
                "value": "Shade of the Mountain",
            }
        ]
        assert str(result[0]) == "Set: Name = 'Shade of the Mountain'"
        assert errors == []

    def test_set_with_comment(self):
        content = textwrap.dedent(
            """\
            - Set
                - *key* Age
                - *value* 23
                - *comment* young for an elf
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "set_1",
                "name": None,
                "comment": "young for an elf",
                "key": "Age",
                "value": "23",
            }
        ]
        assert str(result[0]) == "Set: Age = '23'"
        assert errors == []

    def test_shorthand_format(self):
        content = textwrap.dedent(
            """\
            - Set *Name* Shade of the Mountain
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "set_1",
                "name": None,
                "comment": None,
                "key": "Name",
                "value": "Shade of the Mountain",
            }
        ]
        assert str(result[0]) == "Set: Name = 'Shade of the Mountain'"
        assert errors == []

    def test_missing_key(self):
        content = textwrap.dedent(
            """\
            - Set
                - *value* Shade of the Mountain
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "key" argument is missing.',
            }
        ]

    def test_missing_value(self):
        content = textwrap.dedent(
            """\
            - Set
                - *key* Name
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "value" argument is missing.',
            }
        ]

    def test_missing_both_arguments(self):
        content = textwrap.dedent(
            """\
            - Set
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "key" argument is missing.',
            },
            {
                "line": 1,
                "text": 'Required "value" argument is missing.',
            },
        ]

    def test_empty_key(self):
        content = textwrap.dedent(
            """\
            - Set
                - *key*
                - *value* something
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "key" argument is missing.',
            }
        ]

    def test_empty_value(self):
        content = textwrap.dedent(
            """\
            - Set
                - *key* Name
                - *value*
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "value" argument is missing.',
            }
        ]

    def test_description_against_reference_toml(self):
        result, errors = RuleParser().parse_rules_file("docs/rules/directives/set.md")

        with open("tests/rules/directives/set.toml", "r") as f:
            expected_data = toml.load(f)

        # TOML doesn't have a null type by design so this
        # won't be 100% accurate here; fill in the blanks
        all_keys = {field.name for field in dataclasses.fields(Set)}
        for item in expected_data.get("set", []):
            for key in all_keys:
                if key not in item:
                    item[key] = None

        assert into_dicts(result) == expected_data["set"]

        with open("tests/rules/directives/set.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])

    def test_to_markdown(self):
        # Create Set objects from TOML data
        with open("tests/rules/directives/set.toml", "r") as f:
            toml_data = toml.load(f)

        set_objects = []
        for item in toml_data["set"]:
            set_obj = Set(
                id=item["id"],
                name=item.get("name"),
                comment=item.get("comment"),
                key=item["key"],
                value=item["value"],
            )
            set_objects.append(set_obj)

        # Test first object (with comment)
        expected_markdown_1 = textwrap.dedent(
            """\
            - Set
              - _key_ Name
              - _value_ Shade of the Mountain
              - _comment_ standard array
            """
        )
        assert set_objects[0].to_markdown() == expected_markdown_1

        # Test second object (no comment)
        expected_markdown_2 = textwrap.dedent(
            """\
            - Set _Age_ 23
            """
        )
        assert set_objects[1].to_markdown() == expected_markdown_2

        # Test third object (no comment)
        expected_markdown_3 = textwrap.dedent(
            """\
            - Set _Name_ Shade of the Mountain
            """
        )
        assert set_objects[2].to_markdown() == expected_markdown_3
