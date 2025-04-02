import streamlit as st
import pandas as pd
import random
import ast # For safely evaluating string representations if needed

# --- Configuration ---
DATA_FILE = 'iot_flashcards_v2.csv' # Updated data file
QUESTION_COL = 'Question'
OPTIONS_COL = 'Options'
ANSWER_COL = 'Correct Answer'
CHAPTER_COL = 'Chapter' # New column
MULTI_ANSWER_SEP = ';;' # Separator for multiple correct answers

# --- Load Data ---
@st.cache_data # Cache the data loading to improve performance
def load_flashcards(file_path):
    """Loads flashcard data from the enhanced CSV file."""
    try:
        df = pd.read_csv(file_path)
        # Check for required columns
        required_cols = [CHAPTER_COL, QUESTION_COL, OPTIONS_COL, ANSWER_COL]
        if not all(col in df.columns for col in required_cols):
            st.error(f"CSV file must contain columns: {', '.join(required_cols)}")
            return None

        # Fill potential NaN values in critical columns to avoid errors
        df[QUESTION_COL] = df[QUESTION_COL].fillna('')
        df[OPTIONS_COL] = df[OPTIONS_COL].fillna('')
        df[ANSWER_COL] = df[ANSWER_COL].fillna('')
        df[CHAPTER_COL] = df[CHAPTER_COL].fillna('Unknown')

        # Parse options string into a list, handling potential errors
        def parse_options(options_str):
            if pd.isna(options_str) or not isinstance(options_str, str):
                return []
            return [opt.strip() for opt in options_str.split('|')]
        df[OPTIONS_COL] = df[OPTIONS_COL].apply(parse_options)

        # Ensure Correct Answer is string
        df[ANSWER_COL] = df[ANSWER_COL].astype(str)

        # Basic validation: Check if correct answers exist within options
        valid_rows = []
        for index, row in df.iterrows():
            options_set = set(row[OPTIONS_COL])
            correct_answers_raw = row[ANSWER_COL]
            is_multi = MULTI_ANSWER_SEP in correct_answers_raw
            correct_answers_list = [ans.strip() for ans in correct_answers_raw.split(MULTI_ANSWER_SEP)] if is_multi else [correct_answers_raw.strip()]

            # Check if all correct answers are present in the options list
            if all(ans in options_set for ans in correct_answers_list if ans): # Check non-empty answers
                 valid_rows.append(index)
            # else:
            #     print(f"Warning: Row {index} skipped. Correct answer(s) '{correct_answers_list}' not fully in options '{options_set}'.")


        if len(valid_rows) < len(df):
             print(f"Warning: Filtered out {len(df) - len(valid_rows)} rows due to mismatch between answers and options.")

        df_filtered = df.loc[valid_rows].reset_index(drop=True)

        if df_filtered.empty:
             st.warning("No valid flashcards found after validation. Check CSV content.")
             return None

        return df_filtered

    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return None

# --- Helper Functions ---
def reset_quiz_state(flashcards_df, selected_chapters):
    """Resets the quiz state based on selected chapters."""
    if flashcards_df is None or selected_chapters is None:
        st.session_state.filtered_flashcards = pd.DataFrame()
        st.session_state.shuffled_indices = []
    else:
        # Filter based on selected chapters
        st.session_state.filtered_flashcards = flashcards_df[flashcards_df[CHAPTER_COL].isin(selected_chapters)].reset_index(drop=True)

        if not st.session_state.filtered_flashcards.empty:
            # Create a shuffled list of indices for the filtered data
            indices = list(range(len(st.session_state.filtered_flashcards)))
            random.shuffle(indices)
            st.session_state.shuffled_indices = indices
        else:
            st.session_state.shuffled_indices = []

    # Reset progress
    st.session_state.current_index = 0
    st.session_state.user_answer = None
    st.session_state.show_feedback = False
    st.session_state.correct_count = 0
    st.session_state.total_answered = 0
    # Clear previous selections (important for multiselect)
    st.session_state.current_selection = None


