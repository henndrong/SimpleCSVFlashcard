## Key Components and Their Interactions
- **PDF Processing Script/Logic** (To be developed): Responsible for extracting questions, options, answers, and chapter information from `IOT MCQ.pdf`.
- **iot_flashcards_v2.csv**: The new data source containing structured flashcard data, including a 'Chapter' column.
- **app.py**: The main Streamlit application script. It will be modified to handle:
    - Loading data from `iot_flashcards_v2.csv`.
    - Displaying a chapter selection interface (e.g., `st.multiselect`).
    - Filtering flashcards based on selected chapters.
    - Managing the application state (selected chapters, current card index within the filtered set, user selections).
    - Displaying the current flashcard (question and options).
    - Processing user input (selected answer).
    - Providing feedback.
    - Navigating between cards (forward, potentially backward).
    - Displaying score based on the attempted cards.

## Data Flow
1.  **(Offline)** PDF processing logic extracts data from `IOT MCQ.pdf` into `iot_flashcards_v2.csv`.
2.  `app.py` reads `iot_flashcards_v2.csv` using Pandas into a DataFrame upon startup.
3.  User selects desired chapters using the Streamlit UI.
4.  `app.py` filters the DataFrame based on selected chapters.
5.  The application state (e.g., current index within the filtered set) determines which row is displayed.
6.  User selects an option via `st.radio`.
7.  `app.py` compares the selected option to the correct answer.
8.  Feedback is displayed.
9.  User clicks "Next" (or potentially "Previous"), updating the application state to show the appropriate card from the filtered set.

## External Dependencies
- **streamlit**: Core application framework.
- **pandas**: For reading and manipulating the CSV data.
- **Potential PDF library** (e.g., `PyPDF2`, `pdfminer.six`): May be needed for PDF text extraction if basic `read_file` is insufficient, especially for identifying chapters or structure. (To be determined after PDF analysis).

## Recent Significant Changes
- Initial project setup and documentation creation.
- Development of the first version of `app.py`.
- User feedback received: Switch data source to PDF, add chapter selection.

## User Feedback Integration and Its Impact on Development
- The core data source is changing from `iot_flashcards.csv` to `IOT MCQ.pdf` (processed into `iot_flashcards_v2.csv`).
- Chapter selection functionality will be added to the UI and filtering logic.
- Backward navigation is being considered as an enhancement.
