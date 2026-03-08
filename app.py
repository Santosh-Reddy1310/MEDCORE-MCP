import streamlit as st
import sys
import os
from datetime import datetime
import sqlite3
from dotenv import load_dotenv

load_dotenv(".env.local")

sys.path.append(os.path.join(os.path.dirname(__file__), "client"))
from ai_client import ask_sync

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "hospital.db")

st.set_page_config(
    page_title="MedCore MCP",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@300;400;500;600&family=Outfit:wght@300;400;500;600;700&display=swap');

/* ══════════════════════════════════════════════
   MEDCORE UI REDESIGN - MODERN MEDICAL DASHBOARD
   ══════════════════════════════════════════════ */

/* ── RESET & BASE ── */
*, *::before, *::after { 
    box-sizing: border-box; 
    margin: 0; 
    padding: 0;
}

html, body, .stApp {
    background: linear-gradient(180deg, #0A0E1A 0%, #050812 100%) !important;
    color: #E8EDF5 !important;
    font-family: 'Outfit', -apple-system, sans-serif !important;
    overflow-x: hidden;
}

.block-container {
    padding: 2rem 2.5rem 3rem 2.5rem !important;
    max-width: 100% !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }

/* ── CUSTOM SCROLLBAR ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { 
    background: #0A0E1A; 
    border-radius: 10px;
}
::-webkit-scrollbar-thumb { 
    background: linear-gradient(180deg, #3B82F6 0%, #2563EB 100%);
    border-radius: 10px;
    border: 2px solid #0A0E1A;
}
::-webkit-scrollbar-thumb:hover { 
    background: linear-gradient(180deg, #2563EB 0%, #1D4ED8 100%);
}
* { scrollbar-width: thin; scrollbar-color: #3B82F6 #0A0E1A; }

/* ── SIDEBAR REDESIGN ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F1420 0%, #0A0E1A 100%) !important;
    border-right: 1px solid #1E293B !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3) !important;
}

section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

/* ── NAVIGATION RADIO ── */
.stRadio > div { 
    gap: 6px !important; 
}

.stRadio > label {
    display: none !important;
}

.stRadio label {
    background: transparent !important;
    border: 1.5px solid transparent !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    color: #64748B !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
}

.stRadio label::before {
    content: '' !important;
    position: absolute !important;
    inset: 0 !important;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(37, 99, 235, 0.1)) !important;
    opacity: 0 !important;
    transition: opacity 0.3s ease !important;
}

.stRadio label:hover {
    background: rgba(59, 130, 246, 0.08) !important;
    border-color: rgba(59, 130, 246, 0.3) !important;
    color: #93C5FD !important;
    transform: translateX(4px) !important;
}

.stRadio label:hover::before {
    opacity: 1 !important;
}

.stRadio label:has(input:checked) {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(37, 99, 235, 0.12)) !important;
    border-color: #3B82F6 !important;
    color: #BFDBFE !important;
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    transform: translateX(4px) !important;
}

.stRadio label:has(input:checked)::after {
    content: '' !important;
    position: absolute !important;
    left: 0 !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    width: 4px !important;
    height: 50% !important;
    background: linear-gradient(180deg, #3B82F6 0%, #2563EB 100%) !important;
    border-radius: 0 3px 3px 0 !important;
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.6) !important;
}

/* ── BUTTONS REDESIGN ── */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.08)) !important;
    border: 1.5px solid rgba(59, 130, 246, 0.3) !important;
    color: #93C5FD !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
}

div[data-testid="stButton"] button::before {
    content: '' !important;
    position: absolute !important;
    inset: 0 !important;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.15)) !important;
    opacity: 0 !important;
    transition: opacity 0.3s ease !important;
}

div[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.15)) !important;
    border-color: #3B82F6 !important;
    color: #BFDBFE !important;
    box-shadow: 0 0 25px rgba(59, 130, 246, 0.3), 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    transform: translateY(-2px) !important;
}

div[data-testid="stButton"] button:hover::before {
    opacity: 1 !important;
}

div[data-testid="stButton"] button:active {
    transform: translateY(0) !important;
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.2) !important;
}