# --- Initialize State ---
def initialize_state(flashcards_df):
    """Initializes Streamlit session state variables."""
    if 'all_flashcards' not in st.session_state:
         st.session_state.all_flashcards = flashcards_df # Store the original full dataframe

    if 'available_chapters' not in st.session_state:
        if flashcards_df is not None:
            st.session_state.available_chapters = sorted(flashcards_df[CHAPTER_COL].unique().tolist())
        else:
            st.session_state.available_chapters = []

    # Initialize filter-dependent states if they don't exist
    if 'filtered_flashcards' not in st.session_state:
        st.session_state.filtered_flashcards = pd.DataFrame()
    if 'shuffled_indices' not in st.session_state:
        st.session_state.shuffled_indices = []
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'user_answer' not in st.session_state: # Stores the submitted answer(s)
        st.session_state.user_answer = None
    if 'show_feedback' not in st.session_state:
        st.session_state.show_feedback = False
    if 'correct_count' not in st.session_state:
        st.session_state.correct_count = 0
    if 'total_answered' not in st.session_state:
        st.session_state.total_answered = 0
    if 'selected_chapters' not in st.session_state:
         st.session_state.selected_chapters = st.session_state.available_chapters # Default to all chapters
    if 'current_selection' not in st.session_state: # Stores the current radio/multiselect choice before submission
        st.session_state.current_selection = None


# --- Main App Logic ---
st.set_page_config(layout="wide")
st.title("🧠 IoT Flashcard Quiz")

# Load data once
all_flashcards_df = load_flashcards(DATA_FILE)

initialize_state(all_flashcards_df)

# --- Sidebar for Chapter Selection ---
st.sidebar.header("Chapters")
selected_chapters = st.sidebar.multiselect(
    "Select chapters to study:",
    options=st.session_state.available_chapters,
    default=st.session_state.selected_chapters,
    key="chapter_select"
)

# Detect if chapter selection changed
chapters_changed = False
if 'selected_chapters' in st.session_state and set(selected_chapters) != set(st.session_state.selected_chapters):
    chapters_changed = True
    st.session_state.selected_chapters = selected_chapters

# Reset quiz if chapters changed or if it's the first run with chapters selected
if chapters_changed or ('filtered_flashcards' not in st.session_state or st.session_state.filtered_flashcards.empty) and selected_chapters:
     reset_quiz_state(st.session_state.all_flashcards, selected_chapters)
     st.rerun() # Rerun to apply the new filter immediately


# --- Main Quiz Area ---
filtered_df = st.session_state.filtered_flashcards

if filtered_df is not None and not filtered_df.empty:
    num_cards = len(filtered_df)
    shuffled_indices = st.session_state.shuffled_indices
    current_shuffled_list_index = st.session_state.current_index

    if not shuffled_indices:
         st.warning("No flashcards available for the selected chapters.")
    elif current_shuffled_list_index < len(shuffled_indices):
        actual_card_index = shuffled_indices[current_shuffled_list_index]
        card = filtered_df.iloc[actual_card_index]

        st.subheader(f"Card {current_shuffled_list_index + 1} of {num_cards} (Selected Chapters)")
        st.markdown(f"**Chapter:** {card[CHAPTER_COL]}")
        st.markdown(f"**Question:**\n> {card[QUESTION_COL]}")

        options = card[OPTIONS_COL]
        correct_answers_raw = card[ANSWER_COL]
        is_multi_select = MULTI_ANSWER_SEP in correct_answers_raw
        correct_answers_set = set(ans.strip() for ans in correct_answers_raw.split(MULTI_ANSWER_SEP)) if is_multi_select else {correct_answers_raw.strip()}

        # --- Input Widget (Radio or Multiselect) ---
        widget_key = f"input_{actual_card_index}" # Unique key per card
        current_selection = None

        answer_key = f"answer_{actual_card_index}"
        if is_multi_select:
            st.info("This question may have multiple correct answers.")
            # Use checkboxes for multi-select
            current_selection = []
            for option in options:
                is_selected = st.checkbox(option, key=f"{option}_{actual_card_index}", disabled=st.session_state.show_feedback)
                if is_selected:
                    current_selection.append(option)
            st.session_state.current_selection = current_selection # Store current selection
        else:
            # Radio buttons for single select
            current_selection = st.radio(
                "Choose your answer:",
                options,
                index=options.index(st.session_state.current_selection) if st.session_state.current_selection in options else None, # Persist selection
                key=widget_key,
                disabled=st.session_state.show_feedback
            )
            st.session_state.current_selection = current_selection

        # --- Buttons and Feedback Logic ---
        col1, col2 = st.columns([1, 5])

        with col1:
            submit_disabled = st.session_state.show_feedback or not st.session_state.current_selection
            submit_button = st.button("Submit Answer", key=f"submit_{actual_card_index}", disabled=submit_disabled)

        if submit_button:
            st.session_state.user_answer = st.session_state.current_selection
            st.session_state.show_feedback = True
            st.session_state.total_answered += 1

            # Check correctness
            user_answers_set = set(st.session_state.current_selection) if isinstance(st.session_state.current_selection, list) else {st.session_state.current_selection}
            if user_answers_set == correct_answers_set:
                st.session_state.correct_count += 1

        if st.session_state.show_feedback:
            user_answer = st.session_state.user_answer
            user_answers_set = set(user_answer) if isinstance(user_answer, list) else {user_answer}

            is_correct = (user_answers_set == correct_answers_set)
            correct_answer_display = ", ".join(sorted(list(correct_answers_set)))

            if is_correct:
                st.success(f"Correct! 🎉 The answer is: **{correct_answer_display}**")
            else:
                chosen_display = ", ".join(sorted(list(user_answers_set)))
                st.error(f"Incorrect. 😥 You chose: **{chosen_display}**. The correct answer is: **{correct_answer_display}**")

            with col1:
                if st.button("Next Card", key=f"next_{actual_card_index}"):
                    st.session_state.current_index += 1
                    st.session_state.user_answer = None
                    st.session_state.show_feedback = False
                    st.session_state.current_selection = None
                    # No st.rerun() here - rely on Streamlit's natural update

        # Display Score in Sidebar
        st.sidebar.header("Score")
        st.sidebar.metric("Correct Answers", f"{st.session_state.correct_count} / {st.session_state.total_answered}")

    elif filtered_df is not None and not filtered_df.empty:
        st.success("🎉 You've completed all the flashcards for the selected chapters!")
        st.balloons()
        st.metric("Final Score (Selected Chapters)", f"{st.session_state.correct_count} / {num_cards}")
        if st.button("Restart Quiz (Same Chapters)"):
            reset_quiz_state(st.session_state.all_flashcards, st.session_state.selected_chapters)
            # No st.rerun() here - rely on Streamlit's natural update

