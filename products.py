"""Static product catalog – 6 categories, 10 items each."""

from __future__ import annotations

CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Kitchen",
    "Books",
    "Sports & Fitness",
    "Beauty & Personal Care",
]

PRODUCTS: list[dict] = [
    # ── Electronics ──────────────────────────────────────────────
    {"id": "E001", "name": "Wireless Noise-Cancelling Headphones", "category": "Electronics", "price": 7999,  "image_emoji": "🎧", "description": "Premium over-ear headphones with 30-hr battery and active noise cancellation."},
    {"id": "E002", "name": "Smart LED Desk Lamp",                  "category": "Electronics", "price": 1499,  "image_emoji": "💡", "description": "USB-C powered, 3 colour modes, touch dimmer and built-in wireless charger."},
    {"id": "E003", "name": "Portable Bluetooth Speaker",           "category": "Electronics", "price": 2499,  "image_emoji": "🔊", "description": "360° surround sound, IPX7 waterproof, 12-hr playtime."},
    {"id": "E004", "name": "USB-C Fast Charger (65W)",             "category": "Electronics", "price": 999,   "image_emoji": "⚡", "description": "GaN technology, charges laptop + phone simultaneously."},
    {"id": "E005", "name": "Smart Watch Pro",                      "category": "Electronics", "price": 12999, "image_emoji": "⌚", "description": "AMOLED display, SpO₂ & ECG sensor, 7-day battery."},
    {"id": "E006", "name": "Mechanical Gaming Keyboard",           "category": "Electronics", "price": 4499,  "image_emoji": "⌨️", "description": "TKL layout, RGB backlit, Cherry-compatible blue switches."},
    {"id": "E007", "name": "4K Webcam",                            "category": "Electronics", "price": 5999,  "image_emoji": "📷", "description": "Autofocus, built-in ring light, privacy shutter, plug-and-play."},
    {"id": "E008", "name": "Wireless Mouse (Ergonomic)",           "category": "Electronics", "price": 1799,  "image_emoji": "🖱️", "description": "Silent clicks, 3 DPI settings, Bluetooth + 2.4 GHz dongle."},
    {"id": "E009", "name": "Power Bank 20000mAh",                  "category": "Electronics", "price": 1999,  "image_emoji": "🔋", "description": "Dual USB-A + USB-C, 22.5W fast charge, LED charge indicator."},
    {"id": "E010", "name": "Smart Plug (Wi-Fi)",                   "category": "Electronics", "price": 699,   "image_emoji": "🔌", "description": "Works with Alexa/Google Home, energy monitoring, scheduling."},

    # ── Clothing ─────────────────────────────────────────────────
    {"id": "C001", "name": "Premium Cotton Crew-neck T-shirt",     "category": "Clothing", "price": 599,  "image_emoji": "👕", "description": "180 GSM, enzyme washed, pre-shrunk, available S-3XL."},
    {"id": "C002", "name": "Slim-fit Chino Trousers",              "category": "Clothing", "price": 1299, "image_emoji": "👖", "description": "Stretch cotton blend, 4-way comfort, machine washable."},
    {"id": "C003", "name": "Hooded Zip-up Sweatshirt",             "category": "Clothing", "price": 1799, "image_emoji": "🧥", "description": "80% cotton, kangaroo pocket, ribbed cuffs, unisex fit."},
    {"id": "C004", "name": "Running Shorts (7\")",                  "category": "Clothing", "price": 699,  "image_emoji": "🩳", "description": "Quick-dry polyester, inner liner, reflective strip."},
    {"id": "C005", "name": "Formal Oxford Shirt",                  "category": "Clothing", "price": 1499, "image_emoji": "👔", "description": "100% cotton, non-iron finish, slim & regular fit."},
    {"id": "C006", "name": "Puffer Winter Jacket",                 "category": "Clothing", "price": 2999, "image_emoji": "🧤", "description": "Lightweight insulation, windproof shell, packable."},
    {"id": "C007", "name": "Yoga Leggings (High-waist)",           "category": "Clothing", "price": 899,  "image_emoji": "👚", "description": "4-way stretch, squat-proof, hidden waistband pocket."},
    {"id": "C008", "name": "Canvas Sneakers",                      "category": "Clothing", "price": 1099, "image_emoji": "👟", "description": "Vulcanised rubber sole, breathable canvas, multiple colours."},
    {"id": "C009", "name": "Wide-brim Sun Hat",                    "category": "Clothing", "price": 499,  "image_emoji": "🎩", "description": "UPF 50+, adjustable chinstrap, foldable brim."},
    {"id": "C010", "name": "Merino Wool Scarf",                    "category": "Clothing", "price": 799,  "image_emoji": "🧣", "description": "Extra-fine 17.5μm merino, 180 cm length, 10 colours."},

    # ── Home & Kitchen ───────────────────────────────────────────
    {"id": "H001", "name": "Stainless Steel Cookware Set (5-pc)",  "category": "Home & Kitchen", "price": 3499, "image_emoji": "🍳", "description": "Tri-ply construction, induction compatible, dishwasher safe."},
    {"id": "H002", "name": "Electric Kettle (1.7 L)",              "category": "Home & Kitchen", "price": 899,  "image_emoji": "♨️", "description": "1500W, boil-dry protection, auto shut-off, stainless interior."},
    {"id": "H003", "name": "Air Purifier (HEPA H13)",              "category": "Home & Kitchen", "price": 7999, "image_emoji": "🌬️", "description": "Covers 300 sq ft, PM2.5 display, sleep mode, 3-stage filter."},
    {"id": "H004", "name": "Bamboo Cutting Board (3-pc)",          "category": "Home & Kitchen", "price": 799,  "image_emoji": "🪵", "description": "Anti-bacterial, groove for juice collection, non-slip feet."},
    {"id": "H005", "name": "Non-stick Wok (32 cm)",                "category": "Home & Kitchen", "price": 1299, "image_emoji": "🥘", "description": "Granite-coated interior, heat-resistant handle, induction base."},
    {"id": "H006", "name": "Vacuum Insulated Water Bottle",        "category": "Home & Kitchen", "price": 599,  "image_emoji": "🫙", "description": "1 L, keeps cold 24 hr / hot 12 hr, leak-proof lid."},
    {"id": "H007", "name": "Digital Kitchen Scale",                "category": "Home & Kitchen", "price": 449,  "image_emoji": "⚖️", "description": "5 kg max, 1 g precision, tare function, slim design."},
    {"id": "H008", "name": "Silicone Baking Mat (2-pack)",         "category": "Home & Kitchen", "price": 349,  "image_emoji": "🧁", "description": "Food-grade, reusable, fits half-sheet pans, non-stick."},
    {"id": "H009", "name": "Aromatherapy Diffuser",                "category": "Home & Kitchen", "price": 999,  "image_emoji": "🕯️", "description": "300 ml, 7-colour LED, auto shut-off, whisper-quiet."},
    {"id": "H010", "name": "Wall-mounted Dish Rack",               "category": "Home & Kitchen", "price": 1199, "image_emoji": "🍽️", "description": "304 stainless steel, drip tray, adjustable hooks."},

    # ── Books ────────────────────────────────────────────────────
    {"id": "B001", "name": "Atomic Habits – James Clear",           "category": "Books", "price": 399,  "image_emoji": "📗", "description": "Practical framework for building good habits and breaking bad ones."},
    {"id": "B002", "name": "Deep Work – Cal Newport",               "category": "Books", "price": 349,  "image_emoji": "📘", "description": "Rules for focused success in a distracted world."},
    {"id": "B003", "name": "The Psychology of Money",               "category": "Books", "price": 299,  "image_emoji": "📙", "description": "Timeless lessons on wealth, greed, and happiness."},
    {"id": "B004", "name": "Zero to One – Peter Thiel",             "category": "Books", "price": 349,  "image_emoji": "📕", "description": "Notes on startups and how to build the future."},
    {"id": "B005", "name": "Dune – Frank Herbert",                  "category": "Books", "price": 499,  "image_emoji": "📚", "description": "The definitive science-fiction masterpiece – complete edition."},
    {"id": "B006", "name": "Clean Code – Robert C. Martin",         "category": "Books", "price": 699,  "image_emoji": "💻", "description": "A handbook of agile software craftsmanship."},
    {"id": "B007", "name": "The Lean Startup – Eric Ries",          "category": "Books", "price": 399,  "image_emoji": "🚀", "description": "How today's entrepreneurs use continuous innovation."},
    {"id": "B008", "name": "Sapiens – Yuval Noah Harari",           "category": "Books", "price": 449,  "image_emoji": "🦴", "description": "A brief history of humankind, from Stone Age to today."},
    {"id": "B009", "name": "The Pragmatic Programmer",              "category": "Books", "price": 749,  "image_emoji": "⚙️", "description": "Your journey to mastery – 20th anniversary edition."},
    {"id": "B010", "name": "Ikigai – Héctor García",                "category": "Books", "price": 249,  "image_emoji": "🌸", "description": "The Japanese secret to a long and happy life."},

    # ── Sports & Fitness ─────────────────────────────────────────
    {"id": "S001", "name": "Resistance Bands Set (5 levels)",       "category": "Sports & Fitness", "price": 599,  "image_emoji": "💪", "description": "Natural latex, colour-coded by tension, door anchor included."},
    {"id": "S002", "name": "Yoga Mat (6 mm, non-slip)",             "category": "Sports & Fitness", "price": 799,  "image_emoji": "🧘", "description": "TPE foam, alignment lines, carrying strap, sweat-resistant."},
    {"id": "S003", "name": "Adjustable Dumbbell (20 kg)",           "category": "Sports & Fitness", "price": 4999, "image_emoji": "🏋️", "description": "15 weight settings, space-saving design, knurled grip."},
    {"id": "S004", "name": "Jump Rope (speed cable)",               "category": "Sports & Fitness", "price": 349,  "image_emoji": "🪢", "description": "Ball-bearing handle, adjustable steel cable, 3 m length."},
    {"id": "S005", "name": "Foam Roller (60 cm)",                   "category": "Sports & Fitness", "price": 499,  "image_emoji": "🔵", "description": "High-density EVA, textured surface for deep-tissue massage."},
    {"id": "S006", "name": "Running Shoes (lightweight)",           "category": "Sports & Fitness", "price": 2999, "image_emoji": "👟", "description": "Breathable mesh upper, cushioned midsole, EU 38-46."},
    {"id": "S007", "name": "Gym Gloves (full-finger)",              "category": "Sports & Fitness", "price": 399,  "image_emoji": "🥊", "description": "Anti-slip palm pad, wrist wrap, S-XL sizes."},
    {"id": "S008", "name": "Whey Protein Powder (1 kg)",            "category": "Sports & Fitness", "price": 1699, "image_emoji": "🥛", "description": "24 g protein/serving, 5 g BCAAs, chocolate & vanilla."},
    {"id": "S009", "name": "Smart Body Fat Scale",                  "category": "Sports & Fitness", "price": 1299, "image_emoji": "⚖️", "description": "Bioelectrical impedance, BMI/muscle/fat %, app sync."},
    {"id": "S010", "name": "Insulated Sports Water Bottle",         "category": "Sports & Fitness", "price": 699,  "image_emoji": "💧", "description": "750 ml, leak-proof flip lid, keeps cold 8 hr."},

    # ── Beauty & Personal Care ────────────────────────────────────
    {"id": "P001", "name": "Vitamin C Face Serum (30 ml)",          "category": "Beauty & Personal Care", "price": 799,  "image_emoji": "✨", "description": "15% L-ascorbic acid, hyaluronic acid, brightening & anti-aging."},
    {"id": "P002", "name": "Electric Toothbrush",                   "category": "Beauty & Personal Care", "price": 1499, "image_emoji": "🦷", "description": "Sonic vibration, 3 modes, 2-min timer, USB rechargeable."},
    {"id": "P003", "name": "SPF 50 Sunscreen (100 ml)",             "category": "Beauty & Personal Care", "price": 349,  "image_emoji": "☀️", "description": "PA++++, lightweight gel, non-greasy, suitable for oily skin."},
    {"id": "P004", "name": "Hair Dryer (2000W)",                    "category": "Beauty & Personal Care", "price": 1999, "image_emoji": "💇", "description": "Ionic frizz control, 3 heat / 2 speed settings, cool-shot."},
    {"id": "P005", "name": "Natural Deodorant Stick",               "category": "Beauty & Personal Care", "price": 299,  "image_emoji": "🌿", "description": "Aluminium-free, baking soda, 72-hr protection, vegan."},
    {"id": "P006", "name": "Sheet Mask Bundle (10-pack)",           "category": "Beauty & Personal Care", "price": 499,  "image_emoji": "🎭", "description": "Hyaluronic acid + collagen, 10 different variants."},
    {"id": "P007", "name": "Men's Grooming Kit (6-pc)",             "category": "Beauty & Personal Care", "price": 899,  "image_emoji": "🪮", "description": "Beard comb, oil, balm, trimming scissors, exfoliating face wash."},
    {"id": "P008", "name": "Retinol Night Cream (50 ml)",           "category": "Beauty & Personal Care", "price": 649,  "image_emoji": "🌙", "description": "0.3% retinol, ceramides, niacinamide, reduces fine lines."},
    {"id": "P009", "name": "Lip Balm SPF 30 (3-pack)",             "category": "Beauty & Personal Care", "price": 199,  "image_emoji": "💋", "description": "Beeswax + shea butter, tinted & clear options."},
    {"id": "P010", "name": "Jade Facial Roller",                    "category": "Beauty & Personal Care", "price": 549,  "image_emoji": "💆", "description": "Dual-head, natural jade stone, reduces puffiness."},
]


def get_products_by_category(category: str) -> list[dict]:
    return [p for p in PRODUCTS if p["category"] == category]


def get_product_by_id(product_id: str) -> dict | None:
    return next((p for p in PRODUCTS if p["id"] == product_id), None)
