"""This file contains the lexer and the lexer constructor.
"""

import re
from .lex_bases import token
from .lex_bases import rule


class _lexer:
    """This class is able to convert text to tokens based on rules.

    Attributes:
        original_text (str): It is the original text loaded in the lexer.
        text_to_process (str): It is the text that is being processed by the lexer.
        rules (list(rule)): These are rules used by the lexer to identify tokens.
        rules_toignore (list(rule)): These are rules that tell the lexer to ignore the token in the text.
        pos_in_str (int): Current position of the lexer in the text by character.
        pos_in_line (int): Current position of the lexer in a line by character.
        line (int): This is the line in which the lexer is processing the text.
        deprecated_line_count (int): Is the line where the lexer is based on tokens and not on their value [OBSOLETE].
        custom_error (function or str): Is the error message which is executed if it is a function or shown when something fails.
    """

    def __init__(self, rules, ignore_rules, custom_error=None):
        """Lexer constructor.

        Args:
            rules (list(rule)): These are the rules used by the lexer to recognize tokens in a text.
            ignore_rules (list(rule)): are rules used to ignore tokens in a text.
            custom_error (function or str, optional): Defaults to None. It is a function that is executed when a token is invalid, it can also be a str.
        """

        self._original_text = ""
        self._text_to_process = ""
        self._rules = rules
        self._rules_to_ignore = ignore_rules
        self._pos_in_str = 0
        self._pos_in_line = 0
        self._line = 0
        self._deprecated_line_count = -1
        self._custom_error = custom_error

    def __str__(self):
        """Return a representation of the lexer.

        Returns:
            str: Representation of the lexer.
        """

        # If the lexer not ended processing the loading text when __str__ is called, print a some data
        if self._text_to_process is not None:
            return "Lexer(current_text: '%s', pos: %s, line: %s)" % (
                self._text_to_process.split("\n")[0],
                self._pos_in_str,
                self._line,
            )

        # Print original text if the lexer ended processing the text
        return "Lexer(loaded_text: '%s')" % (self._original_text,)

    def __repr__(self):
        """Returns the representation created by __str__().

        Returns:
            str: Representation of the lexer.
        """

        return self.__str__()

    def _load_text(self, text):
        """Loads text into the lexer.

        Args:
            text (str): It is the text to load in the lexer.

        Returns:
            self: Returns the lexer instance.
        """

        self._original_text = text
        self._text_to_process = text
        return self

    def get_original_text(self):
        """Returns the original text that was loaded into the lexer.

        Returns:
            str: It is a copy of the text loaded to the lexer.
        """

        return self._original_text

    def _get_error_data(self):
        """Compile lexer information when something goes wrong.

        Returns:
            dict: Dictionary with lexer information.
        """

        if isinstance(self._text_to_process, str):

            # Try to use the jump_line rule for split out the text and select the first element
            try:
                invalid_text = self._rules[0].regex_compiled.split(self._text_to_process)[0]
            except:
                invalid_text = self._text_to_process

        return {"line": self._line, "pos": self._pos_in_str, "text": invalid_text}

    def _throw_lexing_error(self):
        """Default error message when there is an error in the lexer.

        Raises:
            SyntaxError: When a token is invalid raises a syntax error.
        """

        data = self._get_error_data()

        # Create default error message for raise
        error_message = "Ilegal character! at line [ %s ] { Invalid Text } -> '%s'" % (
            data["line"],
            data["text"],
        )

        raise SyntaxError(error_message)

    def _reset_lexer(self):
        """This reset the lexer variables for be used again.
        """
        self._pos_in_line = 0
        self._pos_in_str = 0
        self._line = 0
        self._deprecated_line_count = -1

    def evaluate(self, text=None):
        """
        Convert a text to a list of tokens.

        Args:
            text (str): Is the text to be processed by the lexer.

        Returns:
            list(token): Returns a list of tokens.

        """
        self._reset_lexer()
        
        if text is not None:
            self._load_text(text)

        token_stream = []
        actual_token = None
        dependent_token = None
        tokens_matching_dependent = []

        while self._text_to_process is not None:
            if dependent_token is None:
                actual_token = self._get_next_token(
                    self._rules, self._rules_to_ignore, self._custom_error
                )

            else:
                # If this part is executed it means that a dependent token was found.
                for rule_to_check in dependent_token.get_dependencies()["rules"]:

                    # If the rule to check more rules on it.
                    if isinstance(rule_to_check, list):

                        error = rule_to_check[0].get_custom_error()

                        # When the rule dosen't have a custom error build-in call to the default one.
                        if error is None:
                            error = self._custom_error

                        rules = []

                        # Check if the first rule on the dependencies is a jump line.
                        rule_0_in_dependencies = dependent_token.get_dependencies()[
                            "rules"
                        ][0]
                        if rule_0_in_dependencies.type is "JUMP_LINE":
                            rules.append(rule_0_in_dependencies)

                        if dependent_token.get_if_uses_skips():
                            for skip in dependent_token.get_skips_rules():
                                rules.insert(1, skip)

                        for internal_rule in rule_to_check:
                            rules.append(internal_rule)

                    else:

                        if rule_to_check.type == "JUMP_LINE":
                            continue

                        error = rule_to_check.get_custom_error()

                        # When the rule to check doesn't have a custom error, use lexer custom error.
                        if error is None:
                            error = self._custom_error

                        # Here you create a list with the skips, jump lines and the current rule.
                        rules = [
                            dependent_token.get_dependencies()["rules"][0],
                            rule_to_check,
                        ]

                    if dependent_token.get_if_uses_skips():
                        for skip in dependent_token.get_skips_rules():
                            rules.insert(1, skip)

                    # Find out if the next token matches the list of rules.
                    tokens_matching_dependent.append(
                        self._get_next_token(
                            rules,
                            dependent_token.get_dependencies()["ignore_rules"],
                            error,
                        )
                    )

                # In case you had gone all over add the token to the main list.
                token_stream.append(tokens_matching_dependent)
                dependent_token = None
                actual_token = self._get_next_token(self._rules, self._rules_to_ignore)

            if dependent_token is None and actual_token.is_dependent():
                dependent_token = actual_token
                tokens_matching_dependent.append(actual_token)

            elif dependent_token is None:
                token_stream.append(actual_token)

        return token_stream

    def analyze_text(self, text, rules, ignore_rules=None):
        """It is used to analyze text based on specific rules.

        Args:
            text (str): Text to analyze.
            rules (list(rule)): List of rules to be checked.
            ignore_rules (list(rule), optional): Defaults to None. Rules to ignore in the text.

        Returns:
            dict: Dictionary with information about the analyzed text such as the rule, if matched or the compiled token.
        """

        dict_with_info = {
                "fit_with_a_rule": False,
                "rule_that_matched": None,
                "token": None,
            }

        for rule_in_list in rules:

            info_from_text = rule_in_list.check_if_match_with_rule(
                text,
                ignore_rules,
                self._line,
                self._pos_in_line,
                self._deprecated_line_count,
                self._plus_deprecated_line_count,
            )

            if info_from_text[0]:
                dict_with_info = {
                    "fit_with_a_rule": info_from_text[0],
                    "rule_that_matched": rule_in_list,
                    "token": info_from_text[1],
                }

        return dict_with_info

    def _jump_and_remove(self, jump_size, text_to_remove):
        """Allows to jump and remove any value in the text to be processed.

        Args:
            jump_size (int): It is how much to jump in the text.
            text_to_remove (str): Is the text to remove.

        Returns:
            self: Returns the _lexer instance.
        """

        self._pos_in_str += jump_size
        self._pos_in_line += jump_size

        if self._pos_in_str > len(self._original_text) - 1:
            self._text_to_process = None
        else:
            self._text_to_process = self._text_to_process.replace(text_to_remove, "", 1)

        return self

    def _plus_deprecated_line_count(self):
        """It is a function used by the line count to add 1 to the current line [OBSOLETE].
        """

        self._deprecated_line_count += 1

    def _get_next_token(self, rules, ignore_rules, custom_error=None):
        """Allows to obtain the next token in the text to be processed.

        Args:
            rules (list(rule)): They are the sadas rules to recognize tokens in a text.
            ignore_rules (list(rule)): These are the rules to ignore when recognizing tokens in the text.
            custom_error (function or str, optional): Defaults to None. It is the custom error which can be a str or it can be a function that is called when a token is invalid.

        Returns:
            token: Returns a token when a rule fits.
        """

        while self._text_to_process is not None:

            # Check if any of the rules in the ignore_rules list match, if match jump it.
            analyzed_text = self.analyze_text(self._text_to_process, ignore_rules)
            if analyzed_text["fit_with_a_rule"]:
                self._jump_and_remove(
                    len(analyzed_text["token"].get_truly_original_value()),
                    analyzed_text["token"].get_truly_original_value(),
                )
                continue

            # Do the same as above but with the normal rule list this time.
            analyzed_text = self.analyze_text(
                self._text_to_process, rules, ignore_rules
            )

            if not analyzed_text["fit_with_a_rule"]:
                # If not match throw a error.
                if custom_error is None:
                    self._throw_lexing_error()
                data = self._get_error_data()
                if isinstance(custom_error, str):
                    error_message = custom_error.replace("[[LINE]]", str(data["line"]))
                    error_message = error_message.replace("[[TEXT]]", data["text"])
                    raise SyntaxError(error_message)
                else:
                    custom_error(data)

            # Here is counted the line.
            new_line_matches = len(
                re.findall(r"\n", analyzed_text["token"].get_truly_original_value())
            )

            self._line += new_line_matches
            if new_line_matches > 0:
                self._pos_in_line = 0

            if not analyzed_text["token"].get_if_save_to_token_stream():
                self._jump_and_remove(
                    len(analyzed_text["token"].get_truly_original_value()),
                    analyzed_text["token"].get_truly_original_value(),
                )

                continue

            self._jump_and_remove(
                len(analyzed_text["token"].get_truly_original_value()),
                analyzed_text["token"].get_truly_original_value(),
            )

            # When matches return the token.
            return analyzed_text["token"]

        return token("EOF", None).set_line_where_finded(self._line)


