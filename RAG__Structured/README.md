
# Project Title
# SQL Query Assistant using Streamlit and Gemini

1. Project Description

The SQL Query Assistant is an AI-powered web application built using Streamlit, PostgreSQL, and Google Gemini AI.
It automatically connects to a PostgreSQL database, analyzes the schema in the background, and allows users to generate and execute SQL queries simply by typing natural language questions.

The app also provides:

AI-generated data summaries

Automatic visualization suggestions

A contextual chat interface to ask follow-up questions based on previous query results

This tool helps data analysts and developers explore databases efficiently without manually writing SQL queries.

2. Features

Automatic PostgreSQL database connection and schema analysis (runs silently after connection)

Natural language to SQL query generation using Google Gemini

SQL query execution and result display using Pandas and Streamlit

AI-generated data insights and visual summaries

Smart visualization suggestions (bar, pie, scatter charts)

Conversational chat to discuss data insights based on previous results

Modular, Pylint-friendly, and production-ready code structure

3. Project Structure
project/
│
├── app.py                # Main Streamlit application
├── .env                  # Environment variables file (hidden from Git)
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation

4. Installation and Setup

Follow these steps to set up and run the application locally:

Step 1: Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

Step 2: Create and activate a virtual environment
python -m venv venv


For Windows:

venv\Scripts\activate


For macOS/Linux:

source venv/bin/activate

Step 3: Install dependencies
pip install -r requirements.txt

Step 4: Configure environment variables

Create a .env file in the project root directory and add the following variables:

DB_USERNAME=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
GEMINI_API_KEY=your_gemini_api_key


Example:

DB_USERNAME=postgres
DB_PASSWORD=MyPassword123
DB_HOST=localhost
DB_PORT=5432
DB_NAME=northwind
GEMINI_API_KEY=AIzaSyDxxxxx-YourGeminiKey

Step 5: Run the application
streamlit run app.py


After running, open your browser and navigate to:

http://localhost:8501

5. Usage

Connect to Database:
The app automatically connects to your PostgreSQL database and analyzes its schema silently after startup.

Generate SQL Queries:
Enter a natural language query like:

Show the top 10 customers by total sales


The app will use Gemini to generate a valid SQL query, execute it, and display the results.

View Summaries and Visuals:
Gemini automatically provides a brief summary of your data and may suggest an appropriate visualization (bar, pie, or scatter chart).

Conversational Chat:
Ask follow-up questions such as:

Which region had the highest sales?


Gemini responds contextually using previous query data and memory.

6. Configuration Details

The app uses the .env file for secure configuration.
All database and API credentials must be defined there.

Required fields:

DB_USERNAME → PostgreSQL username

DB_PASSWORD → PostgreSQL password

DB_HOST → Database host address (e.g., localhost)

DB_PORT → Port number (default: 5432)

DB_NAME → Name of the PostgreSQL database

GEMINI_API_KEY → Google Gemini API key

7. Troubleshooting
Issue	Possible Cause	Solution
Database connection failed	Incorrect credentials or PostgreSQL not running	Check .env credentials and ensure the database service is active
Gemini API error	Invalid or missing API key	Verify your API key in .env and check Google Cloud Console
No data in results	Query returned no matching rows	Try a different question or verify database contents
Visualization not displayed	Gemini did not find numeric columns	Try a query with numerical data
Streamlit app not launching	Missing packages	Run pip install -r requirements.txt again
8. License

This project is licensed under the MIT License.
You are free to use, modify, and distribute it with attribution.

9. Credits

Developed by Mandar Ingole
Built with:

Streamlit

SQLAlchemy

Google Gemini

Plotly Express

Pandas

Python 3.9+

10. Example Workflow

Start the Streamlit app.

Type a question like:

Show total sales per product category

View the generated SQL query.

See the data, summary, and visualization.

Ask follow-up questions such as:

Which category has the highest average sales?


