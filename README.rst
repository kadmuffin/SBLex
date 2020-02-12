SBLex
=====

.. image:: https://img.shields.io/pypi/v/SBLex.svg
    :target: https://pypi.python.org/pypi/SBLex
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/kadmuffin/SBLex.png
   :target: https://travis-ci.org/kadmuffin/SBLex
   :alt: Latest Travis CI build status

.. image:: https://codecov.io/gh/kadmuffin/SBLex/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/kadmuffin/SBLex/branch/master
   :alt: Latest CodeCov status

A simple library for tokenizing text with additional functionalities. (NOT MAINTAINED ANYMORE)

Overview
--------

SBLex is a lexer that is capable to tokenize text with only a few lines of code, it includes as well other extra functions.

Features
^^^^^^^^
* Dependent Tokens
* Custom Errors
* Custom functions when a token is found
* Custom capture groups
* Support of multiple regular expressions

Planned Features
^^^^^^^^^^^^^^^^
* Ignore patterns
* Documentation (Please use a IDE that supports autocomplete for docs)
Installation
------------

PyPi
^^^^

You can easily install SBLex through `pip`  like this:

.. code:: bash

   pip install SBLex

If you get an environment error, you can also try using the `--user` option:

.. code:: bash

   pip install SBLex --user

Usage
-----

Starting using SBLex is as easy as importing the SBLex and declaring the lexer, here you have a working example lexing the world Hello World!:

.. code:: python

   from SBLex import lex

   lexer = lex.lex()
   
   lexer.add("Hello World", r'Hello World\!')

   lexer.evaluate("Hello World!")

   """
   Returns:
       >>> [token(type: 'Hello World', value: 'Hello World!', line: 0)]
   """

Here is another example using a custom capturing_group.

.. code:: python

   from SBLex import lex

   lexer = lex.lex()

   # Try to lex: The weather today is {weather}
   lexer.add(
       "The weather today is",
       r'The weather today is ([a-zA-Z]+)',
       capturing_group=1
   )

   lexer.evaluate("The weather today is rainy")

   """
   Returns:
       >>> [token(type: 'The weather today is', value: 'rainy', line: 0)]
   """

Compatibility
-------------

SBLex is compatible with Python2 & Python3.

Licence
-------
SBLex is under the `MIT License <https://github.com/kadmuffin/SBLex/blob/master/LICENSE>`_.

Authors
-------

`SBLex` was written by `KadMuffin <KadMuffin@outlook.com>`_.
