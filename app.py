"""
Smart Parking Management System - Main Streamlit Application
Description: Advanced parking management with real-time dynamic visualization and rush prediction
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

# Safe autorefresh for live clock/metrics
with st.sidebar:
    st_autorefresh(interval=3000, key="global_clock_ticker")

def clean_html(html_str):
    """Strips leading whitespace from every line so Streamlit markdown parser never treats it as a code block"""
    return "\n".join(line.strip() for line in html_str.strip().splitlines())

# ───────────────────────────────────────────────────────────
# PIXEL-PERFECT LIGHT THEME CSS
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

html, body, [data-testid="stAppViewContainer"], .main, [data-testid="stApp"] {
    background-color: var(--bg-page) !important;
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
    color: var(--text-navy) !important;
}

/* ─── ELIMINATE UNNECESSARY TOP SPACE & STREAMLIT HEADER ─── */
header[data-testid="stHeader"],
[data-testid="stHeader"],
header {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    visibility: hidden !important;
}

#MainMenu, footer {
    visibility: hidden !important;
    height: 0 !important;
    display: none !important;
}

[data-testid="stAppViewContainer"] > .main,
.main {
    padding-top: 0 !important;
}

.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* ─── FIXED UNSTREAMED / UNSCROLLABLE SIDEBAR ─── */
section[data-testid="stSidebar"],
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"] {
    overflow: hidden !important;
    overflow-y: hidden !important;
    overflow-x: hidden !important;
    height: 100vh !important;
    max-height: 100vh !important;
}

[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #edf2f7 !important;
    box-shadow: 2px 0 16px rgba(0, 0, 0, 0.02) !important;
    padding-top: 0 !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 0.6rem 0.9rem 0.4rem 0.9rem !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    justify-content: flex-start !important;
    overflow: hidden !important;
}

.brand-logo-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.1rem 0 0.5rem 0.2rem;
}

.brand-icon-box {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #6c5dd3, #5a4bcf);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(108, 93, 211, 0.25);
    flex-shrink: 0;
}

.brand-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #1e293b;
    line-height: 1.15;
    letter-spacing: -0.3px;
}

.brand-sub {
    font-size: 0.72rem;
    color: #94a3b8;
    font-weight: 500;
}

/* ─── REMOVE RADIO BUTTONS IN TABS / SIDEBAR NAV ─── */
[data-testid="stSidebar"] [data-testid="stRadio"] > label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] div:has(> [data-testid="stRadio"]) label:first-child:not(:has(input)) {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Aggressively hide any radio circle, dot, SVG, or input element */
[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stRadioIndicator"],
[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"],
[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] input,
[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child,
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child,
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-of-type,
[data-testid="stSidebar"] [data-testid="stRadio"] div:has(> input[type="radio"]),
[data-testid="stSidebar"] [data-testid="stRadio"] svg {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    min-width: 0 !important;
    min-height: 0 !important;
    opacity: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    position: absolute !important;
    pointer-events: none !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 2px !important;
}

/* Style navigation items as sleek clickable tabs */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    padding: 0.42rem 0.85rem !important;
    border-radius: 10px !important;
    margin: 0 !important;
    font-size: 0.84rem !important;
    font-weight: 700 !important;
    color: #475569 !important;
    cursor: pointer !important;
    transition: all 0.16s ease-in-out !important;
    background: transparent !important;
    border: none !important;
    user-select: none !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label p,
[data-testid="stSidebar"] [data-testid="stRadio"] label span {
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
    font-size: 0.84rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #f1f5f9 !important;
    transform: translateX(2px) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover p,
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover span {
    color: #6c5dd3 !important;
    -webkit-text-fill-color: #6c5dd3 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(135deg, #6c5dd3 0%, #5a4bcf 100%) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 12px rgba(108, 93, 211, 0.28) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p,
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 800 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(7) {
    margin-top: 0.65rem !important;
    position: relative !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(7)::before {
    content: "SYSTEM";
    position: absolute;
    top: -0.85rem;
    left: 0.5rem;
    font-size: 0.64rem;
    font-weight: 800;
    letter-spacing: 1.5px;
    color: #94a3b8;
    pointer-events: none;
}

/* Sidebar illustration constraint */
[data-testid="stSidebar"] img {
    max-height: 75px !important;
    width: auto !important;
    margin: 0.2rem auto 0 auto !important;
    display: block !important;
    object-fit: contain !important;
}

/* ─── TOP APP BAR ─── */
.top-app-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem !important;
}

.search-box-pill {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #ffffff;
    border: 1px solid #edf2f7;
    border-radius: 12px;
    padding: 0.45rem 1.1rem;
    width: 360px;
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
}

/* Subpage Header */
.subpage-header-box {
    margin-bottom: 1.4rem;
}

.subpage-badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #eef2ff;
    color: #6c5dd3;
    font-size: 0.75rem;
    font-weight: 800;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 6px;
}

.subpage-main-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #1e293b;
    margin: 0;
    line-height: 1.2;
}

.subpage-sub-desc {
    font-size: 0.9rem;
    color: #475569 !important;
    font-weight: 600;
    margin-top: 4px;
}

/* ─── WELCOME BANNER & CLOCK CARD (Dashboard) ─── */
.welcome-banner {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 1.4rem;
}

.welcome-sub-greeting {
    font-size: 0.95rem;
    color: #475569 !important;
    font-weight: 600;
    margin-bottom: 4px;
}

.welcome-main-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #0f172a !important;
    line-height: 1.2;
    letter-spacing: -0.5px;
    margin: 0;
}

.welcome-main-title span {
    color: #6c5dd3;
}

.welcome-desc {
    font-size: 0.92rem;
    color: #475569 !important;
    font-weight: 600;
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

.clock-day-text { font-size: 0.74rem; color: #475569 !important; font-weight: 700; }
.clock-date-text { font-size: 1.15rem; font-weight: 900; color: #0f172a !important; line-height: 1.2; }
.clock-time-text { font-size: 0.78rem; color: #475569 !important; font-weight: 600; }

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
    transition: transform 0.2s ease;
}

.kpi-card:hover { transform: translateY(-2px); }
.kpi-card.kpi-occupied { background: #f0fdf4 !important; border-color: #dcfce7 !important; }

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

.kpi-body { flex: 1; }
.kpi-label { font-size: 0.8rem; color: #334155 !important; font-weight: 700; margin-bottom: 2px; }
.kpi-value { font-size: 1.9rem; font-weight: 900; color: #0f172a !important; line-height: 1.1; }
.kpi-subtext { font-size: 0.75rem; color: #475569 !important; margin-top: 4px; font-weight: 600; }
.kpi-corner-badge { position: absolute; top: 14px; right: 14px; }

.badge-p-box {
    width: 26px; height: 26px;
    background: #ede9fe; color: #6c5dd3;
    font-weight: 800; font-size: 0.8rem;
    border-radius: 7px; display: flex; align-items: center; justify-content: center;
}

.badge-pill-trend { padding: 3px 8px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; }
.trend-down, .trend-up { background: #dcfce7; color: #15803d; }

/* ─── SECTION CARDS & CONTAINERS ─── */
.ref-section-card, div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid #edf2f7 !important;
    border-radius: 18px !important;
    padding: 1.4rem 1.6rem !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.025) !important;
    margin-bottom: 1.2rem !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    gap: 0.9rem !important;
}

.ref-section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.1rem;
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
    text-decoration: none !important;
}

.ref-pill-btn:hover { background: #6c5dd3; color: white !important; }

/* Floor Switcher Tabs */
.floor-switch-bar {
    display: flex;
    gap: 8px;
    align-items: center;
}

.floor-chip {
    padding: 5px 12px;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: 700;
    text-decoration: none !important;
    background: #f1f5f9;
    color: #64748b;
    border: 1px solid #e2e8f0;
    cursor: pointer;
}

.floor-chip.active {
    background: #6c5dd3;
    color: #ffffff;
    border-color: #6c5dd3;
}

/* Floor Donut Layout */
.floor-columns-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    text-align: center;
}

.donut-card-item { display: flex; flex-direction: column; align-items: center; }
.donut-floor-name { font-size: 0.88rem; font-weight: 700; color: #1e293b; margin-bottom: 12px; }
.donut-ring-wrap { position: relative; width: 120px; height: 120px; }
.donut-center-info {
    position: absolute; top: 0; left: 0; width: 120px; height: 120px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.donut-val-pct { font-size: 1.45rem; font-weight: 800; color: #1e293b; line-height: 1.1; }
.donut-val-sub { font-size: 0.72rem; color: #64748b; font-weight: 500; }

.donut-footer-stats {
    display: flex; justify-content: space-between;
    width: 100%; max-width: 155px; margin-top: 14px; font-size: 0.78rem;
}
.donut-stat-block { text-align: left; }
.donut-stat-block.right { text-align: right; }
.donut-stat-number { font-weight: 800; color: #1e293b; }
.donut-stat-label { font-size: 0.68rem; color: #94a3b8; text-transform: capitalize; }

/* Legend Bar */
.legend-bar {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 18px;
    margin-top: 12px;
    font-size: 0.76rem;
    font-weight: 600;
    color: #64748b;
}

.legend-dot-item { display: flex; align-items: center; gap: 6px; }
.dot-circle { width: 9px; height: 9px; border-radius: 50%; }
.dot-green { background: #22c55e; }
.dot-red { background: #ef4444; }
.dot-amber { background: #f59e0b; }

/* Table in Recent Vehicle Activity */
.activity-table-clean { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.activity-table-clean thead th {
    text-align: left; padding: 8px 8px; color: #94a3b8;
    font-size: 0.72rem; font-weight: 600; border-bottom: 1px solid #f1f5f9;
    white-space: nowrap !important;
}
.activity-table-clean tbody td {
    padding: 9px 8px; color: #475569; border-bottom: 1px solid #f8fafc;
    font-weight: 500; white-space: nowrap !important;
}
.activity-table-clean tbody tr:hover { background: #fbfcfe; }

.badge-status-parked { background: #dcfce7; color: #15803d; font-weight: 700; font-size: 0.72rem; padding: 3px 10px; border-radius: 20px; }
.badge-status-exited { background: #e0f2fe; color: #0369a1; font-weight: 700; font-size: 0.72rem; padding: 3px 10px; border-radius: 20px; }

/* Quick Actions Cards Link Grid */
.qa-grid-container { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.qa-card-link {
    display: flex; align-items: center; gap: 10px;
    padding: 0.85rem 1rem; border-radius: 14px;
    text-decoration: none !important;
    transition: transform 0.18s ease; cursor: pointer;
}
.qa-card-link:hover { transform: translateY(-2px); }

.qa-card-purple { background: #eef2ff; border: 1px solid #e0e7ff; color: #3730a3 !important; }
.qa-card-red { background: #fff1f2; border: 1px solid #ffe4e6; color: #9f1239 !important; }
.qa-card-blue { background: #e0f2fe; border: 1px solid #bae6fd; color: #075985 !important; }
.qa-card-green { background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46 !important; }
.qa-card-title { font-size: 0.82rem; font-weight: 700; flex: 1; }
.qa-card-arrow { font-size: 1.1rem; font-weight: 700; }

/* Digital Parking Pass Ticket (Inline) */
.ticket-pass-card {
    background: #ffffff;
    border: 2px dashed #6c5dd3;
    border-radius: 18px;
    padding: 1.5rem;
    box-shadow: 0 8px 30px rgba(108, 93, 211, 0.12);
    position: relative;
    overflow: hidden;
}

.ticket-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #edf2f7;
    padding-bottom: 1rem;
    margin-bottom: 1.2rem;
}

.ticket-slot-display {
    background: linear-gradient(135deg, #6c5dd3, #5a4bcf);
    color: white;
    padding: 1.2rem;
    border-radius: 14px;
    text-align: center;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 14px rgba(108, 93, 211, 0.35);
}

.ticket-slot-id { font-size: 2.2rem; font-weight: 900; line-height: 1; }
.ticket-slot-sub { font-size: 0.82rem; opacity: 0.9; margin-top: 4px; }

.ticket-data-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 1.2rem;
}

.ticket-field-label { font-size: 0.72rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
.ticket-field-val { font-size: 0.95rem; font-weight: 800; color: #1e293b; }

.ticket-barcode-wrap {
    text-align: center;
    padding-top: 0.8rem;
    border-top: 1px dashed #edf2f7;
}

/* ─── INLINE RECTANGULAR PARKING PASS ─── */
@keyframes rectPassSlideIn {
    0%   { transform: translateX(120px); opacity: 0; }
    60%  { transform: translateX(-4px); opacity: 1; }
    100% { transform: translateX(0); opacity: 1; }
}

@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

.rect-pass-card {
    background: #ffffff;
    border: 2px solid #6c5dd3;
    border-radius: 16px;
    padding: 0.75rem 1rem 0.7rem 1rem;
    box-shadow: 0 6px 24px rgba(108, 93, 211, 0.14);
    animation: rectPassSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    position: relative;
    overflow: hidden;
}

.rect-pass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6c5dd3, #8b5cf6, #6c5dd3);
    background-size: 200% 100%;
    animation: shimmer 2s ease-in-out infinite;
}

.rp-top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.rp-badge {
    font-size: 0.62rem;
    font-weight: 800;
    color: #6c5dd3;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}

.rp-status-pill {
    font-size: 0.6rem;
    font-weight: 700;
    color: #15803d;
    background: #dcfce7;
    padding: 2px 8px;
    border-radius: 12px;
}

.rp-body {
    display: flex;
    gap: 14px;
    align-items: stretch;
}

.rp-slot-block {
    background: linear-gradient(135deg, #6c5dd3, #5a4bcf);
    color: white;
    padding: 0.55rem 0.7rem;
    border-radius: 10px;
    text-align: center;
    min-width: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 3px 10px rgba(108, 93, 211, 0.3);
}

.rp-slot-id {
    font-size: 1.15rem;
    font-weight: 900;
    line-height: 1.1;
}

.rp-slot-floor {
    font-size: 0.58rem;
    opacity: 0.9;
    margin-top: 2px;
}

.rp-slot-dist {
    font-size: 0.55rem;
    opacity: 0.75;
    margin-top: 1px;
}

.rp-info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3px 14px;
    flex: 1;
}

.rp-field-label {
    font-size: 0.56rem;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    line-height: 1;
}

.rp-field-val {
    font-size: 0.76rem;
    font-weight: 800;
    color: #1e293b;
    line-height: 1.2;
}

.rp-barcode-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-top: 6px;
    padding-top: 5px;
    border-top: 1px dashed #edf2f7;
}

.rp-barcode-bars {
    font-family: monospace;
    letter-spacing: 2px;
    font-weight: 800;
    color: #475569;
    font-size: 0.72rem;
}

.rp-barcode-hint {
    font-size: 0.55rem;
    color: #94a3b8;
}

/* ─── Rectangular Pass Styling (Park & Exit) ─── */
.rect-exit-pass-card {
    border: 2px solid #22c55e !important;
    box-shadow: 0 6px 24px rgba(34, 197, 94, 0.16) !important;
}

.rect-exit-pass-card::before {
    background: linear-gradient(90deg, #16a34a, #22c55e, #16a34a) !important;
}

.rect-exit-pass-card .rp-slot-block,
.rp-slot-block.rp-exit-slot-block {
    background: linear-gradient(135deg, #16a34a, #15803d) !important;
    box-shadow: 0 3px 10px rgba(22, 163, 74, 0.28) !important;
}

/* ─── Pass Close Button (Park & Exit) ─── */
div[data-testid="stColumn"]:has(.rect-pass-card),
div[data-testid="stColumn"]:has(.rect-exit-pass-card) {
    position: relative !important;
}

div[data-testid="stColumn"]:has(.rect-pass-card) > div > div:has(button),
div[data-testid="stColumn"]:has(.rect-pass-card) div[data-testid="stVerticalBlock"] > div:has(button),
div[data-testid="stColumn"]:has(.rect-pass-card) div[data-testid="element-container"]:has(button),
div[data-testid="stColumn"]:has(.rect-exit-pass-card) > div > div:has(button),
div[data-testid="stColumn"]:has(.rect-exit-pass-card) div[data-testid="stVerticalBlock"] > div:has(button),
div[data-testid="stColumn"]:has(.rect-exit-pass-card) div[data-testid="element-container"]:has(button) {
    position: absolute !important;
    top: 10px !important;
    right: 14px !important;
    z-index: 99 !important;
    width: auto !important;
    height: auto !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stColumn"]:has(.rect-pass-card) div[data-testid="stButton"],
div[data-testid="stColumn"]:has(.rect-exit-pass-card) div[data-testid="stButton"] {
    position: static !important;
    width: auto !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stColumn"]:has(.rect-pass-card) div[data-testid="stButton"] > button,
div[data-testid="stColumn"]:has(.rect-exit-pass-card) div[data-testid="stButton"] > button {
    width: 24px !important;
    height: 24px !important;
    min-width: 24px !important;
    min-height: 24px !important;
    max-width: 24px !important;
    max-height: 24px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background: #f1f5f9 !important;
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    border: 1px solid #cbd5e1 !important;
    font-size: 11px !important;
    font-weight: 800 !important;
    line-height: 1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
    transition: all 0.18s ease-in-out !important;
    cursor: pointer !important;
}

div[data-testid="stColumn"]:has(.rect-pass-card) div[data-testid="stButton"] > button:hover,
div[data-testid="stColumn"]:has(.rect-exit-pass-card) div[data-testid="stButton"] > button:hover {
    background: #fee2e2 !important;
    color: #ef4444 !important;
    -webkit-text-fill-color: #ef4444 !important;
    border-color: #fca5a5 !important;
    transform: scale(1.12) !important;
}

div[data-testid="stColumn"]:has(.rect-pass-card) div[data-testid="stButton"] > button *,
div[data-testid="stColumn"]:has(.rect-exit-pass-card) div[data-testid="stButton"] > button * {
    color: inherit !important;
    -webkit-text-fill-color: inherit !important;
    font-size: inherit !important;
    font-weight: inherit !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
}

/* ─── Park Vehicle: Equal-Height Columns ─── */
div[data-testid="stHorizontalBlock"]:has(.park-form-box) {
    display: flex !important;
    align-items: stretch !important;
}

div[data-testid="stHorizontalBlock"]:has(.park-form-box) > div[data-testid="stColumn"] {
    display: flex !important;
    flex-direction: column !important;
}

div[data-testid="stHorizontalBlock"]:has(.park-form-box) > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
}

div[data-testid="stHorizontalBlock"]:has(.park-form-box) div[data-testid="stVerticalBlockBorderWrapper"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
    margin-bottom: 0 !important;
    box-sizing: border-box !important;
}

div[data-testid="stHorizontalBlock"]:has(.park-form-box) div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
    justify-content: space-between !important;
}

div[data-testid="stHorizontalBlock"]:has(.park-form-box) .park-map-wrapper {
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    flex: 1 1 auto !important;
    height: 100% !important;
    min-height: 100% !important;
}

div[data-testid="stHorizontalBlock"]:has(.park-form-box) div[data-testid="stColumn"]:has(.park-map-wrapper) .stMarkdown,
div[data-testid="stHorizontalBlock"]:has(.park-form-box) div[data-testid="stColumn"]:has(.park-map-wrapper) [data-testid="stMarkdownContainer"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
    height: 100% !important;
    justify-content: space-between !important;
}

/* ─── Exit Vehicle: Equal-Height Columns ─── */
div[data-testid="stHorizontalBlock"]:has(.exit-form-box) {
    display: flex !important;
    align-items: stretch !important;
}

div[data-testid="stHorizontalBlock"]:has(.exit-form-box) > div[data-testid="stColumn"] {
    display: flex !important;
    flex-direction: column !important;
}

div[data-testid="stHorizontalBlock"]:has(.exit-form-box) > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
}

div[data-testid="stHorizontalBlock"]:has(.exit-form-box) div[data-testid="stVerticalBlockBorderWrapper"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
    margin-bottom: 0 !important;
    box-sizing: border-box !important;
}

div[data-testid="stHorizontalBlock"]:has(.exit-form-box) div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
    justify-content: space-between !important;
}

/* ─── GUARANTEED HIGH-CONTRAST STREAMLIT ELEMENTS & LABELS ─── */
/* Force all headings to be dark and crisp */
h1, h2, h3, h4, h5, h6 {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}

/* All form/widget labels across the entire app */
label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stWidgetLabel"] label,
.stTextInput label,
.stSelectbox label,
.stCheckbox label {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    font-weight: 800 !important;
    font-size: 0.92rem !important;
    line-height: 1.4 !important;
    margin-bottom: 0.35rem !important;
}

/* Text Inputs (Park & Exit terminals, Admin password, search, etc.) */
input,
textarea,
[data-testid="stTextInput"] input,
.stTextInput input {
    background-color: #f8fafc !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    font-family: inherit !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1rem !important;
}

input:focus,
.stTextInput input:focus {
    border-color: #6c5dd3 !important;
    box-shadow: 0 0 0 3px rgba(108, 93, 211, 0.15) !important;
    background-color: #ffffff !important;
}

input::placeholder,
.stTextInput input::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
}

/* Selectbox / Dropdowns */
[data-baseweb="select"],
[data-baseweb="select"] * {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    font-family: inherit !important;
}

div[data-baseweb="select"] > div {
    background-color: #f8fafc !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 2px 4px !important;
}

div[data-baseweb="select"] > div:hover {
    border-color: #6c5dd3 !important;
}

/* Dropdown Popup Menu List */
ul[role="listbox"],
[data-baseweb="popover"],
[data-baseweb="menu"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08) !important;
}

li[role="option"] {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    font-weight: 600 !important;
    padding: 0.6rem 1rem !important;
}

li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background-color: #eef2ff !important;
    color: #6c5dd3 !important;
    -webkit-text-fill-color: #6c5dd3 !important;
}

/* Metrics (Parking Layout & Statistics) */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #edf2f7 !important;
    border-radius: 14px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.02) !important;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #475569 !important;
    -webkit-text-fill-color: #475569 !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    text-transform: capitalize !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    font-weight: 900 !important;
    font-size: 1.9rem !important;
    line-height: 1.2 !important;
}

/* Tabs (Parking Layout) */
[data-testid="stTabs"] [role="tablist"] {
    gap: 8px !important;
    border-bottom: 2px solid #e2e8f0 !important;
    padding-bottom: 4px !important;
    margin-bottom: 1rem !important;
}

[data-testid="stTabs"] button[role="tab"] {
    background: #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.2rem !important;
    border: none !important;
    transition: all 0.18s ease !important;
}

[data-testid="stTabs"] button[role="tab"] * {
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}

[data-testid="stTabs"] button[role="tab"]:hover {
    background: #cbd5e1 !important;
}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #6c5dd3, #5a4bcf) !important;
    box-shadow: 0 4px 12px rgba(108, 93, 211, 0.25) !important;
}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 800 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6c5dd3, #5a4bcf) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: none !important;
    padding: 0.68rem 1.8rem !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    font-size: 0.9rem !important;
    box-shadow: 0 4px 14px rgba(108, 93, 211, 0.25) !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(108, 93, 211, 0.35) !important;
}

.stButton > button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Checkbox */
.stCheckbox * {
    color: #334155 !important;
    -webkit-text-fill-color: #334155 !important;
    font-weight: 600 !important;
}

/* Dataframe & Tables */
[data-testid="stDataFrame"] {
    background-color: #ffffff !important;
    border-radius: 12px !important;
}
</style>
"""), unsafe_allow_html=True)


# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = ParkingManager()
    if st.session_state.get('first_run', True):
        st.session_state.manager.generate_sample_data()
        st.session_state.first_run = False

if "parking_success" not in st.session_state:
    st.session_state.parking_success = None
if "exit_success" not in st.session_state:
    st.session_state.exit_success = None
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "dash_layout_floor" not in st.session_state:
    st.session_state.dash_layout_floor = 0
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "🏠  Dashboard"
if "floating_pass" not in st.session_state:
    st.session_state.floating_pass = None
if "floating_exit_pass" not in st.session_state:
    st.session_state.floating_exit_pass = None

def set_page(page_name):
    st.session_state.nav_page = page_name

def to_uppercase(key):
    if key in st.session_state and st.session_state[key]:
        st.session_state[key] = st.session_state[key].upper()

def is_valid_vehicle_number(vehicle_number):
    pattern = r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'
    return bool(re.match(pattern, vehicle_number))


# ───────────────────────────────────────────────────────────
# DATABASE DATA HELPERS
# ───────────────────────────────────────────────────────────
def get_floor_slots_detail(floor_num):
    """Fetches all slots for a floor joined with active booking details"""
    cursor = st.session_state.manager.db.conn.cursor()
    cursor.execute('''
        SELECT s.slot_id, s.floor_number, s.slot_number, s.vehicle_type, s.is_occupied, 
               s.distance_from_stairs, s.position_x, s.position_y, b.vehicle_number, b.entry_time 
        FROM parking_slots s 
        LEFT JOIN booking_history b ON s.slot_id = b.slot_id AND b.exit_time IS NULL 
        WHERE s.floor_number = ? 
        ORDER BY s.slot_number
    ''', (floor_num,))
    return cursor.fetchall()