div[data-testid="stButton"] button:focus-visible {
    outline: 2px solid #3B82F6 !important;
    outline-offset: 3px !important;
}

/* ── TEXT INPUT REDESIGN ── */
.stTextInput > div > div > input {
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1.5px solid rgba(59, 130, 246, 0.25) !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.9rem !important;
    padding: 13px 18px !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(10px) !important;
}

.stTextInput > div > div > input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15), 0 0 20px rgba(59, 130, 246, 0.2) !important;
    background: rgba(15, 23, 42, 0.95) !important;
    outline: none !important;
}

.stTextInput > div > div > input::placeholder {
    color: #475569 !important;
}

.stTextInput > div > div > input:hover:not(:focus) {
    border-color: rgba(59, 130, 246, 0.4) !important;
    background: rgba(15, 23, 42, 0.9) !important;
}

/* ── SPINNER ── */
.stSpinner > div { 
    border-top-color: #3B82F6 !important;
    border-right-color: #60A5FA !important;
    border-width: 3px !important;
}

/* ── ALERTS ── */
.stAlert {
    background: rgba(59, 130, 246, 0.08) !important;
    border: 1.5px solid rgba(59, 130, 246, 0.3) !important;
    border-left: 4px solid #3B82F6 !important;
    border-radius: 10px !important;
    color: #93C5FD !important;
    padding: 14px 18px !important;
    backdrop-filter: blur(10px) !important;
}

/* ── MARKDOWN STYLING ── */
.stMarkdown p { 
    color: #94A3B8 !important; 
    line-height: 1.7 !important; 
}
.stMarkdown h1 { 
    color: #F1F5F9 !important; 
    font-weight: 700 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
.stMarkdown h2 { 
    color: #E2E8F0 !important; 
    font-weight: 600 !important; 
    font-family: 'Space Grotesk', sans-serif !important;
}
.stMarkdown h3 { 
    color: #CBD5E1 !important; 
    font-weight: 500 !important; 
}
.stMarkdown strong { 
    color: #60A5FA !important; 
    font-weight: 600 !important;
}
.stMarkdown code { 
    background: rgba(59, 130, 246, 0.1) !important; 
    color: #93C5FD !important;
    padding: 3px 8px !important;
    border-radius: 5px !important;
    font-size: 0.88em !important;
    border: 1px solid rgba(59, 130, 246, 0.2) !important;
}

/* ── ANIMATIONS ── */
@keyframes pulse-glow {
    0%, 100% { 
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
        opacity: 1;
    }
    50% { 
        box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
        opacity: 0.8;
    }
}

@keyframes shimmer {
    0% { opacity: 0.8; }
    50% { opacity: 1; }
    100% { opacity: 0.8; }
}

@keyframes slide-up {
    from { 
        opacity: 0; 
        transform: translateY(20px); 
    }
    to { 
        opacity: 1; 
        transform: translateY(0); 
    }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

@keyframes ticker-scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

/* ── RESPONSIVE DESIGN ── */
@media (max-width: 1024px) {
    .block-container { padding: 1.5rem !important; }
}

@media (max-width: 768px) {
    .block-container { padding: 1rem !important; }
    div[data-testid="column"] { 
        min-width: 100% !important; 
        width: 100% !important; 
    }
}

/* ── ACCESSIBILITY ── */
*:focus-visible {
    outline: 2px solid #60A5FA !important;
    outline-offset: 3px !important;
}

/* ── PERFORMANCE ── */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* ── UTILITY CLASSES ── */
.glass-effect {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}

.glow-blue {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.3) !important;
}

.glow-red {
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.3) !important;
}

.glow-green {
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)


# ── DB HELPERS ──────────────────────────────────────────────────

