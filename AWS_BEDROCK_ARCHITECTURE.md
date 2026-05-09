# Delta AI Assistant — AWS Bedrock Architecture Guide
# How to Build and Explain This Project Using AWS Bedrock
### Interview-Ready Technical Documentation

---

# SECTION 1 — UNDERSTANDING AWS BEDROCK

---

## 1.1 What is AWS Bedrock?

AWS Bedrock is a **fully managed AWS service** that gives you access to foundation models (large AI models) via a simple API — without managing any infrastructure.

Think of it like this:

```
WITHOUT Bedrock:
  Download a 70GB model file
  Set up GPU servers
  Configure CUDA drivers
  Write inference code
  Manage scaling
  Pay for GPU uptime 24/7
  → Expensive, complex, slow to start

WITH Bedrock:
  Call an API
  Pay per token (per word processed)
  Zero infrastructure management
  Scales automatically
  → Simple, cheap, production-ready
```

AWS Bedrock is essentially **"AI models as a service"** — the same way S3 is storage as a service.

---

## 1.2 Which Models Does Bedrock Support?

```
Provider        Models Available on Bedrock
───────────────────────────────────────────────────────
Anthropic       Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku
                Claude 3.5 Sonnet (most powerful)
Meta            Llama 3.1 8B, 70B, 405B
Amazon          Titan Text, Titan Embeddings
Mistral AI      Mistral 7B, Mixtral 8x7B
Cohere          Command, Embed
Stability AI    Stable Diffusion (image generation)
```

**For our Delta AI project, we use:**
- **Claude 3 Sonnet** (anthropic.claude-3-sonnet-20240229-v1:0) — for chat responses
- **Amazon Titan Embeddings** (amazon.titan-embed-text-v1) — for document embeddings in ChromaDB

---

## 1.3 AWS Bedrock vs AWS Bedrock Agents — Critical Difference

This is the most important concept to understand for interviews.

```
┌──────────────────────────────────────────────────────────────────┐
│                      AWS BEDROCK                                  │
│                                                                  │
│  Just calls an AI model and returns text.                        │
│  You control all the logic.                                      │
│  You decide when to call it, what to send, what to do with       │
│  the response.                                                   │
│                                                                  │
│  Your code → Bedrock API → Claude generates text → Your code    │
│                                                                  │
│  Used in our Delta project: YES                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                   AWS BEDROCK AGENTS                              │
│                                                                  │
│  An autonomous AI agent that can decide WHAT to do next.         │
│  It can call APIs, query databases, run code — on its own.       │
│  You define "actions" the agent can take.                        │
│  The agent itself decides which action to use.                   │
│                                                                  │
│  User asks question → Agent decides: "I need to call /miles API" │
│  Agent calls API → Gets data → Agent answers                     │
│                                                                  │
│  Used in our Delta project: NO (we built our own routing)        │
└──────────────────────────────────────────────────────────────────┘
```

**Why we chose plain Bedrock (not Agents) for our project:**

1. **Full control** — We built our own intent classifier and RAG pipeline. We decide exactly when to call ChromaDB, when to query SQLite, when to call the LLM.

2. **Predictability** — Bedrock Agents use "chain of thought" reasoning to decide actions. This can be slow (multiple LLM calls per request) and unpredictable. Our system is deterministic.

3. **Cost efficiency** — Bedrock Agents make multiple LLM calls per request. Our system makes exactly one LLM call per request.

4. **Interview gold** — Building your own pipeline shows deeper engineering understanding than using Agents.

**Interview answer when asked "Why not Bedrock Agents?":**

*"Bedrock Agents are great for truly autonomous scenarios where the AI needs to decide what tools to use. But in our case, we have a clear, deterministic flow — classify intent, retrieve if needed, generate. Building this ourselves gave us more control over latency, cost, and accuracy. It's also more production-hardened — you know exactly what's happening at each step."*

---

# SECTION 2 — BEDROCK ARCHITECTURE DIAGRAM

---