def get_active_parked_list():
    """Returns all currently parked vehicles with their slot and entry time"""
    cursor = st.session_state.manager.db.conn.cursor()
    cursor.execute('''
        SELECT b.vehicle_number, b.slot_id, b.vehicle_type, b.entry_time 
        FROM booking_history b 
        WHERE b.exit_time IS NULL 
        ORDER BY b.entry_time DESC
    ''')
    return cursor.fetchall()


# ───────────────────────────────────────────────────────────
# DYNAMIC SVG PARKING LOT GENERATOR
# ───────────────────────────────────────────────────────────
def generate_dynamic_parking_svg(floor_number, highlight_slot=None):
    """
    Generates a 100% dynamic, authentic top-down SVG parking lot.
    Displays realistic parked cars/bikes with vehicle registration plates for occupied slots,
    and clear open green bays for vacant spots.
    """
    slots = get_floor_slots_detail(floor_number)
    n = len(slots)
    if n == 0:
        return "<div style='color:#94a3b8; padding:2rem; text-align:center;'>No slots found for this floor.</div>"

    svg_w, svg_h = 760, 290
    svg = [f'<svg viewBox="0 0 {svg_w} {svg_h}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="border-radius:14px; background:#1b1f28; font-family:\'Plus Jakarta Sans\', sans-serif;">']
    
    # Asphalt pavement
    svg.append(f'<rect width="{svg_w}" height="{svg_h}" fill="#222631" rx="14" />')
    
    # Grass verges on borders
    svg.append('<rect x="0" y="0" width="36" height="290" fill="#171a22" />')
    svg.append('<rect x="3" y="0" width="30" height="290" fill="#1e3a2f" rx="4" />')
    svg.append('<rect x="724" y="0" width="36" height="290" fill="#171a22" />')
    svg.append('<rect x="727" y="0" width="30" height="290" fill="#1e3a2f" rx="4" />')
    
    # Top-down trees
    for ty in [30, 95, 160, 225]:
        svg.append(f'<circle cx="18" cy="{ty}" r="14" fill="#16a34a" opacity="0.9" />')
        svg.append(f'<circle cx="18" cy="{ty}" r="10" fill="#22c55e" />')
        svg.append(f'<circle cx="16" cy="{ty-2}" r="5" fill="#86efac" opacity="0.8" />')
        svg.append(f'<circle cx="742" cy="{ty}" r="14" fill="#16a34a" opacity="0.9" />')
        svg.append(f'<circle cx="742" cy="{ty}" r="10" fill="#22c55e" />')
        svg.append(f'<circle cx="740" cy="{ty-2}" r="5" fill="#86efac" opacity="0.8" />')

    # Central Driving Lane
    svg.append('<rect x="36" y="115" width="688" height="60" fill="#181c24" />')
    svg.append('<line x1="45" y1="145" x2="715" y2="145" stroke="#ffffff" stroke-width="1.5" stroke-dasharray="12,14" opacity="0.35" />')
    
    # Direction arrows
    for ax in [180, 400, 600]:
        svg.append(f'<g transform="translate({ax}, 130)" opacity="0.7"><path d="M0,5 L20,5 L20,2 L28,7 L20,12 L20,9 L0,9 Z" fill="#ffffff" /></g>')
        svg.append(f'<g transform="translate({ax+50}, 150)" opacity="0.7"><path d="M28,5 L8,5 L8,2 L0,7 L8,12 L8,9 L28,9 Z" fill="#ffffff" /></g>')

    # Stairs zone
    svg.append('<g transform="translate(42, 122)"><rect width="48" height="46" rx="6" fill="#f59e0b" fill-opacity="0.15" stroke="#f59e0b" stroke-width="1.5" /><text x="24" y="22" font-size="14" text-anchor="middle">🚶</text><text x="24" y="36" font-size="8" font-weight="800" fill="#f59e0b" text-anchor="middle">STAIRS</text></g>')

    n_top = (n + 1) // 2
    n_bottom = n - n_top
    bay_w = 60 if n <= 16 else 54
    gap = 4
    start_x_top = 100
    is_2w_floor = (floor_number in [0, 1])

    # Top Bays
    for i in range(n_top):
        s = slots[i]
        slot_id, _, slot_num, vtype, is_occ, dist, _, _, veh_num, entry_t = s
        bx = start_x_top + i * (bay_w + gap)
        by = 12
        bh = 98
        is_hl = (highlight_slot and highlight_slot == slot_id)
        border_col = '#6366f1' if is_hl else ('#ef4444' if is_occ else '#22c55e')
        bg_col = 'rgba(99, 102, 241, 0.2)' if is_hl else ('rgba(239, 68, 68, 0.08)' if is_occ else 'rgba(34, 197, 94, 0.08)')
        
        svg.append(f'<rect x="{bx}" y="{by}" width="{bay_w}" height="{bh}" rx="4" fill="{bg_col}" stroke="{border_col}" stroke-width="{3 if is_hl else 1.5}" opacity="0.9" />')
        short_id = slot_id.replace('GF-', '').replace('B1-', '').replace('B2-', '')
        svg.append(f'<text x="{bx + bay_w/2}" y="{by + 14}" font-size="9" font-weight="800" fill="#94a3b8" text-anchor="middle">{short_id}</text>')
        
        if is_occ:
            veh_disp = veh_num[-6:] if veh_num else 'PARKED'
            if is_2w_floor:
                # Top-down motorcycle
                cx = bx + (bay_w - 24) / 2
                cy = by + 26
                b_col = '#3b82f6' if i % 2 == 0 else '#ef4444'
                svg.append(f'''
                    <g transform="translate({cx}, {cy})">
                        <rect x="10" y="2" width="4" height="12" rx="2" fill="#0f172a" />
                        <line x1="2" y1="12" x2="22" y2="12" stroke="#e2e8f0" stroke-width="2.5" stroke-linecap="round" />
                        <circle cx="2" cy="12" r="2" fill="#ef4444" />
                        <circle cx="22" cy="12" r="2" fill="#ef4444" />
                        <path d="M 8 16 C 6 24, 6 32, 8 40 C 12 42, 12 42, 16 40 C 18 32, 18 24, 16 16 Z" fill="{b_col}" />
                        <rect x="8" y="24" width="8" height="16" rx="3" fill="#1e293b" />
                        <rect x="10" y="42" width="4" height="12" rx="2" fill="#0f172a" />
                        <text x="12" y="20" font-size="5" font-weight="800" fill="#ffffff" text-anchor="middle">{veh_disp}</text>
                    </g>
                ''')
            else:
                # Top-down car
                car_w = 28 if n > 16 else 32
                car_h = 56
                cx = bx + (bay_w - car_w) / 2
                cy = by + 24
                car_col = '#3b82f6' if i % 2 == 0 else '#ef4444'
                svg.append(f'''
                    <g transform="translate({cx}, {cy})">
                        <rect x="-2" y="8" width="4" height="10" rx="1" fill="#0f172a" />
                        <rect x="{car_w}" y="8" width="4" height="10" rx="1" fill="#0f172a" />
                        <rect x="-2" y="38" width="4" height="10" rx="1" fill="#0f172a" />
                        <rect x="{car_w}" y="38" width="4" height="10" rx="1" fill="#0f172a" />
                        <rect x="0" y="0" width="{car_w}" height="{car_h}" rx="8" fill="{car_col}" />
                        <rect x="3" y="10" width="{car_w-6}" height="8" rx="2" fill="#0f172a" opacity="0.7" />
                        <rect x="3" y="40" width="{car_w-6}" height="6" rx="2" fill="#0f172a" opacity="0.7" />
                        <rect x="4" y="20" width="{car_w-8}" height="18" rx="3" fill="#ffffff" opacity="0.2" />
                        <text x="{car_w/2}" y="32" font-size="6" font-weight="800" fill="#ffffff" text-anchor="middle">{veh_disp}</text>
                        <circle cx="4" cy="{car_h-2}" r="2" fill="#fef08a" />
                        <circle cx="{car_w-4}" cy="{car_h-2}" r="2" fill="#fef08a" />
                    </g>
                ''')
        else:
            svg.append(f'''
                <circle cx="{bx + bay_w/2}" cy="{by + 48}" r="11" fill="#22c55e" fill-opacity="0.15" stroke="#22c55e" stroke-width="1.5" />
                <circle cx="{bx + bay_w/2}" cy="{by + 48}" r="4" fill="#22c55e" />
                <text x="{bx + bay_w/2}" y="{by + 72}" font-size="8" font-weight="800" fill="#22c55e" text-anchor="middle">OPEN</text>
                <text x="{bx + bay_w/2}" y="{by + 84}" font-size="7" fill="#64748b" text-anchor="middle">{dist}m</text>
            ''')

    # Bottom Bays
    start_x_bottom = 100
    for j in range(n_bottom):
        idx = n_top + j
        s = slots[idx]
        slot_id, _, slot_num, vtype, is_occ, dist, _, _, veh_num, entry_t = s
        bx = start_x_bottom + j * (bay_w + gap)
        by = 180
        bh = 98
        is_hl = (highlight_slot and highlight_slot == slot_id)
        border_col = '#6366f1' if is_hl else ('#ef4444' if is_occ else '#22c55e')
        bg_col = 'rgba(99, 102, 241, 0.2)' if is_hl else ('rgba(239, 68, 68, 0.08)' if is_occ else 'rgba(34, 197, 94, 0.08)')
        
        svg.append(f'<rect x="{bx}" y="{by}" width="{bay_w}" height="{bh}" rx="4" fill="{bg_col}" stroke="{border_col}" stroke-width="{3 if is_hl else 1.5}" opacity="0.9" />')
        short_id = slot_id.replace('GF-', '').replace('B1-', '').replace('B2-', '')
        svg.append(f'<text x="{bx + bay_w/2}" y="{by + bh - 6}" font-size="9" font-weight="800" fill="#94a3b8" text-anchor="middle">{short_id}</text>')
        
        if is_occ:
            veh_disp = veh_num[-6:] if veh_num else 'PARKED'
            if is_2w_floor:
                cx = bx + (bay_w - 24) / 2
                cy = by + 22
                b_col = '#10b981' if j % 2 == 0 else '#8b5cf6'
                svg.append(f'''
                    <g transform="translate({cx}, {cy})">
                        <rect x="10" y="2" width="4" height="12" rx="2" fill="#0f172a" />
                        <line x1="2" y1="12" x2="22" y2="12" stroke="#e2e8f0" stroke-width="2.5" stroke-linecap="round" />
                        <circle cx="2" cy="12" r="2" fill="#ef4444" />
                        <circle cx="22" cy="12" r="2" fill="#ef4444" />
                        <path d="M 8 16 C 6 24, 6 32, 8 40 C 12 42, 12 42, 16 40 C 18 32, 18 24, 16 16 Z" fill="{b_col}" />
                        <rect x="8" y="24" width="8" height="16" rx="3" fill="#1e293b" />
                        <rect x="10" y="42" width="4" height="12" rx="2" fill="#0f172a" />
                        <text x="12" y="20" font-size="5" font-weight="800" fill="#ffffff" text-anchor="middle">{veh_disp}</text>
                    </g>
                ''')
            else:
                car_w = 28 if n > 16 else 32
                car_h = 56
                cx = bx + (bay_w - car_w) / 2
                cy = by + 18
                car_col = '#10b981' if j % 2 == 0 else '#8b5cf6'
                svg.append(f'''
                    <g transform="translate({cx}, {cy})">
                        <rect x="-2" y="8" width="4" height="10" rx="1" fill="#0f172a" />
                        <rect x="{car_w}" y="8" width="4" height="10" rx="1" fill="#0f172a" />
                        <rect x="-2" y="38" width="4" height="10" rx="1" fill="#0f172a" />
                        <rect x="{car_w}" y="38" width="4" height="10" rx="1" fill="#0f172a" />
                        <rect x="0" y="0" width="{car_w}" height="{car_h}" rx="8" fill="{car_col}" />
                        <rect x="3" y="38" width="{car_w-6}" height="8" rx="2" fill="#0f172a" opacity="0.7" />
                        <rect x="3" y="8" width="{car_w-6}" height="6" rx="2" fill="#0f172a" opacity="0.7" />
                        <rect x="4" y="16" width="{car_w-8}" height="20" rx="3" fill="#ffffff" opacity="0.2" />
                        <text x="{car_w/2}" y="28" font-size="6" font-weight="800" fill="#ffffff" text-anchor="middle">{veh_disp}</text>
                        <circle cx="4" cy="2" r="2" fill="#fef08a" />
                        <circle cx="{car_w-4}" cy="2" r="2" fill="#fef08a" />
                    </g>
                ''')
        else:
            svg.append(f'''
                <circle cx="{bx + bay_w/2}" cy="{by + 40}" r="11" fill="#22c55e" fill-opacity="0.15" stroke="#22c55e" stroke-width="1.5" />
                <circle cx="{bx + bay_w/2}" cy="{by + 40}" r="4" fill="#22c55e" />
                <text x="{bx + bay_w/2}" y="{by + 62}" font-size="8" font-weight="800" fill="#22c55e" text-anchor="middle">OPEN</text>
                <text x="{bx + bay_w/2}" y="{by + 74}" font-size="7" fill="#64748b" text-anchor="middle">{dist}m</text>
            ''')

    svg.append('</svg>')
    return ''.join(svg)


