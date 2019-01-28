import pytest
import re
from SBLex import lex, lex_bases, lex_premades


def example_function():
    """Only will be used for testing the function argument in lex.add() and lex.skip()
    """


def convert_dependencies(dependencies, rule_in_pos_0=r"\n"):
    """
    Convert dependencies to a acceptable format for comparation.

    Args:
        dependencies (list): Is the dependencies to "convert".
        rule_in_pos_0 (rule): Is the jump line rule in the pos 0 of lexer.lex().rules
    
    Returns:
        list or dict: Returns the dependencies converted.
    """
    rule_in_pos_0 = lex_bases.rule(["JUMP_LINE", False], rule_in_pos_0)
    converted_dependencies = None

    if (
        isinstance(dependencies, dict)
        and "rules" in dependencies.keys()
        and len(dependencies["rules"]) >= 1
    ):
        converted_dependencies = dependencies
        # Load the jump line rule.
        converted_dependencies["rules"].insert(0, rule_in_pos_0)

    elif isinstance(dependencies, list):
        converted_dependencies = dependencies

        converted_dependencies.insert(0, rule_in_pos_0)

    return converted_dependencies


def test_instance():
    """Checks the instance created by lex.build()
    """
    assert isinstance(lex.lex().build(), lex._lexer)


def test_jump_line():
    # Check if the first value on the rule list have a type of JUMP_LINE
    assert lex.lex().rules[0].type == "JUMP_LINE"


def test_add():
    """Checks if the rule created by lex.add() is valid.
    """
    # Create lex instance
    lexer = lex.lex()

    lexer.add(
        "TEST",
        r"test",
        dependencies=[lex_bases.rule("TEST_2", r"test_2")],
        function=example_function,
    )

    # Create a rule using the rule constructor with the same inputs
    converted_dependencies = convert_dependencies([lex_bases.rule("TEST_2", r"test_2")])
    expected_rule = lex_bases.rule(
        "TEST", r"test", dependencies=converted_dependencies, function=example_function
    )

    # Test capturing group
    lexer_2 = lex.lex()

    # Try to lex: My name is name
    lexer_2.add("His name", r"My name is ([a-zA-Z]+)", capturing_group=1)

    returned_tokens = lexer_2.evaluate("My name is KadMuffin")

    expected_token_2 = lex_bases.token("His name", "KadMuffin")

    assert (
        lexer.rules[1]._complete_equal(expected_rule)
        and returned_tokens[0] == expected_token_2
    )


def test_skip():
    """Checks if the rule created by lex.skip() is valid.
    """
    # Create lex instance
    lexer = lex.lex()

    lexer.skip(
        r"test",
        dependencies=[lex_bases.rule("TEST_2", r"test_2")],
        function=example_function,
    )

    # Create a rule using the rule constructor with the same inputs
    expected_rule = lex_bases.rule(
        ["SKIPPED", False],
        r"test",
        dependencies=convert_dependencies([lex_bases.rule("TEST_2", r"test_2")]),
        function=example_function,
    )

    assert (
        lexer.rules[1]._complete_equal(expected_rule)
        and lexer._skip_rules[0]._complete_equal(expected_rule)
        and lexer.rules[1].get_if_accept_skips()
    )


def test_load_premade():
    working = True

    lexer = lex.lex()
    lexer.load_premade(lex_bases.rule("TEST", r"test"))

    if lexer.rules[1] != lex_bases.rule("TEST", r"test"):
        working = False

    lexer.load_premade(
        [lex_bases.rule("TEST_2", r"test_2"), lex_bases.rule("TEST_3", r"test_3")]
    )

    if lexer.rules[2] != lex_bases.rule("TEST_2", r"test_2") or lexer.rules[
        3
    ] != lex_bases.rule("TEST_3", r"test_3"):
        working = False

    assert working


def test_ignore():
    """Checks if the rule created by lex._ignore() is valid.
    """
    # Create lex instance
    lexer = lex.lex()

    # Add a rule for lex test
    lexer.add("TEST", r"test")

    # Add a ignore rule
    lexer._ignore(r"noise", force_usage=True)

    token_stream = lexer.evaluate("tenoisestt")

    expected_token_stream = [
        lex_bases.token("TEST", "test"),
        lex_bases.token("TEST", "test"),
        lex_bases.token("TEST", "test"),
    ]

    assert token_stream == expected_token_stream


def test_lex_build():
    """Checks if the instance created by lex.build() works as expected.
    """
    # Create a lex instance
    lexer = lex.lex()

    lexer.add(
        "TEST",
        r"test",
        dependencies=[lex_bases.rule("TEST_2", r"test_2")],
        function=example_function,
    )

    # Add a skip rule
    lexer.skip(r"test_skip")

    # Create a expected rule of type skip
    expected_rule = lex_bases.rule(["SKIPPED", False], r"test_skip")

    lexer = lexer.build(add_skips_in_rules=True)

    assert lexer._rules[1]._get_skips_rules()[0]._complete_equal(expected_rule)


