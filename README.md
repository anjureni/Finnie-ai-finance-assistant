# Finnie AI – Finance Education Assistant
🤖 Finnie — AI Finance Assistant
Finnie is an AI-powered personal finance assistant built for financial education and decision support.
It combines LLM reasoning, retrieval-augmented generation (RAG), and interactive dashboards to help users understand markets, portfolios, and financial goals.
⚠️ Educational Use Only
This application provides financial education and general information.
It is not financial, legal, or tax advice.
---

## Features
✨ Key Features
# 💬 Ask Finnie (AI Chat)
Natural-language finance questions
Intelligent agent routing using LangGraph
RAG-powered answers with citations from a knowledge base
Clear source attribution
# 📈 Market Overview
Popular stocks snapshot
Major indices (ETF proxies like SPY, QQQ, DIA)
Historical trend visualization
Educational market explanations
# 📊 Portfolio Dashboard
Portfolio summary (total value, largest holding, diversification score)
Holdings table with asset allocation
Small pie chart for allocation visualization
Add / manage holdings (education-only simulation)
# 🎯 Goal Planner
View all financial goals
Create new goals (target, monthly contribution)
Edit goals (update target / contribution)
Growth-over-time projection with charts
---

## High-Level Architecture

🧠 Architecture Overview
┌───────────────────────────┐
│        Streamlit UI       │
│  - Chat                  │
│  - Portfolio Dashboard   │
│  - Market Overview       │
│  - Goal Planner          │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│     LangGraph Workflow    │
│  - Intent Router          │
│  - Agent Orchestration    │
└─────────────┬─────────────┘
              │
              ▼
┌──────────────────────────────────────────────┐
│                 AI Agents                    │
│                                              │
│  finance_qa   → RAG + LLM answers             │
│  market       → Market data & trends          │
│  portfolio    → Portfolio analysis            │
│  goals        → Goal planning & projections   │
└─────────────┬────────────────────────────────┘
              │
              ▼
┌───────────────────────────┐
│     Knowledge & Data      │
│  - FAISS Vector Index     │
│  - Knowledge Base Files   │
│  - Market APIs (optional) │
└───────────────────────────┘


- **UI**: Built with Streamlit (`src/web_app/`).
- **Agents**: Handle user queries, context, and orchestrate retrieval/LLM calls.
- **RAG**: Retrieves relevant documents and builds context for the LLM.
- **Knowledge Base**: Curated finance documents.
- **Indexing**: FAISS and embeddings for semantic search.
- **Workflow**: Orchestrated via `workflow/graph.py` and `workflow/router.py`.

---
# 🔄 Application Workflow
#  1️⃣ User Interaction
User interacts via Streamlit UI
Can ask a question or navigate dashboards
# 2️⃣ Intent Routing
User query is passed to a rule-based router
Intent is classified as:
finance_qa
market
portfolio
goals
# 3️⃣ Agent Execution
LangGraph routes execution to the correct agent
Each agent handles its own logic and data needs
# 4️⃣ RAG (Finance Q&A Only)
Query is embedded using OpenAI embeddings
FAISS retrieves relevant knowledge chunks
LLM generates answer using context + reasoning
Sources are extracted and returned
# 5️⃣ UI Rendering
Answer is shown in chat
Sources are displayed
Dashboards render charts/tables dynamically
# 📁 Project Structure
Finnie_AI_Finance_Assistant/
│
├── app.py
│
├── src/
│   ├── agents/
│   │   ├── finance_qa.py
│   │   ├── market.py
│   │   ├── portfolio.py
│   │   ├── goals.py
│   │   └── registry.py
│   │
│   ├── workflow/
│   │   ├── graph.py
│   │   ├── router.py
│   │   └── state.py
│   │
│   ├── rag/
│   │   ├── retriever.py
│   │   ├── faiss_store.py
│   │   ├── prompting.py
│   │   └── types.py
│   │
│   ├── web_app/
│   │   ├── ui_chat.py
│   │   ├── ui_market.py
│   │   ├── ui_portfolio.py
│   │   ├── ui_goals.py
│   │   └── session.py
│
├── data/
│   ├── knowledge_base/
│   └── index/
│
├── scripts/
│   └── build_index.py
│
├── .env
└── README.md

## Workflow

1. **User submits a question** via the web UI.
2. **Agent receives the query** and checks for context.
3. If context is missing, the **retriever** searches the knowledge base using semantic search.
4. The **retriever returns relevant context and sources**.
5. The agent **builds a prompt** for the LLM, including the retrieved context and the user’s question.
6. The **LLM (OpenAI API)** generates an answer, which is returned to the agent.
7. The agent **deduplicates sources** and returns the answer and sources to the UI.
8. The **UI displays the answer and sources** to the user, with mini dashboards if relevant.

# 🔍 RAG Design (Finance Q&A)
Vector Store: FAISS
Embeddings: OpenAI text-embedding-3-small
Chunking: Knowledge base text files
Prompt Strategy:
Inject retrieved context
Enforce “don’t hallucinate” rule
Cite sources
Example output:
Answer text…

Sources:
[1] diversification_basics.txt
[2] investing_risks_disclaimer.txt

## Setup & Installation

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd Finnie_AI _Finance Assisant
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory with your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key
```

Optionally, set a custom model:
```
CHAT_MODEL=gpt-4o-mini
```

4. **Build the knowledge base index**

```bash
python scripts/build_index.py
```

5. **Run the app**

```bash
streamlit run app.py
```

---

## Project Structure

```
├── app.py                  # Streamlit entry point
├── config.yaml             # App configuration
├── requirements.txt        # Python dependencies
├── data/
│   ├── knowledge_base/     # Finance documents
│   └── index/              # FAISS index and metadata
├── scripts/
│   └── build_index.py      # Index builder script
├── src/
│   ├── agents/             # Agent logic (QA, market, goals, portfolio)
│   ├── core/               # LLM, prompts, disclaimers
│   ├── rag/                # Retrieval, embeddings, context building
│   ├── utils/              # Config, logging, error handling
│   └── web_app/            # Streamlit UI components
├── workflow/               # Agent routing and state management
└── tests/                  # Unit tests
```

---

## Disclaimers

- Finnie AI is for educational purposes only. It does **not** provide personalized financial advice.
- All answers are based on general finance knowledge and the provided knowledge base.

---


---

## Acknowledgements

- OpenAI for LLM APIs
- Streamlit for the UI framework
- FAISS for semantic search

---
