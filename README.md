# UAE Financial Health Check - FastAPI Backend

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py        # User, Session models
│   │   ├── routes.py        # Authentication endpoints
│   │   └── utils.py         # JWT, password hashing
│   ├── customers/
│   │   ├── __init__.py
│   │   ├── models.py        # Customer profile models
│   │   ├── routes.py        # Customer CRUD endpoints
│   │   └── schemas.py       # Pydantic schemas
│   ├── surveys/
│   │   ├── __init__.py
│   │   ├── models.py        # Survey, Response models
│   │   ├── routes.py        # Survey endpoints
│   │   └── schemas.py       # Survey schemas
│   └── analytics/
│       ├── __init__.py
│       ├── routes.py        # Admin dashboard endpoints
│       └── calculations.py  # Analytics calculations
├── alembic/                 # Database migrations
├── tests/                   # Test files
├── requirements.txt
└── .env.example
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