## 2.1 High Level Architecture with AWS Bedrock

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER / BROWSER                                  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AWS CLOUD (us-east-1)                               │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     Application Load Balancer                        │  │
│  └────────────────────────────────┬─────────────────────────────────────┘  │
│                                   │                                         │
│  ┌────────────────────────────────▼─────────────────────────────────────┐  │
│  │                    ECS Fargate (FastAPI Containers)                   │  │
│  │                                                                      │  │
│  │   Container 1          Container 2          Container 3              │  │
│  │   FastAPI + Uvicorn    FastAPI + Uvicorn    FastAPI + Uvicorn        │  │
│  │   (auto-scales)        (auto-scales)        (auto-scales)           │  │
│  └──────┬─────────────────────────┬────────────────────────┬───────────┘  │
│         │                         │                        │               │
│         │                         │                        │               │
│  ┌──────▼──────┐  ┌───────────────▼──────┐  ┌─────────────▼──────────┐   │
│  │  Amazon RDS │  │  Amazon OpenSearch   │  │    AWS Secrets Manager │   │
│  │  PostgreSQL │  │  (ChromaDB replaced) │  │    (JWT secret,        │   │
│  │             │  │                      │  │     API keys)          │   │
│  │  customers  │  │  Policy doc vectors  │  │                        │   │
│  │  activity   │  │  Semantic search     │  │                        │   │
│  │  invoices   │  │                      │  │                        │   │
│  └─────────────┘  └──────────────────────┘  └────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         AWS Bedrock                                   │  │
│  │                                                                      │  │
│  │   ┌────────────────────────────────────┐                            │  │
│  │   │  Claude 3 Sonnet                    │  ← Chat generation        │  │
│  │   │  anthropic.claude-3-sonnet-...      │                           │  │
│  │   └────────────────────────────────────┘                            │  │
│  │                                                                      │  │
│  │   ┌────────────────────────────────────┐                            │  │
│  │   │  Amazon Titan Embeddings            │  ← Document embeddings    │  │
│  │   │  amazon.titan-embed-text-v1         │                           │  │
│  │   └────────────────────────────────────┘                            │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                   Supporting Services                                 │  │
│  │   CloudWatch Logs  │  S3 (policy docs)  │  ElastiCache Redis         │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2.2 Request Flow Diagram with Bedrock

```
User: "What are the baggage fees?"
              │
              ▼
    Application Load Balancer
    (routes to healthy FastAPI container)
              │
              ▼
    FastAPI — POST /chat/
              │
              ├── Verify JWT token (AWS Secrets Manager for SECRET_KEY)
              │
              ├── Load customer from RDS PostgreSQL
              │      customer = {name, tier, miles_balance}
              │
              ├── intent_classifier.py
              │      intent = "baggage"
              │
              ├── rag_pipeline.py
              │      ┌─────────────────────────────────┐
              │      │  Query → Titan Embeddings API   │  ← Bedrock
              │      │  "baggage fees?" → [0.44, 0.12] │
              │      └─────────────────────────────────┘
              │             │
              │      ┌──────▼──────────────────────────┐
              │      │  Amazon OpenSearch               │
              │      │  Semantic search in policy index │
              │      │  Returns 3 relevant chunks       │
              │      └─────────────────────────────────┘
              │
              ├── prompt_builder.py
              │      Builds: system + customer info + policy chunks + question
              │
              ├── llm_client.py
              │      ┌─────────────────────────────────┐
              │      │  Claude 3 Sonnet on Bedrock      │  ← Bedrock
              │      │  Input: enriched prompt          │
              │      │  Output: personalised answer     │
              │      └─────────────────────────────────┘
              │
              ▼
    "Hi Hari, as Gold Medallion your first two bags are free..."
              │
              ▼
    CloudWatch Logs
    (logs: user_id, intent, latency, tokens_used)
              │
              ▼
    Response → User
```

---

# SECTION 3 — CODE CHANGES FOR AWS BEDROCK

---

## 3.1 What Changes vs What Stays the Same

