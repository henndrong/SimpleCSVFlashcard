## Project Goals
- Create an enhanced Streamlit flashcard application for studying IoT concepts.
- Extract questions, options, answers, and chapter information from `IOT MCQ.pdf`.
- Store the extracted data in a structured CSV file.
- Allow the user to select specific chapters to study.
- Allow the user to navigate through flashcards (forward and potentially backward).
- Display one question at a time with multiple-choice options.
- Provide feedback on whether the selected answer is correct.

## Key Features
- [ ] Extract flashcard data (including chapters) from PDF.
- [ ] Store data in a new CSV file (`iot_flashcards_v2.csv`).
- [x] Load flashcard data from CSV. (Modified for new format)
- [x] Implement chapter selection UI.
- [x] Filter flashcards based on selected chapters.
- [x] Display flashcards sequentially. (Modified for filtering)
- [x] Handle multiple-choice options. (Modified for multi-select)
- [x] Check user answers and provide feedback. (Modified for multi-select)
- [x] Basic navigation (Next card).
- [ ] (Optional) Implement backward navigation (Previous card). (Skipped for now)

## Completion Criteria
- [x] The Streamlit application runs successfully.
- [x] Flashcard data is correctly extracted from the PDF and stored in the new CSV. (Via DOCX processing, with manual chapter correction by user)
- [x] User can select chapters, and only questions from those chapters are shown.
- [x] Flashcards are loaded and displayed correctly from the new CSV.
- [x] User can select an option and receive correct/incorrect feedback.
- [x] User can move to the next flashcard within the selected chapters.
- (Optional) User can move to the previous flashcard. (Skipped for now)

## Progress Tracker
- [x] Initialize project documentation.
- [x] Create Streamlit application structure (initial version).
- [x] Implement flashcard loading logic (initial version).
- [x] Implement flashcard display and interaction logic (initial version).
- [x] Test the application (initial version).
- [x] Update documentation for new requirements.
- [x] Process `IOT MCQ.pdf` to extract data. (Processed DOCX version)
- [x] Create new CSV file (`iot_flashcards_v2.csv`).
- [x] Modify `app.py` for chapter selection and filtering.
- [x] Modify `app.py` for new data format and multi-select.
- [ ] (Optional) Modify `app.py` for backward navigation. (Skipped for now)
- [x] Test the enhanced application.

## Completed Tasks
- Initialized project documentation (`projectRoadmap.md`, `currentTask.md`, `techStack.md`, `codebaseSummary.md`).
- Created `requirements.txt` with dependencies (streamlit, pandas, python-docx).
- Created initial `app.py` with core flashcard logic.
- Installed dependencies (`streamlit`, `pandas`, `python-docx`).
- Ran and tested the initial version of the Streamlit application.
- Received user feedback for improvements (PDF processing, chapter selection, multi-select).
- Created `process_docx_highlight.py` to parse DOCX based on highlights.
- Generated `iot_flashcards_v2.csv` from `IOT MCQ.docx`.
- Updated `app.py` to use new CSV, implement chapter selection, and handle multi-select questions.
- User manually corrected chapter data in `iot_flashcards_v2.csv`.
- User confirmed the enhanced application is working.
