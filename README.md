# Vector DB Gateway

A FastAPI-based microservice that provides a secure gateway to Qdrant vector database with API key authentication, rule-based authorization, and query embedding.

## Features

- **API Key Authentication**: Secure your API with API keys
- **Rule-Based Authorization**: Control access to data based on context
- **Vector Search**: Perform semantic search using embeddings
- **Document Ingestion**: Add documents to the vector database
- **Collection Management**: View and manage Qdrant collections

## Getting Started

### Prerequisites

- Python 3.12 or higher
- PostgreSQL database
- Qdrant vector database

### Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -e .`
5. Copy `.env.example` to `.env` and update the configuration
6. Run the application: `python -m src.main`

### Creating Sample API Keys

Run the sample script to create API keys with different permissions:

```bash
python scripts/create_sample_api_keys.py
```

## API Endpoints

### Authentication

All endpoints require an API key to be provided in the `X-API-Key` header.

### Vector Search

- `POST /hr-info`: Search HR information based on context and query
- `POST /search/{collection_name}`: Search any collection based on context and query

### Collections

- `GET /collections`: List all collections
- `GET /collections/{collection_name}`: Get information about a collection

### Document Ingestion

- `POST /ingest/{collection_name}`: Ingest a document into a collection
- `POST /ingest/{collection_name}/batch`: Ingest multiple documents into a collection

## Authorization Rules

API keys can have allow and deny rules based on context. For example:

```json
{
  "allow_rules": [{"field": "context", "values": ["onboard", "offboard"]}],
  "deny_rules": [{"field": "context", "values": ["salary"]}]
}
```

This API key would allow access to onboarding and offboarding contexts, but deny access to salary context.

## Development

### Project Structure

```
vectordbgateway/
├── scripts/                # Scripts for setup and maintenance
├── src/                    # Source code
│   ├── app/                # Application code
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Database models and session
│   │   ├── qdrant/         # Qdrant client and embedding
│   │   ├── rules/          # Rule checking logic
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── security/       # Security utilities
│   │   └── services/       # Business logic services
│   └── main.py             # Application entry point
└── pyproject.toml          # Project dependencies
```

## Features

- API key authentication via PostgreSQL and bcrypt
- Fine-grained authorization with allow/deny rules stored as JSON
- Query embedding and forwarding to Qdrant vector database
- SOLID and Clean Architecture design principles
- Managed with uv package manager

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy (async, 2.0-style)
- bcrypt
- Qdrant client
- PostgreSQL
- sentence-transformers (for embedding queries)
- uv (for dependency and venv management)
- dotenv / pydantic-settings (for configs)

## Project Structure

```
src/
│
├── main.py                          # FastAPI instance
├── app/
│   ├── api/                         # FastAPI routers
│   │   └── endpoints/
│   ├── core/                        # Core settings and config
│   ├── db/                          # DB setup, models, session
│   ├── schemas/                     # Pydantic models
│   ├── services/                    # Business logic/service layer
│   ├── security/                    # Hashing, token auth
│   ├── qdrant/                      # Qdrant client abstraction
│   └── rules/                       # Logic for allow/deny filters
├── tests/
```

## Setup Instructions

### Prerequisites

- Python 3.12+
- PostgreSQL
- Qdrant vector database
- uv package manager

### Installation with uv

1. Install uv if not already installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create and activate virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
uv pip install -e .
```

4. Create a `.env` file based on `.env.example`

### Database Setup

1. Create a PostgreSQL database
2. Run migrations to create the necessary tables:

```bash
# Migration commands will be provided
```

## Usage

### Running the Server

```bash
uvicorn src.main:app --reload
```

### API Endpoints

- `POST /hr-info`: Search HR information with context-based filtering

### Example Request

```bash
curl -X POST "http://localhost:8000/hr-info" \
  -H "X-API-Key: Qk6I0gsz6ZWPPYlp5nIRnMW4IbwvAiLVfiUyPSENX7I" \
  -H "Content-Type: application/json" \
  -d '{"context": "onboard", "query": "How do we onboard a new employee?"}'
```
Qk6I0gsz6ZWPPYlp5nIRnMW4IbwvAiLVfiUyPSENX7I
### Example Response

```json
{
  "matches": [
    {
      "score": 0.91,
      "payload": {
        "context": "onboard",
        "content": "Onboarding steps after offer letter..."
      }
    }
  ]
}
```

## Security

- API keys are stored as bcrypt hashes in the database
- Keys can be restricted by expiry date and active status
- Fine-grained access control through allow/deny rules
- Deny rules take precedence over allow rules

## License

[MIT](LICENSE)