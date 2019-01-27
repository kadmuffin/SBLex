"""This file contains ready-made rules to use [some functions in the rules use the ast.literal_eval].
"""

from .lex_bases import rule
import re
import ast


def _ast_eval_function(text):
    try:
        return ast.literal_eval(text)
    except SyntaxError:
        return None


def _comment_function(text):
    """Replaces some stuff on the comment text to be valid to ast.literal_eval
    """
    new_text = text
    for regex in [r"\/\*", r"\*\/"]:
        new_text = re.sub(regex, '"""', new_text)

    return _ast_eval_function(re.sub(r"\*", "", new_text))


_string_regex = r"""("|')((?:\\\1|(?:(?!\1).))*)\1"""

_int_regex = r"[0-9]+"

_float_regex = r"([0-9]+|)(\.|\,)[0-9]+"

_bool_regex = r"(True|False)+"

_list_regex = r"""(\[(\n+|)(((\+|-|)[0-9]+\.[0-9]+|(\+|-|)[0-9]+|(True|False)|(("|')((?:\\\9|(?:(?!\9).))*)\9)|)(,(( +)|( +|)\n(\13+|)|)((\+|-|)[0-9]+\.[0-9]+|(\+|-|)[0-9]+|(True|False)|(("|')((?:\\\21|(?:(?!\21).))*)\21))|)+)+(\n+|)\])"""

_tuple_regex = r"""(\((\n+|)(((\+|-|)[0-9]+\.[0-9]+|(\+|-|)[0-9]+|(True|False)|(("|')((?:\\\9|(?:(?!\9).))*)\9)|)(,(( +)|( +|)\n(\13+|)|)((\+|-|)[0-9]+\.[0-9]+|(\+|-|)[0-9]+|(True|False)|(("|')((?:\\\21|(?:(?!\21).))*)\21))|)+)+(\n+|)\))"""

_dict_regex = r"""{(\n+|)(((("|')((?:\\\5|(?:(?!\5).))*)\5( +|)):( +|)((\+|-|)[0-9]+\.[0-9]+|(\+|-|)[0-9]+|(True|False)|(("|')((?:\\\14|(?:(?!\14).))*)\14)))(,(( +|)|( +|)\n( +|)|)((("|')((?:\\\23|(?:(?!\23).))*)\23( +|)):( +|)((\+|-|)[0-9]+\.[0-9]+|(\+|-|)[0-9]+|(True|False)|(("|')((?:\\\32|(?:(?!\32).))*)\32)))+|)+|)+(\n+|)}"""

_comment_regex = r"\/\*[\s\S]*?\*\/|\/\/.*"

_identifier_regex = r"([a-zA-Z]|_[a-zA-Z]){1}[a-zA-Z0-9_]*"
_operator_regex = r"[\+\-\*\%\=\&\|\~\^\<\>\?\:\!\/]+"
_operator_arithmetric_regex = r"\*|\+|\-|\/"
_var_regex = r"var"
var_declaration = rule(
    "VAR_DECLARATION",
    _var_regex,
    {
        "rules": [
            rule("IDENTIFIER", _identifier_regex).set_custom_error(
                "Something is wrong here... in the line: [[LINE]], Expected a IDENTIFIER but got this -> '[[TEXT]]'"
            ),
            rule("EQ_OPERATOR", r"=").set_custom_error(
                "Yay... a error at line: [[LINE]], Expected a '=' but got this -> '[[TEXT]]'"
            ),
            rule(
                "EXPRESSION",
                [
                    r"^[\d ()+-\/\*]+$",
                    _string_regex,
                    _float_regex,
                    _int_regex,
                    _list_regex,
                    _tuple_regex,
                    _dict_regex,
                    _bool_regex,
                ],
                function=_ast_eval_function,
            ).set_custom_error(
                "We need to repair this, at line: [[LINE]], Expected one of this [STRING, FLOAT, INT, LIST, TUPLE, DICT, BOOL] but got this -> '[[TEXT]]'"
            ),
        ],
        "ignore_rules": [],
    },
)

operator_arithmetric = rule("OPERATOR_ARITHMETRIC", _operator_arithmetric_regex)

operator_all = rule("OPERATOR", _operator_regex)
identifier = rule("IDENTIFIER", _identifier_regex)
comment = rule(["COMMENT", False], _comment_regex)
string = rule("STRING", _string_regex, None, _ast_eval_function)
int = rule("INT", _int_regex, None, _ast_eval_function)
float = rule("FLOAT", _float_regex, None, _ast_eval_function)
bool = rule("BOOL", _bool_regex, None, _ast_eval_function)
list = rule("LIST", _list_regex, None, _ast_eval_function)
tuple = rule("TUPLE", _tuple_regex, None, _ast_eval_function)
dict = rule("DICTIONARY", _dict_regex, None, _ast_eval_function)
