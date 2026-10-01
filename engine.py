"""Small, auditable returns workflow using LangChain tools and LangGraph."""

from __future__ import annotations

import csv
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, TypedDict, cast

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_openrouter import ChatOpenRouter
from langgraph.graph import END, START, StateGraph


from db import get_order_by_id, get_user_orders

DATA_FILE = Path(__file__).parent / "data" / "orders.csv"
RETURN_WINDOW_DAYS = 30
REVIEW_THRESHOLD = 60
DEFAULT_OPENROUTER_MODEL = "openrouter/free"


def _mongo_to_engine_order(doc: dict) -> dict[str, Any]:
    """Normalize a MongoDB user order doc into the engine order schema."""
    product_name = ", ".join(i.get("product_name", "") for i in doc.get("items", [])) or "Item"
    category = doc["items"][0].get("category", "General") if doc.get("items") else "General"
    qty = sum(i.get("qty", 1) for i in doc.get("items", []))
    return {
        "order_id": doc["order_id"],
        "customer_id": doc.get("username", ""),
        "customer_name": doc.get("customer_name", doc.get("username", "")),
        "product": product_name,
        "category": category,
        "amount_inr": int(doc.get("total_inr", 0)),
        "quantity": qty,
        "payment_method": doc.get("payment_method", "Online UPI"),
        "status": doc.get("status", "Delivered"),
        "shipping_days": doc.get("shipping_days", 3),
        "city": doc.get("city", "Bangalore"),
        "state": doc.get("state", "Karnataka"),
        "days_since_delivery": int(doc.get("days_since_delivery", 0)),
        "previously_returned": bool(doc.get("previously_returned", False)),
        "return_reason": doc.get("return_reason", ""),
    }


def orders() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if DATA_FILE.exists():
        with DATA_FILE.open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
        for row in rows:
            row["amount_inr"] = int(row["amount_inr"]) if str(row.get("amount_inr", "")).isdigit() else 0
            row["days_since_delivery"] = int(row["days_since_delivery"]) if str(row.get("days_since_delivery", "")).isdigit() else 0
            row["previously_returned"] = str(row.get("previously_returned", "")).lower() == "true"
            row["quantity"] = int(row.get("quantity") or 1)
            row["shipping_days"] = int(row.get("shipping_days") or 0)
            row["payment_method"] = row.get("payment_method", "")
            row["city"] = row.get("city", "")
            row["state"] = row.get("state", "")
            row["return_reason"] = row.get("return_reason", "")
    return rows


@tool
def lookup_order(order_id: str) -> dict[str, Any]:
    """Look up an order by its exact order ID in MongoDB or local demo dataset."""
    try:
        mongo_doc = get_order_by_id(order_id)
        if mongo_doc:
            return _mongo_to_engine_order(mongo_doc)
    except Exception:
        pass
    return next((row.copy() for row in orders() if row["order_id"] == order_id), {})


@tool
def check_eligibility(order_id: str) -> dict[str, Any]:
    """Check delivery status, return window, and excluded product category."""
    order = lookup_order.invoke({"order_id": order_id})
    if not order:
        return {"eligible": False, "reason": "Order not found."}
    if order.get("status") != "Delivered":
        return {"eligible": False, "reason": "The order has not been delivered."}
    if order.get("category") == "Digital":
        return {"eligible": False, "reason": "Digital products are excluded in this demo policy."}
    if int(order.get("days_since_delivery", 0)) > RETURN_WINDOW_DAYS:
        return {"eligible": False, "reason": "The 30-day return window has passed."}
    if order.get("previously_returned"):
        return {"eligible": False, "reason": "This order was already returned."}
    return {"eligible": True, "reason": "Delivered within 30 days and eligible for return."}


@tool
def customer_history(customer_id: str, current_order_id: str) -> dict[str, Any]:
    """Summarize a customer's earlier orders and returns, excluding the current order."""
    combined_orders: dict[str, dict[str, Any]] = {}
    
    # 1. MongoDB orders
    try:
        mongo_orders = get_user_orders(customer_id)
        for doc in mongo_orders:
            oid = doc.get("order_id")
            if oid:
                combined_orders[oid] = _mongo_to_engine_order(doc)
    except Exception:
        pass

    # 2. CSV orders
    for row in orders():
        if row.get("customer_id") == customer_id:
            oid = row.get("order_id")
            if oid and oid not in combined_orders:
                combined_orders[oid] = row

    current = lookup_order.invoke({"order_id": current_order_id})
    cur_days = int(current.get("days_since_delivery", 0)) if current else 0

    prior = [
        o for o in combined_orders.values()
        if o.get("order_id") != current_order_id
    ]
    returns = sum(1 for o in prior if o.get("previously_returned"))
    count = len(prior)
    return {
        "prior_orders": count,
        "prior_returns": returns,
        "return_rate": round(returns / count, 2) if count else 0.0,
    }