```
File                    Change Needed?    What Changes
────────────────────────────────────────────────────────────────────
.env                    YES               Model ID, AWS region, credentials
config.py               YES               Add AWS_REGION, BEDROCK_MODEL_ID
database.py             NO                Identical
auth.py                 NO                Identical
models.py               NO                Identical
all routers             NO                Identical
intent_classifier.py    NO                Identical
rag_pipeline.py         OPTIONAL          Can use Titan Embeddings instead of local model
prompt_builder.py       NO                Identical
llm_client.py           YES               Replace OpenAI client with boto3 Bedrock client
frontend/app.py         NO                Identical
```

**Only 3 files need changes: `.env`, `config.py`, `llm_client.py`**

This is the power of our clean architecture — the AI engine is isolated. Swap the LLM provider by changing one file.

---

## 3.2 Updated `.env` for Bedrock

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1

# Bedrock Model
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_EMBED_MODEL_ID=amazon.titan-embed-text-v1

# Database (production: RDS)
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/delta_db

# JWT Auth
SECRET_KEY=your-long-random-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=60
```

---

## 3.3 Updated `config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # AWS
    aws_access_key_id:      str
    aws_secret_access_key:  str
    aws_region:             str = "us-east-1"

    # Bedrock Models
    bedrock_model_id:       str   # claude or llama model
    bedrock_embed_model_id: str   # titan embeddings

    # Database
    database_url:           str

    # JWT
    secret_key:             str
    jwt_algorithm:          str
    jwt_expiry_minutes:     int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
```

---

## 3.4 Updated `llm_client.py` — The Key Change

```python
import boto3
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from ai_engine.intent_classifier import classify_intent
from ai_engine.rag_pipeline import retrieve
from ai_engine.prompt_builder import build_prompt

# ── AWS Bedrock Client ────────────────────────────────────────────────────────

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

INTENTS_NEEDING_RAG = {"miles_policy", "baggage", "upgrade"}
ALLOWED_INTENTS     = {"miles_policy", "baggage", "upgrade", "account"}

GUARDRAIL_REPLY = (
    "I'm Delta's AI Customer Assistant. I can only help with questions about "
    "your miles balance, baggage policies, flight upgrades, or your account."
)


def call_bedrock_claude(messages: list[dict]) -> str:
    """
    Calls Claude on AWS Bedrock using the Messages API format.
    Claude models on Bedrock use Anthropic's native API format.
    """
    system_message = messages[0]["content"]   # extract system prompt
    user_message   = messages[1]["content"]   # extract user message

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "system": system_message,
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }

    response = bedrock_client.invoke_model(
        modelId     = settings.bedrock_model_id,
        body        = json.dumps(request_body),
        contentType = "application/json",
        accept      = "application/json",
    )

    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"]


def get_ai_response(user_message: str, customer: dict) -> dict:
    intent      = classify_intent(user_message)
    used_rag    = False
    rag_context = ""

    if intent not in ALLOWED_INTENTS:
        return {"reply": GUARDRAIL_REPLY, "intent": intent, "used_rag": False}

    if intent in INTENTS_NEEDING_RAG:
        rag_context = retrieve(user_message, intent)
        used_rag    = True

    messages = build_prompt(
        user_message     = user_message,
        intent           = intent,
        customer_context = customer,
        rag_context      = rag_context,
    )

    reply = call_bedrock_claude(messages)

    return {
        "reply":    reply,
        "intent":   intent,
        "used_rag": used_rag,
    }
```

---

## 3.5 Updated `rag_pipeline.py` — Using Titan Embeddings

```python
import boto3
import json
import chromadb
import os

from backend.config import settings

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

INTENT_TO_SOURCE = {
    "miles_policy": "miles_policy",
    "baggage":      "baggage_policy",
    "upgrade":      "upgrade_policy",
}

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)

_client     = None
_collection = None


