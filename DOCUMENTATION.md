# Delta Air Lines AI Customer Assistant
# Complete Technical Architecture & Documentation
### Author: Hariharan | Senior AI Engineering Portfolio Project

---

# PAGE 1 — EXECUTIVE OVERVIEW

---

## 1.1 Project Summary

The Delta Air Lines AI Customer Assistant is a production-grade, full-stack AI application that combines:

- A **secure REST API** (FastAPI) with JWT authentication
- A **relational database** (SQLite via SQLAlchemy) for customer records
- A **vector database** (ChromaDB) for semantic policy document search
- A **Retrieval Augmented Generation (RAG)** pipeline for accurate AI answers
- An **intent classification** engine to route questions intelligently
- A **large language model** (Groq — llama-3.1-8b-instant) for natural language generation
- A **Streamlit** frontend for an interactive chat interface

The system allows Delta customers to log in securely, ask questions in natural language, and receive personalised, accurate answers — grounded in both their real account data and Delta's official policy documents.

---

## 1.2 Main Goal

To build an AI assistant that answers customer questions accurately by combining:

1. **Personal account data** (miles balance, tier, flight history) pulled from a database
2. **Policy knowledge** (baggage rules, upgrade procedures, miles expiry) retrieved from a vector store
3. **Natural language generation** to produce a friendly, personalised response

The system is designed so the AI never guesses or hallucinates policy details — it reads from the actual policy documents every time.

---

## 1.3 Why Each Technology Was Chosen

| Technology | Why Used |
|------------|----------|
| **FastAPI** | Modern, fast Python web framework. Auto-generates API docs. Native async support. |
| **SQLite** | Zero-configuration relational database. Perfect for structured customer data. |
| **SQLAlchemy** | ORM layer — write Python instead of SQL. Prevents SQL injection. |
| **JWT Auth** | Stateless token-based authentication. No server-side sessions needed. |
| **ChromaDB** | Vector database for semantic search. Finds policy content by meaning, not keywords. |
| **SentenceTransformer** | Converts text to embedding vectors. Free, runs locally. |
| **RAG** | Grounds AI answers in real documents. Eliminates hallucination. |
| **Intent Classification** | Routes each question to the right data source. Optimises cost and speed. |
| **Groq LLM** | Fast, free LLM API. OpenAI-compatible. Can be swapped for AWS Bedrock or OpenAI. |
| **Streamlit** | Rapid frontend development. Ideal for AI/ML demo applications. |

> **Note on AWS Bedrock:** The LLM provider in this project is Groq for cost reasons. The architecture is identical if using AWS Bedrock — only the `OpenAI()` client initialization changes. Bedrock would use `boto3` and the `anthropic.claude-v2` or `amazon.titan-text` model ID. Every other file stays the same.

---

## 1.4 High Level End-to-End Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER (Browser / Streamlit)                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    HTTP Request (POST/GET)
                    + JWT Token in header
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          FastAPI (main.py)                          │
│                                                                     │
│  • Receives HTTP request                                            │
│  • Looks up route table → calls correct router function             │
│  • Runs Depends() chain (auth check, DB session)                    │
└──────────┬──────────────────┬───────────────────┬───────────────────┘
           │                  │                   │
           ▼                  ▼                   ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐
    │ Auth Router  │  │ Data Routers │  │      Chat Router         │
    │ /auth/login  │  │ /miles       │  │      /chat               │
    │              │  │ /profile     │  │                          │
    │ Validates    │  │ /activity    │  │  Calls AI Engine         │
    │ email+pwd    │  │ /invoice     │  │                          │
    │ Returns JWT  │  │              │  └──────────┬───────────────┘
    └──────┬───────┘  └──────┬───────┘             │
           │                 │                      │
           ▼                 ▼                      ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐
    │   SQLite DB  │  │   SQLite DB  │  │      AI Engine           │
    │   delta.db   │  │   delta.db   │  │                          │
    │              │  │              │  │ 1. classify_intent()     │
    │ customers    │  │ customers    │  │ 2. retrieve() ChromaDB   │
    │ table        │  │ activity     │  │ 3. build_prompt()        │
    │              │  │ invoices     │  │ 4. Groq LLM call         │
    └──────────────┘  └──────────────┘  └──────────┬───────────────┘
                                                    │
                                                    ▼
                                         ┌──────────────────────────┐
                                         │    ChromaDB              │
                                         │    (when needed)         │
                                         │                          │
                                         │ 19 policy chunks         │
                                         │ Semantic vector search   │
                                         └──────────────────────────┘
```

---

## 1.5 Full System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                            PRESENTATION LAYER                              │
│                                                                            │
│   ┌──────────────────────────────────────────────────────────────────┐    │
│   │                    Streamlit (frontend/app.py)                   │    │
│   │   Login Page  →  Chat Interface  →  Sidebar (profile info)       │    │
│   └──────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │ HTTP (port 8501 → 8000)
┌────────────────────────────────────▼───────────────────────────────────────┐
│                              API GATEWAY LAYER                              │
│                                                                            │
│   ┌──────────────────────────────────────────────────────────────────┐    │
│   │              FastAPI Application (backend/main.py)               │    │
│   │   Uvicorn (ASGI server) → FastAPI app → Router dispatch          │    │
│   │                                                                  │    │
│   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐  │    │
│   │  │  /auth   │ │  /miles  │ │/activity │ │/profile  │ │/chat │  │    │
│   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────┘  │    │
│   └──────────────────────────────────────────────────────────────────┘    │
└───────────┬────────────────────────────────────────────┬───────────────────┘
            │                                            │
┌───────────▼──────────────────┐         ┌──────────────▼───────────────────┐
│       AUTH LAYER             │         │           AI ENGINE LAYER         │
│                              │         │                                   │
│  backend/auth.py             │         │  ai_engine/                       │
│  • verify_password()         │         │  • intent_classifier.py           │
│  • create_access_token()     │         │  • rag_pipeline.py                │
│  • get_current_user()        │         │  • prompt_builder.py              │
│  • oauth2_scheme             │         │  • llm_client.py                  │
│  • JWTError handling         │         │                                   │
└───────────┬──────────────────┘         └──────────────┬────────────────────┘
            │                                            │
┌───────────▼──────────────────┐         ┌──────────────▼────────────────────┐
│       DATA LAYER             │         │         VECTOR STORE LAYER         │
│                              │         │                                    │
│  SQLite (delta.db)           │         │  ChromaDB (chroma_db/)             │
│  via SQLAlchemy ORM          │         │  • 19 policy chunks                │
│                              │         │  • Embedding vectors               │
│  Tables:                     │         │  • Metadata filters                │
│  • customers                 │         │                                    │
│  • activity                  │         │  Embedding Model:                  │
│  • invoices                  │         │  all-MiniLM-L6-v2                 │
│                              │         │  (SentenceTransformer)             │
└──────────────────────────────┘         └────────────────────────────────────┘
                                                         │
                                         ┌───────────────▼────────────────────┐
                                         │          LLM PROVIDER LAYER         │
                                         │                                    │
                                         │  Groq API                          │
                                         │  Model: llama-3.1-8b-instant       │
                                         │  (Swap for AWS Bedrock or OpenAI   │
                                         │   with zero code change)           │
                                         └────────────────────────────────────┘
```

