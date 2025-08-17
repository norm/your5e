import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import Resource
from .utils import into_dicts


class TestResource:
    def test_with_name_and_uses(self):
        content = textwrap.dedent(
            """\
            - Resource
                - *name* Second Wind
                - *uses* 1
                - *renew* rest
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "resource_1",
                "name": "Second Wind",
                "comment": None,
                "uses": "1",
                "renew": "rest",
                "regain": None,
            },
        ]
        assert str(result[0]) == "Resource: Second Wind (1)"
        assert errors == []

    def test_all_optional_fields(self):
        content = textwrap.dedent(
            """\
            - Resource
                - *name* Wand of Magic Missiles
                - *uses* 7
                - *renew* dawn
                - *regain* 1d6 + 1
            - Resource
                - *name* Simple Resource
                - *uses* 3
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "resource_1",
                "name": "Wand of Magic Missiles",
                "comment": None,
                "uses": "7",
                "renew": "dawn",
                "regain": "1d6 + 1",
            },
            {
                "id": "resource_6",
                "name": "Simple Resource",
                "comment": None,
                "uses": "3",
                "renew": None,
                "regain": None,
            },
        ]
        assert str(result[0]) == "Resource: Wand of Magic Missiles (7)"
        assert str(result[1]) == "Resource: Simple Resource (3)"
        assert errors == []

    def test_valid_renew_values(self):
        valid_renew_values = ["rest", "long rest", "dawn"]

        for renew_value in valid_renew_values:
            content = textwrap.dedent(
                f"""\
                - Resource
                    - *name* Test Resource
                    - *uses* 1
                    - *renew* {renew_value}
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == [
                {
                    "id": "resource_1",
                    "name": "Test Resource",
                    "comment": None,
                    "uses": "1",
                    "renew": renew_value,
                    "regain": None,
                },
            ]
            assert errors == []

    def test_case_insensitive_renew(self):
        content = textwrap.dedent(
            """\
            - Resource
                - *name* Test Resource
                - *uses* 1
                - *renew* LONG REST
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "resource_1",
                "name": "Test Resource",
                "comment": None,
                "uses": "1",
                "renew": "long rest",
                "regain": None,
            }
        ]
        assert errors == []

    def test_shorthand_format(self):
        content = textwrap.dedent(
            """\
            - Resource _Charm of the Storm_ 3
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "resource_1",
                "name": "Charm of the Storm",
                "comment": None,
                "uses": "3",
                "renew": None,
                "regain": None,
            },
        ]
        assert str(result[0]) == "Resource: Charm of the Storm (3)"
        assert errors == []

    def test_unknown_keys_ignored(self):
        content = textwrap.dedent(
            """\
            - Resource
                - *name* Test Resource
                - *uses* 5
                - *damage* 2d6
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "resource_1",
                "name": "Test Resource",
                "comment": None,
                "uses": "5",
                "renew": None,
                "regain": None,
            }
        ]
        assert str(result[0]) == "Resource: Test Resource (5)"
        assert errors == []

    def test_invalid_renew_value(self):
        content = textwrap.dedent(
            """\
            - Resource
                - *name* Test Resource
                - *uses* 1
                - *renew* weekly
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 4,
                "text": 'Renew "weekly" should be either rest, long rest, dawn.',
            },
        ]

    def test_missing_name(self):
        content = textwrap.dedent(
            """\
            - Resource
                - *uses* 3
                - *renew* rest
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

    def test_missing_uses(self):
        content = textwrap.dedent(
            """\
            - Resource
                - *name* Test Resource
                - *renew* rest
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "uses" argument is missing.',
            },
        ]

    def test_empty_name(self):
        content = textwrap.dedent(
            """\
            - Resource
                - *name*
                - *uses* 1
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

    def test_empty_uses(self):
        content = textwrap.dedent(
            """\
            - Resource
                - *name* Test Resource
                - *uses*
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "uses" argument is missing.',
            },
        ]

    def test_description_against_reference_toml(self):
        result, errors = RuleParser().parse_rules_file(
            "docs/rules/directives/resource.md"
        )

        with open("tests/rules/directives/resource.toml", "r") as f:
            expected_data = toml.load(f)

        all_keys = {field.name for field in dataclasses.fields(Resource)}
        for item in expected_data.get("resource", []):
            for key in all_keys:
                if key not in item:
                    item[key] = None

        assert into_dicts(result) == expected_data["resource"]

        with open("tests/rules/directives/resource.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])

    def test_to_markdown(self):
        # Create Resource objects from TOML data
        with open("tests/rules/directives/resource.toml", "r") as f:
            toml_data = toml.load(f)

        resource_objects = []
        for item in toml_data["resource"]:
            resource_obj = Resource(
                id=item["id"],
                name=item["name"],
                comment=item.get("comment"),
                uses=item["uses"],
                renew=item.get("renew"),
                regain=item.get("regain"),
            )
            resource_objects.append(resource_obj)

        # Test first object (has renew field - should use full format)
        expected_markdown_1 = textwrap.dedent(
            """\
            - Resource
              - _uses_ 1
              - _renew_ rest
              - _name_ Second Wind
            """
        )
        assert resource_objects[0].to_markdown() == expected_markdown_1

        # Test second object (has renew and regain fields - should use full format)
        expected_markdown_2 = textwrap.dedent(
            """\
            - Resource
              - _uses_ 7
              - _renew_ dawn
              - _regain_ 1d6 + 1
              - _name_ Wand of Magic Missiles
            """
        )
        assert resource_objects[1].to_markdown() == expected_markdown_2

        # Test third object (only name and uses - should use shorthand)
        expected_markdown_3 = textwrap.dedent(
            """\
            - Resource _Charm of the Storm_ 3
            """
        )
        assert resource_objects[2].to_markdown() == expected_markdown_3