def get_titan_embedding(text: str) -> list[float]:
    """
    Calls Amazon Titan Embeddings on Bedrock.
    Converts text to a list of 1536 floating point numbers.
    """
    response = bedrock_client.invoke_model(
        modelId     = settings.bedrock_embed_model_id,
        body        = json.dumps({"inputText": text}),
        contentType = "application/json",
        accept      = "application/json",
    )
    body = json.loads(response["body"].read())
    return body["embedding"]


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client     = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = _client.get_or_create_collection(
            name="delta_policies",
        )
    return _collection


def retrieve(query: str, intent: str, n_results: int = 3) -> str:
    collection    = _get_collection()
    query_embedding = get_titan_embedding(query)   # ← Bedrock call
    source_filter = INTENT_TO_SOURCE.get(intent)

    if source_filter:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"source": source_filter},
        )
    else:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )

    documents = results.get("documents", [[]])[0]
    return "\n\n".join(documents)
```

---

## 3.6 Updated `ingest_policies.py` — Using Titan for Ingestion

```python
import boto3
import json
import os
import chromadb

from backend.config import settings

POLICIES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policies")
CHROMA_DIR   = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

POLICY_FILES = {
    "miles_policy":   "miles_policy.txt",
    "baggage_policy": "baggage_policy.txt",
    "upgrade_policy": "upgrade_policy.txt",
}

bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)


def get_titan_embedding(text: str) -> list[float]:
    response = bedrock_client.invoke_model(
        modelId     = settings.bedrock_embed_model_id,
        body        = json.dumps({"inputText": text}),
        contentType = "application/json",
        accept      = "application/json",
    )
    return json.loads(response["body"].read())["embedding"]


def read_policy(filename):
    with open(os.path.join(POLICIES_DIR, filename), "r") as f:
        return f.read()


def chunk_text(text, chunk_size=500, overlap=50):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]