---

## 1.6 Component Interaction Diagram

```
                         ┌─────────────┐
                         │  Streamlit  │
                         │  frontend   │
                         └──────┬──────┘
                                │ requests.post/get
                                │
                         ┌──────▼──────┐
                         │   FastAPI   │◄──── uvicorn serves on port 8000
                         │   main.py   │
                         └──────┬──────┘
                                │ include_router()
                    ┌───────────┼───────────────┐
                    │           │               │
             ┌──────▼──┐  ┌────▼────┐  ┌──────▼──────┐
             │  auth   │  │  data   │  │    chat     │
             │ router  │  │ routers │  │   router    │
             └──────┬──┘  └────┬────┘  └──────┬──────┘
                    │           │               │
             ┌──────▼──┐  ┌────▼────┐  ┌──────▼──────┐
             │ backend │  │SQLAlch- │  │  AI Engine  │
             │ auth.py │  │emy ORM  │  │ llm_client  │
             └──────┬──┘  └────┬────┘  └──────┬──────┘
                    │           │               │
             ┌──────▼──┐  ┌────▼────┐    ┌─────┴──────┐
             │ SQLite  │  │ SQLite  │    │            │
             │ delta.db│  │ delta.db│  ChromaDB    Groq
             └─────────┘  └─────────┘   vector     LLM
                                         store      API
```

---

## 1.7 Request Lifecycle Summary

Every request follows this lifecycle:

```
Step 1:  Browser/Streamlit sends HTTP request to port 8000
Step 2:  Uvicorn (ASGI server) receives raw TCP bytes, builds Python request object
Step 3:  FastAPI matches URL to registered route using its route table
Step 4:  FastAPI resolves all Depends() — opens DB session, verifies JWT token
Step 5:  Router function executes with resolved dependencies as arguments
Step 6:  For /chat — AI engine runs: classify → retrieve → prompt → LLM
Step 7:  Response object is serialized to JSON by Pydantic
Step 8:  FastAPI returns HTTP response with JSON body
Step 9:  Streamlit receives JSON, displays to user
```

---

## 1.8 Technology Stack Summary

```
Layer            Technology              Version       Purpose
─────────────────────────────────────────────────────────────────
ASGI Server      Uvicorn                 0.30.0        Runs FastAPI
Web Framework    FastAPI                 0.115.0       API routing, validation
ORM              SQLAlchemy              2.0.35        Database abstraction
Database         SQLite                  built-in      Customer data storage
Auth Library     python-jose             3.3.0         JWT encode/decode
Password Hash    passlib + bcrypt        1.7.4 / 4.0.1 Secure hashing
Config           pydantic-settings       2.4.0         .env file reading
LLM Provider     Groq API                —             Natural language generation
LLM Model        llama-3.1-8b-instant   —             Chat completion
Vector DB        ChromaDB                0.5.0         Semantic document search
Embeddings       SentenceTransformer     3.0.0         Text → vector conversion
Embed Model      all-MiniLM-L6-v2       —             384-dimension embeddings
Frontend         Streamlit               1.38.0        Chat UI
HTTP Client      requests                2.32.0        Frontend → API calls
```

---

# PAGE 2 — COMPLETE PROJECT STRUCTURE

---

## 2.1 Full Folder Structure

```
delta-ai-assistant/
│
├── .env                          ← Real secrets (never commit to GitHub)
├── .env.example                  ← Template showing required variables
├── .gitignore                    ← Tells Git what to ignore
├── requirements.txt              ← Python package dependencies
├── DOCUMENTATION.md              ← This file
│
├── backend/
│   ├── __init__.py               ← Makes backend a Python package
│   ├── config.py                 ← Reads .env into Python using pydantic-settings
│   ├── database.py               ← SQLAlchemy models + seed data + DB session
│   ├── auth.py                   ← JWT creation, password hashing, token verification
│   ├── models.py                 ← Pydantic request/response schemas
│   │
│   └── routers/
│       ├── __init__.py           ← Makes routers a Python package
│       ├── auth.py               ← POST /auth/login endpoint
│       ├── miles.py              ← GET /miles/ endpoint
│       ├── activity.py           ← GET /activity/ endpoint
│       ├── profile.py            ← GET /profile/ endpoint
│       ├── invoice.py            ← GET /invoice/ endpoint
│       └── chat.py               ← POST /chat/ endpoint
│
├── ai_engine/
│   ├── __init__.py               ← Makes ai_engine a Python package
│   ├── intent_classifier.py      ← Keyword-based intent detection
│   ├── rag_pipeline.py           ← ChromaDB query and retrieval
│   ├── prompt_builder.py         ← Assembles the final prompt for LLM
│   └── llm_client.py             ← Groq API call + orchestrates entire AI flow
│
├── data/
│   └── policies/
│       ├── miles_policy.txt      ← Delta miles earning/redemption rules
│       ├── baggage_policy.txt    ← Delta baggage fees and allowances
│       └── upgrade_policy.txt    ← Delta upgrade procedures and certificates
│
├── scripts/
│   ├── __init__.py
│   └── ingest_policies.py        ← One-time script: reads .txt → chunks → ChromaDB
│
├── chroma_db/                    ← Auto-created by ingest script (vector store data)
│
├── delta.db                      ← Auto-created SQLite database file
│
└── frontend/
    └── app.py                    ← Streamlit login page + chat interface
```

---

## 2.2 File Responsibilities and Call Chain

```
main.py
  Imports → routers/auth.py, routers/miles.py, routers/activity.py,
             routers/profile.py, routers/invoice.py, routers/chat.py
  Calls   → database.init_db() on startup

config.py
  Imports → pydantic_settings
  Called by → database.py, auth.py, llm_client.py, rag_pipeline.py
  Role    → single source of all configuration values

database.py
  Imports → config.py, passlib, sqlalchemy
  Called by → all routers (via get_db()), main.py (init_db())
  Role    → defines tables, provides DB session, seeds initial data

auth.py (backend)
  Imports → config.py, database.py, passlib, jose
  Called by → routers/auth.py (authenticate_user, create_access_token)
              all protected routers (get_current_user via Depends)
  Role    → password verification, JWT creation, JWT decoding

models.py
  Imports → pydantic
  Called by → all routers (as request/response type annotations)
  Role    → defines exact shape of API inputs and outputs

routers/auth.py
  Imports → backend/auth.py, database.py, models.py
  Called by → FastAPI (when POST /auth/login is hit)

routers/chat.py
  Imports → backend/auth.py, database.py, models.py, ai_engine/llm_client.py
  Called by → FastAPI (when POST /chat/ is hit)

ai_engine/llm_client.py
  Imports → config.py, intent_classifier.py, rag_pipeline.py, prompt_builder.py
  Called by → routers/chat.py
  Role    → orchestrates the full AI pipeline

ai_engine/intent_classifier.py
  Called by → llm_client.py
  Role    → detects intent from user message

ai_engine/rag_pipeline.py
  Imports → chromadb, sentence-transformers
  Called by → llm_client.py
  Role    → searches ChromaDB, returns relevant policy chunks

ai_engine/prompt_builder.py
  Called by → llm_client.py
  Role    → assembles system + user messages for the LLM

scripts/ingest_policies.py
  Imports → chromadb, sentence-transformers
  Run once → reads .txt files → chunks → embeds → stores in ChromaDB
```