def test_load_text():
    """Test if the function load_text works
    """
    # Create lexer without value
    lexer = lex._lexer(None, None)._load_text("TEST")

    # Check if the loaded text
    assert lexer._original_text == "TEST" and lexer._text_to_process == "TEST"


def test_lexing_error():
    """Check if the lexing error works as expected
    """
    with pytest.raises(SyntaxError):
        lex._lexer(None, None)._load_text("TEST")._throw_lexing_error()


def test_lexing_error_evaluate_1():
    """Check if the lexing error works as expected, in this case in evaluate().
    """
    with pytest.raises(SyntaxError):
        lex._lexer([lex_premades.float], [])._load_text("TEST").evaluate()


def test_lexing_error_evaluate_2():
    """Check if the lexing error works as expected, in this case evaluate() but using str as custom error
    """
    with pytest.raises(SyntaxError):
        lex._lexer([lex_premades.float], [], "[[LINE]] [[TEXT]]")._load_text(
            "TEST"
        ).evaluate()


def test_lexing_error_evaluate_3():
    """Check if the lexing error works as expected, in this case evaluate() but using a function as custom error
    """
    with pytest.raises(SyntaxError):
        lex._lexer([lex_premades.float], [], example_function())._load_text(
            "TEST"
        ).evaluate()


def test_get_original_text():
    """Checks if the value returned  by _lexer.get_original_text() is valid.
    """

    assert lex._lexer(None, None)._load_text("test").get_original_text() == "test"


def test_dependencies():
    """Check if the property dependencies works on evaluate.
    """
    lexer = lex.lex()
    lexer.add("TEST", r"test", dependencies=[lex_bases.rule("TEST_2", r"text")])
    lexer.skip(r"\s+")

    token_stream = lexer.evaluate("test text")

    points = 0

    if token_stream[0][0] == lex_bases.token("TEST", r"test") and token_stream[0][
        1
    ] == lex_bases.token("TEST_2", r"text"):
        points += 1

    lexer = lex.lex()

    lexer.skip("TEST", r"test", {"rules": [lex_bases.rule("TEST_2", r"text")]})

    lexer.load_premade([lex_premades.var_declaration, lex_premades.comment], False)

    lexer.load_premade(lex_premades.var_declaration)


def test_deprecated_line_plus():
    """Test the function _lexer._plus_deprecated_line_count()
    """
    lexer = lex._lexer(None, None)

    lexer._plus_deprecated_line_count()

    assert lexer._deprecated_line_count == 0


def test_reset_lexer():
    """Try to reset the lexer and check if all is correct
    """
    lexer = lex._lexer(None, None)

    # Load ramdom values to check if all are reset to 0 and -1
    lexer._line = 120
    lexer._pos_in_line = 101
    lexer._pos_in_str = 3201
    lexer._deprecated_line_count = 10

    lexer._reset_lexer()

    assert (
        lexer._line == 0
        and lexer._pos_in_line == 0
        and lexer._pos_in_str == 0
        and lexer._deprecated_line_count == -1
    )


def test_evaluate():
    """Try to evaluate text with rules and check if all works
    """
    # Create a lexer instance with rules and text loaded
    lexer = lex._lexer(
        [lex_bases.rule("JUMP_LINE", r"\n"), lex_bases.rule("TEST", r"test")], []
    )._load_text("test")

    # Evalueate the loaded text and compare
    assert lexer.evaluate() == [lex_bases.token("TEST", "test")]


def test_analyze_text():
    """Check if analyze_text works as expected
    """
    # Create a lexer instance and analyze a text with some rules
    new_dict = lex._lexer(None, None).analyze_text(
        "test", [lex_bases.rule("JUMP_LINE", r"\n"), lex_bases.rule("TEST", r"test")]
    )

    # Check if the returned values are correct
    assert (
        new_dict["token"] == lex_bases.token("TEST", "test")
        and new_dict["fit_with_a_rule"]
        and new_dict["rule_that_matched"] == lex_bases.rule("TEST", r"test")
    )


def test_jump_and_remove():
    """Check the values modified by jump_and_remove and see if they are correct
    """
    # Create a lexer instance with loaded text and test _jump_and_remove
    lexer = lex._lexer(None, None)._load_text("TEST")._jump_and_remove(4, "TEST")

    # Check modifications made by the function
    assert (
        lexer._pos_in_str == 4
        and lexer._pos_in_line == 4
        and lexer._text_to_process is None
    )


def test_get_next_token():
    """Check if the function get_next_token works as expected
    """
    # Create a lexer instance with text and try _get_next_token
    assert lex._lexer(None, None)._load_text("test")._get_next_token(
        [lex_bases.rule("TEST", r"test")], []
    ) == lex_bases.token("TEST", "test")