def ingest():
    print("Starting ingestion with Amazon Titan Embeddings...")
    client     = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(name="delta_policies")

    for policy_name, filename in POLICY_FILES.items():
        print(f"  Processing {filename}...")
        chunks    = chunk_text(read_policy(filename))
        ids       = [f"{policy_name}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"source": policy_name, "chunk_index": i} for i in range(len(chunks))]

        embeddings = []
        for chunk in chunks:
            embedding = get_titan_embedding(chunk)    # ← Bedrock call per chunk
            embeddings.append(embedding)

        collection.upsert(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
            embeddings=embeddings,    # ← pass pre-computed Bedrock embeddings
        )
        print(f"    Stored {len(chunks)} chunks")

    print(f"Done. Total: {collection.count()} documents")


if __name__ == "__main__":
    ingest()
```

---

# SECTION 4 — BEDROCK INTERNAL FLOW DIAGRAM

---

## 4.1 How Bedrock Processes a Request Internally

```
Your Code (llm_client.py)
         │
         │ boto3.client("bedrock-runtime").invoke_model(
         │     modelId = "anthropic.claude-3-sonnet-20240229-v1:0",
         │     body    = JSON payload with messages
         │ )
         │
         ▼
AWS API Gateway (Bedrock endpoint)
         │
         │  IAM checks:
         │  Does this AWS user have bedrock:InvokeModel permission?
         │  YES → proceed
         │  NO  → 403 AccessDeniedException
         │
         ▼
AWS Bedrock Model Router
         │
         │  Reads modelId → routes to Anthropic Claude cluster
         │
         ▼
Anthropic Claude 3 Sonnet (running on AWS infrastructure)
         │
         │  Processes your prompt:
         │  system: "You are a Delta assistant..."
         │  user:   "Customer: Hari Kumar, Gold, 45230 miles
         │           Policy: Gold members get 2 free bags...
         │           Question: What are baggage fees?"
         │
         │  Generates token by token:
         │  "Hi" "Hari" "," "as" "a" "Gold" "Medallion"...
         │
         ▼
Response JSON returned:
{
    "id": "msg_01abc123",
    "type": "message",
    "role": "assistant",
    "content": [{"type": "text", "text": "Hi Hari, as a Gold..."}],
    "model": "claude-3-sonnet-20240229",
    "usage": {
        "input_tokens": 387,
        "output_tokens": 142
    }
}
         │
         ▼
Your code:
reply = response_body["content"][0]["text"]
```

---

## 4.2 How Titan Embeddings Works on Bedrock

```
Your Code (rag_pipeline.py)
         │
         │ bedrock_client.invoke_model(
         │     modelId = "amazon.titan-embed-text-v1",
         │     body    = {"inputText": "What are baggage fees?"}
         │ )
         │
         ▼
AWS Bedrock — Titan Embeddings Model
         │
         │  Tokenizes the text
         │  Runs through the neural network
         │  Produces a 1536-dimension vector
         │
         ▼
Response:
{
    "embedding": [0.023, -0.041, 0.187, 0.003, ...],  // 1536 numbers
    "inputTextTokenCount": 5
}
         │
         ▼
ChromaDB uses this vector to find similar chunks
```

---

# SECTION 5 — COMPLETE BEDROCK END-TO-END TRACE

---

## Full trace: "How do I upgrade my seat?" with Bedrock

```
Step 1 — Streamlit sends request
─────────────────────────────────
POST http://your-alb.amazonaws.com/chat/
Authorization: Bearer eyJhbGc...
{"message": "How do I upgrade my seat?"}

Step 2 — ALB routes to FastAPI container
──────────────────────────────────────────
Load balancer picks healthy ECS container
FastAPI receives request

Step 3 — JWT verified using AWS Secrets Manager
────────────────────────────────────────────────
SECRET_KEY fetched from Secrets Manager (cached in memory)
jwt.decode(token, secret_key) → {"sub": "hari@delta.com", "exp": ...}
email = "hari@delta.com"

Step 4 — Customer loaded from RDS PostgreSQL
─────────────────────────────────────────────
db.query(Customer).filter(email == "hari@delta.com").first()

SQL: SELECT * FROM customers WHERE email = 'hari@delta.com';

Result:
  name          = "Hari Kumar"
  tier          = "Gold"
  miles_balance = 45230.0
  member_since  = 2019-03-15

Step 5 — intent_classifier.py
───────────────────────────────
classify_intent("How do I upgrade my seat?")

message_lower = "how do i upgrade my seat?"
Check "upgrade" keywords:
  "upgrade" in message → MATCH
return "upgrade"

intent = "upgrade"

Step 6 — rag_pipeline.py
──────────────────────────
retrieve("How do I upgrade my seat?", "upgrade", n_results=3)

  6a. Call Amazon Titan Embeddings on Bedrock:
  ─────────────────────────────────────────────
  bedrock_client.invoke_model(
      modelId = "amazon.titan-embed-text-v1",
      body    = {"inputText": "How do I upgrade my seat?"}
  )
  → embedding = [0.067, -0.023, 0.341, ...]   (1536 numbers)

  6b. Search ChromaDB with filter:
  ─────────────────────────────────
  collection.query(
      query_embeddings = [[0.067, -0.023, 0.341, ...]],
      n_results = 3,
      where     = {"source": "upgrade_policy"}
  )

  ChromaDB computes similarity with 7 upgrade chunks
  Returns top 3:

  Chunk 1 (sim 0.91): "Members can use SkyMiles to upgrade.
    Domestic upgrades using miles start at 5,000 miles each way.
    International upgrades to Delta One start at 30,000 miles each way."

  Chunk 2 (sim 0.87): "Gold Medallion members receive complimentary upgrades
    to First Class on domestic flights based on availability.
    Upgrades confirmed starting 24 hours before departure."

  Chunk 3 (sim 0.79): "Same day confirmed upgrades: $75 fee for domestic.
    Same day standby: free for Medallion members."

  rag_context = chunk1 + "\n\n" + chunk2 + "\n\n" + chunk3

Step 7 — prompt_builder.py
────────────────────────────
messages = [
  {
    "role": "system",
    "content": "You are a helpful Delta Air Lines customer assistant.
                Be polite, concise, and accurate.
                Address the customer by first name."
  },
  {
    "role": "user",
    "content": "Customer Information:
                - Name: Hari Kumar
                - Tier: Gold
                - Miles Balance: 45,230 miles
                - Member Since: 2019-03-15

                Relevant Delta Policy Information:
                Members can use SkyMiles to upgrade. Domestic upgrades
                start at 5,000 miles each way...

                [chunk2 and chunk3 here]

                Customer Question: How do I upgrade my seat?"
  }
]

Step 8 — llm_client.py calls Claude on Bedrock
────────────────────────────────────────────────
bedrock_client.invoke_model(
    modelId = "anthropic.claude-3-sonnet-20240229-v1:0",
    body    = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "system": "You are a helpful Delta Air Lines customer assistant...",
        "messages": [{"role": "user", "content": "Customer Information: ..."}]
    }
)