---

# PAGE 3 — APPLICATION STARTUP FLOW

---

## 3.1 What Happens When You Run `uvicorn backend.main:app --reload`

This single command triggers a precise sequence of events:

### Step 1 — Uvicorn Starts

```
uvicorn backend.main:app --reload

↓ Uvicorn parses this as:
  module  = "backend.main"    (file: backend/main.py)
  object  = "app"             (the FastAPI() instance inside that file)
  --reload = watch for file changes, restart on save
```

Uvicorn is an ASGI server. ASGI stands for Asynchronous Server Gateway Interface. Think of it like a waiter in a restaurant — it stands at the door, accepts customer requests, and passes them to the kitchen (FastAPI).

### Step 2 — Python Imports `backend/main.py`

```python
# Python executes these imports at startup
from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.database import init_db
from backend.routers import auth, miles, activity, profile, invoice, chat
```

Each import triggers its own chain of imports:
- `backend.database` → imports `config.py` → reads `.env` file
- `backend.routers.auth` → imports `backend.auth` → imports `config.py`, `database.py`

### Step 3 — `.env` File is Read by pydantic-settings

```python
# backend/config.py
class Settings(BaseSettings):
    openai_api_key: str
    openai_base_url: str
    model_name: str
    ...
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()   # ← THIS LINE reads .env immediately
```

The moment `settings = Settings()` executes:
1. pydantic-settings opens `.env` file
2. Reads each line: `OPENAI_API_KEY=gsk_abc123...`
3. Maps to the Python attribute `settings.openai_api_key = "gsk_abc123..."`
4. Validates types — if `JWT_EXPIRY_MINUTES=abc`, it raises a validation error immediately

### Step 4 — FastAPI App Object is Created

```python
app = FastAPI(
    title="Delta Air Lines AI Assistant",
    description="Customer assistant API with JWT auth and AI chat",
    version="1.0.0",
    lifespan=lifespan,
)
```

This creates an empty FastAPI application object. No routes exist yet. Think of it like building an empty building before adding floors.

### Step 5 — Routes are Registered via `include_router()`

```python
app.include_router(auth.router,     prefix="/auth",     tags=["Auth"])
app.include_router(miles.router,    prefix="/miles",    tags=["Miles"])
app.include_router(activity.router, prefix="/activity", tags=["Activity"])
app.include_router(profile.router,  prefix="/profile",  tags=["Profile"])
app.include_router(invoice.router,  prefix="/invoice",  tags=["Invoice"])
app.include_router(chat.router,     prefix="/chat",     tags=["Chat"])
```

**How `include_router()` works internally:**

Each router file (e.g., `routers/miles.py`) defines routes like:

```python
# routers/miles.py
router = APIRouter()

@router.get("/", response_model=MilesResponse)
def get_miles(...):
    ...
```

The `@router.get("/")` decorator registers this function against the path `"/"` inside that router.

When `app.include_router(miles.router, prefix="/miles")`, FastAPI:
1. Takes all routes registered in `miles.router`
2. Prepends `/miles` to each path
3. `"/"` becomes `"/miles/"`
4. Adds these to the application's global route table

**The final route table looks like:**

```
METHOD  PATH              FUNCTION
──────────────────────────────────────────────────────
GET     /                 root()
POST    /auth/login       login()
GET     /miles/           get_miles()
GET     /activity/        get_activity()
GET     /profile/         get_profile()
GET     /invoice/         get_invoices()
POST    /chat/            chat()
```

### Step 6 — Lifespan Event Runs

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()    # ← runs ONCE when server starts
    yield        # ← server now handles requests
```

`init_db()` runs `database.init_db()`:
1. `Base.metadata.create_all(bind=engine)` — creates tables in `delta.db` if they don't exist
2. `seed_data(db)` — checks if data exists, inserts 3 customers + records if empty

### Step 7 — Server is Ready

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

The server now sits in an event loop, waiting for incoming HTTP requests.

---

# PAGE 4 — AUTHENTICATION FLOW

---

## 4.1 Overview

Authentication has two phases:
1. **Login** — exchange credentials for a JWT token (done once)
2. **Verification** — validate the token on every protected request (automatic)

---

## 4.2 Phase 1: Login — POST /auth/login

### The HTTP Request

```
POST http://localhost:8000/auth/login
Content-Type: application/x-www-form-urlencoded

username=hari@delta.com&password=hari123
```

Note: The field is named `username` (not `email`) because `OAuth2PasswordRequestForm` is a standard that uses `username`. We pass the email as the username value.

### Step 1 — FastAPI routes to `routers/auth.py → login()`

```python
@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
```

FastAPI sees two `Depends()` calls and resolves them before calling `login()`:

**Depends(OAuth2PasswordRequestForm):**
- Reads the raw request body
- Parses `username=hari@delta.com&password=hari123`
- Creates `form_data` object with:
  - `form_data.username = "hari@delta.com"`
  - `form_data.password = "hari123"`

**Depends(get_db):**
```python
def get_db():
    db = SessionLocal()   # opens connection to delta.db
    try:
        yield db          # gives the session to the function
    finally:
        db.close()        # closes connection after function returns
```
- Opens a SQLAlchemy session (connection to delta.db)
- Passes it as `db` argument
- Closes it automatically after `login()` returns

### Step 2 — `authenticate_user()` is called

```python
customer = authenticate_user(form_data.username, form_data.password, db)
# authenticate_user("hari@delta.com", "hari123", <db session>)
```

Inside `authenticate_user()` (in `backend/auth.py`):

```python
def authenticate_user(email, password, db):
    customer = db.query(Customer).filter(Customer.email == email).first()
```

SQLAlchemy translates this to:
```sql
SELECT id, name, email, password_hash, tier, miles_balance, member_since
FROM customers
WHERE email = 'hari@delta.com'
LIMIT 1;
```

**Result — a Customer object:**
```
Customer {
    id            = 1
    name          = "Hariharan"
    email         = "hari@delta.com"
    password_hash = "$2b$12$XyZ9abcVeryLongHashString..."
    tier          = "Gold"
    miles_balance = 45230.0
    member_since  = 2019-03-15
}
```

### Step 3 — `verify_password()` is called

```python
if not verify_password(password, customer.password_hash):
    return None
