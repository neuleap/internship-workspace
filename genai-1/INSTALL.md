# Installation Guide

This guide will walk you through setting up the Northwind Database Insights Assistant on your system.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **PostgreSQL**: [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git**: [Download Git](https://git-scm.com/downloads)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd genai-1
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

If you encounter any issues, try upgrading pip first:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

#### Option A: Command Line (Recommended)

```bash
# Create the database
createdb -U postgres northwind

# Import schema and data
psql -U postgres -d northwind -f "sql/northwind_ddl.sql"
psql -U postgres -d northwind -f "sql/northwind_data.sql"
```

#### Option B: Using pgAdmin

1. Open pgAdmin
2. Right-click on "Databases" → "Create" → "Database"
3. Name it "northwind"
4. Right-click on the new database → "Query Tool"
5. Open and execute `sql/northwind_ddl.sql`
6. Open and execute `sql/northwind_data.sql`

### 5. Get Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new API key
5. Copy the key (you'll need it for the next step)

### 6. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your details:
```env
GROQ_API_KEY=your_groq_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=northwind
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

### 7. Test the Installation

#### Test Database Connection:
```bash
python test_northwind.py
```

Expected output:
```
✅ Database connection successful!
Tables found: ['categories', 'customers', 'employees', 'order_details', 'orders', 'products', 'shippers', 'suppliers']
```

#### Test Groq API:
```bash
python test.py
```

Expected output:
```
✅ Groq API Key found.
🚀 Requesting chat completion from Groq...
✅ Success! Model Response: [AI response about fast language models]
```

### 8. Run the Application

```bash
streamlit run src/app.py
```

The application should open in your browser at `http://localhost:8501`

## Troubleshooting

### Common Installation Issues

#### Python/Pip Issues

**Error**: `python: command not found`
- **Solution**: Ensure Python is installed and added to PATH

**Error**: `pip: command not found`
- **Solution**: Try `python -m pip` instead of `pip`

#### PostgreSQL Issues

**Error**: `createdb: command not found`
- **Solution**: Add PostgreSQL bin directory to PATH
- **Windows**: Usually `C:\Program Files\PostgreSQL\XX\bin`
- **macOS**: `/Applications/Postgres.app/Contents/Versions/XX/bin`

**Error**: `psql: FATAL: password authentication failed`
- **Solution**: Check your PostgreSQL password
- Reset password if needed: `ALTER USER postgres PASSWORD 'newpassword';`

#### Package Installation Issues

**Error**: `error: Microsoft Visual C++ 14.0 is required`
- **Solution**: Install Visual Studio Build Tools or Visual Studio Community

**Error**: `psycopg2` installation fails
- **Solution**: Try installing the binary version:
  ```bash
  pip install psycopg2-binary
  ```

#### API Issues

**Error**: `API Key not found`
- **Solution**: Double-check your `.env` file format and API key

**Error**: `Model decommissioned`
- **Solution**: Update the model name in `src/llm/query_generator.py`

### Performance Optimization

1. **Database Performance**:
   ```sql
   -- Add indexes for better query performance
   CREATE INDEX idx_orders_customer_id ON orders(customer_id);
   CREATE INDEX idx_order_details_product_id ON order_details(product_id);
   ```

2. **Python Performance**:
   ```bash
   # Use faster JSON library
   pip install ujson
   ```

### Verification Checklist

- [ ] Python 3.8+ installed
- [ ] PostgreSQL running
- [ ] Virtual environment activated
- [ ] All packages installed (`pip list`)
- [ ] Database created and populated
- [ ] `.env` file configured
- [ ] Database connection test passes
- [ ] API connection test passes
- [ ] Streamlit app launches successfully

## Next Steps

Once installation is complete:

1. Read the [README.md](README.md) for usage instructions
2. Try the sample queries listed in the documentation
3. Explore the Northwind database schema
4. Customize the application for your needs

## Getting Help

If you encounter issues during installation:

1. Check this troubleshooting guide
2. Ensure all prerequisites are met
3. Verify your environment variables
4. Check the GitHub issues page
5. Create a new issue with:
   - Your operating system
   - Python version
   - Error messages
   - Steps you've tried

## Development Setup

For development and contribution:

```bash
# Install additional development dependencies
pip install pytest black flake8 mypy

# Run tests
pytest

# Format code
black src/

# Lint code
flake8 src/
```