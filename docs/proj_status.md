# Project Status Report

Last Updated: Fri Dec 20 03:14:59 AEDT 2024

## Directory Structure

```plaintext
.
├── cursor_env
│   ├── bin
│   │   ├── Activate.ps1
│   │   ├── activate
│   │   ├── activate.csh
│   │   ├── activate.fish
│   │   ├── autoflake
│   │   ├── autopep8
│   │   ├── black
│   │   ├── blackd
│   │   ├── debugpy
│   │   ├── f2py
│   │   ├── fonttools
│   │   ├── httpx
│   │   ├── ipython
│   │   ├── ipython3
│   │   ├── isort
│   │   ├── isort-identify-imports
│   │   ├── jlpm
│   │   ├── jsonpointer
│   │   ├── jsonschema
│   │   ├── jupyter
│   │   ├── jupyter-console
│   │   ├── jupyter-dejavu
│   │   ├── jupyter-events
│   │   ├── jupyter-execute
│   │   ├── jupyter-kernel
│   │   ├── jupyter-kernelspec
│   │   ├── jupyter-lab
│   │   ├── jupyter-labextension
│   │   ├── jupyter-labhub
│   │   ├── jupyter-migrate
│   │   ├── jupyter-nbconvert
│   │   ├── jupyter-notebook
│   │   ├── jupyter-run
│   │   ├── jupyter-server
│   │   ├── jupyter-troubleshoot
│   │   ├── jupyter-trust
│   │   ├── markdown-it
│   │   ├── markdown_py
│   │   ├── normalizer
│   │   ├── numpy-config
│   │   ├── pip
│   │   ├── pip3
│   │   ├── pip3.13
│   │   ├── pybabel
│   │   ├── pycodestyle
│   │   ├── pyflakes
│   │   ├── pyftmerge
│   │   ├── pyftsubset
│   │   ├── pygmentize
│   │   ├── pyjson5
│   │   ├── python -> python3.13
│   │   ├── python3 -> python3.13
│   │   ├── python3.13 -> /opt/homebrew/opt/python@3.13/bin/python3.13
│   │   ├── send2trash
│   │   ├── streamlit
│   │   ├── streamlit.cmd
│   │   ├── ttx
│   │   └── wsdump
│   ├── etc
│   │   └── jupyter
│   ├── include
│   │   └── python3.13
│   ├── lib
│   │   └── python3.13
│   ├── share
│   │   ├── applications
│   │   ├── icons
│   │   ├── jupyter
│   │   └── man
│   └── pyvenv.cfg
├── data
├── docs
│   ├── implementation_plan.md
│   └── proj_status.md
├── logs
│   ├── auto_fix.log
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
│   │   └── __init__.py
│   ├── book_editor.egg-info
│   │   ├── PKG-INFO
│   │   ├── SOURCES.txt
│   │   ├── dependency_links.txt
│   │   ├── requires.txt
│   │   └── top_level.txt
│   ├── components
│   │   ├── __init__.py
│   │   └── editor.py
│   ├── data
│   │   ├── __init__.py
│   │   └── storage.py
│   ├── models
│   │   ├── __init__.py
│   │   └── book.py
│   └── utils
│       └── __init__.py
├── templates
│   ├── Untitled.json
│   └── categories.json
├── tests
│   ├── __pycache__
│   │   ├── test_editor.cpython-313-pytest-8.0.0.pyc
│   │   ├── test_editor.cpython-313-pytest-8.3.4.pyc
│   │   └── test_template.cpython-313-pytest-8.3.4.pyc
│   ├── test_editor.py
│   └── test_template.py
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
│   │   ├── dotenv
│   │   ├── f2py
│   │   ├── flake8
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
│   │   ├── undill
│   │   └── watchmedo
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
├── pyproject.toml
├── pyrightconfig.json
├── requirements.txt
├── setup.py
└── streamlit_app.py

47 directories, 142 files
```

## Recent Changes

- [2024-12-20 03:14:44] Generating commit message from project status... chore: Update project files
- fix: Prevent creation of unwanted backup directories
- chore: Update project files and fix linting issues
- chore(init): Update project structure and align with Streamlit guidelines
- chore(init): Update project structure and align with Streamlit guidelines
