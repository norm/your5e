import dataclasses
import textwrap
import toml

from your5e.rules import RuleParser
from your5e.rules.directives import Action, BonusAction, Reaction
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

    def test_to_markdown(self):
        # Create Action objects from TOML data
        with open("tests/rules/directives/action.toml", "r") as f:
            toml_data = toml.load(f)

        # Test Action directive
        action_data = toml_data["action"][0]
        action_obj = Action(
            id=action_data["id"],
            name=action_data["name"],
            comment=action_data.get("comment"),
            description=action_data["description"],
            uses=action_data.get("uses"),
            effect=action_data.get("effect"),
            amount=action_data.get("amount"),
            roll=action_data.get("roll"),
        )

        expected_action_markdown = textwrap.dedent(
            """\
            - Action
              - _description_ Make a melee attack with your elbow, knee, etc.
              - _effect_ harm
              - _amount_ 1 + {STRENGTH_MOD}
              - _roll_ d20
              - _name_ Unarmed Strike
            """
        )
        assert action_obj.to_markdown() == expected_action_markdown

        # Test BonusAction directive
        bonusaction_data = toml_data["bonusaction"][0]
        bonusaction_obj = BonusAction(
            id=bonusaction_data["id"],
            name=bonusaction_data["name"],
            comment=bonusaction_data.get("comment"),
            description=bonusaction_data["description"],
            uses=bonusaction_data.get("uses"),
            effect=bonusaction_data.get("effect"),
            amount=bonusaction_data.get("amount"),
            roll=bonusaction_data.get("roll"),
        )

        expected_bonusaction_markdown = textwrap.dedent(
            """\
            - Bonus Action
              - _description_ Regain 1d10 + {FIGHTER} Hit Points between rests.
              - _uses_ Second Wind
              - _effect_ heal
              - _amount_ 1d10 + {FIGHTER}
              - _name_ Second Wind
            """
        )
        assert bonusaction_obj.to_markdown() == expected_bonusaction_markdown

        # Test Reaction directive
        reaction_data = toml_data["reaction"][0]
        reaction_obj = Reaction(
            id=reaction_data["id"],
            name=reaction_data["name"],
            comment=reaction_data.get("comment"),
            description=reaction_data["description"],
            uses=reaction_data.get("uses"),
            effect=reaction_data.get("effect"),
            amount=reaction_data.get("amount"),
            roll=reaction_data.get("roll"),
        )

        expected_reaction_markdown = textwrap.dedent(
            """\
            - Reaction
              - _description_ Attempt to interrupt a creature casting a spell.
              - _uses_ Spell Slot
              - _name_ Counterspell
            """
        )
        assert reaction_obj.to_markdown() == expected_reaction_markdown
