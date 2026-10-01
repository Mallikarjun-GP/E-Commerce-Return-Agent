"""Shared CSS utilities injected on every page."""

HIDE_STREAMLIT_CHROME = """
<style>
/* ── Hide Streamlit default header / footer / menu ────────────── */
header[data-testid="stHeader"]          { display: none !important; height: 0 !important; }
header                                  { display: none !important; height: 0 !important; }
footer                                  { display: none !important; }
#MainMenu                               { display: none !important; }
[data-testid="stToolbar"]              { display: none !important; }
[data-testid="stDecoration"]           { display: none !important; }
[data-testid="stStatusWidget"]         { display: none !important; }
.stAppHeader                            { display: none !important; }
.stAppToolbar                           { display: none !important; }
div[data-testid="stAppViewBlockContainer"] > div:first-child { padding-top: 0 !important; }
.block-container { padding-top: 0 !important; }
</style>
"""
