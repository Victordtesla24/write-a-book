# Project Status Report

Last Updated: Fri Dec 20 14:16:35 AEDT 2024

## Directory Structure

```shell
.
├── data
├── docs
│   ├── implementation_plan.md
│   └── proj_status.md
├── logs
│   ├── auto_fix.log
│   ├── auto_fix.log.md
│   ├── auto_fix.log.md.tmp
│   ├── auto_fix.log.pylint
│   ├── lint_report.log
│   ├── verify_and_fix.log
│   ├── verify_and_fix.log.1
│   └── verify_and_fix.log.2
├── pages
├── scripts
│   ├── auto_fix_code.sh
│   ├── fix_zshrc.sh
│   ├── run_tests.sh
│   ├── setup.sh
│   ├── setup_env.sh
│   └── verify_and_fix.sh
├── src
│   ├── __pycache__
│   │   └── __init__.cpython-313.pyc
│   ├── book_editor
│   │   ├── __pycache__
│   │   ├── app
│   │   ├── config
│   │   ├── core
│   │   ├── docs
│   │   ├── scripts
│   │   ├── static
│   │   ├── templates
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── types.py
│   ├── book_editor.egg-info
│   │   ├── PKG-INFO
│   │   ├── SOURCES.txt
│   │   ├── dependency_links.txt
│   │   ├── requires.txt
│   │   └── top_level.txt
│   ├── components
│   │   ├── __pycache__
│   │   ├── __init__.py
│   │   ├── editor.py
│   │   └── text_editor.py
│   ├── data
│   │   ├── __pycache__
│   │   ├── __init__.py
│   │   └── storage.py
│   ├── models
│   │   ├── __pycache__
│   │   ├── __init__.py
│   │   └── book.py
│   ├── utils
│   │   └── __init__.py
│   └── __init__.py
├── storage
│   └── Test.json
├── templates
│   ├── Untitled.json
│   ├── categories.json
│   ├── default.json
│   └── test.json
├── tests
│   ├── __pycache__
│   │   ├── test_app_config.cpython-313-pytest-8.3.4.pyc
│   │   ├── test_app_core.cpython-313-pytest-8.3.4.pyc
│   │   ├── test_app_core_editor.cpython-313-pytest-8.3.4.pyc
│   │   ├── test_book.cpython-313-pytest-8.3.4.pyc
│   │   ├── test_components.cpython-313-pytest-8.3.4.pyc
│   │   ├── test_core_editor.cpython-313-pytest-8.3.4.pyc
│   │   ├── test_core_editor_extended.cpython-313-pytest-8.3.4.pyc
│   │   ├── test_editor.cpython-313-pytest-8.3.4.pyc
│   │   ├── test_main.cpython-313-pytest-8.3.4.pyc
│   │   ├── test_settings.cpython-313-pytest-8.3.4.pyc
│   │   ├── test_storage.cpython-313-pytest-8.3.4.pyc
│   │   ├── test_template.cpython-313-pytest-8.3.4.pyc
│   │   └── test_text_editor_extended.cpython-313-pytest-8.3.4.pyc
│   ├── test_app_config.py
│   ├── test_app_core.py
│   ├── test_app_core_editor.py
│   ├── test_book.py
│   ├── test_components.py
│   ├── test_core_editor.py
│   ├── test_core_editor_extended.py
│   ├── test_editor.py
│   ├── test_main.py
│   ├── test_settings.py
│   ├── test_storage.py
│   ├── test_template.py
│   └── test_text_editor_extended.py
├── venv
│   ├── bin
│   │   ├── Activate.ps1
│   │   ├── activate
│   │   ├── activate.csh
│   │   ├── activate.fish
│   │   ├── autoflake
│   │   ├── autopep8
│   │   ├── black
│   │   ├── blackd
│   │   ├── coverage
│   │   ├── coverage-3.13
│   │   ├── coverage3
│   │   ├── f2py
│   │   ├── get_gprof
│   │   ├── get_objgraph
│   │   ├── isort
│   │   ├── isort-identify-imports
│   │   ├── jsonschema
│   │   ├── markdown-it
│   │   ├── markdown_py
│   │   ├── normalizer
│   │   ├── numpy-config
│   │   ├── pip
│   │   ├── pip3
│   │   ├── pip3.13
│   │   ├── py.test
│   │   ├── pycodestyle
│   │   ├── pyflakes
│   │   ├── pygmentize
│   │   ├── pylint
│   │   ├── pylint-config
│   │   ├── pyreverse
│   │   ├── pytest
│   │   ├── python -> python3.13
│   │   ├── python3 -> python3.13
│   │   ├── python3.13 -> /opt/homebrew/opt/python@3.13/bin/python3.13
│   │   ├── streamlit
│   │   ├── streamlit.cmd
│   │   ├── symilar
│   │   └── undill
│   ├── etc
│   │   └── jupyter
│   ├── include
│   │   └── python3.13
│   ├── lib
│   │   └── python3.13
│   ├── share
│   │   └── jupyter
│   └── pyvenv.cfg
├── README.md
├── agent_directives.md
├── mypy.ini
├── pyproject.toml
├── pyrightconfig.json
├── requirements.txt
├── setup.py
├── streamlit_app.py
└── verify_and_fix.log

39 directories, 115 files
```

