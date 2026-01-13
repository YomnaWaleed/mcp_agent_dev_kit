# 🏦 Banking AI Agent with MCP & RAG

A production-ready banking customer service AI agent built with Google ADK, featuring:
- **MCP (Model Context Protocol)** for secure transaction data access
- **RAG (Retrieval Augmented Generation)** for bank product information
- **Local LLM** support via Ollama (Qwen 3 VL 235B)
- **RESTful API** with JWT authentication

---

## 📋 Table of Contents

1. [Features](#-features)
2. [Architecture](#-architecture)
3. [Prerequisites](#-prerequisites)
4. [Installation](#-installation)
5. [Database Setup](#-database-setup)
6. [Running the Agent](#-running-the-agent)
7. [API Usage](#-api-usage)
8. [Testing](#-testing)
9. [Project Structure](#-project-structure)
10. [Troubleshooting](#-troubleshooting)

---

## ✨ Features

### Core Capabilities
- ✅ **Customer Information Retrieval** - Get customer details by ID
- ✅ **Transaction History** - View last N transactions
- ✅ **Account Balance** - Real-time balance inquiries
- ✅ **Product Search** - RAG-based bank product recommendations
- ✅ **Secure Authentication** - MCP API key validation
- ✅ **RESTful API** - JWT-authenticated endpoints

### Technical Features
- 🔒 **Secure Data Access** - Read-only MCP server
- 🤖 **Local LLM** - Privacy-focused (Ollama Qwen 3 VL)
- 📊 **Real Banking Data** - From comprehensive CSV dataset
- 🔍 **Vector Search** - ChromaDB for product knowledge
- 🚀 **Fast Responses** - Optimized database queries

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│            (ADK Web UI / REST API)                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────┐
│              Banking AI Agent (ADK)                       │
│         Model: Qwen 3 VL 235B (Ollama)                   │
└─────┬────────────────────────────────────────────────────┘
      │
      ├──────────────────────┬──────────────────────────────┐
      │                      │                              │
      ▼                      ▼                              ▼
┌────────────┐    ┌─────────────────┐         ┌────────────────┐
│ MCP Server │    │   RAG System    │         │   REST API     │
│ (stdio)    │    │   (ChromaDB)    │         │   (FastAPI)    │
├────────────┤    ├─────────────────┤         ├────────────────┤
│ - Customer │    │ - Products      │         │ - /auth/login  │
│ - Txns     │    │ - Embeddings    │         │ - /agent/query │
│ - Balance  │    │ - Vector Search │         │ - JWT Auth     │
└─────┬──────┘    └─────────────────┘         └────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────┐
│              SQLite Database                              │
│   ├── customers (20 records)                             │
│   └── transactions (20 records)                          │
└──────────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

### Required Software
- **Python**: 3.10 or higher
- **uv**: Python package installer (`pip install uv`)
- **Ollama**: For local LLM ([Download](https://ollama.com))
- **SQLite**: Pre-installed with Python

### Ollama Model
Download the Qwen 3 VL model:
```bash
ollama pull qwen3-vl:235b-cloud
```

---

## 🚀 Installation

### 1. Clone or Create Project Structure

```bash
# Create project directory
mkdir banking_ai_agent
cd banking_ai_agent

# Initialize uv project
uv init
```

### 2. Install Dependencies

```bash
# Install all required packages
uv add google-adk litellm ollama python-dotenv pandas sentence-transformers chromadb fastapi uvicorn python-jose
```

### 3. Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 4. Create ADK App Structure

```bash
adk create app
```

Choose option **2** (Don't use Gemini - use local LLM)

### 5. Setup Project Structure

Create the following directory structure:
```
banking_ai_agent/
├── .venv/
├── app/
│   ├── agent.py
│   ├── __init__.py
│   └── .env
├── src/
│   ├── api/
│   │   ├── main.py
│   │   ├── models.py
│   │   └── auth.py
│   ├── mcp/
│   │   ├── server.py
│   │   ├── create_db.py
│   │   └── db/
│   └── rag/
│       ├── extract_products.py
│       ├── create_vector_db.py
│       ├── product_knowledge.py
│       └── products/
├── data/
│   └── Comprehensive_Banking_Database.csv
├── .env
├── pyproject.toml
└── README.md
```

### 6. Environment Configuration

Create `.env` file in project root:
```dotenv
MCP_API_KEY=banking-dev-token-2026
OLLAMA_BASE_URL=http://localhost:11434
```

Copy to `app/.env`:
```bash
cp .env app/.env
```

---

## 💾 Database Setup

### Step 1: Prepare Data

Place your `Comprehensive_Banking_Database.csv` in the `data/` folder.

**CSV Format:**
```
Customer ID,First Name,Last Name,Age,Gender,Address,City,...
1,Joshua,Hall,45,Male,Address_1,Fort Worth,...
2,Mark,Taylor,47,Female,Address_2,Louisville,...
...
```

### Step 2: Create Database

```bash
python src/mcp/create_db.py
```

**Expected Output:**
```
Loading data from data/Comprehensive_Banking_Database.csv...
Loaded 20 rows
Columns: ['Customer ID', 'First Name', 'Last Name', ...]

✅ Database created successfully!
   Total customers: 20
   Total transactions: 20
   Location: src/mcp/db/banking.db

Sample customers:
   - ID: 1, Name: Joshua Hall
   - ID: 2, Name: Mark Taylor
   - ID: 3, Name: Joseph Flores
```

### Step 3: Verify Database (Optional)

```bash
sqlite3 src/mcp/db/banking.db

# Run queries
SELECT * FROM customers LIMIT 3;
SELECT * FROM transactions WHERE customer_id = 1;
.exit
```

---

## 🔍 RAG Setup (Product Knowledge Base)

### Step 1: Extract Products from Database

```bash
python src/rag/extract_products.py
```

**Output:**
```
✅ Extracted 8 products
   Account types: 2
   Loan types: 3
   Card types: 3

📁 Saved to: src/rag/products/products.json
```

### Step 2: Create Vector Database

```bash
python src/rag/create_vector_db.py
```

**Output:**
```
✅ Created vector database with 8 products
📁 Location: src/rag/products/chroma_db
```

---

## 🎯 Running the Agent

### Method 1: ADK Web Interface (Recommended)

#### Step 1: Start Ollama
```bash
# Terminal 1
ollama serve
```

#### Step 2: Run ADK Web Server
```bash
# Terminal 2
adk web
```

**Output:**
```
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://127.0.0.1:8000.                         |
+-----------------------------------------------------------------------------+
```

#### Step 3: Access Web UI
Open browser: `http://127.0.0.1:8000`

---

### Method 2: Command Line

```bash
adk run app
```

**Interactive Chat:**
```
Running agent app, type exit to exit.
[user]: Show me last transactions for customer 1
[agent]: Hello Joshua Hall! Here are your last 5 transactions:
         1. 12/7/2023 - Withdrawal: $1,457.61
         2. ...
```

---

## 🌐 API Usage

### Start API Server

```bash
python src/api/main.py
```

Server runs on: `http://localhost:8080`

### API Endpoints

#### 1. Authentication

```bash
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 2. Query Agent

```bash
POST /agent/query
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "query": "What's my balance?",
  "customer_id": 1
}
```

**Response:**
```json
{
  "status": "success",
  "response": "Your current balance is $1,313.38",
  "data": {
    "customer_id": 1
  }
}
```

---

## 🧪 Testing

### Test Scenarios

#### 1. Customer Information
```
Query: "Show me information for customer ID 1"
Expected: Joshua Hall, Age 45, Balance $1,313.38
```

#### 2. Transaction History
```
Query: "Show last 5 transactions for customer 1"
Expected: List of recent transactions with dates, types, amounts
```

#### 3. Account Balance
```
Query: "What's the balance for customer 2?"
Expected: Mark Taylor's balance $5,988.46
```

#### 4. Product Search
```
Query: "Tell me about savings accounts"
Expected: Information about savings account features
```

#### 5. Combined Query
```
Query: "Customer ID 1 first name Joshua show last transaction"
Expected: Extracts ID=1, shows recent transaction
```

---

## 📁 Project Structure

```
banking_ai_agent/
├── .venv/                          # Virtual environment
├── app/
│   ├── agent.py                    # Main ADK agent
│   ├── __init__.py
│   └── .env                        # Agent environment variables
├── src/
│   ├── api/
│   │   ├── main.py                 # FastAPI application
│   │   ├── models.py               # Pydantic models
│   │   └── auth.py                 # JWT authentication
│   ├── mcp/
│   │   ├── server.py               # MCP stdio server
│   │   ├── create_db.py            # Database initialization
│   │   └── db/
│   │       └── banking.db          # SQLite database
│   └── rag/
│       ├── extract_products.py     # Extract products from DB
│       ├── create_vector_db.py     # Create ChromaDB embeddings
│       ├── product_knowledge.py    # RAG query interface
│       └── products/
│           ├── products.json       # Product data
│           └── chroma_db/          # Vector database
├── data/
│   └── Comprehensive_Banking_Database.csv  # Source data
├── .env                            # Root environment variables
├── pyproject.toml                  # Project dependencies
└── README.md                       # This file
```

---

## 🛠️ Troubleshooting

### Issue 1: MCP Server Connection Error

**Error:**
```
Cleaning up disconnected session: stdio_session
```

**Solution:**
Ensure MCP server path is correct in `app/agent.py`:
```python
server_params=StdioServerParameters(
    command="python",
    args=["src/mcp/server.py"],  # ✅ Relative to project root
    ...
)
```

---

### Issue 2: Database Not Found

**Error:**
```
Database not found at src/mcp/db/banking.db
```

**Solution:**
```bash
python src/mcp/create_db.py
```

---

### Issue 3: Ollama Model Not Found

**Error:**
```
LiteLLM completion() model= qwen3-vl:235b-cloud; provider = ollama_chat
[Error] Model not found
```

**Solution:**
```bash
ollama pull qwen3-vl:235b-cloud
ollama list  # Verify installation
```

---

### Issue 4: RAG Search Unavailable

**Error:**
```
Product search unavailable. Run: python src/rag/create_vector_db.py
```

**Solution:**
```bash
python src/rag/extract_products.py
python src/rag/create_vector_db.py
```

---

### Issue 5: Slow Responses

**Cause:** Qwen 3 VL 235B is a large model

**Solutions:**
1. Use smaller model:
   ```bash
   ollama pull llama3.2:3b
   ```
   Update `app/agent.py`:
   ```python
   model=LiteLlm(model="ollama_chat/llama3.2:3b")
   ```

2. Use cloud-hosted model:
   ```python
   model=LiteLlm(model="groq/llama-3.3-70b-versatile")
   ```

---

## 📊 Sample Data

The included CSV contains 20 customers with comprehensive banking data:

| Customer ID | Name | Age | Account Type | Balance | Transactions |
|------------|------|-----|--------------|---------|--------------|
| 1 | Joshua Hall | 45 | Current | $1,313.38 | 1 |
| 2 | Mark Taylor | 47 | Current | $5,988.46 | 1 |
| 3 | Joseph Flores | 25 | Current | $8,277.88 | 1 |
| ... | ... | ... | ... | ... | ... |

---

## 🔐 Security Notes

1. **API Keys**: Change default API keys in production
2. **JWT Secret**: Update `SECRET_KEY` in `src/api/auth.py`
3. **Database**: Use proper database authentication in production
4. **CORS**: Restrict origins in production (`src/api/main.py`)

---

## 📝 License

This project is for educational purposes. Banking data is synthetic.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

---

## 📮 Contact

For questions or issues, please open a GitHub issue.

---

## 🙏 Acknowledgments

- **Google ADK** - Agent Development Kit
- **Ollama** - Local LLM runtime
- **ChromaDB** - Vector database
- **FastAPI** - Modern web framework
- **LiteLLM** - Universal LLM interface

---

**Built with ❤️ using Google ADK, MCP, and RAG**
