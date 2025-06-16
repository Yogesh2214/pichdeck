# Pitch Call Summarizer

A Streamlit application that records audio from calls, transcribes them, and generates summaries using ChatGPT.

## Features

- Audio recording from system audio
- Manual transcription entry
- Automatic summary generation using ChatGPT
- Export functionality for transcripts and summaries
- Recording duration tracking
- Organized file storage

## Requirements

- Python 3.11 or higher
- Streamlit
- OpenAI
- PyAudio
- NumPy
- SciPy
- SoundDevice

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pitch-call-summarizer.git
cd pitch-call-summarizer
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the provided local URL (usually http://localhost:8501)

3. Follow the on-screen instructions to:
   - Record audio
   - Enter transcript
   - Generate summary
   - Export results

## Project Structure

- `app.py`: Main application file
- `requirements.txt`: Python package dependencies
- `recordings/`: Directory for saved audio recordings
- `.env`: Environment variables (not tracked in git)
- `.gitignore`: Git ignore rules

## Security Notes

- Never commit your `.env` file or expose your API keys
- Keep your recordings secure and private
- Regularly update dependencies for security patches

## License

MIT License 