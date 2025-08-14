import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import Action
from .utils import into_dicts


class TestAction:
    def test_with_name_and_description(self):
        content = textwrap.dedent(
            """\
            - Action
                - *name* Unarmed Strike
                - *description* Make a melee attack with your elbow, knee, etc.
                - *roll* d20
                - *effect* harm
                - *amount* 1 + {STRENGTH_MOD}
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "action_1",
                "name": "Unarmed Strike",
                "comment": None,
                "description": "Make a melee attack with your elbow, knee, etc.",
                "uses": None,
                "effect": "harm",
                "amount": "1 + {STRENGTH_MOD}",
                "roll": "d20",
            },
        ]
        assert str(result[0]) == "Action: Unarmed Strike"
        assert errors == []

    def test_all_action_types(self):
        content = textwrap.dedent(
            """\
            - Action
                - *name* Attack
                - *description* Make a weapon attack
            - Bonus Action
                - *name* Second Wind
                - *description* Regain Hit Points
                - *uses* Second Wind
                - *effect* heal
                - *amount* 1d10 + {FIGHTER}
            - Reaction
                - *name* Counterspell
                - *description* Interrupt a creature casting a spell
                - *uses* Spell Slot
            """
        )

        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "action_1",
                "name": "Attack",
                "comment": None,
                "description": "Make a weapon attack",
                "uses": None,
                "effect": None,
                "amount": None,
                "roll": None,
            },
            {
                "id": "bonusaction_4",
                "name": "Second Wind",
                "comment": None,
                "description": "Regain Hit Points",
                "uses": "Second Wind",
                "effect": "heal",
                "amount": "1d10 + {FIGHTER}",
                "roll": None,
            },
            {
                "id": "reaction_10",
                "name": "Counterspell",
                "comment": None,
                "description": "Interrupt a creature casting a spell",
                "uses": "Spell Slot",
                "effect": None,
                "amount": None,
                "roll": None,
            },
        ]
        assert str(result[0]) == "Action: Attack"
        assert str(result[1]) == "Bonus Action: Second Wind"
        assert str(result[2]) == "Reaction: Counterspell"
        assert errors == []

    def test_unknown_keys_ignored(self):
        content = textwrap.dedent(
            """\
            - Action
                - *name* Special Attack
                - *description* A unique attack
                - *damage* 2d6
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "action_1",
                "name": "Special Attack",
                "comment": None,
                "description": "A unique attack",
                "uses": None,
                "effect": None,
                "amount": None,
                "roll": None,
            }
        ]
        assert str(result[0]) == "Action: Special Attack"
        assert errors == []

    def test_missing_name(self):
        content = textwrap.dedent(
            """\
            - Action
                - *description* Some action
            - Bonus Action
                - *description* Some bonus action
            - Reaction
                - *description* Some reaction
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
                "line": 3,
                "text": 'Required "name" argument is missing.',
            },
            {
                "line": 5,
                "text": 'Required "name" argument is missing.',
            },
        ]

    def test_missing_description(self):
        content = textwrap.dedent(
            """\
            - Action
                - *name* Attack
            - Bonus Action
                - *name* Heal
            - Reaction
                - *name* Block
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "description" argument is missing.',
            },
            {
                "line": 3,
                "text": 'Required "description" argument is missing.',
            },
            {
                "line": 5,
                "text": 'Required "description" argument is missing.',
            },
        ]

    def test_empty_name(self):
        content = textwrap.dedent(
            """\
            - Action
                - *name*
                - *description* Some description
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

    def test_empty_description(self):
        content = textwrap.dedent(
            """\
            - Action
                - *name* Attack
                - *description*
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "description" argument is missing.',
            },
        ]

    def test_description_against_reference_toml(self):
        result, errors = RuleParser().parse_rules_file(
            "docs/rules/directives/action.md"
        )

        with open("tests/rules/directives/action.toml", "r") as f:
            expected_data = toml.load(f)

        # Handle all three action types
        all_results = []
        for action_type in ["action", "bonusaction", "reaction"]:
            if action_type in expected_data:
                all_keys = {field.name for field in dataclasses.fields(Action)}
                for item in expected_data[action_type]:
                    for key in all_keys:
                        if key not in item:
                            item[key] = None
                all_results.extend(expected_data[action_type])

        assert into_dicts(result) == all_results

        with open("tests/rules/directives/action.errors.toml", "r") as f:
            expected_errors = toml.load(f)
        assert errors == expected_errors.get("errors", [])