```

Inside `verify_password()`:
```python
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
```

**What bcrypt does internally:**

When we originally seeded the database:
```python
pwd_context.hash("hari123")
→ "$2b$12$XyZ9abc..."
```

The hash contains:
- `$2b$` — bcrypt algorithm identifier
- `$12$` — cost factor (2^12 = 4096 iterations)
- `XyZ9abc...` — salt (random bytes) + actual hash

At verification time:
1. bcrypt extracts the salt from the stored hash
2. Applies the same algorithm with the same salt to `"hari123"`
3. Compares the result with the stored hash
4. Returns `True` if they match

This is why hashing is one-way but verification works — we never reverse the hash. We re-hash with the same salt.

### Step 4 — `create_access_token()` is called

```python
token = create_access_token(data={"sub": customer.email})
# create_access_token({"sub": "hari@delta.com"})
```

Inside `create_access_token()`:
```python
def create_access_token(data: dict) -> str:
    to_encode = {"sub": "hari@delta.com"}
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": 1746789600})   # Unix timestamp 60 mins from now
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
```

**JWT internal structure:**

The token has 3 parts separated by dots:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.
eyJzdWIiOiJoYXJpQGRlbHRhLmNvbSIsImV4cCI6MTc0Njc4OTYwMH0
.
xK9abcSomeSignatureHere
```

Decoded:
```json
Header:  {"alg": "HS256", "typ": "JWT"}
Payload: {"sub": "hari@delta.com", "exp": 1746789600}
Signature: HMACSHA256(base64(header) + "." + base64(payload), SECRET_KEY)
```

The signature is what makes tokens tamper-proof. If anyone changes the payload, the signature breaks.

### Step 5 — Response is returned

```python
return TokenResponse(access_token=token)
```

HTTP Response:
```json
HTTP 200 OK
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

---

## 4.3 Phase 2: Verification — Protected Routes

### How the token travels

Streamlit stores the token and attaches it to every subsequent request:

```python
headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
```

### How `Depends(get_current_user)` works

Every protected route declares:
```python
def get_miles(current_user: Customer = Depends(get_current_user)):
```

FastAPI automatically calls `get_current_user()` before `get_miles()`:

```python
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Customer:
```

`oauth2_scheme` is an instance of `OAuth2PasswordBearer(tokenUrl="/auth/login")`.
It automatically reads the `Authorization` header and extracts the token string (after "Bearer ").

**Token decoding:**
```python
payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
# payload = {"sub": "hari@delta.com", "exp": 1746789600}

email = payload.get("sub")
# email = "hari@delta.com"
```

If the token is expired → `JWTError` is raised → 401 Unauthorized
If the token signature is invalid → `JWTError` is raised → 401 Unauthorized

**Customer lookup:**
```python
customer = db.query(Customer).filter(Customer.email == email).first()
# Returns full Customer object for "hari@delta.com"
```

Returns the Customer object to the calling route function.

### Public vs Protected APIs

```
PUBLIC (no token required):
  POST /auth/login        ← no Depends(get_current_user)
  GET  /                  ← health check

PROTECTED (token required):
  GET  /miles/            ← Depends(get_current_user)
  GET  /activity/         ← Depends(get_current_user)
  GET  /profile/          ← Depends(get_current_user)
  GET  /invoice/          ← Depends(get_current_user)
  POST /chat/             ← Depends(get_current_user)
```

---

# PAGE 5 — SQLITE FLOW

---

## 5.1 When SQLite is Used

SQLite is used in two scenarios:

1. **Authentication** — finding a customer by email to verify credentials
2. **Data retrieval** — fetching personal account data for API responses and AI context

---

## 5.2 SQLAlchemy ORM — How Python Becomes SQL

### Table Definition (database.py)

```python
class Customer(Base):
    __tablename__ = "customers"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    tier          = Column(String, default="Silver")
    miles_balance = Column(Float, default=0.0)
    member_since  = Column(Date, default=datetime.date.today)
```

SQLAlchemy creates this actual SQL table:
```sql
CREATE TABLE customers (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          VARCHAR NOT NULL,
    email         VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    tier          VARCHAR DEFAULT 'Silver',
    miles_balance REAL DEFAULT 0.0,
    member_since  DATE
);
```

### Actual Database Records After Seeding

```
id  name            email              tier      miles_balance  member_since
──  ──────────────  ─────────────────  ────────  ─────────────  ────────────
1   Hariharan      hari@delta.com     Gold      45230.0        2019-03-15
2   Priya Sharma    priya@delta.com    Platinum  120500.0       2017-07-22
3   James Wilson    james@delta.com    Silver    8750.0         2022-01-10
```

### ORM Query Flow

```python
# Python code
customer = db.query(Customer).filter(Customer.email == "hari@delta.com").first()

# SQLAlchemy translates to:
SELECT * FROM customers WHERE email = 'hari@delta.com' LIMIT 1;

# Returns a Python object:
customer.id            → 1
customer.name          → "Hariharan"
customer.email         → "hari@delta.com"
customer.password_hash → "$2b$12$XyZ9abc..."
customer.tier          → "Gold"
customer.miles_balance → 45230.0
customer.member_since  → datetime.date(2019, 3, 15)
```

### Activity Table Records

```
id  customer_id  flight_number  origin  destination  flight_date  miles_earned
──  ───────────  ─────────────  ──────  ───────────  ───────────  ────────────
1   1            DL 204         JFK     LAX          2024-11-05   2475.0
2   1            DL 408         LAX     ATL          2024-12-18   1947.0
3   1            DL 512         ATL     ORD          2025-01-30   606.0
4   2            DL 100         JFK     LHR          2024-10-12   3459.0
5   2            DL 302         LHR     CDG          2024-10-14   215.0
6   3            DL 720         BOS     MIA          2025-02-20   1258.0
```

---

# PAGE 6 — INGESTION FLOW

---

## 6.1 What is Ingestion?

Ingestion is a **one-time setup process** that reads the raw policy text files, splits them into chunks, converts each chunk to embedding vectors, and stores everything in ChromaDB.

Think of it like building the index at the back of a book. You do it once, and then searching is fast forever after.

---

## 6.2 Step-by-Step Execution of `ingest_policies.py`

### Step 1 — `if __name__ == "__main__": ingest()` triggers

```python
if __name__ == "__main__":
    ingest()
```

When you run `python scripts/ingest_policies.py`, Python sets `__name__ = "__main__"` for this file only. This condition is True, so `ingest()` is called.

### Step 2 — Embedding function is created

```python
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
```

This loads the `all-MiniLM-L6-v2` model from HuggingFace (downloaded once, cached locally). This model:
- Takes a string of text as input
- Returns a list of 384 floating point numbers (the embedding vector)
- Similar texts produce similar vectors

### Step 3 — ChromaDB client is created

```python
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(
    name="delta_policies",
    embedding_function=embedding_fn,
)
```

`PersistentClient` means data is saved to disk at `chroma_db/`. If the server restarts, the data survives.

`get_or_create_collection` — creates a named collection called "delta_policies" or retrieves it if it already exists. Think of a collection like a table in a regular database.

### Step 4 — For loop iterates over policy files

```python
POLICY_FILES = {
    "miles_policy":   "miles_policy.txt",
    "baggage_policy": "baggage_policy.txt",
    "upgrade_policy": "upgrade_policy.txt",
}