# ───────────────────────────────────────────────────────────
# TOP BAR COMPONENT
# ───────────────────────────────────────────────────────────
def render_top_bar():
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


# ───────────────────────────────────────────────────────────
# DONUT SVG GENERATOR
# ───────────────────────────────────────────────────────────
def generate_donut_svg_html(floor_name, vehicle_icon, vacant, total, occupied):
    avail_pct = round((vacant / total) * 100) if total > 0 else 0
    r = 44
    circumference = 2 * 3.14159265 * r
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
# 1. DASHBOARD PAGE
# ───────────────────────────────────────────────────────────
def render_dashboard():
    render_top_bar()

    now = datetime.now()
    day_name = now.strftime("%A")
    date_str = now.strftime("%d %b %Y")
    time_str = now.strftime("%I:%M %p")

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

    summary = st.session_state.manager.get_occupancy_summary()
    total_slots = summary['total_slots']
    occupied_slots = summary['occupied_slots']
    vacant_slots = summary['vacant_slots']
    occupancy = summary['overall_occupancy_rate']
    vacancy_pct = round(100 - occupancy, 1)

    # 4 KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(clean_html(f"""
            <div class="kpi-card">
                <div class="kpi-icon-square icon-sq-purple">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path>
                        <circle cx="7" cy="17" r="2"></circle><circle cx="17" cy="17" r="2"></circle>
                    </svg>
                </div>
                <div class="kpi-body">
                    <div class="kpi-label">Total Slots</div>
                    <div class="kpi-value">{total_slots}</div>
                    <div class="kpi-subtext">Parking spaces available</div>
                </div>
                <div class="kpi-corner-badge"><div class="badge-p-box">P</div></div>
            </div>
        """), unsafe_allow_html=True)

    with k2:
        st.markdown(clean_html(f"""
            <div class="kpi-card kpi-occupied">
                <div class="kpi-icon-square icon-sq-green">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path>
                        <circle cx="7" cy="17" r="2"></circle><circle cx="17" cy="17" r="2"></circle>
                    </svg>
                </div>
                <div class="kpi-body">
                    <div class="kpi-label">Occupied</div>
                    <div class="kpi-value">{occupied_slots}</div>
                    <div class="kpi-subtext">Vehicles currently parked</div>
                </div>
                <div class="kpi-corner-badge"><span class="badge-pill-trend trend-down">↓ {occupancy}%</span></div>
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
                <div class="kpi-corner-badge"><span class="badge-pill-trend trend-up">↑ {vacancy_pct}%</span></div>
            </div>
        """), unsafe_allow_html=True)

    with k4:
        st.markdown(clean_html("""
            <div class="kpi-card">
                <div class="kpi-icon-square icon-sq-amber">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>
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

    # Middle Row: Floor Donut Gauges + DYNAMIC PARKING LOT
    col_floor, col_layout = st.columns([1.5, 1.3])

    with col_floor:
        floors = summary['floors']
        f0 = floors[0] if len(floors) > 0 else {'floor_name': 'Ground Floor (2W)', 'vacant_slots': 20, 'total_slots': 20, 'occupied_slots': 0}
        f1 = floors[1] if len(floors) > 1 else {'floor_name': 'Basement 1 (2W)', 'vacant_slots': 15, 'total_slots': 15, 'occupied_slots': 0}
        f2 = floors[2] if len(floors) > 2 else {'floor_name': 'Basement 2 (4W)', 'vacant_slots': 20, 'total_slots': 20, 'occupied_slots': 0}

        donut_0 = generate_donut_svg_html(f0['floor_name'], "🏍️", f0['vacant_slots'], f0['total_slots'], f0['occupied_slots'])
        donut_1 = generate_donut_svg_html(f1['floor_name'], "🏍️", f1['vacant_slots'], f1['total_slots'], f1['occupied_slots'])
        donut_2 = generate_donut_svg_html(f2['floor_name'], "🚗", f2['vacant_slots'], f2['total_slots'], f2['occupied_slots'])

        floor_card_html = f"""
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
        st.markdown(clean_html(floor_card_html), unsafe_allow_html=True)

    with col_layout:
        dash_f = st.session_state.dash_layout_floor
        svg_parking = generate_dynamic_parking_svg(dash_f)
        
        # Floor buttons
        cur_f_name = "Basement 2 (4W)" if dash_f == 2 else ("Basement 1 (2W)" if dash_f == 1 else "Ground Floor (2W)")
        f_slots = get_floor_slots_detail(dash_f)
        occ_cnt = sum(1 for s in f_slots if s[4])
        vac_cnt = len(f_slots) - occ_cnt

        st.markdown(clean_html(f"""
            <div class="ref-section-card">
                <div class="ref-section-header">
                    <div class="ref-section-title">
                        <span style="color:#6c5dd3; font-size:1.2rem;">🗺️</span>
                        Parking Layout <span style="font-size:0.75rem; color:#6c5dd3; font-weight:700; background:#eef2ff; padding:2px 8px; border-radius:12px;">{cur_f_name}</span>
                    </div>
                    <a href="?nav=layout" target="_self" class="ref-pill-btn">View Full</a>
                </div>
                <div>
                    {svg_parking}
                </div>
                <div class="legend-bar">
                    <div class="legend-dot-item"><span class="dot-circle dot-green"></span> Available ({vac_cnt})</div>
                    <div class="legend-dot-item"><span class="dot-circle dot-red"></span> Occupied ({occ_cnt})</div>
                    <div class="legend-dot-item"><span class="dot-circle dot-amber"></span> Stairs</div>
                </div>
            </div>
        """), unsafe_allow_html=True)

        # Floor Switcher Buttons under the card
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            if st.button("🏢 Ground Floor (2W)", key="btn_gf", use_container_width=True):
                st.session_state.dash_layout_floor = 0
                st.rerun()
        with f_col2:
            if st.button("🏢 Basement 1 (2W)", key="btn_b1", use_container_width=True):
                st.session_state.dash_layout_floor = 1
                st.rerun()
        with f_col3:
            if st.button("🚗 Basement 2 (4W)", key="btn_b2", use_container_width=True):
                st.session_state.dash_layout_floor = 2
                st.rerun()

    # Bottom Row: Recent Activity + Trend + Quick Actions
    col_act, col_trend, col_quick = st.columns([1.5, 1.2, 0.95])

    with col_act:
        stats = st.session_state.manager.get_statistics()
        recent = stats.get("recent_bookings", [])[:4]

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
            xaxis=dict(showgrid=False, zeroline=False, color='#334155', tickfont=dict(size=10, color='#334155', family='Plus Jakarta Sans')),
            yaxis=dict(showgrid=True, gridcolor='#edf2f7', zeroline=False, color='#334155', tickfont=dict(size=10, color='#334155', family='Plus Jakarta Sans'), range=[0, 65]),
            legend=dict(
                orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5,
                font=dict(size=10, color='#1e293b', family='Plus Jakarta Sans')
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
                        <div class="qa-card-title">🚗 Park Vehicle</div>
                        <span class="qa-card-arrow">›</span>
                    </a>
                    <a href="?nav=exit" target="_self" class="qa-card-link qa-card-red">
                        <div class="qa-card-title">🚪 Exit Vehicle</div>
                        <span class="qa-card-arrow">›</span>
                    </a>
                    <a href="?nav=layout" target="_self" class="qa-card-link qa-card-blue">
                        <div class="qa-card-title">🗺️ View Layout</div>
                        <span class="qa-card-arrow">›</span>
                    </a>
                    <a href="?nav=stats" target="_self" class="qa-card-link qa-card-green">
                        <div class="qa-card-title">⏱️ View Stats</div>
                        <span class="qa-card-arrow">›</span>
                    </a>
                </div>
            </div>
        """
        st.markdown(clean_html(quick_actions_html), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# 2. PARK VEHICLE PAGE
# ───────────────────────────────────────────────────────────
def render_park_vehicle():
    render_top_bar()

    # ─── HEADER ROW: Title (left) + Rectangular Pass (right blank space) ───
    has_pass = st.session_state.get("floating_pass") is not None

    if has_pass:
        col_hdr, col_pass_area = st.columns([1.15, 1.35])
    else:
        col_hdr = st.container()
        col_pass_area = None

    with col_hdr:
        st.markdown(clean_html("""
            <div class="subpage-header-box">
                <div class="subpage-badge-pill">🅿️ VEHICLE ENTRY TERMINAL</div>
                <h1 class="subpage-main-title">Park Your Vehicle</h1>
                <div class="subpage-sub-desc">Intelligent slot allocation optimizing walking distance to elevators & stairs</div>
            </div>
        """), unsafe_allow_html=True)

    if has_pass and col_pass_area is not None:
        fp = st.session_state.floating_pass
        vtype_icon = "🚗" if fp.get("vtype") == "4-Wheeler" else "🏍️"
        with col_pass_area:
            st.markdown(clean_html(f"""
                <div class="rect-pass-card">
                    <div class="rp-top-row" style="padding-right: 32px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="rp-badge">Smart Parking Pass</span>
                            <span class="rp-status-pill">✓ Allocated</span>
                        </div>
                    </div>
                    <div class="rp-body">
                        <div class="rp-slot-block">
                            <div class="rp-slot-id">{fp['slot_id']}</div>
                            <div class="rp-slot-floor">{fp['floor_name']}</div>
                            <div class="rp-slot-dist">{fp['dist']}m to stairs</div>
                        </div>
                        <div class="rp-info-grid">
                            <div>
                                <div class="rp-field-label">Vehicle</div>
                                <div class="rp-field-val">{vtype_icon} {fp['vehicle']}</div>
                            </div>
                            <div>
                                <div class="rp-field-label">Category</div>
                                <div class="rp-field-val">{fp['vtype']}</div>
                            </div>
                            <div>
                                <div class="rp-field-label">Check-in</div>
                                <div class="rp-field-val">{fp['time']}</div>
                            </div>
                            <div>
                                <div class="rp-field-label">Date</div>
                                <div class="rp-field-val">{fp['date']}</div>
                            </div>
                        </div>
                    </div>
                    <div class="rp-barcode-row">
                        <span class="rp-barcode-bars">||| | |||| | ||| || ||||</span>
                        <span class="rp-barcode-hint">Keep ticket safe for checkout</span>
                    </div>
                </div>
            """), unsafe_allow_html=True)

            if st.button("✕", key="dismiss_park_pass", help="Dismiss pass"):
                st.session_state.floating_pass = None
                st.session_state.parking_success = None
                st.rerun()

    # ─── EQUAL-HEIGHT FORM + MAP COLUMNS ───
    st.markdown('<div class="park-equal-height"></div>', unsafe_allow_html=True)
    col_form, col_preview = st.columns([1.15, 1.35])

    with col_form:
        with st.container(border=True):
            st.markdown('<div class="park-form-box"></div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:800; font-size:1.15rem; color:#1e293b; margin-bottom:0.75rem;">📝 Vehicle Check-in Form</div>', unsafe_allow_html=True)

            st.text_input(
                "Vehicle Registration Number",
                placeholder="e.g. GJ01AB1234",
                key="park_veh_input",
                on_change=to_uppercase,
                args=("park_veh_input",)
            )
            v_num = st.session_state.get("park_veh_input", "").strip()

            # Validation feedback
            is_already_parked = False
            if v_num:
                if not is_valid_vehicle_number(v_num):
                    st.markdown('<div style="color:#ef4444; font-size:0.8rem; font-weight:600; margin-top:-8px; margin-bottom:10px;">⚠️ Invalid format. Example: GJ01AB1234</div>', unsafe_allow_html=True)
                elif st.session_state.manager.is_vehicle_already_parked(v_num):
                    is_already_parked = True
                    st.markdown(f'<div style="color:#ef4444; font-size:0.82rem; font-weight:700; margin-top:-8px; margin-bottom:10px;">🚫 Vehicle {v_num} is ALREADY parked in the building!</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#16a34a; font-size:0.8rem; font-weight:600; margin-top:-8px; margin-bottom:10px;">✅ Valid Registration Number</div>', unsafe_allow_html=True)

            v_type = st.selectbox("Select Vehicle Type", ["2-Wheeler (Bikes / Scooters)", "4-Wheeler (Cars / SUVs)"], key="park_vtype_sel")
            actual_type = "2-Wheeler" if "2-Wheeler" in v_type else "4-Wheeler"

            # Check optimal slot before parking
            best = st.session_state.manager.find_optimal_slot(actual_type)

            if best:
                st.markdown(clean_html(f"""
                    <div style="background:#eef2ff; border:1px solid #c7d2fe; border-radius:12px; padding:0.9rem 1.1rem; margin:0.6rem 0 1rem 0;">
                        <div style="font-size:0.75rem; color:#6c5dd3; font-weight:800; text-transform:uppercase;">🎯 Nearest Slot Available</div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
                            <span style="font-size:1.3rem; font-weight:900; color:#1e293b;">{best['slot_id']}</span>
                            <span style="font-size:0.82rem; font-weight:700; color:#475569;">📍 {best['floor_name']}</span>
                        </div>
                        <div style="font-size:0.75rem; color:#64748b; margin-top:4px;">Walking Distance: <b>{best['distance_from_stairs']}m</b> from entrance stairs</div>
                    </div>
                """), unsafe_allow_html=True)
            else:
                st.error("🚫 Parking is Full for this vehicle type!")

            if st.button("🅿️ Confirm Check-in & Issue Ticket", use_container_width=True, disabled=(is_already_parked or not best)):
                if not v_num:
                    st.error("❌ Please enter a vehicle registration number")
                elif not is_valid_vehicle_number(v_num):
                    st.error("❌ Please enter a valid vehicle number format (e.g. GJ01AB1234)")
                else:
                    success, msg, slot_info = st.session_state.manager.park_vehicle(v_num, actual_type)
                    if success:
                        pass_data = {
                            "slot_id": slot_info["slot_id"],
                            "floor_name": slot_info["floor_name"],
                            "floor_number": slot_info["floor_number"],
                            "vehicle": v_num,
                            "vtype": actual_type,
                            "dist": slot_info["distance_from_stairs"],
                            "time": datetime.now().strftime("%I:%M:%S %p"),
                            "date": datetime.now().strftime("%d-%b-%Y")
                        }
                        st.session_state.parking_success = pass_data
                        st.session_state.floating_pass = pass_data
                        st.session_state["park_veh_input"] = ""
                        st.rerun()
                    else:
                        st.error(msg)

            # Park Another button (only shows after a successful park)
            if st.session_state.get("parking_success"):
                if st.button("🅿️ Park Another Vehicle", use_container_width=True, key="park_another_btn"):
                    st.session_state.parking_success = None
                    st.session_state.floating_pass = None
                    st.session_state["park_veh_input"] = ""
                    st.rerun()

    with col_preview:
        target_f = 2 if actual_type == "4-Wheeler" else 0
        target_f_name = "Basement 2 (4W)" if target_f == 2 else "Ground Floor (2W)"
        hl_slot = st.session_state.parking_success["slot_id"] if st.session_state.get("parking_success") else (best['slot_id'] if best else None)
        
        with st.container(border=True):
            st.markdown(clean_html(f"""
                <div class="park-map-wrapper">
                    <div class="ref-section-header" style="margin-bottom:0.6rem;">
                        <div class="ref-section-title" style="font-size:1.15rem;">
                            <span style="color:#6c5dd3; font-size:1.2rem;">🗺️</span>
                            Live Allocation Map &bull; {target_f_name}
                        </div>
                    </div>
                    <div style="flex:1; display:flex; align-items:center; justify-content:center; padding:0.4rem 0;">
                        {generate_dynamic_parking_svg(target_f, highlight_slot=hl_slot)}
                    </div>
                    <div class="legend-bar" style="margin-top:0.6rem;">
                        <div class="legend-dot-item"><span class="dot-circle dot-green"></span> Available</div>
                        <div class="legend-dot-item"><span class="dot-circle dot-red"></span> Occupied</div>
                        <div class="legend-dot-item"><span style="width:10px; height:10px; border-radius:50%; background:#6c5dd3;"></span> Recommended Slot</div>
                    </div>
                </div>
            """), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# 3. EXIT VEHICLE PAGE
# ───────────────────────────────────────────────────────────
def render_exit_vehicle():
    render_top_bar()

    # ─── HEADER ROW: Title (left) + Rectangular Exit Receipt (right blank space) ───
    has_pass = st.session_state.get("floating_exit_pass") is not None

    if has_pass:
        col_hdr, col_pass_area = st.columns([1.15, 1.35])
    else:
        col_hdr = st.container()
        col_pass_area = None

    with col_hdr:
        st.markdown(clean_html("""
            <div class="subpage-header-box">
                <div class="subpage-badge-pill">🚪 VEHICLE EXIT TERMINAL</div>
                <h1 class="subpage-main-title">Exit & Release Parking</h1>
                <div class="subpage-sub-desc">Automated slot release, duration calculation, and digital checkout receipt</div>
            </div>
        """), unsafe_allow_html=True)

    if has_pass and col_pass_area is not None:
        fp = st.session_state.floating_exit_pass
        vtype_icon = "🚗" if fp.get("vtype") == "4-Wheeler" else "🏍️"
        with col_pass_area:
            st.markdown(clean_html(f"""
                <div class="rect-pass-card rect-exit-pass-card">
                    <div class="rp-top-row" style="padding-right: 32px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="rp-badge" style="color:#16a34a;">Digital Exit Receipt</span>
                            <span class="rp-status-pill" style="background:#dcfce7; color:#15803d;">✓ Paid & Released</span>
                        </div>
                    </div>
                    <div class="rp-body">
                        <div class="rp-slot-block rp-exit-slot-block">
                            <div class="rp-slot-id">{fp['slot_id']}</div>
                            <div class="rp-slot-floor">Slot Released</div>
                            <div class="rp-slot-dist">Vacant Now</div>
                        </div>
                        <div class="rp-info-grid">
                            <div>
                                <div class="rp-field-label">Vehicle</div>
                                <div class="rp-field-val">{vtype_icon} {fp['vehicle']}</div>
                            </div>
                            <div>
                                <div class="rp-field-label">Category</div>
                                <div class="rp-field-val">{fp['vtype']}</div>
                            </div>
                            <div>
                                <div class="rp-field-label">Duration</div>
                                <div class="rp-field-val">{fp['duration_str']}</div>
                            </div>
                            <div>
                                <div class="rp-field-label">Total Fee</div>
                                <div class="rp-field-val" style="color:#16a34a; font-size:0.85rem;">₹{fp['fee']}</div>
                            </div>
                        </div>
                    </div>
                    <div class="rp-barcode-row">
                        <span class="rp-barcode-bars">||| | |||| | ||| || ||||</span>
                        <span class="rp-barcode-hint">Exit verified &bull; Slot released successfully</span>
                    </div>
                </div>
            """), unsafe_allow_html=True)

            if st.button("✕", key="dismiss_exit_pass", help="Dismiss receipt"):
                st.session_state.floating_exit_pass = None
                st.session_state.exit_success = None
                st.rerun()

    # ─── EQUAL-HEIGHT FORM + ACTIVE ROSTER COLUMNS ───
    st.markdown('<div class="exit-equal-height"></div>', unsafe_allow_html=True)
    col_exit_form, col_active_roster = st.columns([1.15, 1.35])

    active_vehicles = get_active_parked_list()

    with col_exit_form:
        with st.container(border=True):
            st.markdown('<div class="exit-form-box"></div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:800; font-size:1.15rem; color:#1e293b; margin-bottom:0.75rem;">🚗 Quick Checkout</div>', unsafe_allow_html=True)

            active_veh_options = ["-- Select from currently parked vehicles --"] + [f"{v[0]}  (Slot: {v[1]}, {v[2]})" for v in active_vehicles]

            selected_active = st.selectbox("Choose Parked Vehicle", active_veh_options, key="active_veh_dropdown")
            
            # Manual input as alternative
            st.text_input(
                "Or Type Vehicle Registration Number",
                placeholder="e.g. GJ01AB1234",
                key="exit_veh_manual",
                on_change=to_uppercase,
                args=("exit_veh_manual",)
            )

            chosen_veh = ""
            if selected_active and selected_active != "-- Select from currently parked vehicles --":
                chosen_veh = selected_active.split()[0].strip()
            elif st.session_state.get("exit_veh_manual", "").strip():
                chosen_veh = st.session_state.get("exit_veh_manual", "").strip()

            # If a vehicle is selected, display live preview card
            if chosen_veh:
                match = next((v for v in active_vehicles if v[0] == chosen_veh), None)
                if match:
                    v_num, s_id, v_cat, e_time = match
                    try:
                        e_dt = datetime.fromisoformat(e_time)
                        dur_min = int(round((datetime.now() - e_dt).total_seconds() / 60))
                    except:
                        dur_min = 25
                        e_dt = datetime.now()

                    rate = 20 if "2-Wheeler" in v_cat else 40
                    hours = max(1, (dur_min + 59) // 60)
                    fee = hours * rate
                    dur_h = dur_min // 60
                    dur_m = dur_min % 60
                    dur_display = f"{dur_h}h {dur_m}m" if dur_h > 0 else f"{dur_min} mins"

                    st.markdown(clean_html(f"""
                        <div style="background:#fff1f2; border:1px solid #fecdd3; border-radius:14px; padding:1rem 1.1rem; margin:0.8rem 0 1rem 0;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:1.25rem; font-weight:800; color:#9f1239;">{v_num}</span>
                                <span style="font-size:0.8rem; font-weight:700; color:#ffffff; background:#e11d48; padding:3px 10px; border-radius:12px;">Slot {s_id}</span>
                            </div>
                            <div style="margin-top:10px; font-size:0.84rem; color:#475569; display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                                <div><b>Parked At:</b> {e_dt.strftime('%I:%M %p')}</div>
                                <div><b>Duration:</b> {dur_display}</div>
                                <div><b>Category:</b> {v_cat}</div>
                                <div><b>Calculated Fee:</b> ₹{fee}</div>
                            </div>
                        </div>
                    """), unsafe_allow_html=True)

            if st.button("🚪 Release Slot & Complete Exit", use_container_width=True):
                if not chosen_veh:
                    st.error("❌ Please select or enter a vehicle registration number to exit")
                else:
                    match = next((v for v in active_vehicles if v[0] == chosen_veh), None)
                    v_cat = match[2] if match else None

                    success, data = st.session_state.manager.exit_vehicle(chosen_veh)
                    if success:
                        s_id = data["slot_id"]
                        if not v_cat:
                            v_cat = "4-Wheeler" if ("4W" in s_id or "B2" in s_id) else "2-Wheeler"

                        dur = data["duration"]
                        dur_h = dur // 60
                        dur_m = dur % 60
                        duration_str = f"{dur_h}h {dur_m}m" if dur_h > 0 else f"{dur} mins"

                        rate = 20 if "2-Wheeler" in v_cat else 40
                        calc_h = max(1, (dur + 59) // 60)
                        fee = calc_h * rate

                        pass_data = {
                            "vehicle": chosen_veh,
                            "slot_id": s_id,
                            "vtype": v_cat,
                            "duration": dur,
                            "duration_str": duration_str,
                            "fee": fee,
                            "entry_time": datetime.fromisoformat(data["entry_time"]).strftime("%I:%M %p"),
                            "exit_time": data["exit_time"].strftime("%I:%M:%S %p"),
                            "date": data["exit_time"].strftime("%d-%b-%Y")
                        }
                        st.session_state.exit_success = pass_data
                        st.session_state.floating_exit_pass = pass_data
                        st.session_state.pop("exit_veh_manual", None)
                        st.session_state.pop("active_veh_dropdown", None)
                        st.rerun()
                    else:
                        st.error(data)

            # Exit Another Vehicle button (only shows after a successful exit)
            if st.session_state.get("floating_exit_pass"):
                if st.button("🚪 Exit Another Vehicle", use_container_width=True, key="exit_another_btn"):
                    st.session_state.exit_success = None
                    st.session_state.floating_exit_pass = None
                    st.rerun()

    with col_active_roster:
        with st.container(border=True):
            st.markdown('<div class="exit-roster-box"></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-weight:800; font-size:1.15rem; color:#1e293b; margin-bottom:0.8rem;">📋 Active Parked Vehicles ({len(active_vehicles)})</div>', unsafe_allow_html=True)

            if active_vehicles:
                roster_html = ""
                for v in active_vehicles:
                    try:
                        e_t = datetime.fromisoformat(v[3]).strftime("%I:%M %p")
                    except:
                        e_t = "12:00 PM"
                    v_icon = "🚗" if v[2] == "4-Wheeler" else "🏍️"
                    roster_html += f"""
                        <tr>
                            <td style="font-weight:800; color:#1e293b;">{v[0]}</td>
                            <td>{v_icon} {v[2]}</td>
                            <td><b style="color:#6c5dd3;">{v[1]}</b></td>
                            <td style="color:#64748b;">{e_t}</td>
                            <td><span class="badge-status-parked">Active</span></td>
                        </tr>
                    """
                st.markdown(clean_html(f"""
                    <div style="max-height: 380px; overflow-y: auto; padding-right: 4px;">
                        <table class="activity-table-clean">
                            <thead>
                                <tr>
                                    <th>Vehicle</th>
                                    <th>Type</th>
                                    <th>Slot</th>
                                    <th>Entry</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {roster_html}
                            </tbody>
                        </table>
                    </div>
                """), unsafe_allow_html=True)
            else:
                st.info("No vehicles currently parked.")


# ───────────────────────────────────────────────────────────
# 4. PARKING LAYOUT PAGE
# ───────────────────────────────────────────────────────────
def render_parking_layout():
    render_top_bar()

    st.markdown(clean_html("""
        <div class="subpage-header-box">
            <div class="subpage-badge-pill">🗺️ LIVE MAP VISUALIZER</div>
            <h1 class="subpage-main-title">Interactive Parking Layout</h1>
            <div class="subpage-sub-desc">Real-time top-down visualizer with live car coordinates, bay occupancy and slot details</div>
        </div>
    """), unsafe_allow_html=True)

    tab_gf, tab_b1, tab_b2 = st.tabs(["🏢 Ground Floor (2W)", "🏢 Basement 1 (2W)", "🚗 Basement 2 (4W)"])

    floor_idx_map = {0: tab_gf, 1: tab_b1, 2: tab_b2}

    for f_num, tab in floor_idx_map.items():
        with tab:
            f_slots = get_floor_slots_detail(f_num)
            occ_count = sum(1 for s in f_slots if s[4])
            vac_count = len(f_slots) - occ_count
            occ_rate = round((occ_count / len(f_slots)) * 100) if len(f_slots) > 0 else 0

            # Filter & Stats Bar
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Total Slots", len(f_slots))
            with m2:
                st.metric("Occupied Slots", occ_count)
            with m3:
                st.metric("Available Slots", vac_count)
            with m4:
                st.metric("Occupancy Rate", f"{occ_rate}%")

            st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

            # Live SVG Map
            svg_code = generate_dynamic_parking_svg(f_num)
            st.markdown(clean_html(f"""
                <div class="ref-section-card">
                    <div>
                        {svg_code}
                    </div>
                    <div class="legend-bar">
                        <div class="legend-dot-item"><span class="dot-circle dot-green"></span> Available ({vac_count})</div>
                        <div class="legend-dot-item"><span class="dot-circle dot-red"></span> Occupied ({occ_count})</div>
                        <div class="legend-dot-item"><span class="dot-circle dot-amber"></span> Stairs & Elevator</div>
                    </div>
                </div>
            """), unsafe_allow_html=True)

            # Slot Details Grid
            st.markdown('<div style="font-weight:800; font-size:1.1rem; color:#1e293b; margin:1rem 0 0.5rem 0;">📋 Slot Roster Breakdown</div>', unsafe_allow_html=True)
            
            grid_cols = st.columns(5)
            for idx, s in enumerate(f_slots):
                col_i = idx % 5
                with grid_cols[col_i]:
                    is_occ = s[4]
                    v_num = s[8] if s[8] else "None"
                    stat_bg = "#fef2f2" if is_occ else "#f0fdf4"
                    stat_border = "#fecaca" if is_occ else "#bbf7d0"
                    stat_txt = f"<b style='color:#dc2626;'>{v_num}</b>" if is_occ else "<span style='color:#16a34a; font-weight:700;'>AVAILABLE</span>"
                    
                    st.markdown(clean_html(f"""
                        <div style="background:{stat_bg}; border:1px solid {stat_border}; border-radius:10px; padding:0.6rem 0.8rem; margin-bottom:8px;">
                            <div style="font-weight:800; font-size:0.9rem; color:#1e293b;">{s[0]}</div>
                            <div style="font-size:0.75rem; margin-top:3px;">{stat_txt}</div>
                            <div style="font-size:0.68rem; color:#94a3b8; margin-top:2px;">Distance: {s[5]}m</div>
                        </div>
                    """), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# 5. RUSH PREDICTION PAGE
# ───────────────────────────────────────────────────────────
def render_rush_prediction():
    render_top_bar()

    st.markdown(clean_html("""
        <div class="subpage-header-box">
            <div class="subpage-badge-pill">📈 AI RUSH FORECASTING</div>
            <h1 class="subpage-main-title">Rush Hour & Congestion Analytics</h1>
            <div class="subpage-sub-desc">Historical occupancy patterns and peak arrival recommendations</div>
        </div>
    """), unsafe_allow_html=True)

    rush_data = st.session_state.manager.predict_rush_hours()
    
    # Current Hour Status
    curr = rush_data.get('current_hour_prediction')
    if curr:
        st.markdown(clean_html(f"""
            <div class="ref-section-card" style="background:#eef2ff; border-color:#c7d2fe;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:0.78rem; font-weight:800; color:#6c5dd3;">CURRENT TIME SLOT ({curr['time_label']})</div>
                        <div style="font-size:1.6rem; font-weight:900; color:#1e293b; margin-top:4px;">{curr['rush_level']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:0.75rem; color:#64748b;">Expected Occupancy</div>
                        <div style="font-size:1.8rem; font-weight:900; color:#6c5dd3;">{curr['avg_occupancy']}%</div>
                    </div>
                </div>
            </div>
        """), unsafe_allow_html=True)

    if rush_data.get('today_predictions'):
        df = pd.DataFrame(rush_data['today_predictions'])
        
        with st.container(border=True):
            st.markdown('<div style="font-weight:800; font-size:1.1rem; color:#1e293b; margin-bottom:1rem;">📅 Today\'s Hourly Occupancy Forecast</div>', unsafe_allow_html=True)

            fig = px.line(
                df, x='time_label', y='avg_occupancy',
                labels={'time_label': 'Hour of Day', 'avg_occupancy': 'Expected Occupancy (%)'},
                markers=True
            )
            fig.add_hrect(y0=80, y1=100, fillcolor="rgba(239,68,68,0.06)", annotation_text="High Rush", annotation_position="right")
            fig.add_hrect(y0=50, y1=80, fillcolor="rgba(245,158,11,0.04)", annotation_text="Moderate", annotation_position="right")
            fig.add_hrect(y0=0, y1=50, fillcolor="rgba(34,197,94,0.04)", annotation_text="Low Rush", annotation_position="right")

            fig.update_layout(
                height=340,
                paper_bgcolor='#ffffff',
                plot_bgcolor='#ffffff',
                font=dict(family='Plus Jakarta Sans', color='#1e293b'),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='#f1f5f9',
                    color='#1e293b',
                    tickfont=dict(color='#1e293b', size=11, family='Plus Jakarta Sans'),
                    title_font=dict(color='#0f172a', size=12, family='Plus Jakarta Sans')
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#edf2f7',
                    color='#1e293b',
                    tickfont=dict(color='#1e293b', size=11, family='Plus Jakarta Sans'),
                    title_font=dict(color='#0f172a', size=12, family='Plus Jakarta Sans'),
                    range=[0, 100]
                ),
            )
            fig.update_traces(line_color='#6c5dd3', marker_color='#5a4bcf')
            st.plotly_chart(fig, use_container_width=True, key="rush_pred_chart_page")


# ───────────────────────────────────────────────────────────
# 6. STATISTICS PAGE
# ───────────────────────────────────────────────────────────
def render_statistics():
    render_top_bar()

    st.markdown(clean_html("""
        <div class="subpage-header-box">
            <div class="subpage-badge-pill">⏱️ VEHICLE LOGS & METRICS</div>
            <h1 class="subpage-main-title">Parking History & Analytics</h1>
            <div class="subpage-sub-desc">Detailed booking audit, duration statistics, and turnover history</div>
        </div>
    """), unsafe_allow_html=True)

    stats = st.session_state.manager.get_statistics()
    recent = stats.get("recent_bookings", [])

    tot = len(recent)
    active_cnt = sum(1 for b in recent if b.get('status') == 'Active')
    exited_cnt = tot - active_cnt

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Records", tot)
    with c2: st.metric("Active Parked", active_cnt)
    with c3: st.metric("Completed Exits", exited_cnt)
    with c4: st.metric("Average Duration", "42 min")

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div style="font-weight:800; font-size:1.1rem; color:#1e293b; margin-bottom:1rem;">📋 Complete Activity Log</div>', unsafe_allow_html=True)

        if recent:
            df = pd.DataFrame(recent)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No activity records found.")


# ───────────────────────────────────────────────────────────
# 7. SETTINGS PAGE
# ───────────────────────────────────────────────────────────
def render_settings():
    render_top_bar()

    st.markdown(clean_html("""
        <div class="subpage-header-box">
            <div class="subpage-badge-pill">⚙️ SYSTEM CONTROLS</div>
            <h1 class="subpage-main-title">Admin Configuration</h1>
            <div class="subpage-sub-desc">Database operations, access privileges, and system resets</div>
        </div>
    """), unsafe_allow_html=True)

    if not st.session_state.admin_authenticated:
        st.markdown(clean_html("""
            <div class="ref-section-card" style="max-width:500px;">
                <div style="font-weight:800; color:#1e293b; font-size:1.1rem; margin-bottom:0.5rem;">🔐 Admin Authentication Required</div>
                <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1rem;">Enter your administrator password to unlock privileged settings.</div>
            </div>
        """), unsafe_allow_html=True)

        admin_pass = st.text_input("Admin Password", type="password", key="admin_pwd_field")
        if st.button("Unlock Admin Mode"):
            if hashlib.sha256(admin_pass.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
                st.session_state.admin_authenticated = True
                st.success("✅ Admin authenticated")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    else:
        st.success("🟢 Administrator Mode Active")

        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown('<div style="font-weight:800; font-size:1.1rem; color:#1e293b; margin-bottom:0.4rem;">↩️ Undo Last Action</div>', unsafe_allow_html=True)
                st.write("Reverse the most recent vehicle check-in.")
                if st.button("Undo Last Parking", use_container_width=True):
                    success, msg = st.session_state.manager.undo_last_parking()
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with col2:
            with st.container(border=True):
                st.markdown('<div style="font-weight:800; font-size:1.1rem; color:#1e293b; margin-bottom:0.4rem;">🔄 Reset Database</div>', unsafe_allow_html=True)
                st.write("Wipe booking logs and restore all slots to vacant.")
                if st.button("Reset Database", use_container_width=True):
                    if st.checkbox("⚠️ Confirm complete database wipe"):
                        st.session_state.manager.db.reset_database()
                        st.success("Database restored successfully")
                        st.rerun()

        if st.button("🔒 Logout Admin Session"):
            st.session_state.admin_authenticated = False
            st.rerun()


# (Floating pass is now rendered inline in render_park_vehicle)


# ───────────────────────────────────────────────────────────
# MAIN APPLICATION CONTROLLER
# ───────────────────────────────────────────────────────────
def main():
    # Handle query param routing
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
                    <circle cx="7" cy="17" r="2"></circle><circle cx="17" cy="17" r="2"></circle>
                </svg>
            </div>
            <div>
                <div class="brand-title">Smart Parking</div>
                <div class="brand-sub">Management System</div>
            </div>
        </div>
    """), unsafe_allow_html=True)

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

    current_idx = menu_items.index(st.session_state.nav_page) if st.session_state.nav_page in menu_items else 0
    selected = st.sidebar.radio(
        "Navigation",
        menu_items,
        index=current_idx,
        label_visibility="collapsed",
        key="sidebar_nav_radio"
    )

    if selected != st.session_state.nav_page:
        st.session_state.nav_page = selected
        st.rerun()

    # Sidebar Bottom Car Illustration
    st.sidebar.markdown('<div style="margin-top: 0.3rem;"></div>', unsafe_allow_html=True)
    if os.path.exists("assets/sidebar_car.png"):
        st.sidebar.image("assets/sidebar_car.png", use_container_width=True)

    # ─── ROUTER ───
    current = st.session_state.nav_page

    # Clear pass when leaving Park Vehicle tab
    if current != "🚗  Park Vehicle":
        st.session_state.floating_pass = None
        st.session_state.parking_success = None

    # Clear exit receipt when leaving Exit Vehicle tab
    if current != "🚪  Exit Vehicle":
        st.session_state.floating_exit_pass = None
        st.session_state.exit_success = None

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