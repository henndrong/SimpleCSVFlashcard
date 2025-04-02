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
        answer_key = f"answer_{actual_card_index}"
        widget_key = f"input_{actual_card_index}" # Unique key per card
        if is_multi_select:
            st.info("This question may have multiple correct answers.")
            # Initialize current selection list if it doesn't exist
            if not isinstance(st.session_state.current_selection, list):
                st.session_state.current_selection = []
            
            # Create a callback function for each option that directly manages the selection state
            def create_checkbox_callback(opt):
                checkbox_key = f"cb_{opt}_{actual_card_index}"
                
                # Define what happens when this specific checkbox changes
                def on_change():
                    is_checked = st.session_state[checkbox_key]
                    # Make a copy of the current selection to avoid reference issues
                    current = list(st.session_state.current_selection) if isinstance(st.session_state.current_selection, list) else []
                    
                    if is_checked and opt not in current:
                        current.append(opt)
                    elif not is_checked and opt in current:
                        current.remove(opt)
                        
                    st.session_state.current_selection = current
                
                return checkbox_key, on_change
            
            # Display each option as a checkbox with its own callback
            for option in options:
                checkbox_key, callback_fn = create_checkbox_callback(option)
                is_selected = option in st.session_state.current_selection
                
                st.checkbox(
                    option,
                    value=is_selected,
                    key=checkbox_key,
                    disabled=st.session_state.show_feedback,
                    on_change=callback_fn
                )
        else:
            # Radio buttons for single select with improved change detection
            radio_key = f"radio_{actual_card_index}"
            
            # Initialize radio_changed flag in session state if not exists
            if f"prev_selection_{actual_card_index}" not in st.session_state:
                st.session_state[f"prev_selection_{actual_card_index}"] = None
            
            # For single-option questions, auto-select it
            if len(options) == 1:
                # If there's only one option, auto-select it
                st.session_state.current_selection = options[0]
                st.radio(
                    "Choose your answer (auto-selected as there's only one option):",
                    options,
                    index=0,
                    key=radio_key,
                    disabled=st.session_state.show_feedback
                )
                # Make sure we also update the previous selection tracker
                st.session_state[f"prev_selection_{actual_card_index}"] = options[0]
            else:
                # Calculate default index for the radio button
                try:
                    default_index = options.index(st.session_state.current_selection) if st.session_state.current_selection in options else 0
                except (ValueError, IndexError):
                    default_index = 0
                
                # Display the radio button
                selected_option = st.radio(
                    "Choose your answer:",
                    options,
                    index=default_index,
                    key=radio_key,
                    disabled=st.session_state.show_feedback
                )
                
                # Check if selection has changed and update
                if selected_option != st.session_state[f"prev_selection_{actual_card_index}"]:
                    # Store the new selection in regular current_selection
                    st.session_state.current_selection = selected_option
                    # Update the previous selection tracker
                    st.session_state[f"prev_selection_{actual_card_index}"] = selected_option
                    
                    # Only rerun if this isn't the initial load
                    if st.session_state[f"prev_selection_{actual_card_index}"] is not None:
                        st.rerun()

        # --- Buttons and Feedback Logic ---
        col1, col2 = st.columns([1, 5])

        # Display either Submit Answer or Next Card button based on feedback state
        with col1:
            if not st.session_state.show_feedback:
                # Only show Submit Answer when feedback is not shown
                # For radio buttons, we always have a selection (the first option by default)
                # For checkboxes, only disable if there's no selection
                if is_multi_select:
                    submit_disabled = not st.session_state.current_selection or len(st.session_state.current_selection) == 0
                else:
                    # For radio buttons, always enable since there's always a selection
                    submit_disabled = False
                
                submit_button = st.button("Submit Answer", key=f"submit_{actual_card_index}", disabled=submit_disabled)
            else:
                # Show Next Card button when feedback is shown (replacing Submit Answer)
                if st.button("Next Card", key=f"next_{actual_card_index}"):
                    st.session_state.current_index += 1
                    st.session_state.user_answer = None
                    st.session_state.show_feedback = False
                    st.session_state.current_selection = None
                    st.rerun()  # Force rerun to update the page immediately

        if not st.session_state.show_feedback and submit_button:
            st.session_state.user_answer = st.session_state.current_selection
            st.session_state.show_feedback = True
            st.session_state.total_answered += 1

            # Check correctness
            user_answers_set = set(st.session_state.current_selection) if isinstance(st.session_state.current_selection, list) else {st.session_state.current_selection}
            if user_answers_set == correct_answers_set:
                st.session_state.correct_count += 1
            
            # Force rerun to update UI (hide Submit button, show Next Card button)
            st.rerun()

        if st.session_state.show_feedback:
            user_answer = st.session_state.user_answer
            # Handle potential None or unusual values in user_answer
            if user_answer is None:
                user_answers_set = set()
            else:
                user_answers_set = set(user_answer) if isinstance(user_answer, list) else {user_answer}

            is_correct = (user_answers_set == correct_answers_set)
            correct_answer_display = ", ".join(sorted(list(correct_answers_set)))

            if is_correct:
                st.success(f"Correct! 🎉 The answer is: **{correct_answer_display}**")
            else:
                # Safely convert user_answers_set to a display string
                if user_answers_set:
                    # Convert all elements to strings before sorting to avoid type errors
                    chosen_display = ", ".join(sorted(str(ans) for ans in user_answers_set))
                else:
                    chosen_display = "No answer provided"
                st.error(f"Incorrect. 😥 You chose: **{chosen_display}**. The correct answer is: **{correct_answer_display}**")

        # Display Score in Sidebar
        st.sidebar.header("Score")
        st.sidebar.metric("Correct Answers", f"{st.session_state.correct_count} / {st.session_state.total_answered}")

    elif filtered_df is not None and not filtered_df.empty:
        st.success("🎉 You've completed all the flashcards for the selected chapters!")
        st.balloons()
        st.metric("Final Score (Selected Chapters)", f"{st.session_state.correct_count} / {num_cards}")
        if st.button("Restart Quiz (Same Chapters)"):
            reset_quiz_state(st.session_state.all_flashcards, st.session_state.selected_chapters)
            st.rerun()  # Force rerun to update the page immediately

elif not selected_chapters:
    st.warning("Please select at least one chapter from the sidebar to start the quiz.")
elif all_flashcards_df is None:
    st.error("Could not load flashcards. Please check the data file 'iot_flashcards_v2.csv' and ensure it's in the correct format.")
else:
    st.warning("No flashcards found for the selected chapters in 'iot_flashcards_v2.csv'.")
