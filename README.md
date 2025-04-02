# IoT Flashcard Quiz

A Streamlit-based flashcard application for studying IoT (Internet of Things) concepts through multiple-choice questions.

## Features

- **Chapter Selection**: Choose specific chapters to focus your study sessions
- **Multi/Single Answer Support**: Handles both single-choice and multiple-choice questions
- **Instant Feedback**: Receive immediate feedback on your answers
- **Progress Tracking**: Tracks your score as you progress through the flashcards
- **Responsive Design**: Works well on both desktop and mobile devices

## Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package installer)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/iot-flashcards.git
   cd iot-flashcards
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Open your browser and navigate to `http://localhost:8501`

## Usage

1. Select the chapters you want to study from the sidebar
2. Answer each question by selecting the appropriate option(s)
3. Submit your answer to receive feedback
4. Click "Next Card" to continue to the next question
5. Track your progress in the sidebar

## Data Format

The application uses a CSV file (`iot_flashcards_v2.csv`) with the following columns:
- **Chapter**: The chapter or category of the question
- **Question**: The flashcard question
- **Options**: Available options, separated by "|" character
- **Correct Answer**: The correct answer(s), separated by ";;" for multiple correct answers

## Deployment

For information on deploying this application to the internet, see the [deployment guide](cline_docs/deployment_guide.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Data processing powered by [Pandas](https://pandas.pydata.org/)