def get_quick_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as n FROM patients WHERE status != 'discharged'")
        active = c.fetchone()["n"]
        c.execute("SELECT COUNT(*) as n, SUM(is_occupied) as occ FROM beds")
        beds = c.fetchone()
        c.execute("SELECT COUNT(*) as n FROM patients WHERE ward = 'ICU'")
        icu = c.fetchone()["n"]
        c.execute("SELECT COUNT(*) as n FROM doctors WHERE available = 1")
        docs = c.fetchone()["n"]
        c.execute("SELECT COUNT(*) as n FROM appointments WHERE status = 'scheduled'")
        appts = c.fetchone()["n"]
        c.execute("SELECT COUNT(*) as n FROM patients WHERE status = 'critical'")
        critical = c.fetchone()["n"]
        conn.close()
        total = beds["n"] or 1
        occ = int(beds["occ"] or 0)
        return {
            "active_patients": active,
            "total_beds": total,
            "occupied_beds": occ,
            "free_beds": total - occ,
            "icu_patients": icu,
            "available_doctors": docs,
            "pending_appointments": appts,
            "critical_patients": critical,
            "occupancy_rate": round((occ / total) * 100, 1),
        }
    except Exception:
        return {}


def get_ward_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT ward, COUNT(*) as total, SUM(is_occupied) as occupied FROM beds GROUP BY ward ORDER BY ward")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows
    except Exception:
        return []


def get_recent_patients(limit=5):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT p.name, p.ward, p.status, p.diagnosis, p.age, p.gender,
                   d.name as doctor_name
            FROM patients p
            LEFT JOIN doctors d ON p.doctor_id = d.id
            WHERE p.status != 'discharged'
            ORDER BY p.admission_date DESC
            LIMIT ?
        """, (limit,))
        return [dict(r) for r in c.fetchall()]
    except Exception:
        return []


# ── SESSION STATE ──────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ── MINIMAL SIDEBAR ────────────────────────────────────────────

with st.sidebar:
    # Compact Sidebar Header
    st.markdown(f"""
    <div style="
        padding: 24px 20px;
        position: relative;
        text-align: center;
    ">
        <div style="
            width:56px; height:56px;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(37, 99, 235, 0.2));
            border: 2px solid rgba(59, 130, 246, 0.5);
            border-radius:14px;
            display:flex; align-items:center; justify-content:center;
            font-size:28px;
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
            margin: 0 auto 16px auto;
        ">🏥</div>
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.6rem; font-weight:700; color:#F1F5F9; letter-spacing:0.02em; text-shadow: 0 2px 8px rgba(59, 130, 246, 0.2); margin-bottom:6px;">MEDCORE</div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.66rem; color:#64748B; letter-spacing:0.1em; margin-bottom:16px;">MCP ÷ AI ÷ v2.0</div>
        
        <div style="
            display:flex; align-items:center; gap:8px; justify-content:center;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.25);
            border-radius:8px;
            padding:6px 10px;
        ">
            <div style="width:6px; height:6px; border-radius:50%; background:#10B981; animation: shimmer 2s ease-in-out infinite; box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);"></div>
            <span style="font-family:'IBM Plex Mono',monospace; font-size:0.66rem; color:#6EE7B7; letter-spacing:0.05em; font-weight:500;">ONLINE</span>
        </div>
        
        <div style="
            margin-top:20px; padding-top:20px;
            border-top: 1px solid rgba(59, 130, 246, 0.15);
            font-family:'IBM Plex Mono',monospace; 
            font-size:0.64rem; 
            color:#64748B;
            line-height:1.6;
        ">
            {datetime.now().strftime('%d %b %Y')}<br>
            {datetime.now().strftime('%H:%M:%S')}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── TOP BAR ────────────────────────────────────────────────────

stats = get_quick_stats()

