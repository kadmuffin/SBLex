from SBLex import lex_bases


def example_function():
    """Only will be used for testing the function argument in the rule functions.
    """


def test_token_constructor():
    """"Checks if the token constructor works as expected.
    """
    test_token = lex_bases.token(
        "TEST", "test", dependencies=[lex_bases.rule("TEST_2", r"test_2")]
    )
    test_token.set_line_where_finded(0)
    test_token.set_col_where_finded(0)
    test_token.set_deprecated_line_pos(0)
    test_token.set_if_save_to_token_stream(True)
    test_token.set_not_processed_value("clear_thistest")
    test_token.set_truly_original_value("clear_this_test")
    test_token.set_token_parent(lex_bases.rule("TEST", r"test"))
    test_token.set_skips_rules([lex_bases.rule(["SKIPPING", False], r"\s+")])

    points = 0

    if test_token.type == "TEST":
        points += 1
    if test_token.value == "test":
        points += 1
    if test_token.dependencies["rules"][0] == lex_bases.rule("TEST_2", r"test_2"):
        points += 1
    if test_token.get_line_where_finded() == 0:
        points += 1
    if test_token.get_col_where_finded() == 0:
        points += 1
    if test_token.get_deprecated_line_pos() == 0:
        points += 1
    if test_token.get_if_save_to_token_stream() == True:
        points += 1
    if test_token.get_not_processed_value() == "clear_thistest":
        points += 1
    if test_token.get_truly_original_value() == "clear_this_test":
        points += 1
    if test_token.get_parent() == lex_bases.rule("TEST", r"test"):
        points += 1
    if test_token.get_skips_rules()[0] == lex_bases.rule(["SKIPPING", False], r"\s+"):
        points += 1

    assert points == 11
    

def test_rule_constructor():
    """Checks if the rule constructor works as expected.
    """
    test_rule = lex_bases.rule(
        "TEST",
        r"test",
        dependencies=[lex_bases.rule("TEST_2", r"test_2")],
        function=example_function,
    )

    points = 0
    """
    The reason why we don't compare with == between
    two rules is because if a error is in the rule always will be true.

    Think it this way:

    Imagine that rule constructor change the way in how works with the regex patterns

    Now if we create two instance with the same config, __eq__ will return us true, 
    but if you compare with the expected results, will be posible to catch a error.
    """
    if test_rule.type == "TEST":
        points += 1

    if test_rule.regex == r"test":
        points += 1

    if len(test_rule.regex_compiled.match("test").group(0)) > 0:
        points += 1

    if test_rule.dependencies[0] == lex_bases.rule("TEST_2", r"test_2"):
        points += 1

    if test_rule.match_function == example_function:
        points += 1

    if test_rule.get_if_save_to_token_stream() == True:
        points += 1

    if test_rule.get_if_uses_skips() == False:
        points += 1

    if test_rule.get_if_accept_skips() == True:
        points += 1

    if test_rule.get_regex_group() == 0:
        points += 1

    assert points == 9


def test_rule_clean_text():
    """Test if the _clean_text_based_on_list function can clean a text.
    """
    assert (
        lex_bases.rule("", r"")._clean_text_based_on_list(
            "test", [lex_bases.rule("TEST", r"test")]
        )
        == ""
    )


def test_rule_compile_token():
    """Tries to compile a token to check if all works as expected.
    """
    test_rule = lex_bases.rule("TEST", r"test")

    new_token = test_rule._compile_text_to_token(
        "test",
        line_where_finded=0,
        col_where_finded=0,
        obsolete_line_count=0,
        obsolete_line_count_function=example_function,
    )

    expected_token = lex_bases.token("TEST", "test")
    expected_token.set_line_where_finded(0)
    expected_token.set_col_where_finded(0)
    expected_token.set_deprecated_line_pos(0)

    assert new_token._complete_equal(expected_token)


def test_match_rule():
    """Checks if the rule can compile a token as expected.
    """
    test_rule = lex_bases.rule("TEST", r"test")

    new_token = test_rule.check_if_match_with_rule(
        "clear_thistest",
        rules_to_ignore=[lex_bases.rule("CLEAR_THIS", r"clear_this")],
        actual_line=0,
        actual_col=0,
        obsolete_line_count=0,
        obsolete_line_count_function=example_function,
    )

    expected_token = lex_bases.token("TEST", "test")
    expected_token.set_line_where_finded(0)
    expected_token.set_col_where_finded(0)
    expected_token.set_deprecated_line_pos(0)

    assert new_token[1]._complete_equal(expected_token)
