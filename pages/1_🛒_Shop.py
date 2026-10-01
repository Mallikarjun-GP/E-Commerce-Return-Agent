"""Page 1 – Shop: Browse products, manage cart, and place orders."""

from __future__ import annotations

import streamlit as st
from ui_utils import HIDE_STREAMLIT_CHROME
from products import CATEGORIES, PRODUCTS, get_product_by_id, get_products_by_category
from db import place_order

# ── Auth guard ───────────────────────────────────────────────────────────────
if not st.session_state.get("user"):
    st.switch_page("app.py")

st.set_page_config(
    page_title="Shop · ShopReturn AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(HIDE_STREAMLIT_CHROME, unsafe_allow_html=True)

user = st.session_state["user"]
if "cart" not in st.session_state:
    st.session_state["cart"] = {}

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: #0d1117; color: #e6edf3; }
    .block-container { max-width: 1280px; padding-top: 0rem; padding-bottom: 3rem; }

    /* ─── Topbar ─────────────────────────────────────────────── */
    .topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, rgba(124,58,237,0.15) 0%, rgba(37,99,235,0.12) 100%);
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1.8rem;
        position: sticky; top: 0; z-index: 100;
    }
    .topbar-brand {
        font-size: 1.6rem; font-weight: 900; letter-spacing: -0.03em;
        background: linear-gradient(90deg,#a78bfa,#60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .topbar-right { display: flex; align-items: center; gap: 1.2rem; }
    .topbar-user {
        display: flex; align-items: center; gap: .5rem;
        color: rgba(255,255,255,0.7); font-size: .95rem; font-weight: 500;
    }
    .topbar-user .avatar {
        width: 36px; height: 36px; border-radius: 50%;
        background: linear-gradient(135deg,#7c3aed,#2563eb);
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem; font-weight: 700; color: #fff;
    }
    .cart-badge {
        background: linear-gradient(90deg,#7c3aed,#2563eb);
        color: #fff; border-radius: 999px;
        padding: .35rem .9rem; font-size: .9rem; font-weight: 700;
        display: flex; align-items: center; gap: .4rem;
        cursor: pointer;
    }

    /* ─── Product cards ───────────────────────────────────────── */
    .product-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.2rem 1rem 1rem;
        transition: all .22s ease;
        display: flex; flex-direction: column;
        min-height: 260px;
    }
    .product-card:hover {
        border-color: rgba(167,139,250,.5);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(124,58,237,.18);
    }
    .product-emoji { font-size: 3rem; text-align: center; margin-bottom: .7rem; line-height: 1; }
    .product-name  { font-weight: 700; font-size: .92rem; color: #e6edf3; margin-bottom: .3rem; line-height: 1.35; }
    .product-desc  { font-size: .78rem; color: rgba(255,255,255,.42); flex: 1; margin-bottom: .7rem; line-height: 1.4; }
    .product-price {
        font-size: 1.2rem; font-weight: 900;
        background: linear-gradient(90deg,#a78bfa,#60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    /* ─── Category chip ───────────────────────────────────────── */
    .cat-chip {
        display: inline-flex; align-items: center; gap: .4rem;
        padding: .4rem 1rem; border-radius: 999px;
        background: rgba(167,139,250,.12);
        border: 1px solid rgba(167,139,250,.3);
        color: #a78bfa; font-size: .85rem; font-weight: 700;
        margin-bottom: 1rem; margin-top: .5rem;
    }

    /* ─── Sidebar (cart) ──────────────────────────────────────── */
    [data-testid="stSidebar"] { background: #0a0d14 !important; border-right: 1px solid rgba(255,255,255,.07); }
    [data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }

    .cart-header { font-size: 1.2rem; font-weight: 800; color: #e6edf3; margin-bottom: 1rem; }
    .cart-line {
        display: flex; align-items: center; justify-content: space-between;
        padding: .55rem 0; border-bottom: 1px solid rgba(255,255,255,.07);
        font-size: .85rem; color: rgba(255,255,255,.8);
    }
    .cart-line-name { font-weight: 600; color: #e6edf3; }
    .cart-total {
        font-size: 1.1rem; font-weight: 800; margin-top: .75rem;
        background: linear-gradient(90deg,#a78bfa,#60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    /* ─── Buttons ─────────────────────────────────────────────── */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg,#7c3aed,#2563eb) !important;
        border: none !important; border-radius: 12px !important;
        font-weight: 700 !important; color: #fff !important;
        font-size: .95rem !important;
        transition: transform .15s, box-shadow .15s;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(124,58,237,.4) !important;
    }
    div.stButton > button[kind="secondary"] {
        background: rgba(255,255,255,.06) !important;
        border: 1px solid rgba(255,255,255,.15) !important;
        border-radius: 10px !important; color: rgba(255,255,255,.75) !important;
        font-size: .85rem !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: rgba(167,139,250,.5) !important;
        color: #a78bfa !important;
    }

    /* Select + search */
    div[data-baseweb="select"] { background: rgba(255,255,255,.06) !important; border-radius: 12px !important; }
    div[data-baseweb="select"] * { color: #e6edf3 !important; }
    div[data-baseweb="input"] input { background: rgba(255,255,255,.06) !important;
        border: 1px solid rgba(255,255,255,.14) !important; border-radius: 12px !important;
        color: #e6edf3 !important; font-size: .95rem !important; }

    /* Alerts */
    div[data-testid="stAlert"] { border-radius: 14px; }

    /* Qty stepper alignment */
    .qty-box { display: flex; align-items: center; justify-content: center; gap: .4rem; padding: .25rem 0; }
    .qty-num { font-size: 1.1rem; font-weight: 800; color: #a78bfa; min-width: 28px; text-align: center; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Topbar ────────────────────────────────────────────────────────────────────
cart_count = sum(st.session_state["cart"].values())
initial = user["full_name"][0].upper()
st.markdown(
    f"""
    <div class="topbar">
      <div class="topbar-brand">🛍️ ShopReturn AI</div>
      <div class="topbar-right">
        <div class="topbar-user">
          <div class="avatar">{initial}</div>
          <span>{user['full_name']}</span>
        </div>
        <div class="cart-badge">🛒 {cart_count} item{"s" if cart_count != 1 else ""}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # User info
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:1rem;">
          <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#2563eb);
               display:flex;align-items:center;justify-content:center;font-size:1.4rem;font-weight:800;color:#fff;flex-shrink:0;">
            {initial}
          </div>
          <div>
            <div style="font-weight:700;font-size:1rem;color:#e6edf3;">{user['full_name']}</div>
            <div style="font-size:.78rem;color:rgba(255,255,255,.45);">{user['email']}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 Orders", use_container_width=True):
            st.switch_page("pages/2_📦_Orders.py")
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.switch_page("app.py")

    st.divider()

    # Cart
    st.markdown('<div class="cart-header">🛒 Your Cart</div>', unsafe_allow_html=True)
    cart = st.session_state["cart"]

    if not cart:
        st.markdown(
            "<div style='color:rgba(255,255,255,.35);font-size:.88rem;text-align:center;padding:1.5rem 0;'>Cart is empty<br><small>Add items from the shop</small></div>",
            unsafe_allow_html=True,
        )
    else:
        total = 0
        for pid, qty in list(cart.items()):
            prod = get_product_by_id(pid)
            if not prod:
                continue
            line = prod["price"] * qty
            total += line

            st.markdown(
                f"""
                <div class="cart-line">
                  <div>
                    <div class="cart-line-name">{prod['image_emoji']} {prod['name'][:20]}{'…' if len(prod['name']) > 20 else ''}</div>
                    <div style="font-size:.78rem;color:rgba(255,255,255,.45);">₹{prod['price']:,} × {qty}</div>
                  </div>
                  <div style="font-weight:700;color:#a78bfa;">₹{line:,}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            rm_col, _ = st.columns([1, 3])
            if rm_col.button("✕ Remove", key=f"rm_{pid}", use_container_width=True):
                del st.session_state["cart"][pid]
                st.rerun()

        st.markdown(f'<div class="cart-total">Total: ₹{total:,}</div>', unsafe_allow_html=True)
        st.write("")

        if st.button("✅ Place Order", type="primary", use_container_width=True):
            items = []
            for pid, qty in cart.items():
                p = get_product_by_id(pid)
                if p:
                    items.append({
                        "product_id": p["id"],
                        "product_name": p["name"],
                        "category": p["category"],
                        "price": p["price"],
                        "qty": qty,
                        "image_emoji": p["image_emoji"],
                    })
            with st.spinner("Placing order…"):
                order = place_order(user["username"], items)
            st.session_state["cart"] = {}
            st.session_state["last_order_id"] = order["order_id"]
            st.session_state["last_order_total"] = order["total_inr"]
            st.success(f"Order {order['order_id']} placed!")
            st.rerun()

        if st.button("🗑️ Clear Cart", use_container_width=True):
            st.session_state["cart"] = {}
            st.rerun()

# ── Order success banner ──────────────────────────────────────────────────────
if st.session_state.get("last_order_id"):
    oid = st.session_state.pop("last_order_id")
    tot = st.session_state.pop("last_order_total", 0)
    st.success(f"🎉 Order **{oid}** placed for ₹{tot:,}! Check **📦 Orders** in the sidebar to manage returns.")

# ── Search + Category filter ──────────────────────────────────────────────────
f_col1, f_col2 = st.columns([1.8, 3])
with f_col1:
    sel_cat = st.selectbox("📂 Category", ["All"] + CATEGORIES, label_visibility="collapsed")
with f_col2:
    search = st.text_input("🔍 Search", placeholder="Search products…", label_visibility="collapsed")

filtered = PRODUCTS if sel_cat == "All" else get_products_by_category(sel_cat)
if search.strip():
    q = search.lower()
    filtered = [p for p in filtered if q in p["name"].lower() or q in p["description"].lower()]

st.write("")

# ── Product Grid ──────────────────────────────────────────────────────────────
if not filtered:
    st.info("No products found. Try a different search or category.")
else:
    from collections import defaultdict
    by_cat: dict = defaultdict(list)
    for p in filtered:
        by_cat[p["category"]].append(p)

    for cat, prods in by_cat.items():
        st.markdown(f'<div class="cat-chip">📂 {cat}</div>', unsafe_allow_html=True)
        cols = st.columns(5, gap="medium")
        for idx, prod in enumerate(prods):
            with cols[idx % 5]:
                st.markdown(
                    f"""
                    <div class="product-card">
                      <div class="product-emoji">{prod['image_emoji']}</div>
                      <div class="product-name">{prod['name']}</div>
                      <div class="product-desc">{prod['description']}</div>
                      <div class="product-price">₹{prod['price']:,}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                in_cart = st.session_state["cart"].get(prod["id"], 0)
                if in_cart:
                    c1, c2, c3 = st.columns([1, 1.2, 1])
                    if c1.button("➖", key=f"dec_{prod['id']}", use_container_width=True):
                        if st.session_state["cart"][prod["id"]] > 1:
                            st.session_state["cart"][prod["id"]] -= 1
                        else:
                            del st.session_state["cart"][prod["id"]]
                        st.rerun()
                    c2.markdown(
                        f"<div style='text-align:center;padding:.4rem 0;color:#a78bfa;font-size:1.1rem;font-weight:800;'>{in_cart}</div>",
                        unsafe_allow_html=True,
                    )
                    if c3.button("➕", key=f"inc_{prod['id']}", use_container_width=True):
                        st.session_state["cart"][prod["id"]] += 1
                        st.rerun()
                else:
                    if st.button("🛒 Add", key=f"add_{prod['id']}", use_container_width=True, type="primary"):
                        st.session_state["cart"][prod["id"]] = 1
                        st.rerun()
        st.write("")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:rgba(255,255,255,.2);font-size:.78rem;'>ShopReturn AI · Demo · No real payments · MongoDB + LangGraph</div>",
    unsafe_allow_html=True,
)
