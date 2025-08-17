import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import Featureless
from .utils import into_dicts


class TestFeatureless:
    def test_basic_featureless(self):
        content = textwrap.dedent(
            """\
            - Featureless
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "featureless_1",
                "name": None,
                "comment": None,
            },
        ]
        assert str(result[0]) == "Featureless"
        assert errors == []

    def test_featureless_with_comment(self):
        content = textwrap.dedent(
            """\
            - Featureless
                - *comment* This section is explanatory text
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "featureless_1",
                "name": None,
                "comment": "This section is explanatory text",
            },
        ]
        assert str(result[0]) == "Featureless"
        assert errors == []

    def test_unknown_keys_ignored(self):
        content = textwrap.dedent(
            """\
            - Featureless
                - *unnecessary* value
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "featureless_1",
                "name": None,
                "comment": None,
            }
        ]
        assert str(result[0]) == "Featureless"
        assert errors == []

    def test_description_against_reference_toml(self):
        result, errors = RuleParser().parse_rules_file(
            "docs/rules/directives/featureless.md"
        )

        with open("tests/rules/directives/featureless.toml", "r") as f:
            expected_data = toml.load(f)

        all_keys = {field.name for field in dataclasses.fields(Featureless)}
        for item in expected_data.get("featureless", []):
            for key in all_keys:
                if key not in item:
                    item[key] = None

        assert into_dicts(result) == expected_data["featureless"]

        with open("tests/rules/directives/featureless.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])

    def test_to_markdown(self):
        # Create Featureless objects from TOML data
        with open("tests/rules/directives/featureless.toml", "r") as f:
            toml_data = toml.load(f)

        featureless_objects = []
        for item in toml_data["featureless"]:
            featureless_obj = Featureless(
                id=item["id"],
                name=item.get("name"),
                comment=item.get("comment"),
            )
            featureless_objects.append(featureless_obj)

        # Test all objects - they should all return simple format regardless of content
        for featureless_obj in featureless_objects:
            assert featureless_obj.to_markdown() == "- Featureless\n"