elif not selected_chapters:
    st.warning("Please select at least one chapter from the sidebar to start the quiz.")
elif all_flashcards_df is None:
    st.error("Could not load flashcards. Please check the data file 'iot_flashcards_v2.csv' and ensure it's in the correct format.")
else:
    st.warning("No flashcards found for the selected chapters in 'iot_flashcards_v2.csv'.")
import streamlit as st
import pandas as pd
import random
import ast # For safely evaluating string representations if needed

# --- Configuration ---
DATA_FILE = 'iot_flashcards_v2.csv' # Updated data file
QUESTION_COL = 'Question'
OPTIONS_COL = 'Options'
ANSWER_COL = 'Correct Answer'
CHAPTER_COL = 'Chapter' # New column
MULTI_ANSWER_SEP = ';;' # Separator for multiple correct answers

# --- Load Data ---
@st.cache_data # Cache the data loading to improve performance
def load_flashcards(file_path):
    """Loads flashcard data from the enhanced CSV file."""
    try:
        df = pd.read_csv(file_path)
        # Check for required columns
        required_cols = [CHAPTER_COL, QUESTION_COL, OPTIONS_COL, ANSWER_COL]
        if not all(col in df.columns for col in required_cols):
            st.error(f"CSV file must contain columns: {', '.join(required_cols)}")
            return None

        # Fill potential NaN values in critical columns to avoid errors
        df[QUESTION_COL] = df[QUESTION_COL].fillna('')
        df[OPTIONS_COL] = df[OPTIONS_COL].fillna('')
        df[ANSWER_COL] = df[ANSWER_COL].fillna('')
        df[CHAPTER_COL] = df[CHAPTER_COL].fillna('Unknown')

        # Parse options string into a list, handling potential errors
        def parse_options(options_str):
            if pd.isna(options_str) or not isinstance(options_str, str):
                return []
            return [opt.strip() for opt in options_str.split('|')]
        df[OPTIONS_COL] = df[OPTIONS_COL].apply(parse_options)

        # Ensure Correct Answer is string
        df[ANSWER_COL] = df[ANSWER_COL].astype(str)

        # Basic validation: Check if correct answers exist within options
        valid_rows = []
        for index, row in df.iterrows():
            options_set = set(row[OPTIONS_COL])
            correct_answers_raw = row[ANSWER_COL]
            is_multi = MULTI_ANSWER_SEP in correct_answers_raw
            correct_answers_list = [ans.strip() for ans in correct_answers_raw.split(MULTI_ANSWER_SEP)] if is_multi else [correct_answers_raw.strip()]

            # Check if all correct answers are present in the options list
            if all(ans in options_set for ans in correct_answers_list if ans): # Check non-empty answers
                 valid_rows.append(index)
            # else:
            #     print(f"Warning: Row {index} skipped. Correct answer(s) '{correct_answers_list}' not fully in options '{options_set}'.")


        if len(valid_rows) < len(df):
             print(f"Warning: Filtered out {len(df) - len(valid_rows)} rows due to mismatch between answers and options.")

        df_filtered = df.loc[valid_rows].reset_index(drop=True)

        if df_filtered.empty:
             st.warning("No valid flashcards found after validation. Check CSV content.")
             return None

        return df_filtered

    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return None

