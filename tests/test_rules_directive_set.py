import pytest
import textwrap
from pathlib import Path
import toml

from your5e.rules import RuleParser
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
        assert errors == []

    def test_set_with_comment(self):
        content = textwrap.dedent(
            """\
            - Set
                - *key* Age
                - *value* 23
                - *comment* standard array
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "set_1",
                "name": None,
                "comment": "standard array",
                "key": "Age",
                "value": "23",
            }
        ]
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
                "line": 2,
                "text": 'Key "" is not valid.',
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
                "line": 3,
                "text": 'Value "" is not valid.',
            }
        ]


@pytest.fixture
def test_data():
    test_file = Path(__file__).parent / "rules" / "directives" / "set.toml"
    with open(test_file, "r") as f:
        return toml.load(f)


@pytest.fixture
def error_test_data():
    test_file = Path(__file__).parent / "rules" / "directives" / "set.errors.toml"
    with open(test_file, "r") as f:
        return toml.load(f)


class TestSetDirectiveFromToml:
    def test_from_toml_file(self, test_data):
        for test_case in test_data["test"]:
            result, errors = RuleParser().parse_rules(test_case["input"])

            # Add None values for missing fields in TOML expected results
            expected = test_case["expected"]
            for item in expected:
                if "name" not in item:
                    item["name"] = None
                if "comment" not in item:
                    item["comment"] = None

            assert into_dicts(result) == expected, f"Failed: {test_case['name']}"
            assert errors == test_case["errors"], f"Failed: {test_case['name']}"

    def test_errors_from_toml_file(self, error_test_data):
        for test_case in error_test_data["test"]:
            result, errors = RuleParser().parse_rules(test_case["input"])
            assert (
                into_dicts(result) == test_case["expected"]
            ), f"Failed: {test_case['name']}"
            assert errors == test_case["errors"], f"Failed: {test_case['name']}"
