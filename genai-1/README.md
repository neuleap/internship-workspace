# Northwind Database Insights Assistant

A powerful natural language to SQL query interface built with Streamlit and Groq AI, designed to make database queries accessible through conversational language.

## 🚀 Features

- **Natural Language Queries**: Ask questions in plain English about your data
- **Real-time SQL Generation**: Powered by Groq's lightning-fast LLM API
- **Interactive Web Interface**: Built with Streamlit for easy use
- **Northwind Database**: Pre-loaded with realistic business data
- **Query Visualization**: See the generated SQL and results side-by-side
- **Schema-Aware**: Automatically understands your database structure

## 📊 Sample Questions You Can Ask

- "What are the top 5 best-selling products?"
- "Which customers have placed the most orders?"
- "What were the total sales by category in 1997?"
- "Show me all orders from customers in Germany"
- "Which employees have the highest sales performance?"
- "What are the most expensive products in each category?"

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI/LLM**: Groq API (Llama 3.3 70B)
- **Database**: PostgreSQL
- **Backend**: Python
- **ORM**: SQLAlchemy
- **Data Processing**: Pandas

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL installed and running
- Groq API key (get one at [console.groq.com](https://console.groq.com))

## ⚡ Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd genai-1

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=northwind
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 3. Database Setup

```bash
# Create the Northwind database
createdb -U postgres northwind

# Load the schema and data
psql -U postgres -d northwind -f "sql/northwind_ddl.sql"
psql -U postgres -d northwind -f "sql/northwind_data.sql"
```

### 4. Test the Setup

```bash
# Test database connection
python test_northwind.py

# Test Groq API
python test.py
```

### 5. Run the Application

```bash
streamlit run src/app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
genai-1/
├── .env                    # Environment variables
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── test_northwind.py     # Database connection test
├── test.py               # Groq API test
├── sql/
│   ├── northwind_ddl.sql # Database schema
│   └── northwind_data.sql # Sample data
└── src/
    ├── app.py            # Main Streamlit application
    ├── database/
    │   └── db_connector.py # Database connection logic
    └── llm/
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key | Required |
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | northwind |
| `DB_USER` | Database user | postgres |
| `DB_PASSWORD` | Database password | Required |

### AI Model Configuration

The application uses `llama-3.3-70b-versatile` model by default. You can modify this in `src/llm/query_generator.py`:

```python
self.model_name = "llama-3.3-70b-versatile"
```

## 🗄️ Database Schema

The Northwind database contains the following tables:

- **categories**: Product categories
- **customers**: Customer information
- **employees**: Employee details
- **orders**: Order headers
- **order_details**: Order line items
- **products**: Product catalog
- **suppliers**: Supplier information
- **shippers**: Shipping companies

## 🧪 Testing

### Database Connection Test

```bash
python test_northwind.py
```

Expected output:
```
✅ Database connection successful!
Tables found: ['categories', 'customers', 'employees', ...]
```

### API Connection Test

```bash
python test.py
```

Expected output:
```
✅ Groq API Key found.
🚀 Requesting chat completion from Groq...
✅ Success! Model Response: [AI response]
```

## 🚨 Troubleshooting

### Common Issues

**Database Connection Error**
```
OperationalError: connection to server failed
```
- Ensure PostgreSQL is running
- Check your database credentials in `.env`
- Verify the database exists

**API Key Error**
```
Error: 400 - API Key not found
```
- Check your `GROQ_API_KEY` in `.env`
- Ensure the key is valid and not expired

**Model Decommissioned Error**
```
Error: model has been decommissioned
```
- Update the model name in `query_generator.py`
- Check [Groq documentation](https://console.groq.com/docs) for current models

### Performance Tips

1. **Query Optimization**: The AI generates optimized SQL, but complex queries may take time
2. **Database Indexing**: Ensure proper indexing on frequently queried columns
3. **API Limits**: Groq has rate limits; avoid rapid successive requests

## 🔒 Security

- Never commit your `.env` file to version control
- Keep your API keys secure
- Use environment variables for all sensitive data
- Consider database connection pooling for production use

## 🚀 Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Connect your repo to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add environment variables in the Streamlit Cloud settings
4. Deploy!

### Docker (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "src/app.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙋‍♂️ Support

If you encounter any issues:

1. Check the troubleshooting section
2. Review the logs for error details
3. Ensure all prerequisites are met
4. Create an issue with detailed error information

## 🎯 Future Enhancements

- [ ] Support for multiple database types
- [ ] Query history and favorites
- [ ] Data visualization charts
- [ ] Export results to CSV/Excel
- [ ] User authentication
- [ ] Query performance analytics
- [ ] Custom database schema upload

---

**Made with ❤️ using Groq AI and Streamlit**
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