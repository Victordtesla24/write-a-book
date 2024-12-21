# Project Status Report
Last Updated: Sat Dec 21 11:47:50 AEDT 2024

## Summary of Resolved Errors

No errors resolved in this run.

## Current Implementation Status

- Python files updated:       38
- Test files updated: 13

## Test Coverage Report

Name                                     Stmts   Miss  Cover
------------------------------------------------------------
src/__init__.py                              2      0   100%
src/book_editor/__init__.py                  2      0   100%
src/book_editor/app/__init__.py              1      0   100%
src/book_editor/app/config/__init__.py       0      0   100%
src/book_editor/app/config/settings.py      11      0   100%
src/book_editor/app/core/__init__.py         0      0   100%
src/book_editor/app/core/editor.py         231     75    68%
src/book_editor/config/__init__.py           0      0   100%
src/book_editor/config/settings.py          22      0   100%
src/book_editor/core/__init__.py             3      0   100%
src/book_editor/core/editor.py             156      5    97%
src/book_editor/core/template.py           107      3    97%
src/book_editor/main.py                    146     63    57%
src/book_editor/types.py                    33      0   100%
src/components/__init__.py                   0      0   100%
src/components/editor.py                    72      0   100%
src/components/text_editor.py               47      1    98%
src/data/__init__.py                         0      0   100%
src/data/storage.py                         48      0   100%
src/models/__init__.py                       0      0   100%
src/models/book.py                          59      3    95%
tests/__init__.py                            0      0   100%
tests/test_app_config.py                    46      0   100%
tests/test_app_core.py                     108      0   100%
tests/test_app_core_editor.py               73      2    97%
tests/test_book.py                          70      0   100%
tests/test_components.py                    36      0   100%
tests/test_core_editor.py                  162      3    98%
tests/test_core_editor_extended.py          88      0   100%
tests/test_editor.py                       119      0   100%
tests/test_main.py                          99     13    87%
tests/test_settings.py                      46      0   100%
tests/test_storage.py                       60      0   100%
tests/test_template.py                      76      0   100%
tests/test_text_editor_extended.py          84      0   100%
------------------------------------------------------------
TOTAL                                     2007    168    92%

## Lint Report