Input tokens:  387   (prompt length)
Output tokens: 198   (response length)
Cost estimate: ~$0.003 per request (Claude 3 Sonnet pricing)

Step 9 — Claude generates response
────────────────────────────────────
response_body["content"][0]["text"] =

"Hi Hari! Great news — as a Gold Medallion member, you have several
upgrade options available.

1. **Complimentary Upgrades**: You're automatically eligible for free
   First Class upgrades on domestic flights based on availability.
   These are processed starting 24 hours before departure.

2. **Miles Upgrades**: With your 45,230 miles, you can upgrade domestic
   flights starting at just 5,000 miles each way — that gives you up to
   9 potential domestic upgrades!

3. **Same Day Upgrades**: If your complimentary upgrade hasn't cleared,
   you can request a same-day standby upgrade for free at the airport.

Would you like help with a specific flight?"

Step 10 — Response logged and returned
────────────────────────────────────────
CloudWatch log entry:
{
    "user_id": 1,
    "intent": "upgrade",
    "used_rag": true,
    "input_tokens": 387,
    "output_tokens": 198,
    "latency_ms": 1243
}

HTTP Response to Streamlit:
{
    "reply": "Hi Hari! Great news...",
    "intent": "upgrade",
    "used_rag": true
}

Streamlit displays response in chat bubble.
```

---

# SECTION 6 — AWS IAM SETUP FOR BEDROCK

---

## 6.1 Required IAM Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
            ]
        }
    ]
}
```

In production, this policy is attached to the **ECS Task Role** — the container automatically gets these permissions without needing access keys in the code.

---

## 6.2 Enabling Models in Bedrock

Before calling a model, you must enable it in the Bedrock console:

```
AWS Console → Amazon Bedrock → Model Access → Request Access

Enable:
✅ Claude 3 Sonnet (Anthropic)
✅ Titan Embeddings G1 - Text (Amazon)
```

This is a one-time setup per AWS account. Without this, you get a `ResourceNotFoundException`.

---

# SECTION 7 — COST COMPARISON

---

## 7.1 Bedrock Pricing vs Current Setup

```
Model                           Input Price        Output Price
────────────────────────────────────────────────────────────────
Claude 3 Sonnet (Bedrock)       $3.00 / 1M tokens  $15.00 / 1M tokens
Claude 3 Haiku (Bedrock)        $0.25 / 1M tokens  $1.25 / 1M tokens
Titan Embeddings (Bedrock)      $0.10 / 1M tokens  —
Groq llama-3.1-8b (current)     FREE               FREE
```

**For interview context:**

"In development, I used Groq's free tier to keep costs zero. The architecture is designed so that switching to AWS Bedrock for production requires changing only 3 lines of configuration. In a production environment, Claude 3 Haiku on Bedrock at $0.25/million input tokens would handle millions of customer queries at very low cost."

---

# SECTION 8 — INTERVIEW SCRIPT

---

## 8.1 How to Explain Your Architecture (2-3 minutes)

*"I built a production-grade AI customer service assistant for Delta Air Lines using a custom RAG pipeline on AWS Bedrock.*