def top_bar():
    items = []
    if stats:
        items = [
            f"\U0001F465 {stats.get('active_patients','\u2014')} ACTIVE",
            f"\U0001F3E5 {stats.get('occupancy_rate','\u2014')}% OCCUPIED",
            f"\U0001F6A8 {stats.get('icu_patients','\u2014')} ICU",
            f"\u2695 {stats.get('available_doctors','\u2014')} DOCTORS",
            f"\u2705 {stats.get('free_beds','\u2014')} FREE BEDS",
            f"\U0001F4C5 {stats.get('pending_appointments','\u2014')} PENDING",
        ]
    ticker_text = "    \u2022    ".join(items * 3) if items else "LOADING HOSPITAL DATA..."
    st.markdown(f"""
    <div style="
        background: rgba(15, 23, 42, 0.6);
        border-bottom: 1px solid rgba(59, 130, 246, 0.2);
        padding: 10px 0;
        margin: -2rem -2.5rem 2rem -2.5rem;
        overflow: hidden;
        position: relative;
        backdrop-filter: blur(10px);
    ">
        <div style="
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, 
                transparent 0%, 
                rgba(59, 130, 246, 0.05) 50%, 
                transparent 100%);
            animation: ticker-scroll 3s linear infinite;
        "></div>
        <div style="
            display: inline-block;
            white-space: nowrap;
            animation: ticker-scroll 45s linear infinite;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            color: #94A3B8;
            letter-spacing: 0.08em;
            font-weight: 500;
        ">{ticker_text}</div>
    </div>
    """, unsafe_allow_html=True)

top_bar()


# ═══════════════════════════════════════════════
# SINGLE PAGE: DASHBOARD + AI ASSISTANT
# ═══════════════════════════════════════════════

