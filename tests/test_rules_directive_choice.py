import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import Choice
from .utils import into_dicts


class TestChoice:
    def test_basic_choice(self):
        content = textwrap.dedent(
            """\
            - Choice
                - *name* First Equipment Choice
                - *choice* chain mail
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "choice_1",
                "name": "First Equipment Choice",
                "comment": None,
                "choice": "chain mail",
            },
        ]
        assert str(result[0]) == "Choice: First Equipment Choice (chain mail)"
        assert errors == []

    def test_shorthand_choice(self):
        content = textwrap.dedent(
            """\
            - Choice _First Equipment Choice_ chain mail
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "choice_1",
                "name": "First Equipment Choice",
                "comment": None,
                "choice": "chain mail",
            },
        ]
        assert str(result[0]) == "Choice: First Equipment Choice (chain mail)"
        assert errors == []

    def test_multiple_choices(self):
        content = textwrap.dedent(
            """\
            - Choice _First Equipment Choice_ chain mail
            - Choice _Second Equipment Choice_ two martial weapons
            - Choice _Third Equipment Choice_ two handaxes
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "choice_1",
                "name": "First Equipment Choice",
                "comment": None,
                "choice": "chain mail",
            },
            {
                "id": "choice_2",
                "name": "Second Equipment Choice",
                "comment": None,
                "choice": "two martial weapons",
            },
            {
                "id": "choice_3",
                "name": "Third Equipment Choice",
                "comment": None,
                "choice": "two handaxes",
            },
        ]
        assert errors == []

    def test_choice_with_comment(self):
        content = textwrap.dedent(
            """\
            - Choice
                - *name* Barbarian Proficiencies
                - *choice* Intimidation
                - *comment* Good for roleplay
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "choice_1",
                "name": "Barbarian Proficiencies",
                "comment": "Good for roleplay",
                "choice": "Intimidation",
            },
        ]
        assert str(result[0]) == "Choice: Barbarian Proficiencies (Intimidation)"
        assert errors == []

    def test_unknown_keys_ignored(self):
        content = textwrap.dedent(
            """\
            - Choice
                - *name* Test Choice
                - *choice* test option
                - *unknown* ignored
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "choice_1",
                "name": "Test Choice",
                "comment": None,
                "choice": "test option",
            }
        ]
        assert str(result[0]) == "Choice: Test Choice (test option)"
        assert errors == []

    def test_missing_name(self):
        content = textwrap.dedent(
            """\
            - Choice
                - *choice* test option
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

    def test_missing_choice(self):
        content = textwrap.dedent(
            """\
            - Choice
                - *name* Test Choice
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "choice" argument is missing.',
            },
        ]

    def test_empty_name(self):
        content = textwrap.dedent(
            """\
            - Choice
                - *name*
                - *choice* test option
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

    def test_empty_choice(self):
        content = textwrap.dedent(
            """\
            - Choice
                - *name* Test Choice
                - *choice*
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "choice" argument is missing.',
            },
        ]

    def test_shorthand_with_extra_arguments_fails(self):
        content = textwrap.dedent(
            """\
            - Choice _Test Choice_ test option
                - *comment* This should fail
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
            "docs/rules/directives/choice.md"
        )

        with open("tests/rules/directives/choice.toml", "r") as f:
            expected_data = toml.load(f)

        all_keys = {field.name for field in dataclasses.fields(Choice)}
        for item in expected_data.get("choice", []):
            for key in all_keys:
                if key not in item:
                    item[key] = None

        assert into_dicts(result) == expected_data["choice"]

        with open("tests/rules/directives/choice.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])

    def test_to_markdown(self):
        # Create Choice objects from TOML data
        with open("tests/rules/directives/choice.toml", "r") as f:
            toml_data = toml.load(f)

        choice_objects = []
        for item in toml_data["choice"]:
            choice_obj = Choice(
                id=item["id"],
                name=item["name"],
                comment=item.get("comment"),
                choice=item["choice"],
            )
            choice_objects.append(choice_obj)

        # Test first object (should use shorthand since only name and choice)
        expected_markdown_1 = textwrap.dedent(
            """\
            - Choice _First Equipment Choice_ chain mail
            """
        )
        assert choice_objects[0].to_markdown() == expected_markdown_1

        # Test second object (should use shorthand)
        expected_markdown_2 = textwrap.dedent(
            """\
            - Choice _Second Equipment Choice_ two martial weapons
            """
        )
        assert choice_objects[1].to_markdown() == expected_markdown_2

        # Test third object (should use shorthand)
        expected_markdown_3 = textwrap.dedent(
            """\
            - Choice _Third Equipment Choice_ two handaxes
            """
        )
        assert choice_objects[2].to_markdown() == expected_markdown_3
