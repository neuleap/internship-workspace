# GenAI Project 1: Sales Insights Assistant

This project implements a Sales Insights Assistant using the Northwind database, Google's Gemini AI, and Streamlit.

## Project Overview
- Natural language to SQL query conversion
- Interactive Streamlit interface
- PostgreSQL database integration
- Real-time query execution and results display

## Setup Instructions

1. **Database Setup**
   ```bash
   # Create a new database
   createdb northwind

   # Import the schema and data
   psql -d northwind -f sql/northwind_ddl.sql
   psql -d northwind -f sql/northwind_data.sql
   ```

2. **Environment Setup**
   Create a `.env` file with:
   ```
   DB_HOST=localhost
   DB_NAME=northwind
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_PORT=5432
   GOOGLE_API_KEY=your_google_api_key
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   streamlit run src/app.py
   ```

## Project Structure
```
genai-1/
├── src/
│   ├── database/       # Database connection handling
│   ├── llm/           # Gemini AI integration
│   ├── utils/         # Utility functions
│   └── app.py         # Main Streamlit application
├── sql/               # Database scripts
├── requirements.txt   # Python dependencies
└── test_gemini.py    # API test script
```

## Features
- Natural language query processing
- SQL query generation
- Interactive data visualization
- Error handling and validation