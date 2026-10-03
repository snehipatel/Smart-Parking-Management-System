"""
Smart Parking Management System - Main Streamlit Application
Description: Advanced parking management with real-time visualization and rush prediction
Pixel-perfect design matching user reference UI
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import re
import hashlib
import os
import base64
from streamlit_autorefresh import st_autorefresh
from parking_logic import ParkingManager

ADMIN_PASSWORD_HASH = hashlib.sha256("admin@123".encode()).hexdigest()

# Page configuration
st.set_page_config(
    page_title="Smart Parking Management System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Safe autorefresh every 2 seconds for live clock/metrics
with st.sidebar:
    st_autorefresh(interval=2000, key="global_clock_ticker")

# Helper to load image as base64 data URI
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return ""

def clean_html(html_str):
    """Strips leading whitespace from every line so Streamlit markdown parser never treats it as a code block"""
    return "\n".join(line.strip() for line in html_str.strip().splitlines())

SIDEBAR_CAR_URI = get_image_base64("assets/sidebar_car.png")
PARKING_LAYOUT_URI = get_image_base64("assets/parking_layout_graphic.png")

# ───────────────────────────────────────────────────────────
# PIXEL-PERFECT LIGHT THEME CSS MATCHING REFERENCE IMAGE
# ───────────────────────────────────────────────────────────
st.markdown(clean_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-page: #f4f6fc;
    --card-bg: #ffffff;
    --text-navy: #1e293b;
    --text-muted: #64748b;
    --text-light: #94a3b8;
    --purple-main: #6c5dd3;
    --purple-dark: #5a4bcf;
    --purple-light: #eef0ff;
    --green-accent: #22c55e;
    --green-soft: #f0fdf4;
    --border-light: #edf2f7;
    --radius-card: 18px;
    --radius-sm: 12px;
}

/* Base resets */
html, body, [data-testid="stAppViewContainer"], .main, [data-testid="stApp"] {
    background-color: var(--bg-page) !important;
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
    color: var(--text-navy) !important;
}

.block-container {
    padding: 1.2rem 2.2rem 2.5rem 2.2rem !important;
    max-width: 100% !important;
}

/* Hide Streamlit default header/footer elements */
#MainMenu, footer, header { visibility: hidden !important; height: 0 !important; }

/* ─── SIDEBAR STYLING ─── */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #edf2f7 !important;
    box-shadow: 2px 0 16px rgba(0, 0, 0, 0.02) !important;
    padding-top: 0.5rem !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1rem 1.2rem !important;
    display: flex;
    flex-direction: column;
}

/* Sidebar Logo */
.brand-logo-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.4rem 0 1.5rem 0.2rem;
}

.brand-icon-box {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #6c5dd3, #5a4bcf);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(108, 93, 211, 0.3);
    flex-shrink: 0;
}

.brand-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #1e293b;
    line-height: 1.2;
    letter-spacing: -0.3px;
}

.brand-sub {
    font-size: 0.76rem;
    color: #94a3b8;
    font-weight: 500;
}

/* Hide Radio Label */
[data-testid="stSidebar"] [data-testid="stRadio"] > label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] div:has(> [data-testid="stRadio"]) label:first-child:not(:has(input)) {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Hide Radio Circles Completely */
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 3px !important;
}

/* Sidebar Navigation Items */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    padding: 0.56rem 1rem !important;
    border-radius: 12px !important;
    margin: 0 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    cursor: pointer !important;
    transition: all 0.18s ease-in-out !important;
    background: transparent !important;
    border: none !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #f4f6fc !important;
    color: #6c5dd3 !important;
}

/* Active Nav Pill: Pure solid purple gradient, white text */
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(135deg, #6c5dd3 0%, #5a4bcf 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 5px 15px rgba(108, 93, 211, 0.3) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p,
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
    color: #ffffff !important;
}

/* Inject SYSTEM Section Header above Settings (the 7th item) */
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(7) {
    margin-top: 1.2rem !important;
    position: relative !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(7)::before {
    content: "SYSTEM";
    position: absolute;
    top: -1.15rem;
    left: 0.5rem;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 1.5px;
    color: #94a3b8;
    pointer-events: none;
}

/* Sidebar Car Illustration */
.sidebar-car-container {
    margin-top: 1.8rem;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
}

.sidebar-car-container img {
    width: 100%;
    display: block;
    border-radius: 14px;
}

/* ─── TOP APP BAR (Search + Profile) ─── */
.top-app-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.search-box-pill {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #ffffff;
    border: 1px solid #edf2f7;
    border-radius: 14px;
    padding: 0.65rem 1.3rem;
    width: 380px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.search-icon {
    color: #94a3b8;
    font-size: 0.95rem;
}

.search-placeholder {
    color: #94a3b8;
    font-size: 0.88rem;
    font-weight: 500;
}

.profile-actions {
    display: flex;
    align-items: center;
    gap: 16px;
}

.bell-badge-btn {
    position: relative;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #ffffff;
    border: 1px solid #edf2f7;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.bell-dot {
    position: absolute;
    top: 7px;
    right: 8px;
    width: 14px;
    height: 14px;
    background: #ef4444;
    border-radius: 50%;
    border: 2px solid #ffffff;
    color: white;
    font-size: 8px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
}

.user-profile-pill {
    display: flex;
    align-items: center;
    gap: 10px;
    background: transparent;
    padding: 3px 6px;
    cursor: pointer;
}

.avatar-circle {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: #4f46e5;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.95rem;
    box-shadow: 0 2px 6px rgba(79, 70, 229, 0.25);
}

.avatar-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* ─── WELCOME BANNER & CLOCK CARD ─── */
.welcome-banner {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 1.6rem;
}

.welcome-sub-greeting {
    font-size: 0.92rem;
    color: #64748b;
    font-weight: 500;
    margin-bottom: 4px;
}

.welcome-main-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #1e293b;
    line-height: 1.2;
    letter-spacing: -0.5px;
    margin: 0;
}

.welcome-main-title span {
    color: #6c5dd3;
}

.welcome-desc {
    font-size: 0.92rem;
    color: #94a3b8;
    margin-top: 6px;
}

.clock-card-ref {
    background: #ffffff;
    border: 1px solid #edf2f7;
    border-radius: 16px;
    padding: 0.85rem 1.4rem;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
}

.clock-icon-bubble {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: #6366f1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3);
}

.clock-day-text {
    font-size: 0.74rem;
    color: #94a3b8;
    font-weight: 600;
}

.clock-date-text {
    font-size: 1.15rem;
    font-weight: 800;
    color: #1e293b;
    line-height: 1.2;
}

.clock-time-text {
    font-size: 0.78rem;
    color: #94a3b8;
    font-weight: 500;
}

/* ─── 4 TOP STAT CARDS ─── */
.kpi-card {
    background: #ffffff;
    border: 1px solid #edf2f7;
    border-radius: 18px;
    padding: 1.25rem 1.4rem;
    position: relative;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.025);
    display: flex;
    align-items: center;
    gap: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
}

.kpi-card.kpi-occupied {
    background: #f0fdf4 !important;
    border-color: #dcfce7 !important;
}

.kpi-icon-square {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.icon-sq-purple { background: #ede9fe; color: #6c5dd3; }
.icon-sq-green { background: #dcfce7; color: #16a34a; }
.icon-sq-blue { background: #e0f2fe; color: #0284c7; }
.icon-sq-amber { background: #ffedd5; color: #ea580c; }

.kpi-body {
    flex: 1;
}

.kpi-label {
    font-size: 0.78rem;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 2px;
}

.kpi-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #1e293b;
    line-height: 1.1;
}

.kpi-subtext {
    font-size: 0.73rem;
    color: #94a3b8;
    margin-top: 4px;
}

.kpi-corner-badge {
    position: absolute;
    top: 14px;
    right: 14px;
}

.badge-p-box {
    width: 26px;
    height: 26px;
    background: #ede9fe;
    color: #6c5dd3;
    font-weight: 800;
    font-size: 0.8rem;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.badge-pill-trend {
    padding: 3px 8px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
}

.trend-down { background: #dcfce7; color: #15803d; }
.trend-up { background: #dcfce7; color: #15803d; }

/* ─── SECTION CARDS (Floor-wise & Parking Layout) ─── */
.ref-section-card {
    background: #ffffff;
    border: 1px solid #edf2f7;
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.025);
    margin-bottom: 1.3rem;
}

.ref-section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.2rem;
}

.ref-section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.08rem;
    font-weight: 800;
    color: #1e293b;
}

.ref-pill-btn {
    background: #eef2ff;
    color: #6c5dd3;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 5px 14px;
    border-radius: 20px;
    cursor: pointer;
    border: none;
    text-decoration: none;
    transition: all 0.2s ease;
}

.ref-pill-btn:hover {
    background: #6c5dd3;
    color: white;
}

/* Floor Donut Layout */
.floor-columns-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    text-align: center;
}

.donut-card-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.donut-floor-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 12px;
}

.donut-ring-wrap {
    position: relative;
    width: 120px;
    height: 120px;
}

.donut-center-info {
    position: absolute;
    top: 0;
    left: 0;
    width: 120px;
    height: 120px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.donut-val-pct {
    font-size: 1.45rem;
    font-weight: 800;
    color: #1e293b;
    line-height: 1.1;
}

.donut-val-sub {
    font-size: 0.72rem;
    color: #64748b;
    font-weight: 500;
}

.donut-footer-stats {
    display: flex;
    justify-content: space-between;
    width: 100%;
    max-width: 155px;
    margin-top: 14px;
    font-size: 0.78rem;
}

.donut-stat-block {
    text-align: left;
}

.donut-stat-block.right {
    text-align: right;
}

.donut-stat-number {
    font-weight: 800;
    color: #1e293b;
}

.donut-stat-label {
    font-size: 0.68rem;
    color: #94a3b8;
    text-transform: capitalize;
}

/* Parking Layout Image inside card */
.parking-lot-img-wrap {
    border-radius: 12px;
    overflow: hidden;
    width: 100%;
    background: #2b303a;
}

.parking-lot-img-wrap img {
    width: 100%;
    height: auto;
    display: block;
    object-fit: cover;
}

.legend-bar {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 20px;
    margin-top: 12px;
    font-size: 0.76rem;
    font-weight: 600;
    color: #64748b;
}

.legend-dot-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.dot-circle {
    width: 9px;
    height: 9px;
    border-radius: 50%;
}

.dot-green { background: #22c55e; }
.dot-red { background: #ef4444; }
.dot-gray { background: #94a3b8; }

/* ─── BOTTOM ROW CARDS ─── */
/* Table in Recent Vehicle Activity */
.activity-table-clean {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
}

.activity-table-clean thead th {
    text-align: left;
    padding: 8px 8px;
    color: #94a3b8;
    font-size: 0.72rem;
    font-weight: 600;
    border-bottom: 1px solid #f1f5f9;
    white-space: nowrap !important;
}

.activity-table-clean tbody td {
    padding: 9px 8px;
    color: #475569;
    border-bottom: 1px solid #f8fafc;
    font-weight: 500;
    white-space: nowrap !important;
}

.activity-table-clean tbody tr:hover {
    background: #fbfcfe;
}

.badge-status-parked {
    background: #dcfce7;
    color: #15803d;
    font-weight: 700;
    font-size: 0.72rem;
    padding: 3px 10px;
    border-radius: 20px;
}

.badge-status-exited {
    background: #e0f2fe;
    color: #0369a1;
    font-weight: 700;
    font-size: 0.72rem;
    padding: 3px 10px;
    border-radius: 20px;
}

/* Quick Actions Cards Link Grid */
.qa-grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.qa-card-link {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.85rem 1rem;
    border-radius: 14px;
    text-decoration: none !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    cursor: pointer;
}

.qa-card-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.qa-card-purple {
    background: #eef2ff;
    border: 1px solid #e0e7ff;
}
.qa-card-purple .qa-icon-wrap { color: #4f46e5; }
.qa-card-purple .qa-card-title { color: #3730a3; }
.qa-card-purple .qa-card-arrow { color: #818cf8; }

.qa-card-red {
    background: #fff1f2;
    border: 1px solid #ffe4e6;
}
.qa-card-red .qa-icon-wrap { color: #e11d48; }
.qa-card-red .qa-card-title { color: #9f1239; }
.qa-card-red .qa-card-arrow { color: #fb7185; }

.qa-card-blue {
    background: #e0f2fe;
    border: 1px solid #bae6fd;
}
.qa-card-blue .qa-icon-wrap { color: #0284c7; }
.qa-card-blue .qa-card-title { color: #075985; }
.qa-card-blue .qa-card-arrow { color: #38bdf8; }

.qa-card-green {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
}
.qa-card-green .qa-icon-wrap { color: #059669; }
.qa-card-green .qa-card-title { color: #065f46; }
.qa-card-green .qa-card-arrow { color: #34d399; }

.qa-icon-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
}

.qa-card-title {
    font-size: 0.82rem;
    font-weight: 700;
    flex: 1;
}

.qa-card-arrow {
    font-size: 1.1rem;
    font-weight: 700;
}

/* Generic Streamlit Elements */
.stButton > button {
    background: linear-gradient(135deg, #6c5dd3, #5a4bcf) !important;
    color: #ffffff !important;
    border: none !important;
    padding: 0.65rem 1.8rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    font-size: 0.88rem !important;
    box-shadow: 0 4px 14px rgba(108, 93, 211, 0.25) !important;
}

.stTextInput > div > div > input {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    color: #1e293b !important;
    font-family: inherit !important;
    padding: 0.6rem 1rem !important;
}

.stSelectbox > div > div {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
}

.success-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 5px solid #22c55e;
    color: #166534;
    padding: 1.2rem 1.5rem;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(34, 197, 94, 0.08);
}
</style>
"""), unsafe_allow_html=True)


# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = ParkingManager()
    if st.session_state.get('first_run', True):
        st.session_state.manager.generate_sample_data()
        st.session_state.first_run = False

if "parking_in_progress" not in st.session_state:
    st.session_state.parking_in_progress = False
if "parking_success" not in st.session_state:
    st.session_state.parking_success = None
if "exit_in_progress" not in st.session_state:
    st.session_state.exit_in_progress = False
if "exit_success" not in st.session_state:
    st.session_state.exit_success = None
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "exit_error" not in st.session_state:
    st.session_state.exit_error = None

# Active navigation state
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "🏠  Dashboard"

def set_page(page_name):
    st.session_state.nav_page = page_name

def to_uppercase(key):
    if key in st.session_state and st.session_state[key]:
        st.session_state[key] = st.session_state[key].upper()

def is_valid_vehicle_number(vehicle_number):
    pattern = r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'
    return bool(re.match(pattern, vehicle_number))


# ───────────────────────────────────────────────────────────
# TOP HEADER BAR & CLOCK
# ───────────────────────────────────────────────────────────
def render_top_bar_and_welcome():
    """Renders the exact top search bar, user profile, welcome banner and clock card"""
    now = datetime.now()
    day_name = now.strftime("%A")
    date_str = now.strftime("%d %b %Y")
    time_str = now.strftime("%I:%M %p")

    # Top search bar and user profile
    st.markdown(clean_html("""
        <div class="top-app-bar">
            <div class="search-box-pill">
                <span class="search-icon">🔍</span>
                <span class="search-placeholder">Search anything...</span>
            </div>
            <div class="profile-actions">
                <div class="bell-badge-btn">
                    <span>🔔</span>
                    <span class="bell-dot">1</span>
                </div>
                <div class="user-profile-pill">
                    <div class="avatar-circle">S</div>
                    <span class="avatar-name">Admin ▾</span>
                </div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # Welcome banner & clock card
    col_welcome, col_clock = st.columns([3.4, 1.2])

    with col_welcome:
        st.markdown(clean_html("""
            <div>
                <div class="welcome-sub-greeting">Welcome Back, Admin! 👋</div>
                <h1 class="welcome-main-title">Smart Parking <span>Management System</span></h1>
                <div class="welcome-desc">Monitor, manage and optimize parking space in real-time.</div>
            </div>
        """), unsafe_allow_html=True)

    with col_clock:
        st.markdown(clean_html(f"""
            <div class="clock-card-ref">
                <div class="clock-icon-bubble">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                </div>
                <div>
                    <div class="clock-day-text">{day_name}</div>
                    <div class="clock-date-text">{date_str}</div>
                    <div class="clock-time-text">{time_str}</div>
                </div>
            </div>
        """), unsafe_allow_html=True)

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# VECTOR SVG DONUT GENERATOR
# ───────────────────────────────────────────────────────────
def generate_donut_svg_html(floor_name, vehicle_icon, vacant, total, occupied):
    avail_pct = round((vacant / total) * 100) if total > 0 else 0
    r = 44
    circumference = 2 * 3.14159265 * r # ~276.46
    offset = circumference * (1 - (avail_pct / 100.0))
    
    return clean_html(f"""
    <div class="donut-card-item">
        <div class="donut-floor-name">{floor_name}</div>
        <div class="donut-ring-wrap">
            <svg width="120" height="120" viewBox="0 0 120 120" style="transform: rotate(-90deg);">
                <circle cx="60" cy="60" r="{r}" fill="none" stroke="#eef2f6" stroke-width="12" />
                <circle cx="60" cy="60" r="{r}" fill="none" stroke="#22c55e" stroke-width="12"
                        stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                        stroke-linecap="round" />
            </svg>
            <div class="donut-center-info">
                <span class="donut-val-pct">{avail_pct}%</span>
                <span class="donut-val-sub">Available</span>
            </div>
        </div>
        <div class="donut-footer-stats">
            <div class="donut-stat-block">
                <div style="display:flex; align-items:center; gap:5px;">
                    <span style="font-size:0.9rem;">{vehicle_icon}</span>
                    <span class="donut-stat-number">{occupied} / {total}</span>
                </div>
                <div class="donut-stat-label">Occupied</div>
            </div>
            <div class="donut-stat-block right">
                <div class="donut-stat-number">{total}</div>
                <div class="donut-stat-label">Total Slots</div>
            </div>
        </div>
    </div>
    """)


# ───────────────────────────────────────────────────────────
# DASHBOARD PAGE
# ───────────────────────────────────────────────────────────
def render_dashboard():
    """Renders the main dashboard exactly as shown in the reference image"""
    render_top_bar_and_welcome()

    summary = st.session_state.manager.get_occupancy_summary()
    total_slots = summary['total_slots']
    occupied_slots = summary['occupied_slots']
    vacant_slots = summary['vacant_slots']
    occupancy = summary['overall_occupancy_rate']
    vacancy_pct = round(100 - occupancy, 1)

    # ─── 4 TOP KPI CARDS ───
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(clean_html(f"""
            <div class="kpi-card">
                <div class="kpi-icon-square icon-sq-purple">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path>
                        <circle cx="7" cy="17" r="2"></circle>
                        <circle cx="17" cy="17" r="2"></circle>
                    </svg>
                </div>
                <div class="kpi-body">
                    <div class="kpi-label">Total Slots</div>
                    <div class="kpi-value">{total_slots}</div>
                    <div class="kpi-subtext">Parking spaces available</div>
                </div>
                <div class="kpi-corner-badge">
                    <div class="badge-p-box">P</div>
                </div>
            </div>
        """), unsafe_allow_html=True)

    with k2:
        st.markdown(clean_html(f"""
            <div class="kpi-card kpi-occupied">
                <div class="kpi-icon-square icon-sq-green">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path>
                        <circle cx="7" cy="17" r="2"></circle>
                        <circle cx="17" cy="17" r="2"></circle>
                    </svg>
                </div>
                <div class="kpi-body">
                    <div class="kpi-label">Occupied</div>
                    <div class="kpi-value">{occupied_slots}</div>
                    <div class="kpi-subtext">Vehicles currently parked</div>
                </div>
                <div class="kpi-corner-badge">
                    <span class="badge-pill-trend trend-down">↓ {occupancy}%</span>
                </div>
            </div>
        """), unsafe_allow_html=True)

    with k3:
        st.markdown(clean_html(f"""
            <div class="kpi-card">
                <div class="kpi-icon-square icon-sq-blue">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="9"></circle>
                    </svg>
                </div>
                <div class="kpi-body">
                    <div class="kpi-label">Vacant</div>
                    <div class="kpi-value">{vacant_slots}</div>
                    <div class="kpi-subtext">Available parking spaces</div>
                </div>
                <div class="kpi-corner-badge">
                    <span class="badge-pill-trend trend-up">↑ {vacancy_pct}%</span>
                </div>
            </div>
        """), unsafe_allow_html=True)

    with k4:
        st.markdown(clean_html("""
            <div class="kpi-card">
                <div class="kpi-icon-square icon-sq-amber">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="20" x2="18" y2="10"></line>
                        <line x1="12" y1="20" x2="12" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="14"></line>
                    </svg>
                </div>
                <div class="kpi-body">
                    <div class="kpi-label">Rush Level</div>
                    <div class="kpi-value" style="display:flex; align-items:center; gap:8px;">
                        <span style="display:inline-block; width:12px; height:12px; background:#22c55e; border-radius:50%;"></span>
                        Low
                    </div>
                    <div class="kpi-subtext">Current parking density</div>
                </div>
            </div>
        """), unsafe_allow_html=True)

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # ─── MIDDLE ROW: FLOOR-WISE AVAILABILITY + PARKING LAYOUT ───
    col_floor, col_layout = st.columns([1.55, 1.2])

    with col_floor:
        floors = summary['floors']
        f0 = floors[0] if len(floors) > 0 else {'floor_name': 'Ground Floor (2W)', 'vacant_slots': 20, 'total_slots': 20, 'occupied_slots': 0}
        f1 = floors[1] if len(floors) > 1 else {'floor_name': 'Basement 1 (2W)', 'vacant_slots': 15, 'total_slots': 15, 'occupied_slots': 0}
        f2 = floors[2] if len(floors) > 2 else {'floor_name': 'Basement 2 (4W)', 'vacant_slots': 20, 'total_slots': 20, 'occupied_slots': 0}

        donut_0 = generate_donut_svg_html(f0['floor_name'], "🏍️", f0['vacant_slots'], f0['total_slots'], f0['occupied_slots'])
        donut_1 = generate_donut_svg_html(f1['floor_name'], "🏍️", f1['vacant_slots'], f1['total_slots'], f1['occupied_slots'])
        donut_2 = generate_donut_svg_html(f2['floor_name'], "🚗", f2['vacant_slots'], f2['total_slots'], f2['occupied_slots'])

        floor_html = f"""
            <div class="ref-section-card">
                <div class="ref-section-header">
                    <div class="ref-section-title">
                        <span style="color:#6c5dd3; font-size:1.2rem;">🏢</span>
                        Floor-wise Availability
                    </div>
                </div>
                <div class="floor-columns-grid">
                    {donut_0}
                    {donut_1}
                    {donut_2}
                </div>
            </div>
        """
        st.markdown(clean_html(floor_html), unsafe_allow_html=True)

    with col_layout:
        layout_card_html = f"""
            <div class="ref-section-card">
                <div class="ref-section-header">
                    <div class="ref-section-title">
                        <span style="color:#6c5dd3; font-size:1.2rem;">🗺️</span>
                        Parking Layout
                    </div>
                    <a href="?nav=layout" target="_self" class="ref-pill-btn">View Full</a>
                </div>
                <div class="parking-lot-img-wrap">
                    <img src="{PARKING_LAYOUT_URI}" alt="Parking Lot Map" />
                </div>
                <div class="legend-bar">
                    <div class="legend-dot-item"><span class="dot-circle dot-green"></span> Available</div>
                    <div class="legend-dot-item"><span class="dot-circle dot-red"></span> Occupied</div>
                    <div class="legend-dot-item"><span class="dot-circle dot-gray"></span> Blocked</div>
                </div>
            </div>
        """
        st.markdown(clean_html(layout_card_html), unsafe_allow_html=True)

    # ─── BOTTOM ROW: RECENT ACTIVITY + PARKING TREND + QUICK ACTIONS ───
    col_act, col_trend, col_quick = st.columns([1.5, 1.2, 0.95])

    with col_act:
        stats = st.session_state.manager.get_statistics()
        recent = stats.get("recent_bookings", [])[:4]

        # Use sample activity from reference if not enough live records
        if len(recent) < 4:
            table_records = [
                {"num": "GJ01AB1234", "type": "🚗 Car", "action": "🟢 Entry", "time": "08:05 PM", "status": "Parked", "badge": "badge-status-parked"},
                {"num": "GJ05CD5678", "type": "🏍️ Bike", "action": "🔴 Exit", "time": "07:42 PM", "status": "Exited", "badge": "badge-status-exited"},
                {"num": "GJ03EF9012", "type": "🏍️ Bike", "action": "🟢 Entry", "time": "07:20 PM", "status": "Parked", "badge": "badge-status-parked"},
                {"num": "GJ09XY3456", "type": "🚗 Car", "action": "🔴 Exit", "time": "06:55 PM", "status": "Exited", "badge": "badge-status-exited"},
            ]
        else:
            table_records = []
            for b in recent:
                vtype = "🚗 Car" if b['vehicle_type'] == "4-Wheeler" else "🏍️ Bike"
                is_active = (b['status'] == "Active")
                act = "🟢 Entry" if is_active else "🔴 Exit"
                status_txt = "Parked" if is_active else "Exited"
                badge_cls = "badge-status-parked" if is_active else "badge-status-exited"
                try:
                    t_str = datetime.fromisoformat(b['entry_time']).strftime("%I:%M %p")
                except:
                    t_str = "08:00 PM"
                table_records.append({
                    "num": b['vehicle_number'],
                    "type": vtype,
                    "action": act,
                    "time": t_str,
                    "status": status_txt,
                    "badge": badge_cls
                })

        tbody_html = ""
        for i, row in enumerate(table_records):
            tbody_html += f"""
                <tr>
                    <td style="color:#94a3b8; font-weight:600;">{i+1}</td>
                    <td style="font-weight:700; color:#1e293b;">{row['num']}</td>
                    <td>{row['type']}</td>
                    <td>{row['action']}</td>
                    <td style="color:#64748b;">{row['time']}</td>
                    <td><span class="{row['badge']}">{row['status']}</span></td>
                </tr>
            """

        act_card_html = f"""
            <div class="ref-section-card">
                <div class="ref-section-header">
                    <div class="ref-section-title">
                        <span style="color:#6c5dd3; font-size:1.2rem;">⚡</span>
                        Recent Vehicle Activity
                    </div>
                    <a href="?nav=stats" target="_self" class="ref-pill-btn">View All</a>
                </div>
                <table class="activity-table-clean">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Vehicle Number</th>
                            <th>Type</th>
                            <th>Action</th>
                            <th>Time</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tbody_html}
                    </tbody>
                </table>
            </div>
        """
        st.markdown(clean_html(act_card_html), unsafe_allow_html=True)

    with col_trend:
        trend_header_html = """
            <div class="ref-section-card" style="padding-bottom: 0.5rem;">
                <div class="ref-section-header" style="margin-bottom: 0.4rem;">
                    <div class="ref-section-title">
                        <span style="color:#6c5dd3; font-size:1.2rem;">📊</span>
                        Parking Trend
                    </div>
                    <span class="ref-pill-btn">Today ▾</span>
                </div>
            </div>
        """
        st.markdown(clean_html(trend_header_html), unsafe_allow_html=True)

        # Plotly chart matching reference image curves
        times = ["6AM", "9AM", "12PM", "3PM", "6PM", "9PM"]
        occ_vals = [2, 5, 4, 3, 2, 4]
        vac_vals = [53, 50, 51, 52, 53, 51]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times, y=occ_vals,
            mode='lines',
            name='Occupied',
            line=dict(color='#8b5cf6', width=3, shape='spline'),
            fill='tozeroy',
            fillcolor='rgba(139, 92, 246, 0.08)'
        ))
        fig.add_trace(go.Scatter(
            x=times, y=vac_vals,
            mode='lines',
            name='Vacant',
            line=dict(color='#38bdf8', width=3, shape='spline')
        ))

        fig.update_layout(
            height=180,
            margin=dict(l=25, r=10, t=10, b=25),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=False, color='#94a3b8', tickfont=dict(size=10, family='Plus Jakarta Sans')),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False, color='#94a3b8', tickfont=dict(size=10, family='Plus Jakarta Sans'), range=[0, 65]),
            legend=dict(
                orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5,
                font=dict(size=10, color='#64748b', family='Plus Jakarta Sans')
            ),
            hovermode='x unified',
        )

        st.plotly_chart(fig, use_container_width=True, key="parking_trend_ref_chart")

    with col_quick:
        quick_actions_html = """
            <div class="ref-section-card" style="margin-bottom: 0.8rem;">
                <div class="ref-section-header" style="margin-bottom: 1rem;">
                    <div class="ref-section-title">
                        <span style="color:#f59e0b; font-size:1.2rem;">⚡</span>
                        Quick Actions
                    </div>
                </div>
                <div class="qa-grid-container">
                    <a href="?nav=park" target="_self" class="qa-card-link qa-card-purple">
                        <div class="qa-icon-wrap">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path>
                                <circle cx="7" cy="17" r="2"></circle>
                                <circle cx="17" cy="17" r="2"></circle>
                            </svg>
                        </div>
                        <span class="qa-card-title">Park Vehicle</span>
                        <span class="qa-card-arrow">›</span>
                    </a>
                    <a href="?nav=exit" target="_self" class="qa-card-link qa-card-red">
                        <div class="qa-icon-wrap">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                                <polyline points="16 17 21 12 16 7"></polyline>
                                <line x1="21" y1="12" x2="9" y2="12"></line>
                            </svg>
                        </div>
                        <span class="qa-card-title">Exit Vehicle</span>
                        <span class="qa-card-arrow">›</span>
                    </a>
                    <a href="?nav=layout" target="_self" class="qa-card-link qa-card-blue">
                        <div class="qa-icon-wrap">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                                <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
                                <line x1="8" y1="2" x2="8" y2="18"></line>
                                <line x1="16" y1="6" x2="16" y2="22"></line>
                            </svg>
                        </div>
                        <span class="qa-card-title">View Layout</span>
                        <span class="qa-card-arrow">›</span>
                    </a>
                    <a href="?nav=stats" target="_self" class="qa-card-link qa-card-green">
                        <div class="qa-icon-wrap">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10"></circle>
                                <polyline points="12 6 12 12 16 14"></polyline>
                            </svg>
                        </div>
                        <span class="qa-card-title">View Statistics</span>
                        <span class="qa-card-arrow">›</span>
                    </a>
                </div>
            </div>
        """
        st.markdown(clean_html(quick_actions_html), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# OTHER FUNCTIONAL PAGES (Park, Exit, Layout, Stats, Settings)
# ───────────────────────────────────────────────────────────
def render_park_vehicle():
    render_top_bar_and_welcome()
    st.markdown('<div style="font-size:1.4rem; font-weight:800; color:#1e293b; margin-bottom:1rem;">🅿️ Park Your Vehicle</div>', unsafe_allow_html=True)

    if st.session_state.parking_in_progress and not st.session_state.parking_success:
        st.info("🔄 Finding best parking slot...")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "Vehicle Registration Number",
            placeholder="e.g., GJ01AB1234",
            key="park_vehicle_number",
            on_change=to_uppercase,
            args=("park_vehicle_number",)
        )
        v_num = st.session_state.get("park_vehicle_number", "").strip()
        if v_num:
            if is_valid_vehicle_number(v_num):
                st.success("✅ Vehicle number format is valid")
            else:
                st.error("❌ Invalid format (e.g., GJ01AB1234)")

    with col2:
        v_type = st.selectbox("Vehicle Type", ["2-Wheeler", "4-Wheeler"], key="park_vehicle_type")

    if v_type:
        available_slots = st.session_state.manager.get_all_available_slots(v_type)
        if available_slots:
            st.info(f"✅ {len(available_slots)} slots available for {v_type}")

    st.markdown("<p style='text-align:center; color:#94a3b8; font-size:13px;'>ⓘ Slot will be assigned automatically based on nearest distance</p>", unsafe_allow_html=True)

    if st.button("🅿️ Find & Park in Best Slot", use_container_width=True, disabled=st.session_state.parking_in_progress):
        st.session_state.parking_in_progress = True
        st.session_state.parking_success = None

        if not v_num:
            st.error("❌ Please enter vehicle number")
            st.session_state.parking_in_progress = False
        elif not is_valid_vehicle_number(v_num):
            st.error("❌ Invalid vehicle number format")
            st.session_state.parking_in_progress = False
        else:
            success, message, slot_info = st.session_state.manager.park_vehicle(v_num, v_type)
            if success:
                st.session_state.parking_success = {
                    "message": message,
                    "slot_id": slot_info["slot_id"],
                    "vehicle": v_num,
                    "timestamp": time.time()
                }
            else:
                st.error(message)
            st.session_state.parking_in_progress = False

    if st.session_state.parking_success:
        data = st.session_state.parking_success
        if (time.time() - data["timestamp"]) < 30:
            st.markdown(clean_html(f"""
                <div class="success-box">
                    <h3 style="margin:0 0 8px 0; color:#166534;">✅ Vehicle parked successfully</h3>
                    <p style="margin:4px 0;"><strong>Assigned Slot:</strong> {data['slot_id']}</p>
                    <p style="margin:4px 0;"><strong>Vehicle:</strong> {data['vehicle']}</p>
                </div>
            """), unsafe_allow_html=True)
        else:
            st.session_state.parking_success = None


def render_exit_vehicle():
    render_top_bar_and_welcome()
    st.markdown('<div style="font-size:1.4rem; font-weight:800; color:#1e293b; margin-bottom:1rem;">🚪 Exit Vehicle</div>', unsafe_allow_html=True)

    st.text_input(
        "Vehicle Registration Number",
        placeholder="e.g., GJ01AB1234",
        key="exit_vehicle_number",
        on_change=to_uppercase,
        args=("exit_vehicle_number",),
    )
    v_num = st.session_state.get("exit_vehicle_number", "").strip()

    if st.button("🚗 Exit Parking", use_container_width=True):
        if not v_num:
            st.error("❌ Please enter vehicle number")
            return

        success, data = st.session_state.manager.exit_vehicle(v_num)
        if success:
            entry_dt = datetime.fromisoformat(data["entry_time"])
            exit_dt = data["exit_time"]
            st.session_state.exit_success = {
                "slot_id": data["slot_id"],
                "duration": data["duration"],
                "entry_time": entry_dt.strftime("%H:%M:%S %d-%m-%Y"),
                "exit_time": exit_dt.strftime("%H:%M:%S %d-%m-%Y"),
                "timestamp": time.time(),
            }
            st.session_state.pop("exit_vehicle_number", None)
            st.rerun()
        else:
            st.error(data)

    if st.session_state.get("exit_success"):
        data = st.session_state.exit_success
        if (time.time() - data["timestamp"]) < 30:
            st.markdown(clean_html(f"""
                <div class="success-box">
                    <h3 style="margin:0 0 8px 0; color:#166534;">✅ Exit Successful</h3>
                    <p style="margin:4px 0;">Slot <strong>{data['slot_id']}</strong> released &bull; Duration: <strong>{data['duration']} min</strong></p>
                    <p style="margin:4px 0;"><strong>Entry Time:</strong> {data['entry_time']}</p>
                    <p style="margin:4px 0;"><strong>Exit Time:</strong> {data['exit_time']}</p>
                </div>
            """), unsafe_allow_html=True)
        else:
            st.session_state.exit_success = None


def render_parking_layout():
    render_top_bar_and_welcome()
    st.markdown('<div style="font-size:1.4rem; font-weight:800; color:#1e293b; margin-bottom:1rem;">🗺️ Parking Layout Visualization</div>', unsafe_allow_html=True)
    
    st.markdown(clean_html(f"""
        <div class="ref-section-card">
            <div class="parking-lot-img-wrap" style="max-height: 500px;">
                <img src="{PARKING_LAYOUT_URI}" alt="Parking Lot Map Full" style="width:100%; border-radius:12px;" />
            </div>
            <div class="legend-bar" style="margin-top:16px;">
                <div class="legend-dot-item"><span class="dot-circle dot-green"></span> Available</div>
                <div class="legend-dot-item"><span class="dot-circle dot-red"></span> Occupied</div>
                <div class="legend-dot-item"><span class="dot-circle dot-gray"></span> Blocked</div>
            </div>
        </div>
    """), unsafe_allow_html=True)


def render_rush_prediction():
    render_top_bar_and_welcome()
    st.markdown('<div style="font-size:1.4rem; font-weight:800; color:#1e293b; margin-bottom:1rem;">📈 Rush Hour Prediction</div>', unsafe_allow_html=True)

    rush_data = st.session_state.manager.predict_rush_hours()
    if rush_data.get('today_predictions'):
        df = pd.DataFrame(rush_data['today_predictions'])
        fig = px.line(
            df, x='time_label', y='avg_occupancy',
            title=f"Expected Parking Occupancy - {rush_data.get('day_name', 'Today')}",
            labels={'time_label': 'Time of Day', 'avg_occupancy': 'Expected Occupancy (%)'},
            markers=True
        )
        fig.update_layout(
            height=380,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Plus Jakarta Sans', color='#64748b'),
            xaxis=dict(showgrid=False, color='#94a3b8'),
            yaxis=dict(showgrid=True, gridcolor='#edf2f7', color='#94a3b8'),
        )
        fig.update_traces(line_color='#6c5dd3', marker_color='#5a4bcf')
        st.plotly_chart(fig, use_container_width=True, key="rush_pred_chart")
    else:
        st.info("Gathering historical parking patterns...")


def render_statistics():
    render_top_bar_and_welcome()
    st.markdown('<div style="font-size:1.4rem; font-weight:800; color:#1e293b; margin-bottom:1rem;">⏱️ Statistics & Booking History</div>', unsafe_allow_html=True)

    stats = st.session_state.manager.get_statistics()
    recent = stats.get("recent_bookings", [])
    if recent:
        df = pd.DataFrame(recent)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No active vehicle logs recorded yet.")


def render_settings():
    render_top_bar_and_welcome()
    st.markdown('<div style="font-size:1.4rem; font-weight:800; color:#1e293b; margin-bottom:1rem;">⚙️ Settings & System Controls</div>', unsafe_allow_html=True)

    st.markdown(clean_html("""
        <div class="ref-section-card">
            <div style="font-weight:700; color:#1e293b; font-size:1.1rem; margin-bottom:1rem;">🔐 Admin Authentication</div>
        </div>
    """), unsafe_allow_html=True)

    if not st.session_state.admin_authenticated:
        admin_pass = st.text_input("Enter Admin Password", type="password")
        if st.button("Login as Admin"):
            if hashlib.sha256(admin_pass.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
                st.session_state.admin_authenticated = True
                st.success("✅ Admin authenticated")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    else:
        st.success("🟢 Admin Access Active")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("↩️ Undo Last Parking", use_container_width=True):
                success, msg = st.session_state.manager.undo_last_parking()
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        with col2:
            if st.button("🔄 Reset Database", use_container_width=True):
                if st.checkbox("⚠️ Confirm Reset All Data"):
                    st.session_state.manager.db.reset_database()
                    st.success("Database reset successfully")
                    st.rerun()

        if st.button("🔒 Logout Admin"):
            st.session_state.admin_authenticated = False
            st.rerun()


# ───────────────────────────────────────────────────────────
# MAIN APPLICATION ENTRY POINT
# ───────────────────────────────────────────────────────────
def main():
    # Handle query param navigation
    if "nav" in st.query_params:
        nav_val = st.query_params["nav"]
        nav_map = {
            "park": "🚗  Park Vehicle",
            "exit": "🚪  Exit Vehicle",
            "layout": "🗺️  Parking Layout",
            "rush": "📈  Rush Prediction",
            "stats": "⏱️  Statistics",
            "settings": "⚙️  Settings",
            "dashboard": "🏠  Dashboard"
        }
        if nav_val in nav_map:
            st.session_state.nav_page = nav_map[nav_val]
        del st.query_params["nav"]

    # ─── SIDEBAR BRANDING ───
    st.sidebar.markdown(clean_html("""
        <div class="brand-logo-wrap">
            <div class="brand-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path>
                    <circle cx="7" cy="17" r="2"></circle>
                    <circle cx="17" cy="17" r="2"></circle>
                </svg>
            </div>
            <div>
                <div class="brand-title">Smart Parking</div>
                <div class="brand-sub">Management System</div>
            </div>
        </div>
    """), unsafe_allow_html=True)

    # All options including SYSTEM items (Settings, Logout)
    menu_items = [
        "🏠  Dashboard",
        "🚗  Park Vehicle",
        "🚪  Exit Vehicle",
        "🗺️  Parking Layout",
        "📈  Rush Prediction",
        "⏱️  Statistics",
        "⚙️  Settings",
        "🔒  Logout"
    ]

    # Sync radio choice with session state nav_page
    current_idx = menu_items.index(st.session_state.nav_page) if st.session_state.nav_page in menu_items else 0
    selected = st.sidebar.radio(
        "Navigation Menu",
        menu_items,
        index=current_idx,
        label_visibility="collapsed",
        key="sidebar_nav_radio"
    )

    # Update session state if changed by clicking radio
    if selected != st.session_state.nav_page:
        st.session_state.nav_page = selected
        st.rerun()

    # Sidebar Bottom Car Illustration
    st.sidebar.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    if os.path.exists("assets/sidebar_car.png"):
        st.sidebar.image("assets/sidebar_car.png", use_container_width=True)

    # ─── ROUTE TO SELECTED PAGE ───
    current = st.session_state.nav_page

    if current == "🏠  Dashboard":
        render_dashboard()
    elif current == "🚗  Park Vehicle":
        render_park_vehicle()
    elif current == "🚪  Exit Vehicle":
        render_exit_vehicle()
    elif current == "🗺️  Parking Layout":
        render_parking_layout()
    elif current == "📈  Rush Prediction":
        render_rush_prediction()
    elif current == "⏱️  Statistics":
        render_statistics()
    elif current == "⚙️  Settings":
        render_settings()
    elif current == "🔒  Logout":
        st.session_state.admin_authenticated = False
        st.success("👋 You have been logged out successfully.")
        if st.button("Return to Dashboard"):
            set_page("🏠  Dashboard")
            st.rerun()


if __name__ == "__main__":
    main()