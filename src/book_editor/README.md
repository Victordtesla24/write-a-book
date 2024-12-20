# Book Editor

A streamlit-based web application for writing and editing books with template support.

## Features

- Modern, intuitive web interface

- Template management system

- Real-time text analysis

- Auto-save functionality

- Export capabilities

- Document versioning

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/book-editor.git
cd book-editor
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:

```bash
pip install -e ".[dev]"
```

## Usage

1. Start the application:

```bash
streamlit run app/main.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically <http://localhost:8501>)

3. Use the sidebar to:

   - Upload templates

   - Create new documents

   - Access saved documents

4. Use the main editor to:

   - Write and edit text

   - View word count and statistics

   - Save and export your work

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
black .
isort .
flake8 .
pylint app tests
```

### Documentation

Project documentation is available in the `docs/` directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
