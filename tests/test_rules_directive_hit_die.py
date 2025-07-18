import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import HitDie
from .utils import into_dicts


class TestHitDie:
    def test_with_value(self):
        content = textwrap.dedent(
            """\
            - Hit Die
                - *Die* d10
                - *Value* 10
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_1",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 10,
            }
        ]
        assert errors == []

    def test_without_value_gets_average(self):
        content = textwrap.dedent(
            """\
            - Hit Die
                - *Die* d10
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_1",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 6,
            }
        ]
        assert errors == []

    def test_valid_average_values(self):
        test_cases = [
            (4, 3),
            (6, 4),
            (8, 5),
            (10, 6),
            (12, 7),
            (20, 11),
        ]

        for die, average in test_cases:
            content = textwrap.dedent(
                f"""\
                - Hit Die
                    - *Die* d{die}
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == [
                {
                    "id": "hitdie_1",
                    "name": None,
                    "comment": None,
                    "die": die,
                    "value": average,
                }
            ]
            assert errors == []

    def test_parse_multiple_hit_dice(self):
        content = textwrap.dedent(
            """\
            - Hit Die
                - *Die* d8
                - *Value* 8
            - Hit Die
                - *Die* d8
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {"id": "hitdie_1", "name": None, "comment": None, "die": 8, "value": 8},
            {"id": "hitdie_4", "name": None, "comment": None, "die": 8, "value": 5},
        ]
        assert errors == []

    def test_shorthand_format(self):
        content = textwrap.dedent(
            """\
            - Hit Die **d10** 8
            - Hit Die _d6_
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_1",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 8,
            },
            {
                "id": "hitdie_2",
                "name": None,
                "comment": None,
                "die": 6,
                "value": 4,
            },
        ]
        assert errors == []

    def test_invalid_die_types(self):
        for die in ["d3", "d5", "d40", "d100"]:
            content = textwrap.dedent(
                f"""\
                - Hit Die
                    - *Die* {die}
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == []
            assert errors == [
                {
                    "line": 2,
                    "text": f'Die "{die}" is not a standard die.',
                }
            ]

        content = textwrap.dedent(
            """\
            - Hit Die *d3* 2
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Die "d3" is not a standard die.',
            }
        ]

    def test_invalid_values(self):
        for value in [-1, 0, 7, 8]:
            content = textwrap.dedent(
                f"""\
                - Hit Die
                    - *Die* d6
                    - *Value* {value}
                - Hit Die *d6* {value}
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == []
            assert errors == [
                {
                    "line": 3,
                    "text": f'Value "{value}" is out of range.',
                },
                {
                    "line": 4,
                    "text": f'Value "{value}" is out of range.',
                },
            ]

        content = textwrap.dedent(
            """\
            - Hit Die
                - *Die* d6
                - *Value* six
            - Hit Die *d6* six
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 3,
                "text": 'Value "six" is not a number.',
            },
            {
                "line": 4,
                "text": 'Value "six" is not a number.',
            },
        ]

    def test_missing_required_die(self):
        content = textwrap.dedent(
            """\
            - Hit Die
                - *Value* 5
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "die" argument is missing.',
            },
        ]

    def test_invalid_die_format(self):
        content = textwrap.dedent(
            """\
            - Hit Die
                - *Die* 10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 2,
                "text": 'Die "10" is not a die.',
            },
        ]

    def test_unknown_keys_ignored(self):
        content = textwrap.dedent(
            """\
            - Hit Die
                - *Die* d10
                - *Value* 4
                - *Ability* Strength
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {"id": "hitdie_1", "name": None, "comment": None, "die": 10, "value": 4}
        ]
        assert errors == []

    def test_description_against_reference_toml(self):
        result, errors = RuleParser().parse_rules_file("rules/directives/hit_die.md")

        with open("tests/rules/directives/hit_die.toml", "r") as f:
            expected_data = toml.load(f)

        # TOML doesn't have a null type by design so this
        # won't be 100% accurate here; fill in the blanks
        all_keys = {field.name for field in dataclasses.fields(HitDie)}
        for item in expected_data.get("hit_die", []):
            for key in all_keys:
                if key not in item:
                    item[key] = None

        assert into_dicts(result) == expected_data["hit_die"]

        with open("tests/rules/directives/hit_die.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])