for policy_name, filename in POLICY_FILES.items():
    text   = read_policy(filename)
    chunks = chunk_text(text)
```

**Iteration 1:** policy_name="miles_policy", filename="miles_policy.txt"
**Iteration 2:** policy_name="baggage_policy", filename="baggage_policy.txt"
**Iteration 3:** policy_name="upgrade_policy", filename="upgrade_policy.txt"

### Step 5 — `chunk_text()` splits the document

```python
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start  = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]
```

**Runtime trace with miles_policy.txt (2847 characters):**

```
Iteration 1: start=0,    end=500,  chunk = "DELTA AIR LINES - SKYMILES PROGRAM POLICY\n\nEARNING MILES\nDelta SkyMiles..."
Iteration 2: start=450,  end=950,  chunk = "...Gold Medallion members earn 8 miles per dollar spent on Delta flights..."
Iteration 3: start=900,  end=1400, chunk = "...Miles are also earned on partner airlines..."
Iteration 4: start=1350, end=1850, chunk = "...REDEEMING MILES\nMiles can be redeemed for award flights..."
Iteration 5: start=1800, end=2300, chunk = "...Award flight redemptions start at 5,000 miles..."
Iteration 6: start=2250, end=2750, chunk = "...MEDALLION STATUS REQUIREMENTS\nSilver Medallion: 25,000..."

Result: 6 chunks from miles_policy.txt
```

The **50-character overlap** means each chunk shares the last 50 characters of the previous chunk. This ensures sentences that fall at chunk boundaries are still findable.

### Step 6 — IDs and metadata are generated

```python
ids       = [f"{policy_name}_chunk_{i}" for i in range(len(chunks))]
metadatas = [{"source": policy_name, "chunk_index": i} for i in range(len(chunks))]
```

For miles_policy with 6 chunks:
```
ids = [
    "miles_policy_chunk_0",
    "miles_policy_chunk_1",
    "miles_policy_chunk_2",
    "miles_policy_chunk_3",
    "miles_policy_chunk_4",
    "miles_policy_chunk_5",
]

metadatas = [
    {"source": "miles_policy", "chunk_index": 0},
    {"source": "miles_policy", "chunk_index": 1},
    ...
    {"source": "miles_policy", "chunk_index": 5},
]
```

### Step 7 — `collection.upsert()` stores everything

```python
collection.upsert(
    ids=ids,
    documents=chunks,
    metadatas=metadatas,
)
```

For each document (chunk), ChromaDB:
1. Calls `embedding_fn(chunk)` → runs the text through `all-MiniLM-L6-v2` → gets 384 numbers
2. Stores the chunk text, its embedding vector, and its metadata
3. Builds an index for fast nearest-neighbour search

**Final state of ChromaDB after ingestion:**

```
Collection: "delta_policies" — 19 total documents

ID                        Source          Text (first 60 chars)            Vector
────────────────────────  ──────────────  ───────────────────────────────  ───────────────
miles_policy_chunk_0      miles_policy    "DELTA AIR LINES - SKYMILES..."  [0.23, 0.87...]
miles_policy_chunk_1      miles_policy    "...Gold members earn 8 miles"   [0.21, 0.85...]
...
baggage_policy_chunk_0    baggage_policy  "DELTA AIR LINES - BAGGAGE..."   [0.44, 0.12...]
baggage_policy_chunk_1    baggage_policy  "Each passenger is allowed..."   [0.46, 0.11...]
...
upgrade_policy_chunk_0    upgrade_policy  "DELTA AIR LINES - UPGRADE..."   [0.67, 0.33...]
```

---

# PAGE 7 — CHROMADB INTERNAL FLOW

---

## 7.1 What ChromaDB Stores Internally

For each document, ChromaDB stores 4 things:

```
1. ID          → "baggage_policy_chunk_1"         (unique string identifier)
2. Document    → "Each passenger is allowed one carry-on bag..."  (original text)
3. Embedding   → [0.44, 0.12, 0.76, 0.03, ...]   (384 numbers)
4. Metadata    → {"source": "baggage_policy", "chunk_index": 1}
```

The **embedding** is the mathematical representation of the text's meaning. Similar sentences produce similar embeddings (similar number patterns).

---

## 7.2 How Vector Search Works

When a user asks: "What are the fees for overweight luggage?"

```
Step 1: Query text → embedding
"What are the fees for overweight luggage?"
→ [0.45, 0.11, 0.78, 0.02, ...]   (384 numbers)

Step 2: Compare with stored embeddings
────────────────────────────────────────────────────────────────
Chunk                              Similarity Score
────────────────────────────────────────────────────────────────
"Overweight bags (51-70 lbs): $100 fee"    →  0.94  ← HIGHEST
"Gold members first bag free"              →  0.43
"Upgrade certificates expire Jan 31"       →  0.11
────────────────────────────────────────────────────────────────

Step 3: Return top 3 most similar chunks
```

**Why vector search is fast:**

ChromaDB uses a technique called HNSW (Hierarchical Navigable Small World) indexing. Instead of comparing the query vector with every single stored vector (which would be slow), it builds a graph structure that allows it to jump to the approximate nearest neighbours in milliseconds.

---

## 7.3 Metadata Filtering

Our `retrieve()` function adds a metadata filter:

```python
results = collection.query(
    query_texts=[query],
    n_results=3,
    where={"source": "baggage_policy"},   # ← filter
)
```

This tells ChromaDB: "Only search within the 6 chunks that have `source=baggage_policy`."

Without this filter, ChromaDB would search all 19 chunks and might return upgrade information when the user asked about baggage. The metadata filter is a performance optimization AND an accuracy improvement.

---

# PAGE 8 — INTENT CLASSIFICATION FLOW

---

## 8.1 Why Intent Classification Exists

Without intent classification, every question would go to ChromaDB. This creates two problems:

**Problem 1 — Accuracy:**
"What is my miles balance?" → ChromaDB would search policy docs → returns miles policy rules → not the user's actual balance

**Problem 2 — Performance:**
Every question hitting ChromaDB means an embedding model call on every request. For account questions, this is wasted computation.

Intent classification solves both by routing questions to the right data source before any retrieval happens.

---

## 8.2 How `classify_intent()` Works

```python
INTENT_KEYWORDS = {
    "miles_policy": ["miles expire", "earn miles", "redeem miles", "skymiles"...],
    "baggage":      ["baggage", "bag", "luggage", "carry on", "checked bag"...],
    "upgrade":      ["upgrade", "first class", "better seat", "delta one"...],
    "account":      ["my miles", "my balance", "my account", "my profile"...],
}

