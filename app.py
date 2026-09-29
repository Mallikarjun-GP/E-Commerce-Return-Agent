"""Streamlit UI for the e-commerce returns agent demo."""

import os

import streamlit as st

from engine import DEFAULT_OPENROUTER_MODEL, create_mock_refund, orders, process_return


st.set_page_config(page_title="Returns Agent", page_icon="↩", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #f7f8fa; color: #17212f; }
    .block-container { max-width: 1120px; padding-top: 4rem; padding-bottom: 3rem; }
    h1, h2, h3 { letter-spacing: -0.035em; }
    h1 { font-size: 2.5rem !important; margin-bottom: .25rem; }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { border-radius: 18px; }
    div.stButton > button[kind="primary"] { background: #1b5edb; border-radius: 10px; }
    .eyebrow { color: #1b5edb; font-size: .8rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
    .muted { color: #64748b; }
    .flow { color: #475569; background: #eef3ff; padding: .85rem 1rem; border-radius: 12px; font-size: .94rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def rupees(value: int) -> str:
    return f"₹{value:,.0f}"


st.markdown('<div class="eyebrow">Agentic AI demo</div>', unsafe_allow_html=True)
st.title("E-commerce Returns Agent")
st.markdown(
    '<p class="muted">Submit a return request and see each tool call, risk score, and decision.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="flow">Order lookup&nbsp; → &nbsp;Eligibility&nbsp; → &nbsp;Customer history&nbsp; → &nbsp;Risk score&nbsp; → &nbsp;AI investigation&nbsp; → &nbsp;Decision</div>',
    unsafe_allow_html=True,
)
st.write("")

grid_rows = []
for item in orders():
    if item["previously_returned"]:
        return_status = "Already returned"
    elif item["category"] == "Digital":
        return_status = "Excluded item"
    elif item["days_since_delivery"] > 30:
        return_status = "Window closed"
    else:
        return_status = "Can request"
    grid_rows.append({
        "Order ID": item["order_id"],
        "Product": item["product"],
        "Customer": item["customer_name"],
        "Category": item["category"],
        "Price": rupees(item["amount_inr"]),
        "Qty": item["quantity"],
        "Payment": item["payment_method"],
        "City": item["city"],
        "Delivered": f'{item["days_since_delivery"]} days ago',
        "Status": return_status,
    })

with st.container(border=True):
    st.subheader("Orders")
    st.caption("Click a row to choose the order you want to return.")
    selected_row = st.dataframe(
        grid_rows,
        hide_index=True,
        width="stretch",
        height=450,
        on_select="rerun",
        selection_mode="single-row-required",
        key="order_grid",
    )["selection"]["rows"][0]

selected_order = orders()[selected_row]
order_id = selected_order["order_id"]
if st.session_state.get("selected_order_id") != order_id:
    st.session_state["selected_order_id"] = order_id
    st.session_state.pop("result", None)
    st.session_state["review_action"] = None

st.write("")
left, right = st.columns([0.93, 1.25], gap="large")
with left:
    with st.container(border=True):
        st.subheader("Return request")
        st.write(f'**Selected:** `{order_id}` · {selected_order["product"]}')
        reason = st.selectbox("Return reason", ["Damaged item", "Wrong item", "Changed my mind", "Other"])
        with st.expander("AI connection · OpenRouter"):
            ai_key = st.text_input(
                "OpenRouter API key",
                type="password",
                help="Leave blank if OPENROUTER_API_KEY is already set in your terminal.",
            )
            ai_model = st.text_input("Model ID", value=DEFAULT_OPENROUTER_MODEL)
            st.caption("The key is held in this Streamlit session and sent to OpenRouter for the AI request; it is not saved to a file.")
        if ai_key or os.getenv("OPENROUTER_API_KEY"):
            st.caption("AI investigation enabled for eligible returns.")
        else:
            st.caption("Add an OpenRouter key to enable AI investigation. Policy demo still works without one.")
        submitted = st.button("Process return", type="primary", use_container_width=True)
        st.caption("Refunds are simulated; no payment is made.")

with right:
    if submitted:
        st.session_state["result"] = process_return(
            order_id, reason,
            openrouter_api_key=ai_key,
            openrouter_model=ai_model.strip() or DEFAULT_OPENROUTER_MODEL,
        )
        st.session_state["review_action"] = None

    result = st.session_state.get("result")
    if not result:
        with st.container(border=True):
            st.subheader("Decision workspace")
            st.info("Select an order in the grid, then click Process return.")
            st.write("The result will show the order, the path taken, and the final decision.")
    else:
        decision = result["decision"]
        order = result.get("order")
        if decision == "auto_refund":
            st.success("Mock refund approved")
        elif decision == "review_required":
            action = st.session_state.get("review_action")
            if action == "approved":
                st.success("Human approved the mock refund")
            elif action == "rejected":
                st.error("Human rejected the return")
            else:
                st.warning("Human approval required")
        elif decision == "ineligible":
            st.error("Return ineligible")
        else:
            st.error("Order not found")

        if order:
            with st.container(border=True):
                st.subheader(order["product"])
                st.caption(f'{order["order_id"]} · {order["customer_name"]} · {order["category"]}')
                a, b, c, d = st.columns(4)
                a.metric("Order value", rupees(order["amount_inr"]))
                b.metric("Delivered", f'{order["days_since_delivery"]} days ago')
                c.metric("Earlier returns", str(result.get("history", {}).get("prior_returns", "—")))
                d.metric("Qty ordered", str(order["quantity"]))
                st.write(f'**Reason:** {result["reason"]}  ·  **Payment:** {order["payment_method"]}  ·  **Ship to:** {order["city"]}, {order["state"]}')

        if "risk" in result:
            with st.container(border=True):
                st.subheader("Risk assessment")
                st.metric("Risk score", f'{result["risk"]["score"]}/100')
                st.progress(result["risk"]["score"] / 100)
                for factor in result["risk"]["factors"]:
                    st.write(f"• {factor}")
                st.caption("Demo heuristic, not a trained fraud model. Scores ≥60 need human review.")

        if "ai_status" in result:
            with st.container(border=True):
                st.subheader("AI investigation")
                if result["ai_status"] == "connected":
                    st.write(result["ai_analysis"])
                    tool_names = ", ".join(result["ai_tool_calls"]) or "none"
                    st.caption(f'Model: {result["ai_model"]} · AI tool calls: {tool_names}')
                    st.caption("AI assessment is advisory. Eligibility and refund routing are enforced by the workflow.")
                elif result["ai_status"] == "error":
                    st.warning("OpenRouter could not complete the investigation. Check the key and model ID; the policy decision still ran.")
                    st.caption(f'Error type: {result["ai_error"]}')
                else:
                    st.info("AI not connected. Add an OpenRouter API key to run the investigation.")

        if decision == "review_required" and st.session_state.get("review_action") is None:
            approve, reject = st.columns(2)
            if approve.button("Approve mock refund", type="primary", use_container_width=True):
                refund = create_mock_refund.invoke({"order_id": result["order_id"]})
                result["refund"] = refund
                result["trace"].append({"step": "Human approval", "detail": "Reviewer approved the return"})
                result["trace"].append({"step": "Mock refund", "detail": refund["reference"]})
                st.session_state["review_action"] = "approved"
                st.rerun()
            if reject.button("Reject return", use_container_width=True):
                result["trace"].append({"step": "Human review", "detail": "Reviewer rejected the return"})
                st.session_state["review_action"] = "rejected"
                st.rerun()

        if "refund" in result:
            st.caption(f'Mock refund reference: {result["refund"]["reference"]}')

        with st.container(border=True):
            st.subheader("Agent pipeline")
            for index, event in enumerate(result["trace"], 1):
                st.write(f'**{index:02d} · {event["step"]}**  —  {event["detail"]}')
            st.caption("A LangChain agent investigates with tools inside the LangGraph workflow. Policy checks control the final action.")

st.divider()
st.caption("Class demo · Local sample data · OpenRouter AI optional · Rule-based refund gate · No real payments")
