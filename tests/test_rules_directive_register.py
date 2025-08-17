import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import Register
from .utils import into_dicts


class TestRegister:
    def test_ability_score_type(self):
        content = textwrap.dedent(
            """\
            - Register
                - *type* Ability Score
                - *name* Dexterity
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "register_1",
                "name": "Dexterity",
                "comment": None,
                "type": "Ability Score",
            },
        ]
        assert str(result[0]) == "Register: Dexterity (Ability Score)"
        assert errors == []

    def test_skill_type(self):
        content = textwrap.dedent(
            """\
            - Register
                - *type* Skill
                - *name* Acrobatics (Dexterity)
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "register_1",
                "name": "Acrobatics (Dexterity)",
                "comment": None,
                "type": "Skill",
            },
        ]
        assert str(result[0]) == "Register: Acrobatics (Dexterity) (Skill)"
        assert errors == []

    def test_roll_type(self):
        content = textwrap.dedent(
            """\
            - Register
                - *type* Roll
                - *name* Initiative
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "register_1",
                "name": "Initiative",
                "comment": None,
                "type": "Roll",
            },
        ]
        assert str(result[0]) == "Register: Initiative (Roll)"
        assert errors == []

    def test_shorthand_ability_score(self):
        content = textwrap.dedent(
            """\
            - Register _Ability Score_ Dexterity
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "register_1",
                "name": "Dexterity",
                "comment": None,
                "type": "Ability Score",
            },
        ]
        assert str(result[0]) == "Register: Dexterity (Ability Score)"
        assert errors == []

    def test_shorthand_skill(self):
        content = textwrap.dedent(
            """\
            - Register _Skill_ Acrobatics (Dexterity)
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "register_1",
                "name": "Acrobatics (Dexterity)",
                "comment": None,
                "type": "Skill",
            },
        ]
        assert str(result[0]) == "Register: Acrobatics (Dexterity) (Skill)"
        assert errors == []

    def test_valid_types(self):
        valid_types = ["Ability Score", "Roll", "Skill"]

        for type_value in valid_types:
            content = textwrap.dedent(
                f"""\
                - Register
                    - *type* {type_value}
                    - *name* Test Feature
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == [
                {
                    "id": "register_1",
                    "name": "Test Feature",
                    "comment": None,
                    "type": type_value,
                },
            ]
            assert errors == []

    def test_case_insensitive_types(self):
        content = textwrap.dedent(
            """\
            - Register
                - *type* ability score
                - *name* Test Feature
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "register_1",
                "name": "Test Feature",
                "comment": None,
                "type": "Ability Score",
            }
        ]
        assert errors == []

    def test_unknown_keys_ignored(self):
        content = textwrap.dedent(
            """\
            - Register
                - *type* Skill
                - *name* Test Skill
                - *uses* Dexterity
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "register_1",
                "name": "Test Skill",
                "comment": None,
                "type": "Skill",
            }
        ]
        assert str(result[0]) == "Register: Test Skill (Skill)"
        assert errors == []

    def test_invalid_type(self):
        content = textwrap.dedent(
            """\
            - Register
                - *type* Feature
                - *name* Test Feature
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 2,
                "text": 'Type "Feature" should be either Ability Score, Roll, Skill.',
            },
        ]

    def test_missing_type(self):
        content = textwrap.dedent(
            """\
            - Register
                - *name* Test Feature
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

    def test_missing_name(self):
        content = textwrap.dedent(
            """\
            - Register
                - *type* Skill
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "name" argument is missing.',
            },
        ]

    def test_empty_type(self):
        content = textwrap.dedent(
            """\
            - Register
                - *type*
                - *name* Test Feature
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

    def test_empty_name(self):
        content = textwrap.dedent(
            """\
            - Register
                - *type* Skill
                - *name*
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "name" argument is missing.',
            },
        ]

    def test_shorthand_with_extra_arguments_fails(self):
        content = textwrap.dedent(
            """\
            - Register _Skill_ Stealth
                - *uses* Dexterity
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": "No arguments when using shorthand notation.",
            },
        ]

    def test_description_against_reference_toml(self):
        result, errors = RuleParser().parse_rules_file(
            "docs/rules/directives/register.md"
        )

        with open("tests/rules/directives/register.toml", "r") as f:
            expected_data = toml.load(f)

        all_keys = {field.name for field in dataclasses.fields(Register)}
        for item in expected_data.get("register", []):
            for key in all_keys:
                if key not in item:
                    item[key] = None

        assert into_dicts(result) == expected_data["register"]

        with open("tests/rules/directives/register.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])

    def test_to_markdown(self):
        # Create Register objects from TOML data
        with open("tests/rules/directives/register.toml", "r") as f:
            toml_data = toml.load(f)

        register_objects = []
        for item in toml_data["register"]:
            register_obj = Register(
                id=item["id"],
                name=item["name"],
                comment=item.get("comment"),
                type=item["type"],
            )
            register_objects.append(register_obj)

        # Test first object (no comment - should use shorthand)
        expected_markdown_1 = textwrap.dedent(
            """\
            - Register _Ability Score_ Dexterity
            """
        )
        assert register_objects[0].to_markdown() == expected_markdown_1

        # Test second object (no comment - should use shorthand)
        expected_markdown_2 = textwrap.dedent(
            """\
            - Register _Skill_ Acrobatics (Dexterity)
            """
        )
        assert register_objects[1].to_markdown() == expected_markdown_2

        # Test third object (no comment - should use shorthand)
        expected_markdown_3 = textwrap.dedent(
            """\
            - Register _Roll_ Initiative
            """
        )
        assert register_objects[2].to_markdown() == expected_markdown_3