# --- Helper Functions ---
def reset_quiz_state(flashcards_df, selected_chapters):
    """Resets the quiz state based on selected chapters."""
    if flashcards_df is None or selected_chapters is None:
        st.session_state.filtered_flashcards = pd.DataFrame()
        st.session_state.shuffled_indices = []
    else:
        # Filter based on selected chapters
        st.session_state.filtered_flashcards = flashcards_df[flashcards_df[CHAPTER_COL].isin(selected_chapters)].reset_index(drop=True)

        if not st.session_state.filtered_flashcards.empty:
            # Create a shuffled list of indices for the filtered data
            indices = list(range(len(st.session_state.filtered_flashcards)))
            random.shuffle(indices)
            st.session_state.shuffled_indices = indices
        else:
            st.session_state.shuffled_indices = []

    # Reset progress
    st.session_state.current_index = 0
    st.session_state.user_answer = None
    st.session_state.show_feedback = False
    st.session_state.correct_count = 0
    st.session_state.total_answered = 0
    # Clear previous selections (important for multiselect)
    st.session_state.current_selection = None


# --- Initialize State ---
def initialize_state(flashcards_df):
    """Initializes Streamlit session state variables."""
    if 'all_flashcards' not in st.session_state:
         st.session_state.all_flashcards = flashcards_df # Store the original full dataframe

    if 'available_chapters' not in st.session_state:
        if flashcards_df is not None:
            st.session_state.available_chapters = sorted(flashcards_df[CHAPTER_COL].unique().tolist())
        else:
            st.session_state.available_chapters = []

    # Initialize filter-dependent states if they don't exist
    if 'filtered_flashcards' not in st.session_state:
        st.session_state.filtered_flashcards = pd.DataFrame()
    if 'shuffled_indices' not in st.session_state:
        st.session_state.shuffled_indices = []
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'user_answer' not in st.session_state: # Stores the submitted answer(s)
        st.session_state.user_answer = None
    if 'show_feedback' not in st.session_state:
        st.session_state.show_feedback = False
    if 'correct_count' not in st.session_state:
        st.session_state.correct_count = 0
    if 'total_answered' not in st.session_state:
        st.session_state.total_answered = 0
    if 'selected_chapters' not in st.session_state:
         st.session_state.selected_chapters = st.session_state.available_chapters # Default to all chapters
    if 'current_selection' not in st.session_state: # Stores the current radio/multiselect choice before submission
        st.session_state.current_selection = None


# --- Main App Logic ---
st.set_page_config(layout="wide")
st.title("🧠 IoT Flashcard Quiz")

# Load data once
all_flashcards_df = load_flashcards(DATA_FILE)

initialize_state(all_flashcards_df)

# --- Sidebar for Chapter Selection ---
st.sidebar.header("Chapters")
selected_chapters = st.sidebar.multiselect(
    "Select chapters to study:",
    options=st.session_state.available_chapters,
    default=st.session_state.selected_chapters,
    key="chapter_select"
)

# Detect if chapter selection changed
chapters_changed = False
if 'selected_chapters' in st.session_state and set(selected_chapters) != set(st.session_state.selected_chapters):
    chapters_changed = True
    st.session_state.selected_chapters = selected_chapters

# Reset quiz if chapters changed or if it's the first run with chapters selected
if chapters_changed or ('filtered_flashcards' not in st.session_state or st.session_state.filtered_flashcards.empty) and selected_chapters:
     reset_quiz_state(st.session_state.all_flashcards, selected_chapters)
     st.rerun() # Rerun to apply the new filter immediately


# --- Main Quiz Area ---
filtered_df = st.session_state.filtered_flashcards