************* Module tests.test_core_editor_extended
tests/test_core_editor_extended.py:3:0: W0105: String statement has no effect (pointless-string-statement)
tests/test_core_editor_extended.py:5:0: C0413: Import "import tempfile" should be placed at the top of the module (wrong-import-position)
tests/test_core_editor_extended.py:6:0: C0413: Import "from pathlib import Path" should be placed at the top of the module (wrong-import-position)
tests/test_core_editor_extended.py:8:0: C0413: Import "import pytest" should be placed at the top of the module (wrong-import-position)
tests/test_core_editor_extended.py:10:0: C0413: Import "from src.book_editor.core.editor import Editor" should be placed at the top of the module (wrong-import-position)
tests/test_core_editor_extended.py:20:31: W0621: Redefining name 'editor' from outer scope (line 14) (redefined-outer-name)
tests/test_core_editor_extended.py:27:34: W0621: Redefining name 'editor' from outer scope (line 14) (redefined-outer-name)
tests/test_core_editor_extended.py:42:32: W0621: Redefining name 'editor' from outer scope (line 14) (redefined-outer-name)
tests/test_core_editor_extended.py:54:33: W0621: Redefining name 'editor' from outer scope (line 14) (redefined-outer-name)
tests/test_core_editor_extended.py:68:33: W0621: Redefining name 'editor' from outer scope (line 14) (redefined-outer-name)
tests/test_core_editor_extended.py:86:30: W0621: Redefining name 'editor' from outer scope (line 14) (redefined-outer-name)
tests/test_core_editor_extended.py:98:31: W0621: Redefining name 'editor' from outer scope (line 14) (redefined-outer-name)
tests/test_core_editor_extended.py:117:34: W0621: Redefining name 'editor' from outer scope (line 14) (redefined-outer-name)
tests/test_core_editor_extended.py:150:8: W0621: Redefining name 'editor' from outer scope (line 14) (redefined-outer-name)
tests/test_core_editor_extended.py:1:0: W0611: Unused Dict imported from typing (unused-import)
tests/test_core_editor_extended.py:1:0: W0611: Unused List imported from typing (unused-import)
tests/test_core_editor_extended.py:1:0: W0611: Unused Optional imported from typing (unused-import)
************* Module tests.test_app_core
tests/test_app_core.py:3:0: W0105: String statement has no effect (pointless-string-statement)
tests/test_app_core.py:5:0: C0413: Import "import tempfile" should be placed at the top of the module (wrong-import-position)
tests/test_app_core.py:6:0: C0413: Import "from unittest.mock import patch" should be placed at the top of the module (wrong-import-position)
tests/test_app_core.py:8:0: C0413: Import "import pytest" should be placed at the top of the module (wrong-import-position)
tests/test_app_core.py:10:0: C0413: Import "from book_editor.core.template import Template" should be placed at the top of the module (wrong-import-position)
tests/test_app_core.py:11:0: C0413: Import "from src.book_editor.app.core.editor import AppEditor, DocumentManager, PreviewManager, TemplateRenderer" should be placed at the top of the module (wrong-import-position)
tests/test_app_core.py:27:15: W0621: Redefining name 'temp_dir' from outer scope (line 20) (redefined-outer-name)
tests/test_app_core.py:37:21: W0621: Redefining name 'temp_dir' from outer scope (line 20) (redefined-outer-name)
tests/test_app_core.py:44:22: W0621: Redefining name 'temp_dir' from outer scope (line 20) (redefined-outer-name)
tests/test_app_core.py:55:35: W0621: Redefining name 'app_editor' from outer scope (line 27) (redefined-outer-name)
tests/test_app_core.py:63:37: W0621: Redefining name 'document_manager' from outer scope (line 37) (redefined-outer-name)
tests/test_app_core.py:84:38: W0621: Redefining name 'template_renderer' from outer scope (line 44) (redefined-outer-name)
tests/test_app_core.py:98:36: W0621: Redefining name 'preview_manager' from outer scope (line 50) (redefined-outer-name)
tests/test_app_core.py:98:53: W0621: Redefining name 'temp_dir' from outer scope (line 20) (redefined-outer-name)
tests/test_app_core.py:117:53: W0621: Redefining name 'app_editor' from outer scope (line 27) (redefined-outer-name)
tests/test_app_core.py:137:38: W0621: Redefining name 'app_editor' from outer scope (line 27) (redefined-outer-name)
tests/test_app_core.py:154:35: W0621: Redefining name 'app_editor' from outer scope (line 27) (redefined-outer-name)
tests/test_app_core.py:171:37: W0621: Redefining name 'document_manager' from outer scope (line 37) (redefined-outer-name)
tests/test_app_core.py:187:38: W0621: Redefining name 'template_renderer' from outer scope (line 44) (redefined-outer-name)
tests/test_app_core.py:197:36: W0621: Redefining name 'preview_manager' from outer scope (line 50) (redefined-outer-name)
tests/test_app_core.py:5:0: C0411: standard import "tempfile" should be placed before third party import "streamlit" (wrong-import-order)
tests/test_app_core.py:6:0: C0411: standard import "unittest.mock.patch" should be placed before third party import "streamlit" (wrong-import-order)
tests/test_app_core.py:1:0: W0611: Unused streamlit imported as st (unused-import)
************* Module tests.test_main
tests/test_main.py:3:0: W0105: String statement has no effect (pointless-string-statement)
tests/test_main.py:5:0: C0413: Import "import tempfile" should be placed at the top of the module (wrong-import-position)
tests/test_main.py:6:0: C0413: Import "from pathlib import Path" should be placed at the top of the module (wrong-import-position)
tests/test_main.py:7:0: C0413: Import "from unittest.mock import MagicMock, patch" should be placed at the top of the module (wrong-import-position)
tests/test_main.py:9:0: C0413: Import "import pytest" should be placed at the top of the module (wrong-import-position)
tests/test_main.py:11:0: C0413: Import "from src.book_editor.main import BookEditor, main, render_template_manager" should be placed at the top of the module (wrong-import-position)
tests/test_main.py:24:20: W0621: Redefining name 'temp_dir' from outer scope (line 15) (redefined-outer-name)
tests/test_main.py:43:36: W0621: Redefining name 'editor_instance' from outer scope (line 24) (redefined-outer-name)
tests/test_main.py:89:19: W0621: Redefining name 'editor_instance' from outer scope (line 24) (redefined-outer-name)
tests/test_main.py:101:29: W0621: Redefining name 'editor_instance' from outer scope (line 24) (redefined-outer-name)
tests/test_main.py:122:25: W0621: Redefining name 'editor_instance' from outer scope (line 24) (redefined-outer-name)
tests/test_main.py:137:26: W0621: Redefining name 'editor_instance' from outer scope (line 24) (redefined-outer-name)
tests/test_main.py:153:33: W0621: Redefining name 'editor_instance' from outer scope (line 24) (redefined-outer-name)
tests/test_main.py:165:27: W0621: Redefining name 'editor_instance' from outer scope (line 24) (redefined-outer-name)
tests/test_main.py:180:26: W0621: Redefining name 'editor_instance' from outer scope (line 24) (redefined-outer-name)
tests/test_main.py:5:0: C0411: standard import "tempfile" should be placed before third party import "streamlit" (wrong-import-order)
tests/test_main.py:6:0: C0411: standard import "pathlib.Path" should be placed before third party import "streamlit" (wrong-import-order)
tests/test_main.py:7:0: C0411: standard import "unittest.mock.MagicMock" should be placed before third party import "streamlit" (wrong-import-order)
tests/test_main.py:1:0: W0611: Unused streamlit imported as st (unused-import)

------------------------------------------------------------------
Your code has been rated at 9.70/10 (previous run: 9.70/10, +0.00)


Pylint Score: 9.70
9.70
0.00/10.00

## Recent Changes
- Auto-commit: 2024-12-21 11:45:33 - Remaining Errors: 28 - Test Results: 0 0 passed, 0 0 failed - Lint Score: 0.00/10.00
- Auto-commit: 2024-12-21 11:37:57 - Test Results: 104 passed, 0 0 failed - Lint Score: 0.00 0.00 0.00/10.00
- Auto-commit: 2024-12-21 11:31:57 - Test Results: 104 passed, 0 0 failed - Lint Score: 0.00 0.00 0.00/10.00
- Auto-commit: 2024-12-21 11:30:04 - Test Results: 104 passed, 0 0 failed - Lint Score: 0.00 0.00 0.00/10.00
- Auto-commit: 2024-12-21 11:28:16 - Test Results: 104 passed, 0 0 failed - Lint Score: 0.00 0.00 0.00/10.00
