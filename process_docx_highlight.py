# process_docx_highlight.py
import docx
import pandas as pd
import re
import os
from docx.enum.text import WD_COLOR_INDEX # Import the enum

# --- Configuration ---
INPUT_DOCX = 'IOT MCQ.docx'
OUTPUT_CSV = 'iot_flashcards_v2.csv'
CHAPTER_HIGHLIGHT_COLOR = WD_COLOR_INDEX.GREEN # Enum value for Green
ANSWER_HIGHLIGHT_COLOR = WD_COLOR_INDEX.YELLOW # Enum value for Yellow

# --- Helper Functions ---
def get_paragraph_text(paragraph):
    """Extracts full text from a paragraph, preserving runs."""
    return "".join(run.text for run in paragraph.runs)

def get_highlighted_text(paragraph, highlight_color):
    """Extracts text with a specific highlight color from a paragraph."""
    highlighted_runs = [run.text for run in paragraph.runs if run.font.highlight_color == highlight_color]
    return "".join(highlighted_runs).strip()

def is_paragraph_highlighted(paragraph, highlight_color):
    """Checks if any run in the paragraph has the specified highlight color."""
    return any(run.font.highlight_color == highlight_color for run in paragraph.runs)

# --- Main Parsing Logic ---
def parse_docx(file_path):
    """Parses the DOCX file to extract flashcard data based on highlighting."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    try:
        document = docx.Document(file_path)
    except Exception as e:
        print(f"Error opening DOCX file: {e}")
        return None

    flashcards = []
    current_chapter = "Unknown"
    current_question_text = ""
    current_options = []
    current_correct_answers = [] # Changed to a list for multi-select
    question_number = 0
    parsing_options = False # Flag to indicate we are looking for options

    question_pattern = re.compile(r"^\s*(\d+)\.\s*(.*)") # Matches "1. Question text"

    print("Starting DOCX parsing...")

    for i, para in enumerate(document.paragraphs):
        para_text = get_paragraph_text(para).strip()
        if not para_text: # Skip empty paragraphs
            continue

        # --- Detect Chapter ---
        is_green_highlighted = is_paragraph_highlighted(para, CHAPTER_HIGHLIGHT_COLOR)
        chapter_match = re.match(r"Chapter\s+(\d+)\s*-\s*(.*)", para_text, re.IGNORECASE)

        if is_green_highlighted and chapter_match:
             # Finalize previous question before starting new chapter
            if current_question_text and current_options and current_correct_answers: # Check list instead of single answer
                flashcards.append({
                    'Chapter': current_chapter,
                    'Question_No': question_number,
                    'Question': current_question_text.strip(),
                    'Options': "|".join(current_options),
                    'Correct Answer': ";;".join(current_correct_answers) # Join list with ;;
                })
            # Reset for next question/chapter
            current_question_text = ""
            current_options = []
            current_correct_answers = [] # Reset list
            parsing_options = False

            current_chapter = para_text # Use the full text identified as chapter
            print(f"--- Found Chapter: {current_chapter} ---")
            continue # Move to next paragraph after finding chapter

        # --- Detect Question ---
        question_match = question_pattern.match(para_text)
        if question_match:
             # Finalize previous question before starting new one
            if current_question_text and current_options and current_correct_answers: # Check list
                 flashcards.append({
                    'Chapter': current_chapter,
                    'Question_No': question_number,
                    'Question': current_question_text.strip(),
                    'Options': "|".join(current_options),
                    'Correct Answer': ";;".join(current_correct_answers) # Join list with ;;
                })

            # Start new question
            question_number = int(question_match.group(1))
            # Combine text from all runs in the paragraph for the question
            current_question_text = "".join(run.text for run in para.runs).strip()
            # Remove the leading number and period
            current_question_text = re.sub(r"^\s*\d+\.\s*", "", current_question_text).strip()

            current_options = []
            current_correct_answers = [] # Reset list
            parsing_options = True # Assume options follow immediately
            # print(f"Q{question_number}: {current_question_text}")
            continue # Check next paragraph for options

        # --- Detect Options ---
        # This assumes options are typically in paragraphs immediately following the question
        # and continues until a new chapter or question is detected.
        if parsing_options:
            is_yellow_highlighted = is_paragraph_highlighted(para, ANSWER_HIGHLIGHT_COLOR)
            # Combine text from all runs in the paragraph for the option
            option_text = "".join(run.text for run in para.runs).strip()

            # Basic check to stop collecting options if it looks like a new chapter/question start
            is_new_chapter = chapter_match and is_paragraph_highlighted(para, CHAPTER_HIGHLIGHT_COLOR)
            is_new_question = question_pattern.match(option_text)

            if is_new_chapter or is_new_question:
                 # Finalize the current question before moving on
                if current_question_text and current_options and current_correct_answers: # Check list
                    flashcards.append({
                        'Chapter': current_chapter,
                        'Question_No': question_number,
                        'Question': current_question_text.strip(),
                        'Options': "|".join(current_options),
                        'Correct Answer': ";;".join(current_correct_answers) # Join list with ;;
                    })
                # Reset state as we've hit something that isn't an option
                current_question_text = ""
                current_options = []
                current_correct_answers = [] # Reset list
                parsing_options = False
                # Re-process the current paragraph if it was a chapter/question start
                if is_new_chapter:
                     current_chapter = para_text
                     print(f"--- Found Chapter: {current_chapter} ---")
                elif is_new_question:
                    q_match_rerun = question_pattern.match(option_text) # Need to re-match
                    question_number = int(q_match_rerun.group(1))
                    current_question_text = "".join(run.text for run in para.runs).strip()
                    current_question_text = re.sub(r"^\s*\d+\.\s*", "", current_question_text).strip()
                    current_options = []
                    current_correct_answers = [] # Reset list
                    parsing_options = True # Start parsing options for this new question
                continue # Move processing to the next paragraph


            # Clean option text (e.g., remove potential leading bullets)
            option_text_cleaned = re.sub(r"^\s*●\s*", "", option_text).strip()

            if option_text_cleaned: # Add if it's not empty
                current_options.append(option_text_cleaned)
                # print(f"  Opt: {option_text_cleaned}")
                if is_yellow_highlighted:
                    # Append all yellow highlighted options to the list
                    current_correct_answers.append(option_text_cleaned)
                    # print(f"    -> Correct Answer Found: {option_text_cleaned}")


    # Add the last processed question after the loop finishes
    if current_question_text and current_options and current_correct_answers: # Check list
        flashcards.append({
            'Chapter': current_chapter,
            'Question_No': question_number,
            'Question': current_question_text.strip(),
            'Options': "|".join(current_options),
            'Correct Answer': ";;".join(current_correct_answers) # Join list with ;;
        })

    print(f"Parsing complete. Found {len(flashcards)} potential flashcards.")

    if not flashcards:
        print("Warning: No flashcards were extracted. Check DOCX formatting and script logic.")
        return None

    # Ensure required columns exist, even if empty
    final_df = pd.DataFrame(flashcards)
    for col in ['Chapter', 'Question_No', 'Question', 'Options', 'Correct Answer']:
        if col not in final_df.columns:
            final_df[col] = None # Add missing column

    return final_df[['Chapter', 'Question_No', 'Question', 'Options', 'Correct Answer']] # Ensure column order


# --- Execution ---
if __name__ == "__main__":
    df_flashcards = parse_docx(INPUT_DOCX)

    if df_flashcards is not None and not df_flashcards.empty:
        try:
            df_flashcards.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
            print(f"Successfully saved flashcards to {OUTPUT_CSV}")
        except Exception as e:
            print(f"Error saving DataFrame to CSV: {e}")
    else:
        print("Failed to extract flashcards or DataFrame is empty.")
