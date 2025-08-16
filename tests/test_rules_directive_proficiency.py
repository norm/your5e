import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import Proficiency
from .utils import into_dicts


class TestProficiency:
    def test_with_type_and_value(self):
        content = textwrap.dedent(
            """\
            - Proficiency
                - *type* weapon
                - *value* Martial
                - *comment* all Martial class weapons
            - Proficiency _saving throw_ Strength
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "proficiency_1",
                "name": None,
                "comment": "all Martial class weapons",
                "type": "weapon",
                "value": "Martial",
            },
            {
                "id": "proficiency_5",
                "name": None,
                "comment": None,
                "type": "saving throw",
                "value": "Strength",
            },
        ]
        assert str(result[0]) == "Proficiency: weapon Martial"
        assert str(result[1]) == "Proficiency: saving throw Strength"
        assert errors == []

    def test_valid_types(self):
        valid_types = [
            "armor",
            "initiative",
            "saving throw",
            "skill",
            "tool",
            "weapon",
        ]

        for proficiency_type in valid_types:
            content = textwrap.dedent(
                f"""\
                - Proficiency
                    - *type* {proficiency_type}
                    - *value* Test Value
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == [
                {
                    "id": "proficiency_1",
                    "name": None,
                    "comment": None,
                    "type": proficiency_type,
                    "value": "Test Value",
                },
            ]
            assert errors == []

    def test_case_insensitive_type(self):
        content = textwrap.dedent(
            """\
            - Proficiency
                - *type* WEAPON
                - *value* Longsword
            - Proficiency
                - *type* Saving Throw
                - *value* Constitution
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "proficiency_1",
                "name": None,
                "comment": None,
                "type": "weapon",
                "value": "Longsword",
            },
            {
                "id": "proficiency_4",
                "name": None,
                "comment": None,
                "type": "saving throw",
                "value": "Constitution",
            },
        ]
        assert errors == []

    def test_unknown_keys_ignored(self):
        content = textwrap.dedent(
            """\
            - Proficiency
                - *type* skill
                - *value* Stealth
                - *bonus* +2
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "proficiency_1",
                "name": None,
                "comment": None,
                "type": "skill",
                "value": "Stealth",
            }
        ]
        assert str(result[0]) == "Proficiency: skill Stealth"
        assert errors == []

    def test_invalid_type(self):
        content = textwrap.dedent(
            """\
            - Proficiency
                - *type* dancing
                - *value* Ballroom
            - Proficiency _spell_ Fireball
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 2,
                "text": 'Type "dancing" should be either '
                "armor, initiative, saving throw, skill, tool, weapon.",
            },
            {
                "line": 4,
                "text": 'Type "spell" should be either '
                "armor, initiative, saving throw, skill, tool, weapon.",
            },
        ]

    def test_missing_type(self):
        content = textwrap.dedent(
            """\
            - Proficiency
                - *value* Stealth
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "type" argument is missing.',
            },
        ]

    def test_missing_value(self):
        content = textwrap.dedent(
            """\
            - Proficiency
                - *type* skill
            - Proficiency _weapon_
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "value" argument is missing.',
            },
            {
                "line": 3,
                "text": 'Required "value" argument is missing.',
            },
        ]

    def test_empty_value(self):
        content = textwrap.dedent(
            """\
            - Proficiency
                - *type* tool
                - *value*
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "value" argument is missing.',
            },
        ]

    def test_description_against_reference_toml(self):
        result, errors = RuleParser().parse_rules_file(
            "docs/rules/directives/proficiency.md"
        )

        with open("tests/rules/directives/proficiency.toml", "r") as f:
            expected_data = toml.load(f)

        all_keys = {field.name for field in dataclasses.fields(Proficiency)}
        for item in expected_data.get("proficiency", []):
            for key in all_keys:
                if key not in item:
                    item[key] = None

        assert into_dicts(result) == expected_data["proficiency"]

        with open("tests/rules/directives/proficiency.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])