if filtered_df is not None and not filtered_df.empty:
    num_cards = len(filtered_df)
    shuffled_indices = st.session_state.shuffled_indices
    current_shuffled_list_index = st.session_state.current_index

    if not shuffled_indices:
         st.warning("No flashcards available for the selected chapters.")
    elif current_shuffled_list_index < len(shuffled_indices):
        actual_card_index = shuffled_indices[current_shuffled_list_index]
        card = filtered_df.iloc[actual_card_index]

        st.subheader(f"Card {current_shuffled_list_index + 1} of {num_cards} (Selected Chapters)")
        st.markdown(f"**Chapter:** {card[CHAPTER_COL]}")
        st.markdown(f"**Question:**\n> {card[QUESTION_COL]}")

        options = card[OPTIONS_COL]
        correct_answers_raw = card[ANSWER_COL]
        is_multi_select = MULTI_ANSWER_SEP in correct_answers_raw
        correct_answers_set = set(ans.strip() for ans in correct_answers_raw.split(MULTI_ANSWER_SEP)) if is_multi_select else {correct_answers_raw.strip()}

        # --- Input Widget (Radio or Multiselect) ---
        widget_key = f"input_{actual_card_index}" # Unique key per card
        current_selection = None

        if is_multi_select:
            st.info("This question may have multiple correct answers.")
            current_selection = st.multiselect(
                "Choose your answer(s):",
                options,
                key=widget_key,
                default=st.session_state.current_selection if isinstance(st.session_state.current_selection, list) else [], # Persist selection before submit
                disabled=st.session_state.show_feedback
            )
        else:
            # Need to handle index persistence carefully for radio
            current_selection = st.radio(
                "Choose your answer:",
                options,
                index=options.index(st.session_state.current_selection) if st.session_state.current_selection in options else None, # Persist selection
                key=widget_key,
                disabled=st.session_state.show_feedback
            )

        # Store current widget state before potential rerun by button clicks
        st.session_state.current_selection = current_selection

        # --- Buttons and Feedback Logic ---
        col1, col2 = st.columns([1, 5]) # Adjust column ratios as needed

        with col1:
            # Disable submit if no answer is chosen (handles both single and multi-select)
            submit_disabled = st.session_state.show_feedback or not current_selection
            submit_button = st.button("Submit Answer", key=f"submit_{actual_card_index}", disabled=submit_disabled)

        if submit_button and current_selection is not None:
            st.session_state.user_answer = current_selection # Store the submitted answer(s)
            st.session_state.show_feedback = True
            st.session_state.total_answered += 1

            # Check correctness
            user_answers_set = set(current_selection) if isinstance(current_selection, list) else {current_selection}
            if user_answers_set == correct_answers_set:
                st.session_state.correct_count += 1

            st.rerun() # Rerun to show feedback and disable input/submit

        if st.session_state.show_feedback:
            user_answer = st.session_state.user_answer # Retrieve the submitted answer
            user_answers_set = set(user_answer) if isinstance(user_answer, list) else {user_answer}

            is_correct = (user_answers_set == correct_answers_set)

            correct_answer_display = ", ".join(sorted(list(correct_answers_set)))

            if is_correct:
                st.success(f"Correct! 🎉 The answer is: **{correct_answer_display}**")
            else:
                chosen_display = ", ".join(sorted(list(user_answers_set)))
                st.error(f"Incorrect. 😥 You chose: **{chosen_display}**. The correct answer is: **{correct_answer_display}**")

            with col1: # Place the Next button in the same column as Submit
                 if st.button("Next Card", key=f"next_{actual_card_index}"):
                    st.session_state.current_index += 1
                    st.session_state.user_answer = None
                    st.session_state.show_feedback = False
                    st.session_state.current_selection = None # Reset widget selection state
                    st.rerun() # Rerun to display the next card

        # Display Score in Sidebar
        st.sidebar.header("Score")
        st.sidebar.metric("Correct Answers", f"{st.session_state.correct_count} / {st.session_state.total_answered}")

    elif filtered_df is not None and not filtered_df.empty: # End of quiz for selected chapters
        st.success("🎉 You've completed all the flashcards for the selected chapters!")
        st.balloons()
        st.metric("Final Score (Selected Chapters)", f"{st.session_state.correct_count} / {num_cards}")
        if st.button("Restart Quiz (Same Chapters)"):
            # Reset state for the same selected chapters
            reset_quiz_state(st.session_state.all_flashcards, st.session_state.selected_chapters)
            st.rerun()

elif not selected_chapters:
     st.warning("Please select at least one chapter from the sidebar to start the quiz.")
elif all_flashcards_df is None:
    st.error("Could not load flashcards. Please check the data file 'iot_flashcards_v2.csv' and ensure it's in the correct format.")
else: # filtered_df is empty but chapters were selected
     st.warning("No flashcards found for the selected chapters in 'iot_flashcards_v2.csv'.")


st.sidebar.markdown("---")
st.sidebar.markdown("Created by Cline.")