*The system has five layers. At the frontend, users interact through a Streamlit chat interface. The backend is a FastAPI application running on AWS ECS Fargate, behind an Application Load Balancer. Authentication uses JWT tokens — the customer logs in once and all subsequent API calls use the token, which is verified using a secret stored in AWS Secrets Manager.*

*For the AI layer, I built a custom RAG pipeline rather than using Bedrock Agents. Here's why: when a customer asks a question, my intent classifier first determines what type of question it is — about their account, about baggage policy, upgrades, or miles rules. For account questions, the system fetches the customer's actual data from RDS PostgreSQL. For policy questions, it calls Amazon Titan Embeddings on Bedrock to convert the question to a vector, then does a semantic similarity search in ChromaDB to retrieve the three most relevant policy chunks.*

*These retrieved chunks, combined with the customer's personal account data, are injected into the prompt as context before calling Claude 3 Sonnet on Bedrock. This is RAG — Retrieval Augmented Generation — and it eliminates hallucination because the AI is reading actual policy documents rather than guessing from training data.*

*The entire pipeline makes exactly one LLM call per request, with a guardrail layer that blocks off-topic questions before they reach Bedrock, saving both cost and latency."*

---

## 8.2 Expected Interview Questions and Answers

**Q: Why Bedrock instead of calling OpenAI directly?**

*"AWS Bedrock keeps everything within the AWS ecosystem — better security, no data leaving AWS, unified billing, and native IAM-based access control. In a financial or airline context, data residency is critical. Bedrock also offers multiple model providers (Anthropic, Meta, Mistral) so we can A/B test models without changing infrastructure."*

---

**Q: Why not use Bedrock Agents instead of building your own pipeline?**

*"Bedrock Agents are great for fully autonomous scenarios where the AI decides what tools to call. But in our case, the routing logic is deterministic — we always follow the same path: classify → retrieve → augment → generate. Building our own pipeline gives us predictable latency, exact cost control, and full observability. Bedrock Agents also make multiple LLM calls internally which increases both latency and cost."*

---

**Q: How does the RAG pipeline work at a technical level?**

*"When a policy question arrives, we first call Amazon Titan Embeddings to convert the user's question into a 1536-dimension vector. We then query ChromaDB using this vector to find the three most semantically similar policy document chunks. Semantic similarity means we find relevant content even if the exact words don't match — 'heavy luggage' finds the 'overweight baggage' policy. These chunks are injected into the Claude prompt as context. Claude then reads both the policy and the customer's account data to generate a personalised, accurate answer."*

---

**Q: How does authentication work?**

*"Users POST their email and password to /auth/login. The password is verified against a bcrypt hash stored in RDS — we never store plain passwords. On success, we create a JWT token containing the user's email and a 60-minute expiry, signed with a secret from AWS Secrets Manager. Every subsequent request includes this token in the Authorization header. FastAPI's dependency injection automatically verifies the token before any protected route executes."*

---

**Q: How would you scale this to 10 million users?**

*"The API layer on ECS Fargate auto-scales horizontally behind the ALB. For the database, I'd move from single-instance RDS to Aurora with read replicas. ChromaDB would be replaced with a managed vector database service like Pinecone. I'd add ElastiCache Redis to cache frequent query results — common policy questions get the same answer, so caching saves Bedrock costs significantly. CloudFront would cache the Streamlit frontend globally. The Bedrock API itself is serverless and scales automatically."*

---

**Q: What is the cost per query?**

*"With Claude 3 Sonnet, a typical customer query uses about 400 input tokens and 200 output tokens. That's approximately $0.0012 per query (400 × $0.003/1K + 200 × $0.015/1K). For a million queries per day, that's $1,200/day. Using Claude 3 Haiku instead brings that to about $0.0002 per query — $200/day for a million queries. The guardrail layer blocks off-topic questions before they hit Bedrock, reducing cost further."*

---

*End of AWS Bedrock Architecture Document*

*Delta AI Assistant — Built by Hari Kumar*
*Architecture: FastAPI + RDS PostgreSQL + ChromaDB + AWS Bedrock (Claude 3 + Titan) + ECS Fargate*
