# E-commerce Returns Agent MVP

A small working class demo based on the project deck. It uses 12 synthetic orders, LangChain tools, a LangGraph workflow, and an OpenRouter powered investigation agent. Pick an order from the grid, choose a return reason, and process it. The UI shows tool calls, the decision path, and a simulated refund or human review.

## Run

The project needs Python 3.11 or newer. This workspace already has a ready-to-use `.venv` with Python 3.12 and all dependencies installed. To run it here:

```bash
source .venv/bin/activate
streamlit run app.py
```

To create the environment again on another machine, use its Python 3.11+ executable:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`). No API key is needed.

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