def classify_intent(message: str) -> str:
    message_lower = message.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                return intent
    return "general"
```

**Runtime trace — "What are the baggage fees for Gold members?"**

```
message_lower = "what are the baggage fees for gold members?"

Check "miles_policy" keywords:
  "miles expire" in message? NO
  "earn miles" in message? NO
  "redeem miles" in message? NO
  ... (all NO)

Check "baggage" keywords:
  "baggage" in message? YES ← MATCH FOUND
  return "baggage"
```

**Runtime trace — "What is my miles balance?"**

```
message_lower = "what is my miles balance?"

Check "miles_policy" keywords:
  "miles expire" in message? NO
  "earn miles" in message? NO
  ...

Check "baggage" keywords:
  "baggage" in message? NO
  ...

Check "upgrade" keywords:
  "upgrade" in message? NO
  ...

Check "account" keywords:
  "my miles" in message? YES ← MATCH FOUND
  return "account"
```

---

## 8.3 Routing Decision Diagram

```
User Question
      │
      ▼
classify_intent()
      │
      ├─── "miles_policy" ──► ChromaDB (search miles_policy chunks)
      │                       + customer context from SQLite
      │                       → Groq LLM
      │
      ├─── "baggage"      ──► ChromaDB (search baggage_policy chunks)
      │                       + customer context from SQLite
      │                       → Groq LLM
      │
      ├─── "upgrade"      ──► ChromaDB (search upgrade_policy chunks)
      │                       + customer context from SQLite
      │                       → Groq LLM
      │
      ├─── "account"      ──► Skip ChromaDB
      │                       customer context from SQLite only
      │                       → Groq LLM
      │
      └─── "general"      ──► GUARDRAIL — return fixed message
                              Groq LLM never called
```

---

# PAGE 9 — RAG FLOW

---

## 9.1 What is RAG and Why it Exists

**Without RAG:**
```
User: "How many miles do I need for an upgrade?"
LLM:  "I believe it's around 25,000 miles..."  ← GUESSED, WRONG
```

LLMs are trained on internet data. They may have seen outdated or incorrect Delta policy information. They cannot look up current policies.

**With RAG:**
```
User: "How many miles do I need for an upgrade?"
RAG:  → fetches from upgrade_policy.txt chunk:
         "Domestic upgrades using miles start at 5,000 miles each way."
LLM:  "Domestic upgrades using miles start at 5,000 miles each way,
        and since you have 45,230 miles, you can upgrade 9 domestic
        flights!"  ← ACCURATE, from actual policy document
```

RAG grounds the AI's answer in verified source documents.

---

## 9.2 The Complete RAG Lifecycle

```
Step 1: User question arrives
────────────────────────────
"What are the baggage fees?"

Step 2: intent_classifier.py
─────────────────────────────
classify_intent("What are the baggage fees?")
→ "baggage"

Step 3: rag_pipeline.py — retrieve()
──────────────────────────────────────
retrieve("What are the baggage fees?", "baggage", n_results=3)

  3a. Load ChromaDB collection
  3b. Convert query to embedding:
      "What are the baggage fees?" → [0.44, 0.12, 0.78, ...]

  3c. Search with metadata filter {"source": "baggage_policy"}
  3d. ChromaDB computes similarity with 6 baggage chunks
  3e. Returns top 3 most similar chunks:

  Chunk 1: "First checked bag fee for domestic flights: $30 per bag.
            Second checked bag fee for domestic flights: $40 per bag..."

  Chunk 2: "Silver Medallion members: first checked bag free.
            Gold Medallion members: first and second checked bags free..."

  Chunk 3: "Carry-on bag maximum dimensions are 22 x 14 x 9 inches..."

  3f. Join chunks with "\n\n" separator
  3g. Return as single string

Step 4: prompt_builder.py
──────────────────────────
build_prompt(
    user_message = "What are the baggage fees?",
    intent       = "baggage",
    customer_context = {
        "name": "Hariharan",
        "tier": "Gold",
        "miles_balance": 45230,
        "member_since": "2019-03-15"
    },
    rag_context = "<3 retrieved chunks joined>"
)

Builds this message list:
[
  {
    "role": "system",
    "content": "You are a helpful and friendly Delta Air Lines customer
                assistant. Always be polite, concise, and accurate.
                Always address the customer by their first name."
  },
  {
    "role": "user",
    "content": "Customer Information:
                - Name: Hariharan
                - Tier: Gold
                - Miles Balance: 45,230 miles
                - Member Since: 2019-03-15

                Relevant Delta Policy Information:
                First checked bag fee for domestic flights: $30 per bag.
                Gold Medallion members: first and second checked bags free...
                [more chunks]

                Customer Question: What are the baggage fees?"
  }
]

Step 5: llm_client.py — Groq API call
───────────────────────────────────────
client.chat.completions.create(
    model    = "llama-3.1-8b-instant",
    messages = [system_message, user_message],
    max_tokens  = 512,
    temperature = 0.7,
)

Step 6: LLM generates response
────────────────────────────────
"Good morning, Hari. As a Gold Medallion member, you're eligible for
 free first and second checked bags on domestic flights. For a third bag,
 the fee is $150 each way. On international flights, your first bag is
 also free. Oversized bags incur an additional $200 fee."

Step 7: Response returned
──────────────────────────
{
    "reply":    "Good morning, Hari...",
    "intent":   "baggage",
    "used_rag": True
}
```

---

# PAGE 10 — END-TO-END RUNTIME TRACE

---

## Complete Trace: "How much baggage is allowed for business class?"

### The HTTP Request

```
POST http://localhost:8000/chat/
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  Content-Type: application/json

Body:
  {"message": "How much baggage is allowed for business class?"}
```

### Trace Step 1 — Uvicorn receives raw bytes

```
TCP bytes arrive on port 8000
Uvicorn parses HTTP headers + body
Creates ASGI scope dict with method="POST", path="/chat/"
Passes to FastAPI
```

### Trace Step 2 — FastAPI matches route

```
Route table lookup: POST "/chat/" → chat() function in routers/chat.py
FastAPI resolves dependencies:
  Depends(get_current_user) → must run first
  Depends(get_db)           → must run first
```

### Trace Step 3 — Depends chain resolves

```
oauth2_scheme reads Authorization header:
  "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  extracts token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

get_db() opens SQLite connection:
  db = SessionLocal()   ← delta.db connection open

get_current_user(token, db) runs:
  payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
  payload = {"sub": "hari@delta.com", "exp": 1746789600}
  email   = "hari@delta.com"
  customer = db.query(Customer).filter(Customer.email == "hari@delta.com").first()
  customer = Customer(id=1, name="Hariharan", tier="Gold", miles_balance=45230.0...)
  return customer
```

### Trace Step 4 — `chat()` function runs

```python
# routers/chat.py
def chat(request, current_user, db):
    customer_context = {
        "name":          "Hariharan",
        "tier":          "Gold",
        "miles_balance": 45230.0,
        "member_since":  "2019-03-15",
    }
    result = get_ai_response(
        "How much baggage is allowed for business class?",
        customer_context
    )