@tool
def score_return_risk(prior_orders: int, prior_returns: int, amount_inr: int) -> dict[str, Any]:
    """Calculate a transparent demo risk score from prior returns and order value."""
    rate = prior_returns / prior_orders if prior_orders else 0.0
    rate_points = round(rate * 60)
    repeated_points = 20 if prior_returns >= 3 else 0
    value_points = 20 if amount_inr >= 10000 else 0
    score = min(100, rate_points + repeated_points + value_points)
    return {
        "score": score,
        "review_threshold": REVIEW_THRESHOLD,
        "factors": [
            f"Return rate: {prior_returns}/{prior_orders} earlier orders (+{rate_points})",
            f"Three or more prior returns (+{repeated_points})",
            f"Order value at least ₹10,000 (+{value_points})",
        ],
    }


@tool
def create_mock_refund(order_id: str) -> dict[str, str]:
    """Create a display-only refund reference; no payment service is called."""
    return {"reference": f"DEMO-{order_id}", "message": "Mock refund approved"}


class ReturnState(TypedDict, total=False):
    order_id: str
    reason: str
    order: dict[str, Any]
    eligibility: dict[str, Any]
    history: dict[str, Any]
    risk: dict[str, Any]
    refund: dict[str, str]
    decision: str
    trace: list[dict[str, str]]
    ai_analysis: str
    ai_status: str
    ai_model: str
    ai_tool_calls: list[str]
    ai_error: str


def _step(state: ReturnState, name: str, detail: str, **updates: Any) -> ReturnState:
    new_trace = list(state.get("trace", [])) + [{"step": name, "detail": detail}]
    result = dict(state)
    result["trace"] = new_trace
    result.update(updates)
    return cast(ReturnState, result)


def _lookup(state: ReturnState) -> ReturnState:
    order = lookup_order.invoke({"order_id": state["order_id"]})
    return _step(state, "Order lookup", "Order found" if order else "Order ID not found", order=order)


def _eligibility(state: ReturnState) -> ReturnState:
    order = state.get("order")
    if order:
        if order.get("status") != "Delivered":
            result = {"eligible": False, "reason": "The order has not been delivered."}
        elif order.get("category") == "Digital":
            result = {"eligible": False, "reason": "Digital products are excluded in this demo policy."}
        elif int(order.get("days_since_delivery", 0)) > RETURN_WINDOW_DAYS:
            result = {"eligible": False, "reason": "The 30-day return window has passed."}
        elif order.get("previously_returned"):
            result = {"eligible": False, "reason": "This order was already returned."}
        else:
            result = {"eligible": True, "reason": "Delivered within 30 days and eligible for return."}
    else:
        result = check_eligibility.invoke({"order_id": state["order_id"]})
    return _step(state, "Eligibility check", result["reason"], eligibility=result)


def _history(state: ReturnState) -> ReturnState:
    result = customer_history.invoke({
        "customer_id": state["order"]["customer_id"],
        "current_order_id": state["order_id"],
    })
    detail = f'{result["prior_returns"]} returns from {result["prior_orders"]} earlier orders'
    return _step(state, "Customer history", detail, history=result)


