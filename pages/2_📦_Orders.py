"""Page 2 – My Orders & Returns: view personal orders and submit AI-powered return requests."""

from __future__ import annotations

import os
from datetime import datetime, timezone

import streamlit as st

from ui_utils import HIDE_STREAMLIT_CHROME
from db import get_order_by_id, get_user_orders, mark_returned
from engine import DEFAULT_OPENROUTER_MODEL, ReturnState, REVIEW_THRESHOLD, RETURN_WINDOW_DAYS, create_mock_refund

# ── Auth guard ───────────────────────────────────────────────────────────────
if not st.session_state.get("user"):
    st.switch_page("app.py")

st.set_page_config(
    page_title="My Orders · ShopReturn AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(HIDE_STREAMLIT_CHROME, unsafe_allow_html=True)

user = st.session_state["user"]

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: #0d1117; color: #e6edf3; }
    .block-container { max-width: 1200px; padding-top: 0; padding-bottom: 3rem; }

    /* ─── Topbar ────────────────────────────────────────── */
    .topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, rgba(124,58,237,0.15) 0%, rgba(37,99,235,0.12) 100%);
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1.8rem;
    }
    .topbar-brand {
        font-size: 1.5rem; font-weight: 900; letter-spacing: -0.03em;
        background: linear-gradient(90deg,#a78bfa,#60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .topbar-user {
        display: flex; align-items: center; gap: .6rem;
        color: rgba(255,255,255,.65); font-size: .9rem;
    }
    .avatar {
        width: 38px; height: 38px; border-radius: 50%;
        background: linear-gradient(135deg,#7c3aed,#2563eb);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem; font-weight: 800; color: #fff;
    }

    /* ─── Sidebar ───────────────────────────────────────── */
    [data-testid="stSidebar"] { background: #0a0d14 !important; border-right: 1px solid rgba(255,255,255,.07); }

    /* ─── Order card ────────────────────────────────────── */
    .order-header {
        display: flex; justify-content: space-between; align-items: flex-start;
        margin-bottom: .75rem;
    }
    .order-id    { font-size: .75rem; font-weight: 800; letter-spacing: .1em; color: #a78bfa; text-transform: uppercase; }
    .order-date  { font-size: .78rem; color: rgba(255,255,255,.4); }
    .order-total { font-size: 1.35rem; font-weight: 900;
        background: linear-gradient(90deg,#a78bfa,#60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

    .item-row {
        display: flex; align-items: center; gap: .75rem;
        padding: .45rem .6rem; border-radius: 10px;
        background: rgba(255,255,255,.03); margin-bottom: .35rem;
        font-size: .86rem;
    }
    .item-emoji { font-size: 1.6rem; }
    .item-name  { font-weight: 600; color: #e6edf3; }
    .item-sub   { font-size: .76rem; color: rgba(255,255,255,.4); }

    /* ─── Status badges ─────────────────────────────────── */
    .badge {
        display: inline-block; padding: .22rem .65rem;
        border-radius: 999px; font-size: .75rem; font-weight: 700;
    }
    .badge-eligible  { background:rgba(34,197,94,.12); color:#4ade80; border:1px solid rgba(34,197,94,.3); }
    .badge-returned  { background:rgba(251,191,36,.1);  color:#fbbf24; border:1px solid rgba(251,191,36,.25); }
    .badge-closed    { background:rgba(239,68,68,.1);   color:#f87171; border:1px solid rgba(239,68,68,.25); }
    .badge-review    { background:rgba(251,146,60,.1);  color:#fb923c; border:1px solid rgba(251,146,60,.25); }

    /* ─── Pipeline flow strip ───────────────────────────── */
    .flow-strip {
        display: flex; align-items: center; gap: .35rem; flex-wrap: wrap;
        padding: .6rem 1rem; border-radius: 12px;
        background: rgba(96,165,250,.07); border: 1px solid rgba(96,165,250,.15);
        margin-bottom: 1rem; font-size: .78rem; color: #60a5fa; font-weight: 600;
    }
    .flow-sep { color: rgba(255,255,255,.25); }

    /* ─── Risk bar ──────────────────────────────────────── */
    .risk-wrap { background: rgba(255,255,255,.08); border-radius: 999px; height: 10px;
        overflow: hidden; margin: .4rem 0 .6rem; }
    .risk-fill { height: 100%; border-radius: 999px;
        background: linear-gradient(90deg, #22c55e 0%, #f59e0b 50%, #ef4444 100%); }

    /* ─── Buttons ───────────────────────────────────────── */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg,#7c3aed,#2563eb) !important;
        border: none !important; border-radius: 12px !important;
        font-weight: 700 !important; color: #fff !important;
        transition: transform .15s, box-shadow .15s;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(124,58,237,.4) !important;
    }
    div.stButton > button[kind="secondary"] {
        background: rgba(255,255,255,.05) !important;
        border: 1px solid rgba(255,255,255,.14) !important;
        border-radius: 10px !important; color: rgba(255,255,255,.7) !important;
    }

    div[data-baseweb="select"] { background: rgba(255,255,255,.06) !important; border-radius: 12px !important; }
    div[data-baseweb="select"] * { color: #e6edf3 !important; }
    div[data-baseweb="input"] input { background: rgba(255,255,255,.06) !important;
        border: 1px solid rgba(255,255,255,.13) !important; border-radius: 10px !important;
        color: #e6edf3 !important; }
    div[data-testid="stAlert"] { border-radius: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Topbar ────────────────────────────────────────────────────────────────────
initial = user["full_name"][0].upper()
st.markdown(
    f"""
    <div class="topbar">
      <div class="topbar-brand">📦 My Orders &amp; Returns</div>
      <div class="topbar-user">
        <div class="avatar">{initial}</div>
        <span>{user['full_name']}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:1.2rem;">
          <div style="width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#2563eb);
               display:flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:800;color:#fff;">
            {initial}
          </div>
          <div>
            <div style="font-weight:800;font-size:1.05rem;color:#e6edf3;">{user['full_name']}</div>
            <div style="font-size:.8rem;color:rgba(255,255,255,.4);">{user['email']}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🛒 Continue Shopping", use_container_width=True, type="primary"):
        st.switch_page("pages/1_🛒_Shop.py")
    st.write("")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

    st.divider()
    st.markdown(
        """
        <div style='font-size:.8rem;color:rgba(255,255,255,.35);line-height:1.6;'>
        <b style='color:rgba(255,255,255,.55)'>Return policy</b><br>
        ✔ Within 30 days of delivery<br>
        ✔ Non-digital products only<br>
        ✔ One return per order<br>
        ⚠ High-risk returns need human review
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Helpers ───────────────────────────────────────────────────────────────────
RETURN_REASONS = [
    "Product is defective / damaged",
    "Wrong item delivered",
    "Item not as described",
    "Changed my mind",
    "Duplicate / accidental order",
    "Missing parts or accessories",
    "Quality not satisfactory",
    "Other",
]

REASON_TO_ENGINE = {
    "Product is defective / damaged": "Damaged item",
    "Wrong item delivered":           "Wrong item",
    "Item not as described":          "Wrong item",
    "Changed my mind":                "Changed my mind",
    "Duplicate / accidental order":   "Changed my mind",
    "Missing parts or accessories":   "Damaged item",
    "Quality not satisfactory":       "Damaged item",
    "Other":                          "Other",
}


def _days_since(placed_at) -> int:
    if not placed_at:
        return 0
    if isinstance(placed_at, str):
        try:
            placed_at = datetime.fromisoformat(placed_at)
        except Exception:
            return 0
    if placed_at.tzinfo is None:
        placed_at = placed_at.replace(tzinfo=timezone.utc)
    return max(0, (datetime.now(timezone.utc) - placed_at).days)


def _fmt_date(placed_at) -> str:
    if not placed_at:
        return "—"
    if isinstance(placed_at, str):
        try:
            placed_at = datetime.fromisoformat(placed_at)
        except Exception:
            return "—"
    return placed_at.strftime("%d %b %Y, %I:%M %p")


def _run_return_workflow(order_doc: dict, engine_reason: str, ai_key: str, ai_model: str) -> dict:
    """Build and run a one-shot LangGraph workflow for a user order."""
    from langgraph.graph import END, START, StateGraph
    from langchain_core.runnables import RunnableConfig
    from engine import (
        _after_decision, _after_eligibility, _after_lookup,
        _decision, _eligibility, _ineligible, _not_found, _refund, _risk, _step,
        _ai_review,
    )

    oid = order_doc["order_id"]
    d_since = _days_since(order_doc.get("placed_at"))

    # Synthetic order dict that engine nodes understand
    synthetic = {
        "order_id": oid,
        "customer_id": order_doc["username"],
        "customer_name": user["full_name"],
        "product": ", ".join(i["product_name"] for i in order_doc["items"][:2]),
        "category": order_doc["items"][0]["category"] if order_doc["items"] else "Electronics",
        "amount_inr": order_doc["total_inr"],
        "quantity": sum(i["qty"] for i in order_doc["items"]),
        "days_since_delivery": d_since,
        "status": "Delivered",
        "previously_returned": order_doc.get("previously_returned", False),
        "payment_method": "Online",
        "city": "—", "state": "—",
        "shipping_days": 0,
        "return_reason": "",
    }

    def _patched_lookup(state: ReturnState) -> ReturnState:
        found = state["order_id"] == oid
        return {
            "trace": state.get("trace", []) + [{
                "step": "Order lookup",
                "detail": "Order found in your account" if found else "Order not found",
            }],
            "order": synthetic if found else {},
        }

    def _patched_history(state: ReturnState) -> ReturnState:
        # Fresh user → no prior return history
        return _step(
            state, "Customer history",
            "0 returns from 0 earlier orders",
            history={"prior_orders": 0, "prior_returns": 0, "return_rate": 0.0},
        )

    graph = StateGraph(ReturnState)
    graph.add_node("lookup",      _patched_lookup)
    graph.add_node("eligibility", _eligibility)
    graph.add_node("history",     _patched_history)
    graph.add_node("risk",        _risk)
    graph.add_node("ai_review",   _ai_review)
    graph.add_node("decision",    _decision)
    graph.add_node("refund",      _refund)
    graph.add_node("not_found",   _not_found)
    graph.add_node("ineligible",  _ineligible)
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
    wf = graph.compile()

    return wf.invoke(
        {"order_id": oid, "reason": engine_reason, "trace": []},
        config={"configurable": {
            "openrouter_api_key": ai_key or os.getenv("OPENROUTER_API_KEY", ""),
            "openrouter_model": ai_model.strip() or DEFAULT_OPENROUTER_MODEL,
        }},
    )


# ── Load user orders ──────────────────────────────────────────────────────────
orders = get_user_orders(user["username"])

if not orders:
    st.markdown(
        """
        <div style="text-align:center;padding:4rem 2rem;">
          <div style="font-size:4rem;margin-bottom:1rem;">📭</div>
          <div style="font-size:1.4rem;font-weight:800;color:#e6edf3;margin-bottom:.5rem;">No orders yet</div>
          <div style="color:rgba(255,255,255,.4);">Head to the shop and place your first order!</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🛒 Go to Shop", type="primary"):
        st.switch_page("pages/1_🛒_Shop.py")
    st.stop()

# ── Page title ────────────────────────────────────────────────────────────────
st.markdown(
    f"<h2 style='font-size:1.6rem;font-weight:800;margin-bottom:1.5rem;'>Your {len(orders)} Order{'s' if len(orders)!=1 else ''}</h2>",
    unsafe_allow_html=True,
)

# ── Render each order ─────────────────────────────────────────────────────────
for order in orders:
    oid = order["order_id"]
    already_returned = order.get("previously_returned", False)
    d_since = _days_since(order.get("placed_at"))
    window_open = d_since <= RETURN_WINDOW_DAYS

    # Badge
    if already_returned:
        badge_html = '<span class="badge badge-returned">↩ Returned</span>'
    elif not window_open:
        badge_html = '<span class="badge badge-closed">⌛ Window Closed</span>'
    else:
        badge_html = '<span class="badge badge-eligible">✔ Eligible for Return</span>'

    # Expander label
    label_emoji = "↩" if already_returned else ("⌛" if not window_open else "✅")
    expander_label = f"{label_emoji}  {oid}  ·  ₹{order['total_inr']:,}  ·  {len(order['items'])} item(s)  ·  {d_since}d ago"

    with st.expander(expander_label, expanded=False):

        # ── Order header row ─────────────────────────────────────────
        hc1, hc2 = st.columns([2, 1])
        with hc1:
            st.markdown(
                f'<div class="order-id">{oid}</div>'
                f'<div class="order-total">₹{order["total_inr"]:,}</div>'
                f'<div class="order-date">📅 Placed: {_fmt_date(order.get("placed_at"))} &nbsp;·&nbsp; {d_since}d ago</div>',
                unsafe_allow_html=True,
            )
        with hc2:
            st.markdown(f'<div style="text-align:right;padding-top:.5rem;">{badge_html}</div>', unsafe_allow_html=True)

        st.write("")

        # ── Items list ───────────────────────────────────────────────
        st.markdown("**🛍️ Items in this order:**")
        for item in order["items"]:
            st.markdown(
                f"""
                <div class="item-row">
                  <span class="item-emoji">{item.get('image_emoji','📦')}</span>
                  <div>
                    <div class="item-name">{item['product_name']}</div>
                    <div class="item-sub">{item['category']} &nbsp;·&nbsp; ₹{item['price']:,} × {item['qty']} = ₹{item['price']*item['qty']:,}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")

        # ── Return section ───────────────────────────────────────────
        if already_returned:
            ret_reason = order.get("return_reason", "—")
            st.markdown(
                f"""
                <div style="background:rgba(251,191,36,.07);border:1px solid rgba(251,191,36,.2);
                     border-radius:14px;padding:1rem 1.2rem;margin-top:.5rem;">
                  <div style="font-weight:700;color:#fbbf24;margin-bottom:.3rem;">↩ Return Processed</div>
                  <div style="font-size:.88rem;color:rgba(255,255,255,.6);">Reason: {ret_reason}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif not window_open:
            st.markdown(
                f"""
                <div style="background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.2);
                     border-radius:14px;padding:1rem 1.2rem;margin-top:.5rem;">
                  <div style="font-weight:700;color:#f87171;">⌛ Return Window Closed</div>
                  <div style="font-size:.88rem;color:rgba(255,255,255,.5);">
                    The 30-day return window expired {d_since - RETURN_WINDOW_DAYS}d ago.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:
            # ── Active return form ───────────────────────────────────
            st.markdown(
                '<div class="flow-strip">'
                '🔍 Lookup <span class="flow-sep">→</span> '
                '✅ Eligibility <span class="flow-sep">→</span> '
                '📋 History <span class="flow-sep">→</span> '
                '⚠️ Risk Score <span class="flow-sep">→</span> '
                '🤖 AI Review <span class="flow-sep">→</span> '
                '🏁 Decision'
                '</div>',
                unsafe_allow_html=True,
            )

            reason_key = f"rsn_{oid}"
            aikey_key  = f"aik_{oid}"
            aimod_key  = f"aim_{oid}"

            reason_label = st.selectbox(
                "📋 Return reason",
                RETURN_REASONS,
                key=reason_key,
            )

            with st.expander("⚙️ AI Settings (OpenRouter) — optional"):
                ai_key = st.text_input(
                    "OpenRouter API Key",
                    type="password",
                    key=aikey_key,
                    help="Leave blank for rule-based demo mode.",
                )
                ai_model = st.text_input("Model ID", value=DEFAULT_OPENROUTER_MODEL, key=aimod_key)
                st.caption("Key is only held in this session and never saved.")

            process_btn = st.button(
                "🔄 Process Return Request",
                key=f"proc_{oid}",
                type="primary",
                use_container_width=True,
            )

            result_key  = f"result_{oid}"
            rev_key     = f"rev_{oid}"
            reason_used = f"reason_used_{oid}"

            if process_btn:
                with st.spinner("Running return workflow via LangGraph…"):
                    engine_reason = REASON_TO_ENGINE.get(reason_label, "Other")
                    res = _run_return_workflow(
                        order,
                        engine_reason,
                        ai_key=ai_key if "ai_key" in dir() else "",
                        ai_model=ai_model if "ai_model" in dir() else DEFAULT_OPENROUTER_MODEL,
                    )
                st.session_state[result_key]  = res
                st.session_state[rev_key]     = None
                st.session_state[reason_used] = reason_label
                st.rerun()

            # ── Display result ───────────────────────────────────────
            res = st.session_state.get(result_key)
            if res:
                decision   = res.get("decision")
                rev_action = st.session_state.get(rev_key)
                r_label    = st.session_state.get(reason_used, "—")

                st.divider()

                # Decision banner
                if decision == "auto_refund":
                    st.success("✅ **Mock refund approved automatically!** Your return is being processed.")
                    mark_returned(oid, r_label)
                elif decision == "review_required":
                    if rev_action == "approved":
                        st.success("✅ **Human reviewer approved the mock refund!**")
                    elif rev_action == "rejected":
                        st.error("❌ **Human reviewer rejected this return.**")
                    else:
                        st.warning("⚠️ **Human approval required** — risk score exceeded threshold.")
                elif decision == "ineligible":
                    st.error("🚫 **Return ineligible** — see pipeline trace for details.")
                else:
                    st.error("❌ Order not found in workflow.")

                # ── Risk panel ───────────────────────────────────────
                if "risk" in res:
                    risk  = res["risk"]
                    score = risk["score"]
                    pct   = score / 100
                    st.markdown(f"**📊 Risk Score: {score}/100** *(review threshold: {risk['review_threshold']})*")
                    st.markdown(
                        f'<div class="risk-wrap"><div class="risk-fill" style="width:{pct*100:.0f}%"></div></div>',
                        unsafe_allow_html=True,
                    )
                    for f in risk["factors"]:
                        st.caption(f"• {f}")

                # ── AI investigation panel ───────────────────────────
                if "ai_status" in res:
                    ai_s = res["ai_status"]
                    if ai_s == "connected":
                        st.markdown("**🤖 AI Investigation**")
                        st.info(res["ai_analysis"])
                        calls = ", ".join(res.get("ai_tool_calls", [])) or "none"
                        st.caption(f"Model: {res.get('ai_model')} · Tool calls: {calls}")
                        st.caption("AI assessment is advisory only; policy gate enforces the final decision.")
                    elif ai_s == "error":
                        st.warning("🤖 OpenRouter unavailable — policy workflow completed without AI.")
                        st.caption(f"Error: {res.get('ai_error')}")
                    else:
                        st.caption("🤖 AI not connected. Add an OpenRouter key to enable AI investigation.")

                # ── Human review buttons ─────────────────────────────
                if decision == "review_required" and rev_action is None:
                    st.markdown("**👤 Human Review Action**")
                    rc1, rc2 = st.columns(2)
                    if rc1.button("✅ Approve Mock Refund", key=f"appr_{oid}", type="primary", use_container_width=True):
                        refund = create_mock_refund.invoke({"order_id": oid})
                        res["refund"] = refund
                        st.session_state[rev_key] = "approved"
                        mark_returned(oid, r_label)
                        st.rerun()
                    if rc2.button("❌ Reject Return", key=f"rej_{oid}", use_container_width=True):
                        st.session_state[rev_key] = "rejected"
                        st.rerun()

                # Refund ref
                if "refund" in res:
                    st.success(f"🧾 Mock refund reference: **{res['refund']['reference']}**")

                # ── Pipeline trace ───────────────────────────────────
                with st.expander("🔍 View Agent Pipeline Trace"):
                    for i, event in enumerate(res.get("trace", []), 1):
                        st.markdown(
                            f"<code style='color:#a78bfa;background:rgba(167,139,250,.1);padding:.1rem .4rem;border-radius:6px;font-size:.8rem;'>{i:02d}</code>"
                            f" &nbsp; <b>{event['step']}</b> — {event['detail']}",
                            unsafe_allow_html=True,
                        )
                    st.caption("LangChain agent + LangGraph workflow · No real payments · MongoDB persistence.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:rgba(255,255,255,.2);font-size:.78rem;'>ShopReturn AI · Demo · MongoDB · LangGraph · OpenRouter optional</div>",
    unsafe_allow_html=True,
)
