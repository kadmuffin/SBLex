"""This file contains the lexer bases: token and rule.
"""

import re


def _convert_to_token_dependent_format(dependencies):
    """Converts the entered value to a dependency format acceptable for the token() class.

    Args:
        dependencies (list(rule) or dict): These are rules in a list.

    Returns:
        list: Returns a list with a boolean in position 0 and dependencies in position 1.
    """

    if isinstance(dependencies, dict) and "rules" in dependencies.keys():
        converted_input = dependencies
        if "ignore_rules" not in dependencies.keys():
            converted_input["ignore_rules"] = []

        return [True, converted_input]

    elif isinstance(dependencies, list):
        converted_input = {"rules": dependencies, "ignore_rules": []}
        return [True, converted_input]

    else:
        return [False, {"rules": [], "ignore_rules": []}]


class token(object):
    """A token mainly stores a value and the type of text found by the lexer.

    Attributes:
        type (object): This is the type/name of the token.
        value (object): It is the value of the token.
        _not_processed_value (str): Is the original value of the token in case of the value to be modified by a function.
        _truly_original_value (str): Truly original value, with no capturing groups or functions editing the value.
        _show_on_token_stream (bool): Says if the lexer returns the token in the token list.
        _finded_in_line (int): This is the line where the token was found.
        _uses_skips (bool): Represents if it uses skips rules.
        _skips_rules (list(rule) or None): List of skip type rules.
        _deprecated_line_count (int): This is the line in which was found [OBSOLETE].
        _is_dependent (bool): It is a boolean that indicates if the token has dependencies.
        dependencies (list(rule) or dict): It is a list of dependencies to consider the token valid.
        _token_parent (rule or None): It is the rule that created the token.

    """

    def __init__(self, type, value, dependencies=None):
        """Token constructor.

        Args:
            type (object): It is the type of the token, which is usually a string.
            value (object): It is the value of the token.
            dependencies (list(rule) or dict, optional): Defaults to None. These are the dependencies of the token to be considered valid.
        """
        self.type = type
        self.value = value
        self._not_processed_value = None
        self._truly_original_value = None
        self._show_on_token_stream = True
        self._finded_in_line = None
        self._finded_in_col = None
        self._uses_skips = False
        self._skips_rules = None
        self._deprecated_line_count = None
        self._token_parent = None

        converted_input = _convert_to_token_dependent_format(dependencies)

        self._is_dependent = converted_input[0]
        self.dependencies = converted_input[1]

    def __eq__(self, other):
        """Checks if the other object is equal to this rule.

        Args:
            other (rule): Is the other object to check if equal to this object.

        Returns:
            bool: Returns True when it is the same and False when it is not.
        """
        if self.type != other.type and self.value != other.value:
            return False
            
        return True

    def __ne__(self, other):
        """Needed for be possible to use != on Python2, Returns the inverse if __eq__().

        Args:
            other (rule): Is the other rule to check if the inverse of ==.
        """
        return not self.__eq__(other)

    def __str__(self):
        """Returns a String representation of the token() class.

        Returns:
            str: Representation of the token class.
        """
        if self._not_processed_value is not None:
            return "token(type: '%s', value: %s, original_value: %s, line: %s)" % (
                self.type,
                repr(self.value),
                repr(self._not_processed_value),
                self._finded_in_line,
            )

        return "token(type: '%s', value: %s, line: %s)" % (
            self.type,
            repr(self.value),
            self._finded_in_line,
        )

    def __repr__(self):
        """Returns the representation created by __str__().

        Returns:
            str: Returns the representation of the token class.
        """

        return self.__str__()

    def _complete_equal(self, other):
        """Checks if the other object is exactly equal to this rule.

        Args:
            other (token): Is the other object to check if exactly equal to this object.

        Returns:
            bool: Returns True when it is the same and False when it is not.
        """
        if (
            self.type != other.type
            or self.value != other.value
            or self._show_on_token_stream != other.get_if_save_to_token_stream()
            or self._finded_in_line != other.get_line_where_finded()
            or self._finded_in_col != other.get_col_where_finded()
            or self._deprecated_line_count != other.get_deprecated_line_pos()
        ):
            return False

        return True

    def set_truly_original_value(self, value):
        """It lets you modify the truly original value of the token.

        Args:
            value (str): It will be the new original value.

        Returns:
            self: Returns the token instance.
        """
        self._truly_original_value = value
        return self

    def set_token_parent(self, parent):
        """Allows you to set which rule I create to the token.

        Args:
            parent (rule): Is the rule that created this token.

        Returns:
            self: Returns the instance of the token.
        """

        self._token_parent = parent
        return self

    def set_if_save_to_token_stream(self, display):
        """Allows you to configure whether the token is saved in the list of tokens returned by the lexer.

        Args:
            display (bool): If it is `True` the lexer would return the token.

        Returns:
            self: Returns the instance of the token when used.
        """

        self._show_on_token_stream = display
        return self

    def set_col_where_finded(self, column):
        """Allows you to configure in what column the token was found in a string.

        Args:
            column (int): Is the column where a token was found.

        Returns:
            self: Returns the token instance.
        """

        self._finded_in_col = column
        return self

    def set_line_where_finded(self, line):
        """Allows you to configure in what line the token was found in a string.

        Args:
            line (int): Is the line where a token was found.

        Returns:
            self: Returns the token instance.
        """

        self._finded_in_line = line
        return self

    def set_not_processed_value(self, value):
        """It is the original value of the token in case of the value to be modified by a function.

        Args:
            value (str): Value to be set to original_value

        Returns:
            self: Returns the token instance.
        """

        self._not_processed_value = value
        return self

    def set_deprecated_line_pos(self, index):
        """Used to set a value for the line counter [OBSOLETE].

        Args:
            index (int): It is the pocision of the object based on the end of the value.

        Returns:
            self: Returns the token instance.
        """
        self._deprecated_line_count = index
        return self

    def set_skips_rules(self, skips_list):
        """Defines the skip type rules that are used when finding a dependency.

        Args:
            skips_list (list(rule)): List of skip type rules.

        Returns:
            self: Returns the token instance.
        """

        if skips_list is None:
            self._uses_skips = False
        else:
            self._uses_skips = True
        self._skips_rules = skips_list
        return self

    def get_parent(self):
        """Return the rule that created this token.

        Returns:
            rule: It's the rule that compiled this token.
        """

        return self._token_parent

    def get_truly_original_value(self):
        """Returns the truly original value of the token.

        Returns:
            str: Is the original value of the token.
        """
        if self._truly_original_value is not None:
            return self._truly_original_value
        return self.value

    def get_skips_rules(self):
        """Returns the list of skip rules.

        Returns:
            list: List of rules.
        """
        return self._skips_rules

    def get_if_uses_skips(self):
        """Returns True if has skip rules.

        Returns:
            bool: Returns True if it has a skip type rule and False if not.
        """

        return self._uses_skips

    def get_value(self):
        """Returns the value of the token when called.

        Returns:
            object: It is the value of the token, which can be any type.
        """
        return self.value

    def get_length_of_value(self):
        """Returns the length of the value, is equal to using len(token.getvalue()).

        Returns:
            int: Length of the value.
        """

        return len(self.value)

    def get_not_processed_value(self):
        """Returns the original value or the backup of the value.

        Returns:
            str: It is the original value/backup.
        """

        if self._not_processed_value is not None:
            return self._not_processed_value
        return self.value

    def get_length_of_not_processed_value(self):
        """Returns the length of the original value, is equivalent to using len().

        Returns:
            int: It is the length of the original value/backup.
        """

        if self._not_processed_value is not None:
            return len(self._not_processed_value)
        return len(self.value)

    def get_type(self):
        """Returns the type/name of the token.

        Returns:
            object: Is the type of the token, which can be any format, commonly str.
        """

        return self.type

    def is_dependent(self):
        """Returns True if the token has dependencies and False if not.

        Returns:
            bool: True if it has dependencies and False if not.
        """

        return self._is_dependent

    def get_dependencies(self):
        """Returns a dictionary with dependencies and rules to ignore.

        Returns:
            dict: It is a dictionary with the dependencies and rules to ignore.
        """

        return self.dependencies

    def get_if_save_to_token_stream(self):
        """Returns a boolean that indicates if the token will be saved by the lexer.

        Returns:
            bool: Represents whether the token is saved by the lexer.
        """

        return self._show_on_token_stream

    def get_line_where_finded(self):
        """Returns where the line where the token was found in a text.

        Returns:
            int: The line where the token was found.
        """

        return self._finded_in_line

    def get_col_where_finded(self):
        """Returns where the column where the token was found in a text.

        Returns:
            int: The column where the token was found.
        """

        return self._finded_in_col

    def get_deprecated_line_pos(self):
        """It's the line where the token was found [OBSOLETE].

        Returns:
            int: The position of the token based on the line breaks.
        """

        return self._deprecated_line_count