class lex:
    """It is a builder made to facilitate the process of using lexer which allows you to convert text to a list of tokens.

    Attributes:
        rules (list(rule)): These are the functions used to recognize tokens in a text.
        ignore_r (list(rule)): These are the rules used to ignore tokens in the text.
        skip_rules (list(rule)): These are skip type rules.
        custom_error (function or str): Is the custom error message, which can be a str or a function which is called when a token is invalid.
    
    Args:
        jump_regex (regexp, optional): Defaults to r"\n". These are the regex patterns used to separate each token.
        custom_error (function or str, optional): Defaults to None. This is the custom error text or function.
    """

    def __init__(self, jump_regex=r"\n", custom_error=None):
        """Constructor of lex().

        Args:
            jump_regex (regexp, optional): Defaults to r"\n". These are the regex patterns used to separate each token.
            custom_error (function or str, optional): Defaults to None. This is the custom error text or function.
        """

        self.rules = [rule(["JUMP_LINE", False], jump_regex)]
        self.ignore_r = []
        self._skip_rules = []
        self.custom_error = custom_error

    def add(
        self,
        name,
        pattern,
        dependencies=None,
        function=None,
        accept_skips_rules=True,
        capturing_group=0,
    ):
        """Allows you to add a rule to the lexer.

        Args:
            name (object or list): It is the name of the rule, in case to be a list: the position 0 will mean the name of the rule and the position 1 a bool that say if is returned by the lexer.
            pattern (str or list(str)): These are the regex patterns used by the rule to identify tokens.
            dependencies (list(rule) o dict, optional): Defaults to None. They are the dependencies of the rule to consider a valid rule.
            function (function, optional): Defaults to None. It is the function that is executed when a token is found that fits with the pattern of the rule, it can modify the value of the token.
            accept_skips_rules (bool, optional): Defaults to True. Allows you to set whether to add skips rules to dependencies.
            capturing_group (int, optional): Defaults to 0. Allow you to set what capturing group of regex to use.
        
        Returns:
            int: Returns the position where the rule was added in the list of the constructor.
        """

        if (
            isinstance(dependencies, dict)
            and "rules" in dependencies.keys()
            and len(dependencies["rules"]) >= 1
        ):
            converted_dependencies = dependencies
            converted_dependencies["rules"].insert(0, self.rules[0])

        elif isinstance(dependencies, list):
            converted_dependencies = dependencies
            converted_dependencies.insert(0, self.rules[0])

        else:
            converted_dependencies = None

        self.rules.append(
            rule(name, pattern, converted_dependencies, function)
            .set_accept_skips(accept_skips_rules)
            .set_regex_group(capturing_group)
        )

        return len(self.rules) - 1

    def skip(self, pattern, dependencies=None, function=None, accept_skips_rules=True):
        """They are rules that are jumped when they are encuntran but they can execute functions and have dependencies.

        Args:
            pattern (str or list(str)): regex patterns to recognize tokens in a text.
            dependencies (list(rule) or dict, optional): Defaults to None. These are the dependencies to consider a token valid.            
            function (function, optional): Defaults to None. It is the function to execute when a token is found and can change the value of the token if necessary.
            accept_skips_rules (bool, optional): Defaults to True. Allows to set if skips rules are added to dependencies.
        
        Returns:
            int: Returns the position where the rule was added in the constructor list.
        """

        converted_dependencies = None

        if (
            isinstance(dependencies, dict)
            and "rules" in dependencies.keys()
            and len(dependencies["rules"]) >= 1
        ):
            converted_dependencies = dependencies
            # Insert the jump line rule into the dependencies dict['rules']
            converted_dependencies["rules"].insert(0, self.rules[0])

        elif isinstance(dependencies, list):
            converted_dependencies = dependencies

            # Insert the jump line rule into the dependencies list
            converted_dependencies.insert(0, self.rules[0])

        self._skip_rules.append(
            rule(
                ["SKIPPED", False], pattern, converted_dependencies, function
            ).set_accept_skips(accept_skips_rules)
        )

        self.rules.append(
            rule(
                ["SKIPPED", False], pattern, converted_dependencies, function
            ).set_accept_skips(accept_skips_rules)
        )

        # Return the pos where was loaded the rule in self.rules
        return len(self.rules) - 1

    def load_premade(self, premade, load_functions=True):
        """Allows to load pre-made rules to the builder in a simpler way.

        Args:
            premade (rule or list(rule)): These are the rules to load to the lexer.
            load_functions (bool, optional): Defaults to True. Allows you to choose whether to load the functions of the pre-done rules.

        Returns:
            list(int): Returns the position where the rules were added in the constructor list.
        """
        pos_in_rule_list = []

        if isinstance(premade, list):
            for premade_rule in premade:
                tmp = premade_rule
                if tmp.dependencies is not None:
                    # Insert the jump line rule into the dependencies list
                    tmp.dependencies["rules"].insert(0, self.rules[0])

                if not load_functions:
                    tmp.match_function = None

                # Save the actual position on the rules list
                pos_in_rule_list.append(len(self.rules))

                # Add rule to rule list
                self.rules.append(tmp)

        else:
            tmp = premade
            if tmp.dependencies is not None:
                # Insert the jump line rule into the dependencies list
                tmp.dependencies["rules"].insert(0, self.rules[0])

            if not load_functions:
                tmp.match_function = None

            # Save the actual position on the rules list
            pos_in_rule_list.append(len(self.rules))

            # Add rule to rule list
            self.rules.append(tmp)

        return pos_in_rule_list

    def _ignore(self, pattern, force_usage=False):
        """[NOT WORKING RIGHT NOW, FOR USE IT ANYWAY USE THE PARAMETER FORCE_USAGE] It allows to add a rule that is recognized and omitted before passing through the lexer.

        Args:
            pattern (str): It is the regex pattern used to recognize the rule in the text.

        Returns:
            int: Returns the position where the rule was added in the constructor list.
        """
        if not force_usage: raise Warning("This function is not working right now, most likely it will break the lexer, if you want to use it anyway you need to use the option force_usage=True like this -> _ignore(r'my_pattern', force_usage=True).")
        self.ignore_r.append(rule("IGNORED", pattern))

        return len(self.rules) - 1

    def build(self, add_skips_in_rules=True):
        """Allows you to build the lexer.

        Args:
            add_skips_in_rules (bool, optional): Defaults to True. Allows you to decide whether to add the skips to the dependencies of other rules.

        Returns:
            _lexer: Returns the built lexer.
        """

        if add_skips_in_rules:
            for rule_d in self.rules:
                if not rule_d.get_if_accept_skips():
                    continue

                rule_d.set_skip_rules(self._skip_rules)

        return _lexer(self.rules, self.ignore_r, self.custom_error)


    def evaluate(self, text):
        """Convert a text to a list of tokens.

        Args:
            text (str): Is the text to be processed by the lexer.

        Returns:
            list(token): Returns a list of tokens.

        """
        return self.build().evaluate(text)

# ------------------------------------------#
