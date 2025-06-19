# WhatsApp Chat Summarizer

## Overview
This is an AI-powered WhatsApp chat summarizer built with Streamlit and Google Gemini. It's designed for police officers to analyze WhatsApp chat exports and extract structured summaries, actionable tasks, and flagged keywords.

## Features
- Upload WhatsApp chat exports (.txt files)
- Parse timestamped messages with sender information
- Generate AI-powered summaries using Google Gemini
- Extract actionable tasks with responsible parties and deadlines
- Identify and flag important keywords
- Store results in SQLite database
- View historical summaries
- Download results as JSON or CSV

## Installation

### Prerequisites
- Python 3.11+
- Google Gemini API key

### Setup
1. Clone or download the project files
2. Install required packages:
   ```bash
   pip install streamlit google-generativeai pandas
   ```
3. Update the API key in `gemini_integration.py`
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage
1. **Export WhatsApp Chat**: Open WhatsApp, go to the chat you want to analyze, tap the three dots menu, select "More" → "Export chat" → "Without media"
2. **Upload File**: Use the sidebar to upload the exported .txt file
3. **Review Preview**: Check the parsed chat data in the preview table
4. **Generate Summary**: Click the "Generate Summary" button to process with AI
5. **Review Results**: Examine the summary, tasks, and keywords
6. **Download**: Save results as JSON or CSV files

## File Structure
- `app.py` - Main Streamlit application
- `whatsapp_parser.py` - WhatsApp chat parsing module
- `gemini_integration.py` - Google Gemini API integration
- `database.py` - SQLite database operations
- `chat_summaries.db` - SQLite database file (created automatically)

## API Configuration
Update the API key in `gemini_integration.py`:
```python
API_KEY = "your-gemini-api-key-here"
```

## Database Schema
The application uses SQLite with the following table:
- `chat_summaries`: Stores chat analysis results with ID, filename, timestamp, summary, tasks, keywords, and raw output

## Tech Stack
- **Frontend**: Streamlit (Python)
- **LLM**: Google Gemini via `google-generativeai`
- **Data Processing**: pandas, re, datetime
- **Storage**: SQLite (`sqlite3`)