class rule(object):
    """The rules contain patterns that the lexer uses to identify tokens.

    Attributes:
        type (object): This is the type/name of the token.
        regex (str or list(str)): These are patterns used to recognize tokens.
        regex_compiled (Pattern or list(Pattern)): These are the compiled patterns.
        regex_is_array (bool): It is a boolean that says if regex is a list.
        match_function (function): Is a function that is used when a pattern recognizes a token.
        custom_error (function or str): This is a custom error message.
        dependencies (list(rule) or dict): Are the dependencies of the token to be valid.
        _show_on_token_stream (bool): Tells the lexer if he has to return it.
        _uses_skips (bool): Dice uses skips type rules in dependencies.
        _skips_rules (list(rule)): List of skip type rules.
        _accept_skips (bool): Tells the constructor whether to add skip rules.
        _regex_group (int): Is the capturing group of regex.
    """

    def __init__(self, rule_type, regex, dependencies=None, function=None):
        """Rule constructor.

        Args:
            rule_type (object): It is the type/name of the rule.
            regex (str or list(str)): These are the regex patterns for finding tokens.
            dependencies (list(rule) or dict, optional): Defaults to None. These are the dependencies to consider a token valid.
            function (function, optional): Defaults to None. It is a function that is executed when a token is found.
        """

        if isinstance(rule_type, list):
            self.type = rule_type[0]
            self._show_on_token_stream = rule_type[1]
        else:
            self.type = rule_type
            self._show_on_token_stream = True

        self.dependencies = dependencies

        if isinstance(regex, list):
            self.regex = []
            self.regex_compiled = []
            for regex_alone in regex:
                self.regex.append(regex_alone)
                self.regex_compiled.append(re.compile(regex_alone))
                self.regex_is_array = True
        else:
            self.regex = regex
            self.regex_compiled = re.compile(regex)
            self.regex_is_array = False

        self._uses_skips = False
        self._skips_rules = None
        self.match_function = function
        self.custom_error = None
        if dependencies is not None:
            self._accept_skips = True
        else:
            self._accept_skips = False
        self._regex_group = 0

    def __eq__(self, other):
        """Checks if the other object is equal to this rule.

        Args:
            other (rule): Is the other object to check if equal to this object.

        Returns:
            bool: Returns True when it is the same and False when it is not.
        """
        if (
            self.type != other.type
            or self.regex != other.regex
        ):
            return False

        return True

    def __ne__(self, other):
        """Needed for be possible to use != on Python2, Returns the inverse if __eq__().

        Args:
            other (rule): Is the other rule to check if the inverse of ==.
        """
        return not self.__eq__(other)

    def __str__(self):
        """Returns a representation of the rule in str format.

        Returns:
            str: Representation of the rule.
        """

        return "rule(name: '%s', pattern: r'%s')" % (self.type, self.regex)

    def __repr__(self):
        """Returns the representation created by __str__().

        Returns:
            str: Representation of the rule.
        """

        return self.__str__()

    def _complete_equal(self, other):
        """Checks if the other object is exactly equal to this rule.

        Args:
            other (rule): Is the other object to check if exactly equal to this object.

        Returns:
            bool: Returns True when it is the same and False when it is not.
        """
        if (
            self.type != other.type
            or self.regex != other.regex
            or self.regex_compiled != other.regex_compiled
            or self.dependencies != other.dependencies
            or self.match_function != other.match_function
            or self.get_if_save_to_token_stream() != other.get_if_save_to_token_stream()
        ):
            return False

        return True

    def get_regex_group(self):
        """Returns the _regex_group value.
        
        Returns:
            int: Indicates in what group of the regex get the token value.
        """
        return self._regex_group

    def get_if_accept_skips(self):
        """Returns property _accept_skips.

        Returns:
            str: Indicates if it accepts skips.
        """
        return self._accept_skips

    def get_custom_error(self):
        """Returns a custom error.

        Returns:
            function or str: Custom error.
        """

        return self.custom_error

    def get_if_uses_skips(self):
        """Returns True if has skip rules.

        Returns:
            bool: Returns True if it has a skip type rule and False if not.
        """

        return self._uses_skips

    def get_if_save_to_token_stream(self):
        """Indicates if the token is saved in the list of tokens returned by the lexer.

        Returns:
            bool: If it is `True` the lexer would return the token.
        """

        return self._show_on_token_stream

    def _get_skips_rules(self):
        """Returns the skips type rules.

        Returns:
            list: These are the skip type rules.
        """

        return self._skips_rules

    def set_if_save_to_token_stream(self, display):
        """Allows you to configure whether the token is saved in the list of tokens returned by the lexer.

        Args:
            display (bool): If it is `True` the lexer would return the token.

        Returns:
            self: Returns the instance of the token when used.
        """

        self._show_on_token_stream = display
        return self

    def set_regex_group(self, group):
        """Allow you to set what capturing group of regex to use.

        Args:
            group (int): Is the capturing group of regex.

        Returns:
            self: Returns the instance of the rule.
        """
        self._regex_group = group

        return self

    def set_skip_rules(self, skips_list):
        """Allows you to set which skips rules are used.

        Args:
            skips_list (list(rule)): These are skip type rules.

        Returns:
            self: Returns the instance of the rule.
        """

        if skips_list is not None:
            self._uses_skips = True

        else:
            self._uses_skips = False

        self._skips_rules = skips_list
        return self

    def set_accept_skips(self, bool):
        """Allows you to set whether the constructor can add skips rules.

        Args:
            bool: Sets whether the builder can add skip rules to it.

        Returns:
            self: Returns the instance of the rule.
        """

        self._accept_skips = bool
        return self

    def set_custom_error(self, error):
        """Used to set the value or function to be used when there is an error.

        Args:
            error (str or function): This is a custom error.

        Returns:
            self: Returns the rule instance.
        """

        self.custom_error = error
        return self

    def _compile_text_to_token(
        self,
        text,
        line_where_finded=None,
        col_where_finded=None,
        obsolete_line_count=None,
        obsolete_line_count_function=None,
        truly_original_value=None,
    ):
        """Compiles text in a token based on the rule.

        Args:
            text (str): It is the text, which will be considered the value of the token.
            line_where_finded (int, optional): Defaults to None. Line where the token was found.
            obsolete_line_count (int, optional): Defaults to None. It is a line counter [OBSOLETE].
            obsolete_line_count_function (function, optional): Defaults to None. Function to count the lines [OBSOLETE].
            truly_original_value (str, optional): Defaults to None. Is the value of the regex.group(0).

        Returns:
            token: Token compiled by the function.
        """

        if self.match_function is not None:

            if self.type == "SKIPPED":

                token_instance = token(self.type, text, self.dependencies)

                token_instance.set_token_parent(self)

                token_instance.set_if_save_to_token_stream(
                    self.get_if_save_to_token_stream()
                )
                
                if truly_original_value is not None: token_instance.set_truly_original_value(truly_original_value)

                token_instance.set_line_where_finded(line_where_finded)

                token_instance.set_col_where_finded(col_where_finded)

                token_instance.set_deprecated_line_pos(obsolete_line_count)

                token_instance.set_skips_rules(self._get_skips_rules())

                self.match_function()

                return token_instance

            else:
                try:
                    text_processed_by_function = self.match_function(text)
                except TypeError:
                    # If fails, the most probable is that the function doesn't have inputs.
                    self.match_function()
                    text_processed_by_function = None

                if text_processed_by_function is not None:
                    token_instance = token(
                        self.type, text_processed_by_function, self.dependencies
                    )

                    token_instance.set_token_parent(self)

                    token_instance.set_if_save_to_token_stream(
                        self.get_if_save_to_token_stream()
                    )

                    if truly_original_value is not None: token_instance.set_truly_original_value(truly_original_value)

                    token_instance.set_line_where_finded(line_where_finded)

                    token_instance.set_col_where_finded(col_where_finded)

                    token_instance.set_not_processed_value(text)

                    token_instance.set_deprecated_line_pos(obsolete_line_count)

                    token_instance.set_skips_rules(self._get_skips_rules())

                    return token_instance

                else:
                    token_instance = token(self.type, text, self.dependencies)

                    token_instance.set_token_parent(self)

                    token_instance.set_if_save_to_token_stream(
                        self.get_if_save_to_token_stream()
                    )

                    if truly_original_value is not None: token_instance.set_truly_original_value(truly_original_value)

                    token_instance.set_line_where_finded(line_where_finded)

                    token_instance.set_col_where_finded(col_where_finded)

                    token_instance.set_deprecated_line_pos(obsolete_line_count)

                    token_instance.set_skips_rules(self._get_skips_rules())

                    return token_instance
        else:

            # OBSOLETE LINE COUNTING SYSTEM
            # If the token has JUMP_LINE type, count the line with the function entered.
            if (
                isinstance(self.type, str)
                and self.type == "JUMP_LINE"
                and obsolete_line_count is not None
            ):
                obsolete_line_count_function()

            token_instance = token(self.type, text, self.dependencies)

            token_instance.set_token_parent(self)

            token_instance.set_if_save_to_token_stream(
                self.get_if_save_to_token_stream()
            )

            if truly_original_value is not None: token_instance.set_truly_original_value(truly_original_value)

            token_instance.set_line_where_finded(line_where_finded)

            token_instance.set_col_where_finded(col_where_finded)

            token_instance.set_deprecated_line_pos(obsolete_line_count)

            token_instance.set_skips_rules(self._get_skips_rules())

            return token_instance

    def _clean_text_based_on_list(self, text, rules_to_clean_in_text):
        """It is a function which eliminates rules that fit in a text.

        Args:
            text (str): It is the text where certain rules are going to be eliminated.
            rules_to_clean_in_text (list(rule)): Rules to be removed from the text.

        Returns:
            str: This is the text in which the entered rules were removed.
        """

        my_text = text
        for rule_to_remove in rules_to_clean_in_text:
            my_text = re.sub(rule_to_remove.regex, "", my_text)

        return my_text

    def check_if_match_with_rule(
        self,
        text_to_analize,
        rules_to_ignore=None,
        actual_line=None,
        actual_col=None,
        obsolete_line_count=None,
        obsolete_line_count_function=None,
        find_all=False,
    ):
        """This function searches if any section of the text fits the rule.

        Args:
            text_to_analize (str): Is the text to analyze
            rules_to_ignore (list(rule), optional): Defaults to None. This is the list of rules to ignore.
            actual_line (int, optional): Defaults to None. It is the line where the lexer is.
            obsolete_line_count (int, optional): Defaults to None. It is a line counter [OBSOLETE].
            obsolete_line_count_function (function, optional): Defaults to None. It is a function to count lines [OBSOLETE].

        Returns:
            token: It is a token compiled with the text and based on the rule.
        """

        text = text_to_analize
        if rules_to_ignore is not None:
            text = self._clean_text_based_on_list(text, rules_to_ignore)

        if self.regex_is_array:

            # Use the already compiled regex in the list for find a match in text.
            for regex in self.regex_compiled:
                matched = regex.match(text)

                if matched:
                    text = matched.group(self._regex_group)
                    truly_original_value = None
                    if self._regex_group > 0: 
                        truly_original_value = matched.group(0)
                    checked_token = self._compile_text_to_token(
                        text,
                        actual_line,
                        actual_col,
                        obsolete_line_count,
                        obsolete_line_count_function,
                        truly_original_value,
                    )

                    return [True, checked_token]

            return [False, None]
        else:
            matched = self.regex_compiled.match(text)

            if matched:
                text = matched.group(self._regex_group)
                truly_original_value = None
                if self._regex_group > 0: 
                    truly_original_value = matched.group(0)
                token = self._compile_text_to_token(
                    text,
                    actual_line,
                    actual_col,
                    obsolete_line_count,
                    obsolete_line_count_function,
                    truly_original_value,
                )

                return [True, token]

            if not matched:
                return [False, None]