```

### Trace Step 5 — `get_ai_response()` in `llm_client.py`

```python
intent = classify_intent("How much baggage is allowed for business class?")
```

**Inside classify_intent():**
```
message_lower = "how much baggage is allowed for business class?"
Check miles_policy → no match
Check baggage → "baggage" found ← MATCH
return "baggage"
```

```python
intent = "baggage"
intent in INTENTS_NEEDING_RAG?  → YES {"miles_policy", "baggage", "upgrade"}
```

### Trace Step 6 — `retrieve()` in `rag_pipeline.py`

```python
rag_context = retrieve(
    "How much baggage is allowed for business class?",
    "baggage",
    n_results=3
)
```

**Inside retrieve():**
```python
collection = _get_collection()   # ChromaDB loaded

results = collection.query(
    query_texts=["How much baggage is allowed for business class?"],
    n_results=3,
    where={"source": "baggage_policy"},
)
```

ChromaDB:
1. Converts query to embedding vector: `[0.41, 0.15, 0.74, ...]`
2. Searches 6 baggage_policy chunks
3. Computes cosine similarity with each chunk's embedding
4. Returns top 3:

```
Retrieved chunks:
─────────────────────────────────────────────────────
Chunk 1 (similarity 0.89):
"First checked bag fee for domestic flights: $30 per bag.
 Second checked bag fee for domestic flights: $40 per bag.
 Third and additional checked bags: $150 per bag each way."

Chunk 2 (similarity 0.84):
"Silver Medallion members: first checked bag free on domestic.
 Gold Medallion members: first and second checked bags free.
 Platinum Medallion members: first and second checked bags free."

Chunk 3 (similarity 0.71):
"Carry-on bag maximum dimensions are 22 x 14 x 9 inches.
 Personal item maximum dimensions are 18 x 14 x 8 inches."
─────────────────────────────────────────────────────

rag_context = chunk1 + "\n\n" + chunk2 + "\n\n" + chunk3
```

### Trace Step 7 — `build_prompt()` assembles messages

```python
messages = build_prompt(
    user_message     = "How much baggage is allowed for business class?",
    intent           = "baggage",
    customer_context = {"name": "Hariharan", "tier": "Gold", "miles_balance": 45230},
    rag_context      = "<joined chunks>"
)
```

**Final messages list sent to Groq:**
```json
[
  {
    "role": "system",
    "content": "You are a helpful and friendly Delta Air Lines customer assistant..."
  },
  {
    "role": "user",
    "content": "Customer Information:\n- Name: Hariharan\n- Tier: Gold\n- Miles Balance: 45,230 miles\n- Member Since: 2019-03-15\n\nRelevant Delta Policy Information:\nFirst checked bag fee for domestic flights: $30 per bag...\n[chunk2]\n[chunk3]\n\nCustomer Question: How much baggage is allowed for business class?"
  }
]
```

### Trace Step 8 — Groq API call

```python
response = client.chat.completions.create(
    model       = "llama-3.1-8b-instant",
    messages    = messages,
    max_tokens  = 512,
    temperature = 0.7,
)

reply = response.choices[0].message.content.strip()
```

**Groq returns:**
```
"Hi Hari! As a Gold Medallion member, you receive free first and second
 checked bags on domestic flights. For international flights, your first
 bag is also free. A third bag costs $150 each way. Carry-on bags must
 fit within 22 x 14 x 9 inches. Is there anything else I can help you with?"
```

### Trace Step 9 — Response travels back

```
llm_client.py returns:
  {"reply": "Hi Hari!...", "intent": "baggage", "used_rag": True}

chat() returns:
  ChatResponse(reply="Hi Hari!...", intent="baggage", used_rag=True)

FastAPI serializes to JSON:
  {"reply": "Hi Hari!...", "intent": "baggage", "used_rag": true}

HTTP 200 Response sent to Streamlit

Streamlit displays:
  st.chat_message("assistant") → "Hi Hari!..."
```

**Total time:** ~800ms–2000ms (most time is the Groq API call)

---

# PAGE 11 — MEMORY + OBJECT FLOW

---

## 11.1 What Objects Exist in Memory During a Chat Request

```
Object            Type              Contents
──────────────────────────────────────────────────────────────────────
form_data         OAuth2Password-   .username = "hari@delta.com"
                  RequestForm       .password = "hari123"

token (string)    str               "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

jwt_payload       dict              {"sub": "hari@delta.com", "exp": 1746789600}

customer          Customer          .id=1, .name="Hariharan", .tier="Gold"
                  (SQLAlchemy obj)  .miles_balance=45230.0, .email="hari@delta.com"

customer_context  dict              {"name": "Hariharan", "tier": "Gold",
                                     "miles_balance": 45230, "member_since": "2019-03-15"}

intent            str               "baggage"

rag_context       str               "First checked bag fee: $30...\n\nGold members..."

messages          list[dict]        [{"role": "system", "content": "..."},
                                     {"role": "user", "content": "..."}]

response          ChatCompletion    .choices[0].message.content = "Hi Hari!..."

reply             str               "Hi Hari! As a Gold Medallion member..."
```

---

## 11.2 ChromaDB Collection Object in Memory

```
collection object:
  .name       = "delta_policies"
  .count()    = 19

When queried, results object:
  results = {
      "ids":       [["baggage_policy_chunk_1", "baggage_policy_chunk_2", ...]],
      "documents": [["First checked bag fee...", "Gold members first bag...", ...]],
      "metadatas": [[{"source": "baggage_policy", "chunk_index": 1}, ...]],
      "distances": [[0.11, 0.16, 0.29]],   # lower = more similar
  }

documents = results["documents"][0]   # first query's results
# ["First checked bag fee...", "Gold members first bag...", "Carry-on 22x14x9..."]
```

---

## 11.3 JWT Token Anatomy

```
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJpQGRlbHRhLmNvbSIsImV4cCI6MTc0Njc4OTYwMH0.xK9abc

Part 1 (Header — base64 decoded):
  {"alg": "HS256", "typ": "JWT"}

Part 2 (Payload — base64 decoded):
  {"sub": "hari@delta.com", "exp": 1746789600}
  "sub" = subject = who this token is for
  "exp" = Unix timestamp when token expires

Part 3 (Signature):
  HMACSHA256(
      base64url(header) + "." + base64url(payload),
      SECRET_KEY
  )
  = "xK9abc..."
  Cannot be faked without SECRET_KEY
