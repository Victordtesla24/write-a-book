# Project Status Report

Last Updated: Fri Dec 20 15:25:16 AEDT 2024

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
│   ├── markdown_errors.log
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

37 directories, 116 files
```

## Recent Changes

- [2024-12-20 14:55:45] Update documentation: docs/proj_status.md logs/auto_fix.log.md src/book_editor/README.md
- Initial commit
## Lint Report

```shell
************* Module tests.test_core_editor_extended
tests/test_core_editor_extended.py:23:11: W0212: Access to a protected member _autosave_enabled of a client class (protected-access)
************* Module tests.test_core_editor
tests/test_core_editor.py:113:11: W0212: Access to a protected member _autosave_enabled of a client class (protected-access)
tests/test_core_editor.py:288:4: W0212: Access to a protected member _metadata of a client class (protected-access)
tests/test_core_editor.py:291:4: W0212: Access to a protected member _metadata of a client class (protected-access)

------------------------------------------------------------------
Your code has been rated at 9.98/10 (previous run: 9.98/10, +0.00)

```
