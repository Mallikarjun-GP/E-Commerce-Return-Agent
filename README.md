# E-commerce Returns Agent & Shop

An intelligent e-commerce return processing platform powered by **LangChain**, **LangGraph**, **Streamlit**, and **MongoDB**. The platform includes a full shopping storefront, user authentication, orders dashboard, and an agentic AI return decision engine that evaluates return policies, customer history, fraud/risk heuristics, and OpenRouter-powered reasoning.

## Features
- 🛒 **Storefront & Cart**: Browse products by category, manage cart, and place orders with instant MongoDB synchronization.
- 📦 **Order Tracking**: Real-time order status, cancellation, and returns management.
- 🤖 **Agentic Return Workflow**: Multi-step LangGraph workflow (`lookup_order` → `check_eligibility` → `customer_history` → `score_return_risk` → AI investigation).
- 🗄️ **MongoDB & CSV Sync**: Seamless data layer supporting MongoDB Atlas alongside CSV data.

## Configuration & Setup

### 1. Database Configuration
Create a `.env` or `.streamlit/secrets.toml` file in the project root:

```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
```

### 2. Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Connect the AI

Create an OpenRouter API key, then paste it into **AI connection · OpenRouter** in the app. The default model ID is `openrouter/free`; you can change it in the same panel. Alternatively, set `OPENROUTER_API_KEY` in the terminal before starting Streamlit. The key is not written to a project file.

With a key, the LangChain agent uses order, eligibility, history, and risk tools to investigate eligible returns, then writes a short assessment. Its tool calls and assessment appear in the UI. The code still enforces eligibility and the risk threshold before any mock refund. If the API is unavailable, the policy workflow still completes and the UI reports the AI error. Without a key, the app runs in rule-based demo mode.

## Three demo cases

| Order | Expected result | Why |
| --- | --- | --- |
| `ORD-1001` | Mock refund approved | Within 30 days and low risk |
| `ORD-2005` | Human approval required | Four earlier returns and a high-value order |
| `ORD-3001` | Return ineligible | Outside the 30-day return window |

`ORD-4001` demonstrates the excluded digital-product category. You can also type an unknown order ID.

## How the pipeline works

`lookup_order` → `check_eligibility` → `customer_history` → `score_return_risk` → OpenRouter AI investigation → decision gate → `create_mock_refund` or human review.

The risk score is a transparent teaching heuristic: up to 60 points for previous return rate, 20 for at least three prior returns, and 20 for an order worth at least ₹10,000. A score of 60 or more requires human approval. This is **not** a trained fraud detector, and a flagged customer is not proven fraudulent.

The small CSV is synthetic. Refund references are display-only. Data and decisions stay in the current Streamlit session; restarting the app resets review actions. LangChain provides the agent and callable tools; LangGraph coordinates the unified workflow and conditional routing. The AI investigates and explains; the application enforces the final refund gate.

## Check the workflow

```bash
python3 -m unittest discover -s tests -v
```