```

---

# PAGE 12 — INTERVIEW EXPLANATION MODE

---

## 12.1 How to Explain This Project Professionally

### 30-Second Elevator Pitch

"I built a production-grade AI customer service assistant for Delta Air Lines. It uses FastAPI as the backend with JWT authentication, SQLite for customer data, and a RAG pipeline using ChromaDB and a sentence transformer for semantic policy retrieval. The AI generates personalised answers by combining real account data with relevant policy documents, eliminating hallucination. The frontend is Streamlit."

---

### Architecture Explanation (2 minutes)

"The system has 5 layers. The presentation layer is Streamlit — a Python web framework for rapid UI development. The API gateway is FastAPI running on Uvicorn, with 6 endpoints protected by JWT authentication. The auth layer uses bcrypt for password hashing and python-jose for JWT creation and validation.

For the AI, we have a conditional RAG pipeline. An intent classifier first routes the question — if it's about the user's account, we skip the vector database and answer purely from the SQLite record. If it's a policy question, we search ChromaDB using semantic similarity, retrieve the top 3 relevant chunks, inject them into the prompt alongside the customer's account data, and send the enriched prompt to the LLM. The LLM then generates a personalised, grounded answer."

---

## 12.2 Production Design Decisions — Why We Made These Choices

| Decision | Why |
|----------|-----|
| SQLite over PostgreSQL | Simplicity for portfolio. In production, swap for PostgreSQL with connection pooling |
| bcrypt for passwords | Industry standard. Work factor of 12 makes brute force impractical |
| JWT over sessions | Stateless — scales horizontally without shared session storage |
| Sentence-Transformers locally | Free, no API calls for embeddings. In production, use OpenAI ada-002 or AWS Bedrock Titan |
| Metadata filtering in ChromaDB | Avoids cross-contamination between policy types, improves speed |
| Overlap in chunking | Prevents information loss at chunk boundaries |
| Conditional RAG | Avoids unnecessary embedding calls for account questions — cost and latency savings |
| Guardrails before LLM | Blocks off-topic questions without spending any API credits |
| Temperature 0.7 | Balanced between deterministic (0) and creative (1) for customer service |

---

## 12.3 Scalability Improvements for Production

```
Current (Portfolio)          Production Grade
────────────────────         ─────────────────────────────────────────────
SQLite                   →   PostgreSQL with connection pooling (asyncpg)
Local ChromaDB           →   ChromaDB Cloud or Pinecone or Weaviate
Single server            →   Kubernetes with horizontal pod autoscaling
No caching               →   Redis cache for repeated questions
Groq free tier           →   AWS Bedrock (Claude/Titan) for enterprise SLA
No logging               →   Structured logging → CloudWatch / Datadog
No rate limiting         →   API Gateway with rate limiting per user
Single model             →   A/B testing across multiple models
Keyword intent           →   Fine-tuned intent classifier or LLM-based classification
```

---

## 12.4 AWS Deployment Architecture

```
Internet
    │
    ▼
AWS Route53 (DNS)
    │
    ▼
Application Load Balancer
    │
    ├── FastAPI pods (ECS Fargate or EKS)
    │       ↕ reads secrets from AWS Secrets Manager
    │       ↕ connects to RDS PostgreSQL
    │       ↕ connects to ElastiCache (Redis) for session/cache
    │
    ├── ChromaDB pod (persistent volume)
    │       OR Pinecone cloud vector DB
    │
    └── Streamlit pod (ECS Fargate)

                        ↕
              AWS Bedrock (Claude v3)
                        ↕
              CloudWatch (logging + monitoring)
                        ↕
              S3 (store policy documents + embeddings backup)
```

To switch from Groq to AWS Bedrock, only `llm_client.py` changes:
```python
# Current (Groq):
client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

# AWS Bedrock:
import boto3
client = boto3.client("bedrock-runtime", region_name="us-east-1")
```

---

## 12.5 RAG Improvements for Production

```
Current                          Production
────────────────────────────────────────────────────────────
500-char fixed chunks        →   Semantic chunking (split at paragraph/section)
top-3 retrieval              →   Adaptive retrieval (top-k based on confidence score)
No reranking                 →   Cross-encoder reranking (Cohere Rerank API)
all-MiniLM-L6-v2             →   text-embedding-3-large (OpenAI) or Titan Embeddings
Static policies              →   Automated re-ingestion when policies update (S3 trigger → Lambda)
No confidence threshold      →   If similarity score < 0.5, skip RAG, answer from LLM only
```

---

## 12.6 Security Improvements

```
Current                          Should Add
────────────────────────────────────────────────────
SECRET_KEY in .env           →   AWS Secrets Manager or HashiCorp Vault
No HTTPS                     →   TLS certificate (AWS ACM)
No rate limiting             →   Per-user rate limiting (slowapi library)
JWT in localStorage          →   HttpOnly cookies
No input sanitization        →   Length limits, injection protection
Passwords in seed data       →   Remove hardcoded passwords from code
No audit logging             →   Log every auth event to CloudWatch
```

---

## 12.7 Monitoring and Logging Ideas

```python
# Add structured logging to every endpoint:
import logging
logger = logging.getLogger(__name__)

@router.post("/chat/")
def chat(request, current_user):
    logger.info({
        "event":     "chat_request",
        "user_id":   current_user.id,
        "intent":    intent,
        "used_rag":  used_rag,
        "latency_ms": elapsed,
    })
```

Metrics to track:
- Intent distribution (how often each intent is triggered)
- RAG hit rate (% of questions using ChromaDB)
- Guardrail trigger rate (% of off-topic questions)
- LLM latency (p50, p95, p99)
- Auth failure rate

---

## 12.8 Common Interview Questions and Answers

**Q: Why use RAG instead of fine-tuning the model on Delta policies?**

A: Fine-tuning is expensive ($thousands), requires retraining whenever policies change, and models can still hallucinate. RAG is free, policies update instantly by re-running the ingest script, and answers are directly grounded in source documents. RAG is preferred for factual, document-based use cases.

**Q: Why ChromaDB instead of a regular database for policies?**

A: Regular databases do keyword search. ChromaDB does semantic search. "Overweight luggage fees" and "heavy bag charges" mean the same thing but share no keywords. ChromaDB finds the correct policy chunk regardless of exact wording.

**Q: How does JWT prevent token tampering?**

A: The signature is generated by hashing the header + payload with SECRET_KEY using HMAC-SHA256. To tamper with the payload (e.g., change the email), you'd need to regenerate the signature, which requires SECRET_KEY. Without it, the decode step fails and returns 401.

**Q: What happens if the same user logs in from two devices?**

A: Both tokens are valid simultaneously. JWTs are stateless — the server doesn't store them. To implement single-session-only, you'd need a token blacklist in Redis.

**Q: How would you scale this to 1 million users?**

A: Replace SQLite with Aurora PostgreSQL (auto-scaling). Move ChromaDB to Pinecone (managed, scalable). Add Redis for caching frequent queries. Use ECS Fargate for API pods behind an ALB. Use CloudFront for the Streamlit frontend. LLM calls are already API-based (Bedrock/Groq) so they scale independently.

---

*End of Documentation*

*Built by Hariharan — AI Engineering Portfolio Project*
*Stack: FastAPI + SQLite + ChromaDB + JWT + Groq LLM + SentenceTransformer + Streamlit*
