import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import Language
from .utils import into_dicts


class TestLanguage:
    def test_with_name(self):
        content = textwrap.dedent(
            """\
            - Language
                - *name* Common
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "language_1",
                "name": "Common",
                "comment": None,
            },
        ]
        assert str(result[0]) == "Language: Common"
        assert errors == []

    def test_multiple_languages(self):
        content = textwrap.dedent(
            """\
            - Language
                - *name* Sylvan
            - Language
                - *name* Undercommon
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "language_1",
                "name": "Sylvan",
                "comment": None,
            },
            {
                "id": "language_3",
                "name": "Undercommon",
                "comment": None,
            },
        ]
        assert str(result[0]) == "Language: Sylvan"
        assert str(result[1]) == "Language: Undercommon"
        assert errors == []

    def test_shorthand_format(self):
        content = textwrap.dedent(
            """\
            - Language _Sylvan_
            - Language _Undercommon_
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "language_1",
                "name": "Sylvan",
                "comment": None,
            },
            {
                "id": "language_2",
                "name": "Undercommon",
                "comment": None,
            },
        ]
        assert str(result[0]) == "Language: Sylvan"
        assert str(result[1]) == "Language: Undercommon"
        assert errors == []

    def test_unknown_keys_ignored(self):
        content = textwrap.dedent(
            """\
            - Language
                - *name* Draconic
                - *region* Ancient
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "language_1",
                "name": "Draconic",
                "comment": None,
            }
        ]
        assert str(result[0]) == "Language: Draconic"
        assert errors == []

    def test_missing_name(self):
        content = textwrap.dedent(
            """\
            - Language
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

    def test_empty_name(self):
        content = textwrap.dedent(
            """\
            - Language
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

    def test_wrong_key_format(self):
        content = textwrap.dedent(
            """\
            - Language
                - Undercommon
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "name" argument is missing.',
            },
            {
                "line": 2,
                "text": "Argument has no key.",
            },
        ]

    def test_invalid_key_format(self):
        content = textwrap.dedent(
            """\
            - Language
                - *language* Common
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

    def test_description_against_reference_toml(self):
        result, errors = RuleParser().parse_rules_file(
            "docs/rules/directives/language.md"
        )

        with open("tests/rules/directives/language.toml", "r") as f:
            expected_data = toml.load(f)

        all_keys = {field.name for field in dataclasses.fields(Language)}
        for item in expected_data.get("language", []):
            for key in all_keys:
                if key not in item:
                    item[key] = None

        assert into_dicts(result) == expected_data["language"]

        with open("tests/rules/directives/language.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])
