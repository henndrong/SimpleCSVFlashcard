## Core Framework
- **Streamlit**: Chosen for its simplicity and speed in creating data-driven web applications, suitable for a quick flashcard app.

## Data Handling
- **Pandas**: Will be used to read and process the `iot_flashcards.csv` file efficiently.

## Language
- **Python**: The standard language for Streamlit and Pandas.

## DOCX Processing
- **python-docx**: Will be used to parse the DOCX file, identify text runs, and check for highlight colors (Yellow for answers, Green for chapters).

## Architecture
- **Data Extraction**: A separate script (`process_docx_highlight.py`) will parse the DOCX file and generate `iot_flashcards_v2.csv`.
- **Main Application**: Single-script application (`app.py`) handling UI, state, and data filtering based on the generated CSV.
- State management relies on Streamlit's session state.
- Data processing involves the `process_docx_highlight.py` script to convert DOCX to CSV.
