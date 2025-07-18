import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import AbilityScore
from .utils import into_dicts


class TestAbilityScore:
    def test_with_value(self):
        content = textwrap.dedent(
            """\
            - Ability Score
                - *ability* Dexterity
                - *value* 15
                - *comment* standard array
            - Ability Score *Strength* 8
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "abilityscore_1",
                "name": None,
                "comment": "standard array",
                "ability": "dexterity",
                "value": "15",
                "override": None,
                "minimum": None,
                "maximum": None,
            },
            {
                "id": "abilityscore_5",
                "name": None,
                "comment": None,
                "ability": "strength",
                "value": "8",
                "override": None,
                "minimum": None,
                "maximum": None,
            },
        ]
        assert errors == []

    def test_abilities(self):
        valid_abilities = [
            "STRENGTH",
            "DEXTERITY",
            "CONSTITUTION",
            "INTELLIGENCE",
            "WISDOM",
            "CHARISMA",
        ]

        for ability in valid_abilities:
            content = textwrap.dedent(
                f"""\
                - Ability Score
                    - *ability* {ability}
                    - *value* 15
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == [
                {
                    "id": "abilityscore_1",
                    "name": None,
                    "comment": None,
                    "ability": ability.lower(),
                    "value": "15",
                    "override": None,
                    "minimum": None,
                    "maximum": None,
                },
            ]
            assert errors == []

    def test_unknown_keys_ignored(self):
        content = textwrap.dedent(
            """\
            - Ability Score
                - *ability* Strength
                - *value* 15
                - *die* d20
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "abilityscore_1",
                "name": None,
                "comment": None,
                "ability": "strength",
                "value": "15",
                "override": None,
                "minimum": None,
                "maximum": None,
            }
        ]
        assert errors == []

    def test_with_modifier_value(self):
        content = textwrap.dedent(
            """\
            - Ability Score
                - *ability* Strength
                - *value* +2
            - Ability Score *constitution* -1
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "abilityscore_1",
                "name": None,
                "comment": None,
                "ability": "strength",
                "value": "+2",
                "override": None,
                "minimum": None,
                "maximum": "20",
            },
            {
                "id": "abilityscore_4",
                "name": None,
                "comment": None,
                "ability": "constitution",
                "value": "-1",
                "override": None,
                "minimum": "1",
                "maximum": None,
            },
        ]
        assert errors == []

    def test_with_override(self):
        content = textwrap.dedent(
            """\
            - Ability Score
                - *ability* Strength
                - *override* 21
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "abilityscore_1",
                "name": None,
                "comment": None,
                "ability": "strength",
                "value": None,
                "override": "21",
                "minimum": None,
                "maximum": None,
            }
        ]
        assert errors == []

    def test_with_modifier_constraints(self):
        content = textwrap.dedent(
            """\
            - Ability Score
                - *ability* Intelligence
                - *override* minimum 19
            - Ability Score
                - *ability* Constitution
                - *override* +2, maximum 20
            - Ability Score
                - *ability* Strength
                - *override* maximum 10
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "abilityscore_1",
                "name": None,
                "comment": None,
                "ability": "intelligence",
                "value": None,
                "override": "19",
                "minimum": "19",
                "maximum": None,
            },
            {
                "id": "abilityscore_4",
                "name": None,
                "comment": None,
                "ability": "constitution",
                "value": None,
                "override": "+2",
                "minimum": None,
                "maximum": "20",
            },
            {
                "id": "abilityscore_7",
                "name": None,
                "comment": None,
                "ability": "strength",
                "value": None,
                "override": "10",
                "minimum": None,
                "maximum": "10",
            },
        ]
        assert errors == []

    def test_override_modifier_default_bounds(self):
        content = textwrap.dedent(
            """\
            - Ability Score
                - *ability* Strength
                - *override* +2
            - Ability Score
                - *ability* Dexterity
                - *override* -1
            - Ability Score
                - *ability* Constitution
                - *override* +3, maximum 25
            - Ability Score
                - *ability* Intelligence
                - *override* -2, minimum 3
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "abilityscore_1",
                "name": None,
                "comment": None,
                "ability": "strength",
                "value": None,
                "override": "+2",
                "minimum": None,
                "maximum": "30",
            },
            {
                "id": "abilityscore_4",
                "name": None,
                "comment": None,
                "ability": "dexterity",
                "value": None,
                "override": "-1",
                "minimum": "1",
                "maximum": None,
            },
            {
                "id": "abilityscore_7",
                "name": None,
                "comment": None,
                "ability": "constitution",
                "value": None,
                "override": "+3",
                "minimum": None,
                "maximum": "25",
            },
            {
                "id": "abilityscore_10",
                "name": None,
                "comment": None,
                "ability": "intelligence",
                "value": None,
                "override": "-2",
                "minimum": "3",
                "maximum": None,
            },
        ]
        assert errors == []

    def test_invalid_ability(self):
        content = textwrap.dedent(
            """\
            - Ability Score
                - *ability* Finesse
                - *value* 15
            - Ability Score *dancing* 12
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 2,
                "text": '"Finesse" is not an ability.',
            },
            {
                "line": 4,
                "text": '"dancing" is not an ability.',
            },
        ]

    def test_missing_ability(self):
        content = textwrap.dedent(
            """\
            - Ability Score
                - *value* 15
            - Ability Score
                - *override* 15
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "ability" argument is missing.',
            },
            {
                "line": 3,
                "text": 'Required "ability" argument is missing.',
            },
        ]

    def test_value_and_override_are_mutual_but_required(self):
        content = textwrap.dedent(
            """\
            - Ability Score
                - *ability* Strength
            - Ability Score *dexterity*
            - Ability Score
                - *ability* Strength
                - *value* 15
                - *override* 21
            - Ability Score
                - *ability* Dexterity
                - *value* 12
                - *override* +2
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Either "value" or "override" must be specified.',
            },
            {
                "line": 3,
                "text": 'Either "value" or "override" must be specified.',
            },
            {
                "line": 4,
                "text": 'Only one of "value" and "override" can be specified.',
            },
            {
                "line": 8,
                "text": 'Only one of "value" and "override" can be specified.',
            },
        ]

    def test_invalid_out_of_range(self):
        for value in [1, 2, 19, 20, 21]:
            content = textwrap.dedent(
                f"""\
                - Ability Score
                    - *ability* Charisma
                    - *value* {value}
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == []
            assert errors == [
                {
                    "line": 3,
                    "text": f'Value "{value}" is out of range (3-18).',
                }
            ]

        for value in [0, 31]:
            content = textwrap.dedent(
                f"""\
                - Ability Score
                    - *ability* Charisma
                    - *override* {value}
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == []
            assert errors == [
                {
                    "line": 3,
                    "text": f'Override "{value}" is out of range (1-30).',
                }
            ]

        for value in ["minimum 0", "maximum 31"]:
            content = textwrap.dedent(
                f"""\
                - Ability Score
                    - *ability* Charisma
                    - *override* 10, {value}
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == []
            assert errors == [
                {
                    "line": 3,
                    "text": f'Override "{value}" is out of range (1-30).',
                }
            ]

    def test_invalid_value_format(self):
        content = textwrap.dedent(
            """\
            - Ability Score
                - *ability* Dexterity
                - *value* high
            - Ability Score
                - *ability* Intelligence
                - *override* very high
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 3,
                "text": 'Value "high" is not a valid score or modifier.',
            },
            {
                "line": 6,
                "text": 'Override "very high" is not a valid score or modifier.',
            },
        ]

    def test_description_against_reference_toml(self):
        result, errors = RuleParser().parse_rules_file(
            "rules/directives/ability_score.md"
        )

        with open("tests/rules/directives/ability_score.toml", "r") as f:
            expected_data = toml.load(f)

        # TOML doesn't have a null type by design so this
        # won't be 100% accurate here; fill in the blanks
        all_keys = {field.name for field in dataclasses.fields(AbilityScore)}
        for item in expected_data.get("ability_score", []):
            for key in all_keys:
                if key not in item:
                    item[key] = None

        assert into_dicts(result) == expected_data["ability_score"]

        with open("tests/rules/directives/ability_score.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])
