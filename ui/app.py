import sys
from pathlib import Path

# Ensure project root is first in sys.path so the 'app' package is found correctly,
# and remove 'ui' from sys.path so 'ui/app.py' does not collide with the 'app' package
PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

while str(UI_DIR) in sys.path:
    sys.path.remove(str(UI_DIR))

if "app" in sys.modules and not hasattr(sys.modules["app"], "__path__"):
    del sys.modules["app"]

import json
from datetime import datetime, timezone
import folium
import requests
import streamlit as st
from streamlit_folium import st_folium

from app.tools import load_town_coordinates
from app.trek_data import (
    WIKIPEDIA_ATTRIBUTION,
    get_trek_cards_with_distance,
    load_trek_cards,
)

# -----------------------------
# Configuration
# -----------------------------

API_URL = "http://127.0.0.1:8000"
FEEDBACK_FILE = Path(__file__).resolve().parent.parent / "data" / "feedback.jsonl"

st.set_page_config(
    page_title="GadKille – Maharashtra Fort Explorer",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #d97706;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .trek-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease-in-out;
    }
    .trek-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .attribution-text {
        font-size: 0.8rem;
        color: #64748b;
        border-top: 1px dashed #cbd5e1;
        padding-top: 0.5rem;
        margin-top: 0.75rem;
    }
    .badge-near {
        background-color: #22c55e;
        color: white;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-mid {
        background-color: #eab308;
        color: #78350f;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-far {
        background-color: #f97316;
        color: white;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-extra {
        background-color: #8b5cf6;
        color: white;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Session State Initialization
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "Ask"

if "user_town" not in st.session_state:
    st.session_state.user_town = "Kopargaon"

if "radius_km" not in st.session_state:
    st.session_state.radius_km = 150

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = {}

if "prefill_question" not in st.session_state:
    st.session_state.prefill_question = None


# -----------------------------
# Helper Functions
# -----------------------------

def save_feedback_record(question, answer, mode, rating, comment=""):
    """Save feedback locally to feedback.jsonl and post to API if available."""
    payload = {
        "question": question,
        "answer": answer,
        "mode": mode,
        "rating": rating,
        "comment": comment,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # 1. Save directly to data/feedback.jsonl
    try:
        FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as err:
        st.warning(f"Failed to write local feedback: {err}")

    # 2. Also attempt to post to backend /feedback
    try:
        requests.post(f"{API_URL}/feedback", json=payload, timeout=3)
    except Exception:
        pass


def get_color_category(distance_km):
    """Categorize distance into pin color, label, and hex code."""
    if distance_km < 50:
        return "green", "< 50 km (Day Excursion)", "#22c55e", "badge-near"
    elif distance_km <= 100:
        return "orange", "50 - 100 km (Weekend Trek)", "#eab308", "badge-mid"
    elif distance_km <= 150:
        return "red", "100 - 150 km (Target Club Zone)", "#f97316", "badge-far"
    else:
        return "darkpurple", "> 150 km (Extended Trail)", "#8b5cf6", "badge-extra"


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1627894483216-2138af692e32?w=400&auto=format&fit=crop&q=60",
        caption="Sahyadri Western Ghats",
        use_container_width=True
    )

    st.markdown("### ⚙️ Settings & Controls")

    # Town selection
    town_coords = load_town_coordinates()
    town_names = [t.title() for t in town_coords.keys()]
    default_town_index = town_names.index("Kopargaon") if "Kopargaon" in town_names else 0

    selected_town = st.selectbox(
        "📍 Your Home Town",
        town_names,
        index=default_town_index,
        help="Target user: Engineering student from Kopargaon planning weekend club treks."
    )
    st.session_state.user_town = selected_town

    # Distance Radius slider
    radius = st.slider(
        "📏 Search Radius (km)",
        min_value=25,
        max_value=300,
        value=150,
        step=25,
        help="Default 150 km matches college trekking club weekend radius."
    )
    st.session_state.radius_km = radius

    # Mode Selector
    mode_selection = st.radio(
        "🤖 AI Assistant Mode",
        ["Ask (/ask - RAG)", "Agent (/agent - Autonomous)"],
        index=0 if st.session_state.mode == "Ask" else 1,
        help="/ask queries Wikipedia RAG directly. /agent reasons and invokes distance & RAG tools."
    )
    st.session_state.mode = "Ask" if "Ask" in mode_selection else "Agent"

    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback_log = {}
        st.session_state.prefill_question = None
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🎨 Distance Pin Legend")
    st.markdown("🟢 **< 50 km**: Day Excursion")
    st.markdown("🟡 **50 – 100 km**: Easy Weekend Trek")
    st.markdown("🔴 **100 – 150 km**: College Club Target")
    st.markdown("🟣 **> 150 km**: Extended Trail")
    st.markdown("🔵 **Home Pin**: User Base Location")

    st.markdown("---")
    st.caption("🏰 **GadKille** | Maharashtra Fort Explorer Checkpoint 2")


# -----------------------------
# Main Header
# -----------------------------

st.markdown('<div class="main-header">🏰 GadKille – Maharashtra Fort Explorer</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header">Personalized trek discovery and RAG AI assistant for <b>{selected_town}</b> trekking enthusiasts</div>',
    unsafe_allow_html=True
)

# -----------------------------
# Main Navigation Tabs
# -----------------------------

tab_map, tab_cards, tab_chat, tab_stats = st.tabs([
    "🗺️ Interactive Distance Map",
    "📋 Trek Cards",
    "💬 AI Trek Assistant",
    "📊 Feedback & Activity"
])


# ==========================================
# TAB 1: INTERACTIVE DISTANCE MAP
# ==========================================

with tab_map:
    st.markdown(f"### 📍 Forts within {radius} km of {selected_town}")
    st.caption("Pins are color-coded based on distance from your chosen base location.")

    forts_in_radius = get_trek_cards_with_distance(selected_town, radius_km=radius)
    all_forts_dist = get_trek_cards_with_distance(selected_town, radius_km=None)

    # Metrics row
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Forts within Radius", f"{len(forts_in_radius)} forts")
    with col_m2:
        if forts_in_radius:
            nearest = forts_in_radius[0]
            st.metric("Nearest Fort", f"{nearest['fort_name']}", f"{nearest['distance_km']} km")
        else:
            st.metric("Nearest Fort", "None", "-")
    with col_m3:
        if forts_in_radius:
            highest = max(forts_in_radius, key=lambda x: x.get("height_ft") or 0)
            st.metric("Highest Fort", f"{highest['fort_name']}", f"{highest.get('height_ft', 'N/A')} ft")
        else:
            st.metric("Highest Fort", "None", "-")
    with col_m4:
        st.metric("Base Location", f"{selected_town}")

    # Build Map
    town_info = town_coords.get(selected_town.lower(), town_coords["kopargaon"])
    map_center = [town_info["latitude"], town_info["longitude"]]

    fort_map = folium.Map(
        location=map_center,
        zoom_start=8,
        tiles="CartoDB positron"
    )

    # User's Town Marker
    folium.Marker(
        location=map_center,
        popup=folium.Popup(f"<b>Home: {selected_town}</b><br>Reference Location", max_width=250),
        tooltip=f"📍 Base: {selected_town}",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(fort_map)

    # Distance Radius Circles
    folium.Circle(
        radius=50000,
        location=map_center,
        color="#22c55e",
        fill=False,
        weight=1.5,
        dash_array="5, 5",
        tooltip="50 km radius"
    ).add_to(fort_map)

    folium.Circle(
        radius=100000,
        location=map_center,
        color="#eab308",
        fill=False,
        weight=1.5,
        dash_array="5, 5",
        tooltip="100 km radius"
    ).add_to(fort_map)

    folium.Circle(
        radius=150000,
        location=map_center,
        color="#f97316",
        fill=False,
        weight=2,
        dash_array="5, 5",
        tooltip="150 km target radius"
    ).add_to(fort_map)

    # Add Fort Pins
    display_forts = forts_in_radius if forts_in_radius else all_forts_dist
    for fort in display_forts:
        f_lat = fort.get("latitude")
        f_lon = fort.get("longitude")
        if f_lat is None or f_lon is None:
            continue

        color_name, cat_label, hex_code, _ = get_color_category(fort["distance_km"])

        popup_html = f"""
        <div style="font-family: sans-serif; width: 220px;">
            <h4 style="margin: 0 0 5px 0; color: #1e293b;">{fort['fort_name']}</h4>
            <p style="margin: 0; font-size: 13px; color: {hex_code}; font-weight: bold;">
                📍 {fort['distance_km']} km from {selected_town}
            </p>
            <p style="margin: 4px 0; font-size: 12px; color: #475569;">
                <b>District:</b> {fort.get('district', 'N/A')}<br>
                <b>Height:</b> {fort.get('height', 'N/A')}<br>
                <b>Base:</b> {fort.get('base_village', 'N/A')}<br>
                <b>Climb Time:</b> {fort.get('time_to_climb', 'N/A')}
            </p>
            <a href="{fort.get('source_url', '#')}" target="_blank" style="font-size: 11px; color: #2563eb;">
                View on Wikipedia ↗
            </a>
        </div>
        """

        folium.Marker(
            location=[f_lat, f_lon],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{fort['fort_name']} ({fort['distance_km']} km)",
            icon=folium.Icon(color=color_name, icon="mountain", prefix="fa")
        ).add_to(fort_map)

    # Render folium map in Streamlit
    st_folium(fort_map, width=None, height=520, use_container_width=True)


# ==========================================
# TAB 2: TREK CARDS (SIGNATURE FEATURE)
# ==========================================

with tab_cards:
    st.markdown(f"### 📋 Fort Trek Cards (Relative to {selected_town})")
    st.caption("Each card details height, base village, climb time, water availability, night stay, and Wikipedia attribution.")

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        search_query = st.text_input("🔍 Filter forts by name or district", placeholder="e.g. Harishchandragad, Nashik, Pune...")
    with col_f2:
        max_dist_filter = st.selectbox(
            "Filter distance limit",
            [f"Within {radius} km", "All Maharashtra Forts"],
            index=0
        )

    cards_to_show = forts_in_radius if max_dist_filter.startswith("Within") else all_forts_dist

    if search_query:
        sq = search_query.strip().lower()
        cards_to_show = [
            c for c in cards_to_show
            if sq in c["fort_name"].lower() or sq in str(c.get("district", "")).lower()
        ]

    st.write(f"Showing **{len(cards_to_show)}** trek cards:")

    # Render Trek Cards in 2 columns
    col_card1, col_card2 = st.columns(2)

    for idx, fort in enumerate(cards_to_show):
        target_col = col_card1 if idx % 2 == 0 else col_card2
        color_name, cat_label, hex_code, badge_class = get_color_category(fort["distance_km"])

        with target_col:
            st.markdown(f"""
            <div class="trek-card">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <h3 style="margin: 0; color: #0f172a;">🏰 {fort['fort_name']}</h3>
                    <span class="{badge_class}">{fort['distance_km']} km</span>
                </div>
                <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 0.8rem;">
                    📍 {fort.get('district', 'Maharashtra')} District &bull; {cat_label}
                </div>
                <div style="font-size: 0.92rem; line-height: 1.6; color: #334155;">
                    <div>🏔️ <b>Height:</b> {fort.get('height', 'Information not documented')}</div>
                    <div>🏡 <b>Base Village:</b> {fort.get('base_village', 'Contact local guides')}</div>
                    <div>⏱️ <b>Time to Climb:</b> {fort.get('time_to_climb', '1.5 - 2.5 hours')}</div>
                    <div>💧 <b>Water:</b> {fort.get('water', 'Cisterns on top; carry potable drinking water')}</div>
                    <div>⛺ <b>Night Stay:</b> {fort.get('night_stay', 'Base village homestay recommended')}</div>
                    {f"<div>✨ <b>Highlights:</b> {fort.get('highlights')}</div>" if fort.get('highlights') else ""}
                </div>
                <div class="attribution-text">
                    📜 <i>{WIKIPEDIA_ATTRIBUTION}</i><br>
                    <a href="{fort.get('source_url', 'https://en.wikipedia.org/wiki/List_of_forts_in_Maharashtra')}" target="_blank" style="color: #2563eb; text-decoration: underline;">
                        Source: Wikipedia Article &rarr;
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"💬 Ask AI about {fort['fort_name']}", key=f"ask_btn_{idx}"):
                st.session_state.prefill_question = f"Tell me about {fort['fort_name']} trek route, height, and history from {selected_town}."
                st.rerun()


# ==========================================
# TAB 3: CHAT ASSISTANT
# ==========================================

with tab_chat:
    st.markdown("### 💬 AI Fort Assistant")
    st.caption(f"Currently operating in **{st.session_state.mode}** mode via FastAPI backend ({API_URL}).")

    # Quick prompt chips
    st.markdown("**Quick Prompts:**")
    prompt_cols = st.columns(4)
    if prompt_cols[0].button("📍 Forts near Kopargaon"):
        st.session_state.prefill_question = f"Which forts are located within 100 km of {selected_town}?"
        st.rerun()
    if prompt_cols[1].button("🧗 Trek to Harihar Fort"):
        st.session_state.prefill_question = "How difficult is the trek to Harihar Fort and what are the rock-cut steps like?"
        st.rerun()
    if prompt_cols[2].button("⛺ Harishchandragad Stay"):
        st.session_state.prefill_question = "Can I stay overnight at Harishchandragad and where is potable water available?"
        st.rerun()
    if prompt_cols[3].button("💧 Ratangad Water Sources"):
        st.session_state.prefill_question = "What is the base village of Ratangad and is drinking water available at the top?"
        st.rerun()

    st.markdown("---")

    # Display Chat History
    for msg_idx, message in enumerate(st.session_state.messages):
        role = message["role"]
        content = message["content"]

        with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🏰"):
            st.markdown(content)

            if role == "assistant":
                # Confidence badge
                confidence = message.get("confidence")
                if confidence:
                    badge_color = "green" if confidence.lower() == "high" else "orange" if confidence.lower() == "medium" else "gray"
                    st.caption(f"Confidence: :{badge_color}[{confidence.capitalize()}]")

                # Follow-up suggestion
                follow_up = message.get("follow_up")
                if follow_up:
                    st.info(f"💡 **Suggested Follow-up:** {follow_up}")

                # Citations / Sources
                sources = message.get("sources", [])
                if sources:
                    with st.expander("📚 Wikipedia Citations & Sources"):
                        for src in sources:
                            st.markdown(f"- [{src}]({src})")

                # Thumbs Up / Down Feedback Widget
                feedback_key = f"feedback_{msg_idx}"
                current_feedback = st.session_state.feedback_log.get(msg_idx)

                col_fback1, col_fback2, col_fback3 = st.columns([1, 1, 6])
                with col_fback1:
                    thumbs_up = st.button("👍 Useful", key=f"up_{msg_idx}", disabled=current_feedback is not None)
                with col_fback2:
                    thumbs_down = st.button("👎 Poor", key=f"down_{msg_idx}", disabled=current_feedback is not None)

                if thumbs_up:
                    st.session_state.feedback_log[msg_idx] = "thumbs_up"
                    save_feedback_record(
                        question=st.session_state.messages[msg_idx - 1]["content"] if msg_idx > 0 else "N/A",
                        answer=content,
                        mode=st.session_state.mode,
                        rating="thumbs_up"
                    )
                    st.rerun()

                if thumbs_down:
                    st.session_state.feedback_log[msg_idx] = "thumbs_down"
                    save_feedback_record(
                        question=st.session_state.messages[msg_idx - 1]["content"] if msg_idx > 0 else "N/A",
                        answer=content,
                        mode=st.session_state.mode,
                        rating="thumbs_down"
                    )
                    st.rerun()

                if current_feedback == "thumbs_up":
                    st.success("✅ Thank you! You marked this answer as helpful.")
                elif current_feedback == "thumbs_down":
                    st.error("⚠️ Thank you for the feedback. We will improve this answer.")

    # Check for prefilled question
    initial_val = ""
    if st.session_state.prefill_question:
        initial_val = st.session_state.prefill_question
        st.session_state.prefill_question = None

    # Chat Input
    user_query = st.chat_input("Ask anything about Maharashtra forts, base villages, or treks...", key="chat_input")
    if not user_query and initial_val:
        user_query = initial_val

    if user_query:
        # Append User Message
        st.session_state.messages.append({
            "role": "user",
            "content": user_query
        })

        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_query)

        endpoint = "/ask" if st.session_state.mode == "Ask" else "/agent"
        payload = {"question": user_query}

        with st.chat_message("assistant", avatar="🏰"):
            with st.spinner("GadKille AI is retrieving insights..."):
                try:
                    response = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=60)
                    response.raise_for_status()
                    data = response.json()

                    if st.session_state.mode == "Ask":
                        answer = data.get("answer", "No answer received.")
                        sources = data.get("sources", [])
                        confidence = data.get("confidence", "medium")
                        follow_up = data.get("follow_up", "")

                        st.markdown(answer)

                        if confidence:
                            badge_color = "green" if confidence.lower() == "high" else "orange" if confidence.lower() == "medium" else "gray"
                            st.caption(f"Confidence: :{badge_color}[{confidence.capitalize()}]")

                        if follow_up:
                            st.info(f"💡 **Suggested Follow-up:** {follow_up}")

                        if sources:
                            with st.expander("📚 Wikipedia Citations & Sources"):
                                for src in sources:
                                    st.markdown(f"- [{src}]({src})")

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "confidence": confidence,
                            "follow_up": follow_up,
                            "sources": sources
                        })

                    else:  # Agent Mode
                        action = data.get("action", "processed")
                        results = data.get("results", {})

                        st.markdown(f"**Agent Action:** `{action}`")

                        formatted_parts = []
                        sources = []

                        if "rag_search" in results:
                            rag_data = results["rag_search"]
                            ans = rag_data.get("answer", "")
                            st.markdown(f"### Fort Information\n{ans}")
                            formatted_parts.append(ans)
                            sources.extend(rag_data.get("sources", []))

                        if "forts_within_km" in results:
                            fort_list = results["forts_within_km"]
                            st.markdown(f"### 📍 Found {len(fort_list)} Forts Near You")

                            if fort_list:
                                table_data = [
                                    {
                                        "Fort": f["fort_name"],
                                        "District": f.get("district", ""),
                                        "Distance": f"{f.get('distance_km')} km",
                                        "Height": f"{f.get('height_ft', 'N/A')} ft" if f.get("height_ft") else "N/A"
                                    }
                                    for f in fort_list[:15]
                                ]
                                st.dataframe(table_data, use_container_width=True)
                                formatted_parts.append(f"Retrieved {len(fort_list)} forts matching your distance radius.")

                        if not results and "message" in data:
                            msg = data["message"]
                            st.markdown(msg)
                            formatted_parts.append(msg)

                        full_content = "\n\n".join(formatted_parts) if formatted_parts else json.dumps(data, indent=2)

                        if sources:
                            with st.expander("📚 Wikipedia Citations & Sources"):
                                for src in sources:
                                    st.markdown(f"- [{src}]({src})")

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": full_content,
                            "confidence": "high",
                            "follow_up": "Would you like directions or trek details for any of these forts?",
                            "sources": sources
                        })

                    st.rerun()

                except requests.exceptions.RequestException as err:
                    err_msg = f"Backend connection failed ({endpoint}): {err}. Ensure the FastAPI server is running."
                    st.error(err_msg)


# ==========================================
# TAB 4: FEEDBACK & STATS
# ==========================================

with tab_stats:
    st.markdown("### 📊 Feedback Activity & Metrics")
    st.caption("All user ratings (thumbs up / thumbs down) are saved to persistent storage.")

    # Load feedback file
    feedback_entries = []
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        feedback_entries.append(json.loads(line))
                    except Exception:
                        pass

    total_fb = len(feedback_entries)
    up_count = sum(1 for f in feedback_entries if f.get("rating") == "thumbs_up")
    down_count = sum(1 for f in feedback_entries if f.get("rating") == "thumbs_down")
    sat_rate = f"{(up_count / total_fb * 100):.1f}%" if total_fb > 0 else "N/A"

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Total Ratings", total_fb)
    with col_s2:
        st.metric("👍 Thumbs Up", up_count)
    with col_s3:
        st.metric("👎 Thumbs Down", down_count)
    with col_s4:
        st.metric("Satisfaction Rate", sat_rate)

    st.markdown("---")
    st.markdown("#### Recent Ratings Log")
    if feedback_entries:
        st.dataframe(
            [
                {
                    "Timestamp": entry.get("timestamp", "")[:19].replace("T", " "),
                    "Rating": "👍 Helpful" if entry.get("rating") == "thumbs_up" else "👎 Poor",
                    "Mode": entry.get("mode", ""),
                    "Question": entry.get("question", "")[:60] + "...",
                    "Answer Preview": entry.get("answer", "")[:80] + "..."
                }
                for entry in reversed(feedback_entries[-20:])
            ],
            use_container_width=True
        )
    else:
        st.info("No feedback records logged yet. Vote 👍 or 👎 in the AI Trek Assistant tab!")