## Recent Changes

- [2024-12-20 12:11:44] Update project files
- [2024-12-20 11:40:23] Update project files
- [2024-12-20 11:39:32] Update project files
- [2024-12-20 04:39:16] Update project files
- [2024-12-20 04:37:04] Update project files

## Lint Report

```shell
************* Module src.book_editor.app.core.editor
src/book_editor/app/core/editor.py:47:4: W0237: Parameter 'o' has been renamed to 'obj' in overriding 'DateTimeEncoder.default' method (arguments-renamed)
src/book_editor/app/core/editor.py:81:15: W0718: Catching too general exception Exception (broad-exception-caught)
src/book_editor/app/core/editor.py:82:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
src/book_editor/app/core/editor.py:130:15: W0718: Catching too general exception Exception (broad-exception-caught)
src/book_editor/app/core/editor.py:131:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
src/book_editor/app/core/editor.py:146:17: W1514: Using open without explicitly specifying an encoding (unspecified-encoding)
src/book_editor/app/core/editor.py:153:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
src/book_editor/app/core/editor.py:179:15: W0718: Catching too general exception Exception (broad-exception-caught)
src/book_editor/app/core/editor.py:165:17: W1514: Using open without explicitly specifying an encoding (unspecified-encoding)
src/book_editor/app/core/editor.py:180:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
src/book_editor/app/core/editor.py:190:15: W0718: Catching too general exception Exception (broad-exception-caught)
src/book_editor/app/core/editor.py:191:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
src/book_editor/app/core/editor.py:229:15: W0718: Catching too general exception Exception (broad-exception-caught)
src/book_editor/app/core/editor.py:230:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
src/book_editor/app/core/editor.py:249:15: W0718: Catching too general exception Exception (broad-exception-caught)
src/book_editor/app/core/editor.py:250:12: W1203: Use lazy % formatting in logging functions (logging-fstring-interpolation)
************* Module tests.test_app_config
tests/test_app_config.py:4:0: W0611: Unused import pytest (unused-import)
************* Module tests.test_core_editor_extended
tests/test_core_editor_extended.py:23:11: W0212: Access to a protected member _autosave_enabled of a client class (protected-access)
************* Module tests.test_app_core
tests/test_app_core.py:137:38: W0613: Unused argument 'mock_sidebar' (unused-argument)
************* Module tests.test_text_editor_extended
tests/test_text_editor_extended.py:21:15: W0212: Access to a protected member _undo_stack of a client class (protected-access)
tests/test_text_editor_extended.py:22:15: W0212: Access to a protected member _redo_stack of a client class (protected-access)
tests/test_text_editor_extended.py:36:12: W0212: Access to a protected member _undo_stack of a client class (protected-access)
tests/test_text_editor_extended.py:138:15: W0212: Access to a protected member _undo_stack of a client class (protected-access)
tests/test_text_editor_extended.py:142:15: W0212: Access to a protected member _undo_stack of a client class (protected-access)
tests/test_text_editor_extended.py:143:15: W0212: Access to a protected member _redo_stack of a client class (protected-access)
tests/test_text_editor_extended.py:148:15: W0212: Access to a protected member _undo_stack of a client class (protected-access)
tests/test_text_editor_extended.py:153:15: W0212: Access to a protected member _redo_stack of a client class (protected-access)
************* Module tests.test_book
tests/test_book.py:13:11: C1803: "book.metadata == {}" can be simplified to "not book.metadata", if it is strictly a sequence, as an empty dict is falsey (use-implicit-booleaness-not-comparison)
************* Module tests.test_main
tests/test_main.py:69:4: C0415: Import outside toplevel (src.book_editor.main.main) (import-outside-toplevel)
************* Module tests.test_core_editor
tests/test_core_editor.py:113:11: W0212: Access to a protected member _autosave_enabled of a client class (protected-access)
tests/test_core_editor.py:186:8: R1732: Consider using 'with' for resource-allocating operations (consider-using-with)
tests/test_core_editor.py:186:8: W1514: Using open without explicitly specifying an encoding (unspecified-encoding)
tests/test_core_editor.py:193:4: W0212: Access to a protected member _metadata of a client class (protected-access)
tests/test_core_editor.py:198:18: W0212: Access to a protected member _html_content of a client class (protected-access)
tests/test_core_editor.py:203:11: W0212: Access to a protected member _html_content of a client class (protected-access)
tests/test_core_editor.py:289:4: W0212: Access to a protected member _metadata of a client class (protected-access)
tests/test_core_editor.py:290:4: W0212: Access to a protected member _metadata of a client class (protected-access)
************* Module tests.test_settings
tests/test_settings.py:4:0: W0611: Unused import pytest (unused-import)

------------------------------------------------------------------
Your code has been rated at 9.81/10 (previous run: 9.81/10, +0.00)

```