def _risk(state: ReturnState) -> ReturnState:
    history = state["history"]
    result = score_return_risk.invoke({
        "prior_orders": history["prior_orders"],
        "prior_returns": history["prior_returns"],
        "amount_inr": state["order"]["amount_inr"],
    })
    return _step(state, "Fraud risk", f'Score {result["score"]}/100', risk=result)


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        return " ".join(
            block.get("text", "") for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()
    return ""


def _ai_review(state: ReturnState, config: RunnableConfig) -> ReturnState:
    settings = config.get("configurable", {})
    api_key = settings.get("openrouter_api_key") or os.getenv("OPENROUTER_API_KEY", "")
    model_name = settings.get("openrouter_model") or os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
    if not api_key:
        return _step(
            state, "AI investigation", "Skipped: OpenRouter API key not configured",
            ai_status="not_connected", ai_analysis="", ai_tool_calls=[],
        )

    try:
        model = ChatOpenRouter(
            model=model_name,
            api_key=api_key,
            temperature=0,
            max_tokens=300,
            max_retries=1,
            timeout=25,
        )
        agent = create_agent(
            model=model,
            tools=[lookup_order, check_eligibility, customer_history, score_return_risk],
            system_prompt=(
                "You are a returns investigation agent. Use the available tools to verify the "
                "order, eligibility, customer history, and risk score before answering. "
                "Give a factual explanation in at most two short sentences. "
                "Never claim the customer committed fraud. Never promise or issue a refund. "
                "The application enforces the final policy decision."
            ),
        )
        response = agent.invoke(
            {"messages": [{"role": "user", "content": (
                f'Investigate return request for order {state["order_id"]}. '
                f'Reason: {state["reason"]}. Use the tools, then explain the evidence and '
                "whether this case merits human review."
            )}]},
            config={"recursion_limit": 16},
        )
        messages = response["messages"]
        tool_calls = [
            call["name"]
            for message in messages
            for call in getattr(message, "tool_calls", [])
        ]
        analysis = _message_text(messages[-1].content)
        if not analysis:
            raise ValueError("The model returned no explanation")
    except Exception as exc:
        return _step(
            state, "AI investigation", f"Unavailable ({type(exc).__name__}); policy workflow continued",
            ai_status="error", ai_analysis="", ai_tool_calls=[],
            ai_error=type(exc).__name__, ai_model=model_name,
        )

    trace = state.get("trace", []) + [
        {"step": "AI tool call", "detail": name} for name in tool_calls
    ] + [{"step": "AI investigation", "detail": f"Completed with {model_name}"}]
    return {
        "trace": trace,
        "ai_status": "connected",
        "ai_analysis": analysis,
        "ai_tool_calls": tool_calls,
        "ai_model": model_name,
    }


def _decision(state: ReturnState) -> ReturnState:
    decision = "review_required" if state["risk"]["score"] >= REVIEW_THRESHOLD else "auto_refund"
    detail = "Human approval required" if decision == "review_required" else "Low risk; refund can be approved"
    return _step(state, "Decision gate", detail, decision=decision)


def _refund(state: ReturnState) -> ReturnState:
    result = create_mock_refund.invoke({"order_id": state["order_id"]})
    return _step(state, "Mock refund", result["reference"], refund=result)


def _after_lookup(state: ReturnState) -> str:
    return "eligibility" if state["order"] else "not_found"


def _after_eligibility(state: ReturnState) -> str:
    return "history" if state["eligibility"]["eligible"] else "ineligible"


def _after_decision(state: ReturnState) -> str:
    return "refund" if state["decision"] == "auto_refund" else "end"


def _not_found(state: ReturnState) -> ReturnState:
    return {"decision": "not_found"}


def _ineligible(state: ReturnState) -> ReturnState:
    return {"decision": "ineligible"}


@lru_cache(maxsize=1)
def workflow():
    graph = StateGraph(ReturnState)
    graph.add_node("lookup", _lookup)
    graph.add_node("eligibility", _eligibility)
    graph.add_node("history", _history)
    graph.add_node("risk", _risk)
    graph.add_node("ai_review", _ai_review)
    graph.add_node("decision", _decision)
    graph.add_node("refund", _refund)
    graph.add_node("not_found", _not_found)
    graph.add_node("ineligible", _ineligible)
    graph.add_edge(START, "lookup")
    graph.add_conditional_edges("lookup", _after_lookup, {"eligibility": "eligibility", "not_found": "not_found"})
    graph.add_conditional_edges("eligibility", _after_eligibility, {"history": "history", "ineligible": "ineligible"})
    graph.add_edge("history", "risk")
    graph.add_edge("risk", "ai_review")
    graph.add_edge("ai_review", "decision")
    graph.add_conditional_edges("decision", _after_decision, {"refund": "refund", "end": END})
    graph.add_edge("refund", END)
    graph.add_edge("not_found", END)
    graph.add_edge("ineligible", END)
    return graph.compile()


def process_return(
    order_id: str,
    reason: str,
    *,
    openrouter_api_key: str = "",
    openrouter_model: str = DEFAULT_OPENROUTER_MODEL,
) -> ReturnState:
    """Run the complete returns workflow for a single demo request."""
    return workflow().invoke(
        {
            "order_id": order_id.strip().upper(),
            "reason": reason.strip(),
            "trace": [],
        },
        config={"configurable": {
            "openrouter_api_key": openrouter_api_key,
            "openrouter_model": openrouter_model,
        }},
    )