# Always show everything on one page
if True:

    # Modern Page Header
    st.markdown(f"""
    <div style="
        margin-bottom: 2.5rem;
        padding: 24px;
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: 16px;
        backdrop-filter: blur(10px);
        animation: slide-up 0.5s ease;
    ">
        <div style="display:flex; align-items:center; gap:16px; margin-bottom:10px;">
            <div style="
                width: 12px;
                height: 48px;
                background: linear-gradient(180deg, #3B82F6 0%, #2563EB 100%);
                border-radius: 6px;
                box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
            "></div>
            <div>
                <div style="display:flex; align-items:baseline; gap:14px;">
                    <span style="font-family:'Space Grotesk',sans-serif; font-size:2.2rem; font-weight:700; color:#F1F5F9; letter-spacing:0.02em; text-shadow: 0 2px 8px rgba(0,0,0,0.3);">Hospital Overview</span>
                    <span style="
                        font-family:'IBM Plex Mono',monospace; 
                        font-size:0.7rem; 
                        color:#10B981; 
                        background: rgba(16, 185, 129, 0.15);
                        padding: 4px 12px;
                        border-radius: 6px;
                        letter-spacing: 0.08em;
                        border: 1px solid rgba(16, 185, 129, 0.3);
                        font-weight: 600;
                    ">• LIVE</span>
                </div>
                <span style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem; color:#64748B; letter-spacing:0.04em; margin-top:6px; display:block;">
                    📅 {datetime.now().strftime('%A, %d %B %Y  •  %H:%M')}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if stats:
        occ = stats["occupancy_rate"]
        occ_color = "#EF4444" if occ > 85 else ("#F59E0B" if occ > 65 else "#10B981")
        occ_glow = "rgba(239, 68, 68, 0.3)" if occ > 85 else ("rgba(245, 158, 11, 0.3)" if occ > 65 else "rgba(16, 185, 129, 0.3)")

        # ── ROW 1: FOUR PRIMARY METRICS ──
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(15, 23, 42, 0.7) 100%);
                border: 1.5px solid rgba(59, 130, 246, 0.3);
                border-top: 3px solid #3B82F6;
                border-radius: 16px;
                padding: 24px;
                position: relative;
                overflow: hidden;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                animation: slide-up 0.6s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 40px rgba(59, 130, 246, 0.25)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                <div style="
                    position: absolute;
                    top: -50%;
                    right: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
                    pointer-events: none;
                "></div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#64748B; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:14px; font-weight:600;">👥 Active Patients</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-size:3.2rem; font-weight:700; color:#60A5FA; line-height:1; text-shadow: 0 0 20px rgba(96, 165, 250, 0.3);">{stats['active_patients']}</div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#475569; margin-top:10px;">Currently admitted</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(15, 23, 42, 0.7) 100%);
                border: 1.5px solid rgba(168, 85, 247, 0.3);
                border-top: 3px solid {occ_color};
                border-radius: 16px;
                padding: 24px;
                position: relative;
                overflow: hidden;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                animation: slide-up 0.7s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 40px {occ_glow}';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                <div style="
                    position: absolute;
                    top: -50%;
                    right: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(circle, {occ_glow} 0%, transparent 70%);
                    pointer-events: none;
                "></div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#64748B; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:14px; font-weight:600;">🏥 Bed Occupancy</div>
                <div style="display:flex; align-items:baseline; gap:8px;">
                    <span style="font-family:'Space Grotesk',sans-serif; font-size:3.2rem; font-weight:700; color:{occ_color}; line-height:1; text-shadow: 0 0 20px {occ_glow};">{occ:.1f}</span>
                    <span style="font-family:'Space Grotesk',sans-serif; font-size:1.6rem; font-weight:600; color:#475569;">%</span>
                </div>
                <div style="
                    margin-top:14px;
                    height:6px;
                    background:rgba(30,41,59,0.6);
                    border-radius:3px;
                    overflow:hidden;
                    border: 1px solid rgba(59, 130, 246, 0.1);
                ">
                    <div style="
                        width:{occ}%;
                        height:100%;
                        background:linear-gradient(90deg, {occ_color} 0%, {occ_color}AA 100%);
                        border-radius:3px;
                        animation: expand-bar 1s ease;
                        box-shadow: 0 0 10px {occ_glow};
                    "></div>
                </div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#475569; margin-top:10px;">{stats['occupied_beds']}/{stats['total_beds']} beds occupied</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(15, 23, 42, 0.7) 100%);
                border: 1.5px solid rgba(239, 68, 68, 0.3);
                border-top: 3px solid #EF4444;
                border-radius: 16px;
                padding: 24px;
                position: relative;
                overflow: hidden;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                animation: slide-up 0.8s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 40px rgba(239, 68, 68, 0.25)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                <div style="
                    position: absolute;
                    top: -50%;
                    right: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(circle, rgba(239, 68, 68, 0.1) 0%, transparent 70%);
                    pointer-events: none;
                "></div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#64748B; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:14px; font-weight:600;">⚠️ Critical / ICU</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-size:3.2rem; font-weight:700; color:#F87171; line-height:1; text-shadow: 0 0 20px rgba(248, 113, 113, 0.3);">{stats['critical_patients']}</div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#475569; margin-top:10px;">Require attention</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(15, 23, 42, 0.7) 100%);
                border: 1.5px solid rgba(16, 185, 129, 0.3);
                border-top: 3px solid #10B981;
                border-radius: 16px;
                padding: 24px;
                position: relative;
                overflow: hidden;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                animation: slide-up 0.9s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 40px rgba(16, 185, 129, 0.25)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                <div style="
                    position: absolute;
                    top: -50%;
                    right: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
                    pointer-events: none;
                "></div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#64748B; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:14px; font-weight:600;">⚕ Doctors On Duty</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-size:3.2rem; font-weight:700; color:#34D399; line-height:1; text-shadow: 0 0 20px rgba(52, 211, 153, 0.3);">{stats['available_doctors']}</div>
                <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:#475569; margin-top:10px;">Available now</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── ROW 2: SECONDARY METRICS ──
        c5, c6, c7 = st.columns(3)

        with c5:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.6) 100%);
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius:12px;
                padding:20px;
                transition: all 0.3s ease;
                animation: slide-up 1s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 40px rgba(59, 130, 246, 0.25)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#64748B;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px; font-weight:600;">Free Beds</div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:2.8rem;font-weight:700;color:#60A5FA; text-shadow: 0 0 15px rgba(96, 165, 250, 0.3);">{stats['free_beds']}</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.64rem;color:#64748B;margin-top:8px;">Available now</div>
            </div>
            """, unsafe_allow_html=True)

        with c6:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.6) 100%);
                border: 1px solid rgba(100, 116, 139, 0.2);
                border-radius:12px;
                padding:20px;
                transition: all 0.3s ease;
                animation: slide-up 1.1s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 40px rgba(100, 116, 139, 0.15)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#64748B;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px; font-weight:600;">Occupied</div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:2.8rem;font-weight:700;color:#94A3B8;">{stats['occupied_beds']}</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.64rem;color:#64748B;margin-top:8px;">Currently in use</div>
            </div>
            """, unsafe_allow_html=True)

        with c7:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.6) 100%);
                border: 1px solid rgba(245, 158, 11, 0.2);
                border-radius:12px;
                padding:20px;
                transition: all 0.3s ease;
                animation: slide-up 1.2s ease;
            " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 30px rgba(245, 158, 11, 0.25)';" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#64748B;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px; font-weight:600;">Pending Appointments</div>
                <div style="display:flex;align-items:baseline;gap:8px;">
                    <div style="font-family:'Space Grotesk',sans-serif;font-size:2.8rem;font-weight:700;color:#FBBF24; text-shadow: 0 0 15px rgba(251, 191, 36, 0.3);">{stats['pending_appointments']}</div>
                </div>
                <div style="background:rgba(30,41,59,0.6);border-radius:3px;height:4px;margin-top:10px;overflow:hidden; border: 1px solid rgba(245, 158, 11, 0.1);">
                    <div style="background:linear-gradient(90deg, #FBBF24 0%, #F59E0B 100%);width:{min(stats['pending_appointments']*4,100)}%;height:100%;border-radius:3px; animation: expand-bar 1s ease;"></div>
                </div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.64rem;color:#64748B;margin-top:8px;">Scheduled</div>
            </div>
            """, unsafe_allow_html=True)

        # ── SPACER ──
        st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
        
        # ════════════════════════════════════════════
        # AI ASSISTANT SECTION (INLINE)
        # ════════════════════════════════════════════
        
        st.markdown(f"""
        <div style="
            margin-bottom: 2rem;
            padding: 24px;
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid rgba(139, 92, 246, 0.15);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            animation: slide-up 0.5s ease;
        ">
            <div style="display:flex; align-items:center; gap:16px; margin-bottom:10px;">
                <div style="
                    width: 12px;
                    height: 48px;
                    background: linear-gradient(180deg, #8B5CF6 0%, #7C3AED 100%);
                    border-radius: 6px;
                    box-shadow: 0 0 20px rgba(139, 92, 246, 0.4);
                "></div>
                <div>
                    <div style="display:flex; align-items:baseline; gap:14px;">
                        <span style="font-family:'Space Grotesk',sans-serif; font-size:2.2rem; font-weight:700; color:#F1F5F9; letter-spacing:0.02em; text-shadow: 0 2px 8px rgba(0,0,0,0.3);">AI Assistant</span>
                        <span style="
                            font-family:'IBM Plex Mono',monospace; 
                            font-size:0.68rem; 
                            color:#A78BFA; 
                            background: rgba(167, 139, 250, 0.15);
                            padding: 4px 12px;
                            border-radius: 6px;
                            letter-spacing: 0.08em;
                            border: 1px solid rgba(167, 139, 250, 0.3);
                            font-weight: 600;
                        ">GROQ · LLAMA 3.3 · MCP</span>
                    </div>
                    <span style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem; color:#64748B; letter-spacing:0.04em; margin-top:6px; display:block;">
                        💬 Query hospital data in natural language — real-time data, no hallucination
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat history
        chat_container = st.container()
        with chat_container:
            if not st.session_state.messages:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, rgba(15, 23, 42, 0.6) 0%, rgba(15, 23, 42, 0.4) 100%);
                    border:1.5px dashed rgba(59, 130, 246, 0.3);
                    border-radius:16px;
                    padding:48px;
                    text-align:center;
                    margin:32px 0;
                    backdrop-filter: blur(10px);
                ">
                    <div style="font-size:3.5rem;margin-bottom:20px;opacity:0.6; filter: drop-shadow(0 4px 12px rgba(59, 130, 246, 0.3));">🤖</div>
                    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.4rem;color:#E2E8F0;font-weight:700;margin-bottom:12px; text-shadow: 0 2px 6px rgba(0,0,0,0.3);">Ask me anything about the hospital</div>
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.78rem;color:#94A3B8;line-height:2; letter-spacing: 0.02em;">
                        Query about patients · doctors · beds · wards · appointments · statistics<br>
                        Type your question below to get started
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div style="
                            animation:slide-in 0.3s ease;
                            margin:16px 0;
                            display:flex;
                            gap:14px;
                            align-items:flex-start;
                        ">
                            <div style="
                                width:36px;height:36px;min-width:36px;
                                background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.2) 100%);
                                border:1.5px solid rgba(59, 130, 246, 0.4);
                                border-radius:10px;
                                display:flex;align-items:center;justify-content:center;
                                font-size:16px;margin-top:2px;
                                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
                            ">👤</div>
                            <div style="
                                background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.6) 100%);
                                border:1px solid rgba(59, 130, 246, 0.3);
                                border-left:3px solid #3B82F6;
                                border-radius:0 12px 12px 0;
                                padding:16px 20px;
                                flex:1;
                                font-family:'Outfit',sans-serif;
                                font-size:0.95rem;
                                color:#E2E8F0;
                                line-height:1.7;
                                box-shadow: 0 4px 16px rgba(59, 130, 246, 0.1);
                                backdrop-filter: blur(10px);
                            ">{msg['content']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        content = msg['content'].replace('\n', '<br>')
                        st.markdown(f"""
                        <div style="
                            animation:slide-in 0.3s ease;
                            margin:16px 0;
                            display:flex;
                            gap:14px;
                            align-items:flex-start;
                        ">
                            <div style="
                                width:36px;height:36px;min-width:36px;
                                background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%);
                                border:1.5px solid rgba(16, 185, 129, 0.4);
                                border-radius:10px;
                                display:flex;align-items:center;justify-content:center;
                                font-size:16px;margin-top:2px;
                                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
                            ">🤖</div>
                            <div style="
                                background: linear-gradient(135deg, rgba(15, 23, 42, 0.7) 0%, rgba(15, 23, 42, 0.5) 100%);
                                border:1px solid rgba(16, 185, 129, 0.2);
                                border-left:3px solid #10B981;
                                border-radius:0 12px 12px 0;
                                padding:16px 20px;
                                flex:1;
                                font-family:'Outfit',sans-serif;
                                font-size:0.95rem;
                                color:#CBD5E1;
                                line-height:1.7;
                                box-shadow: 0 4px 16px rgba(16, 185, 129, 0.08);
                                backdrop-filter: blur(10px);
                            ">{content}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        
        # Input area
        pending = st.session_state.pop("pending_query", None)
        
        st.markdown("""
        <div style="
            background:rgba(10, 20, 32, 0.8);
            border:1.5px solid rgba(59, 130, 246, 0.3);
            border-radius:12px;
            padding:20px;
            backdrop-filter: blur(10px);
        ">
        """, unsafe_allow_html=True)
        
        user_input = st.text_input(
            "Query",
            value=pending or "",
            placeholder="e.g.  Which wards have free beds?  ·  Show all critical patients  ·  List cardiologists available  ·  What is ICU occupancy?",
            key="chat_input",
            label_visibility="collapsed",
        )
        
        col_send, col_clear, col_space = st.columns([1, 1, 6])
        with col_send:
            send = st.button("↑  SEND", key="send_btn", use_container_width=True)
        with col_clear:
            if st.button("✕  CLEAR", key="clear_btn", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if (send or pending) and (user_input or pending):
            query = user_input or pending
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner(""):
                st.markdown("""
                <div style="
                    display:flex;align-items:center;gap:12px;
                    padding:14px 18px;
                    background:#060E0A;
                    border:1px solid #00E67620;
                    border-left:3px solid #00E676;
                    border-radius:0 8px 8px 0;
                    margin:12px 0;
                    font-family:'IBM Plex Mono',monospace;
                    font-size:0.72rem;color:#2A5A3A;
                ">
                    <div style="width:8px;height:8px;border-radius:50%;background:#00E676;animation:blink 0.8s infinite;"></div>
                    MEDCORE AI IS QUERYING HOSPITAL DATA VIA MCP...
                </div>
                """, unsafe_allow_html=True)
                history = st.session_state.messages[-6:-1] if len(st.session_state.messages) > 1 else []
                response = ask_sync(query, history)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        # Remove the old chat interface section that was here
        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            margin: 32px auto 0 auto;
            max-width: 900px;
            padding: 20px;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(15, 23, 42, 0.8) 100%);
            border: 1.5px solid rgba(59, 130, 246, 0.3);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 40px rgba(59, 130, 246, 0.2);
            animation: slide-up 0.8s ease;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid rgba(59, 130, 246, 0.15);
            ">
                <div style="
                    width: 8px;
                    height: 32px;
                    background: linear-gradient(180deg, #8B5CF6 0%, #7C3AED 100%);
                    border-radius: 4px;
                    box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
                "></div>
                <span style="
                    font-family: 'Space Grotesk', sans-serif;
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: #F1F5F9;
                    letter-spacing: 0.02em;
                ">Ask AI Assistant</span>
                <span style="
                    font-family: 'IBM Plex Mono', monospace;
                    font-size: 0.62rem;
                    color: #A78BFA;
                    background: rgba(167, 139, 250, 0.15);
                    padding: 3px 8px;
                    border-radius: 4px;
                    border: 1px solid rgba(167, 139, 250, 0.3);
                    letter-spacing: 0.08em;
                    font-weight: 600;
                ">POWERED BY GROQ</span>
            </div>
            <div style="
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.7rem;
                color: #64748B;
                margin-bottom: 12px;
                letter-spacing: 0.02em;
            ">Try these example queries:</div>
        </div>
        """, unsafe_allow_html=True)

        # Example query buttons in a centered container
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            example_queries = [
                ("🚨", "Show all critical patients", "Show me all critical patients"),
                ("🏥", "Which wards have free beds?", "Which wards have free beds?"),
                ("📊", "Hospital occupancy rate", "What is the hospital occupancy rate?"),
                ("⚕", "Available doctors now", "List all available doctors"),
            ]
            
            cols = st.columns(2)
            for idx, (icon, label, query) in enumerate(example_queries):
                with cols[idx % 2]:
                    if st.button(f"{icon} {label}", key=f"example_{idx}", use_container_width=True):
                        st.session_state.page = "AI Assistant"
                        st.session_state.pending_query = query
                        st.rerun()

            # Custom query input with form for Enter key support
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style="
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.68rem;
                color: #94A3B8;
                text-align: center;
                margin-bottom: 10px;
                letter-spacing: 0.04em;
            ">Or type your own question:</div>
            """, unsafe_allow_html=True)
            
            with st.form(key="dashboard_chat_form", clear_on_submit=True):
                custom_query = st.text_input(
                    "custom_query",
                    placeholder="e.g., How many patients are in the ICU? (Press Enter to ask)",
                    key="dashboard_custom_query_input",
                    label_visibility="collapsed"
                )
                
                col_left, col_center, col_right = st.columns([1.5, 1, 1.5])
                with col_center:
                    submitted = st.form_submit_button("🤖 Ask AI", use_container_width=True, type="primary")
                
                if submitted and custom_query and custom_query.strip():
                    st.session_state.page = "AI Assistant"
                    st.session_state.pending_query = custom_query.strip()
                    st.rerun()

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="background:#0F0608;border:1px solid #FF174433;border-left:3px solid #FF1744;border-radius:8px;padding:24px;text-align:center;">
            <div style="font-size:2rem;margin-bottom:12px;opacity:0.4;">⚠️</div>
            <div style="font-family:'JetBrains Mono',monospace;color:#FF174488;font-size:0.85rem;margin-bottom:8px;letter-spacing:0.05em;">DATABASE OFFLINE</div>
            <div style="font-family:'JetBrains Mono',monospace;color:#3A2030;font-size:0.72rem;margin-top:8px;">Run: <code style='background:#1A0810;padding:2px 8px;border-radius:3px;color:#FF174488;'>python db/setup_db.py</code></div>
        </div>
        """, unsafe_allow_html=True)