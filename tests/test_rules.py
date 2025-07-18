import textwrap

from your5e.rules import RuleParser, DirectiveExtract
from .utils import into_dicts


class TestParseRules:
    def test_empty_content(self):
        result, errors = RuleParser().parse_rules("")
        assert result == []
        assert errors == []

    def test_no_directives(self):
        content = "Just some text without directives"
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == []

    def test_directive_position_validation(self):
        content = textwrap.dedent(
            """\
            - Hit Die
                - *Die* d10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_1",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 6,
            }
        ]
        assert errors == []

        # valid directly after heading
        content = textwrap.dedent(
            """\
            # Fighter
            - Hit Die
                - *Die* d10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_2",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 6,
            }
        ]
        assert errors == []

        # allow spaces before headings
        content = textwrap.dedent(
            """\
            # Fighter

            - Hit Die
                - *Die* d10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_3",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 6,
            }
        ]
        assert errors == []

        # allow spaces between directives
        content = textwrap.dedent(
            """\
            # Fighter

            - Hit Die
                - *Die* d10

            - Hit Die
                - *die* d8
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_3",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 6,
            },
            {
                "id": "hitdie_6",
                "name": None,
                "comment": None,
                "die": 8,
                "value": 5,
            },
        ]
        assert errors == []

        # text after heading makes it markdown not directives
        content = textwrap.dedent(
            """\
            # Fighter
            Fighters get a d10 hit die.

            - Hit Die
                - *Die* d10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == []

        # no indentation
        content = textwrap.dedent(
            """\
            # Example directive
                - Hit Die
                    - *Die* d10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == []

    def test_argument_formatting(self):
        test_cases = [
            "*",
            "**",
            "_",
            "__",
        ]

        for marker in test_cases:
            content = textwrap.dedent(
                f"""\
                - Hit Die
                    - {marker}Die{marker} d10
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == [
                {
                    "id": "hitdie_1",
                    "name": None,
                    "comment": None,
                    "die": 10,
                    "value": 6,
                }
            ]
            assert errors == []

        content = textwrap.dedent(
            """\
            - Hit Die
                - **Die__ d10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "die" argument is missing.',
            },
            {
                "line": 2,
                "text": "Argument has no key.",
            },
        ]

        content = textwrap.dedent(
            """\
            - Hit Die
                - **die** d10
                - **** 4
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 3,
                "text": "Argument has no key.",
            },
        ]

    def test_duplicates_last_wins(self):
        content = textwrap.dedent(
            """\
            - Hit Die
                - *Die* d6
                - *Die* d10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_1",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 6,
            }
        ]
        assert errors == []

    def test_duplicates_still_produces_errors(self):
        content = textwrap.dedent(
            """\
            - Hit Die
                - *Die* d6
                - *Die* invalid
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 3,
                "text": 'Die "invalid" is not a die.',
            },
        ]

    def test_indentation_depth(self):
        content = textwrap.dedent(
            """\
            - Hit Die
             - *Die* d10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_1",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 6,
            }
        ]
        assert errors == []

    def test_no_indentation(self):
        content = textwrap.dedent(
            """\
            - Hit Die
            - *Die* d10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "die" argument is missing.',
            },
            {
                "line": 2,
                "text": "Unknown directive: *Die* d10",
            },
        ]

    def test_case_insensitive_directive_names(self):
        test_cases = [
            "Hit Die",
            "hit die",
            "HIT DIE",
            "hit Die",
        ]

        for directive in test_cases:
            content = textwrap.dedent(
                f"""\
                - {directive}
                    - *Die* d10
                """
            )
            result, errors = RuleParser().parse_rules(content)
            assert into_dicts(result) == [
                {
                    "id": "hitdie_1",
                    "name": None,
                    "comment": None,
                    "die": 10,
                    "value": 6,
                }
            ]
            assert errors == []

    def test_case_insensitive_keys(self):
        content = textwrap.dedent(
            """\
            - Hit Die
                - *DIE* d10
                - *VALUE* 5
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_1",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 5,
            }
        ]
        assert errors == []

    def test_invalid_argument_format(self):
        content = textwrap.dedent(
            """\
            - Hit Die
                - Die d10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "die" argument is missing.',
            },
            {
                "line": 2,
                "text": "Argument has no key.",
            },
        ]

        content = textwrap.dedent(
            """\
            - Hit Die
                - *Die d10*
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": 'Required "die" argument is missing.',
            },
            {
                "line": 2,
                "text": "Argument has no key.",
            },
        ]

    def test_unknown_directive_error(self):
        content = textwrap.dedent(
            """\
            - Do Something
                - *What* No idea
                - *When* At some point
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": "Unknown directive: Do Something",
            },
        ]

    def test_comment_lines_are_skipped(self):
        content = textwrap.dedent(
            """\
            - Comment This is a comment
            - comment another comment
            - COMMENT case insensitive
            - # hash comment
            - comment with *emphasis* on **strong opinions**
            - Hit Die
                - *Die* d10
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_6",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 6,
            }
        ]
        assert errors == []

    def test_shorthand_markdown_emphasis_formats(self):
        content = textwrap.dedent(
            """\
            - Hit Die *d10* 8
            - Hit Die _d8_ 6
            - Hit Die **d12** 10
            - Hit Die __d6__ 4
            - Set *Name* John
            - Set _Age_ 25
            - Set **Class** Fighter
            - Set __Race__ Human
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == [
            {
                "id": "hitdie_1",
                "name": None,
                "comment": None,
                "die": 10,
                "value": 8,
            },
            {
                "id": "hitdie_2",
                "name": None,
                "comment": None,
                "die": 8,
                "value": 6,
            },
            {
                "id": "hitdie_3",
                "name": None,
                "comment": None,
                "die": 12,
                "value": 10,
            },
            {
                "id": "hitdie_4",
                "name": None,
                "comment": None,
                "die": 6,
                "value": 4,
            },
            {
                "id": "set_5",
                "name": None,
                "comment": None,
                "key": "Name",
                "value": "John",
            },
            {
                "id": "set_6",
                "name": None,
                "comment": None,
                "key": "Age",
                "value": "25",
            },
            {
                "id": "set_7",
                "name": None,
                "comment": None,
                "key": "Class",
                "value": "Fighter",
            },
            {
                "id": "set_8",
                "name": None,
                "comment": None,
                "key": "Race",
                "value": "Human",
            },
        ]
        assert errors == []

    def test_shorthand_mismatched_emphasis_markers(self):
        content = textwrap.dedent(
            """\
            - Hit Die **d6_ 2
            - Hit Die *d8__ 5
            - Hit Die _d10* 7
            - Set **Name_ John
            - Set *Age__ 25
            - Set _Class* Fighter
            """
        )
        result, errors = RuleParser().parse_rules(content)
        assert into_dicts(result) == []
        assert errors == [
            {
                "line": 1,
                "text": "Unknown directive: Hit Die **d6_ 2",
            },
            {
                "line": 2,
                "text": "Unknown directive: Hit Die *d8__ 5",
            },
            {
                "line": 3,
                "text": "Unknown directive: Hit Die _d10* 7",
            },
            {
                "line": 4,
                "text": "Unknown directive: Set **Name_ John",
            },
            {
                "line": 5,
                "text": "Unknown directive: Set *Age__ 25",
            },
            {
                "line": 6,
                "text": "Unknown directive: Set _Class* Fighter",
            },
        ]


class TestDirectiveExtract:
    def test_extract_with_example_file(self):
        example_path = "tests/rules/example.md"
        with open(example_path, "r") as f:
            example_content = f.read()

        extractor = DirectiveExtract()
        stripped_md, directives = extractor.extract(example_content)

        with open("tests/rules/example_stripped.md", "r") as f:
            expected_stripped = f.read()
        assert stripped_md == expected_stripped

        with open("tests/rules/example_directives.txt", "r") as f:
            expected_directives = f.read()
        assert directives == expected_directives
