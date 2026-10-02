"""
Smart Parking Management System - Main Streamlit Application
Author: College Project
Description: Advanced parking management with real-time visualization and rush prediction
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import re
import hashlib
from streamlit_autorefresh import st_autorefresh
from parking_logic import ParkingManager
import streamlit.components.v1 as components

ADMIN_PASSWORD_HASH = hashlib.sha256("admin@123".encode()).hexdigest()


# Page configuration
st.set_page_config(
    page_title="Smart Parking System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔄 Auto refresh every 1 second (safe)
with st.sidebar:
    st_autorefresh(interval=1000, key="clock_refresh")



# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1f2933, #111827);
        padding: 1rem;
        border-radius: 0.75rem;
        border-left: 4px solid #667eea;
        color: #e5e7eb;          /* light readable text */
        font-size: 0.95rem;
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
    }

    .metric-card strong {
        color: #ffffff;
        font-size: 1.05rem;
    }

    }
    /* ===============================
    SUCCESS ALERT CARD (ENTRY + EXIT)
    =============================== */

    .success-box {
        background: linear-gradient(
            135deg,
            rgba(34, 197, 94, 0.35),
            rgba(22, 163, 74, 0.25)
        );
        border: 2px solid rgba(34, 197, 94, 0.75);
        border-left: 8px solid #22c55e;

        color: #eafff2;

        padding: 1.6rem 2rem;
        border-radius: 18px;

        box-shadow:
            0 10px 30px rgba(34, 197, 94, 0.45),
            inset 0 0 0 1px rgba(255,255,255,0.05);

        margin-top: 1.2rem;
        animation: successPop 0.35s ease-out;
    }

    /* BIG SUCCESS TITLE */
    .success-box h2,
    .success-box h3 {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: 0.6px;
        margin-bottom: 0.8rem;
        color: #dcfce7;
    }

    /* MESSAGE TEXT */
    .success-box p {
        font-size: 1.05rem;
        font-weight: 500;
        color: #f0fdf4;
        margin: 0.45rem 0;
    }

    /* TIME LABEL */
    .success-box strong {
        font-size: 1.05rem;
        color: #bbf7d0;
    }

    /* POP ANIMATION */
    @keyframes successPop {
        from {
            opacity: 0;
            transform: scale(0.97) translateY(8px);
        }
        to {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }

    .success-box {
        animation: fadeInUp 0.4s ease-out;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(8px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = ParkingManager()
    # Generate sample data for rush prediction on first run
    if st.session_state.get('first_run', True):
        st.session_state.manager.generate_sample_data()
        st.session_state.first_run = False

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

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



def render_header():
    """Render the application header"""
    st.markdown('<h1 class="main-header">🚗 Smart Parking Management System</h1>', 
                unsafe_allow_html=True)
    st.markdown("---")

def to_uppercase(key):
    if key in st.session_state and st.session_state[key]:
        st.session_state[key] = st.session_state[key].upper()

def is_valid_vehicle_number(vehicle_number):
    """
    Validates Indian vehicle registration number
    Format: GJ27BH8909, MH12AB1234, etc.
    """
    pattern = r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'
    return bool(re.match(pattern, vehicle_number))



def render_parking_grid(floor_number):
    """
    Render interactive parking grid visualization using Plotly
    """
    viz_data = st.session_state.manager.get_parking_visualization(floor_number)
    
    if not viz_data:
        st.warning("No data available for this floor")
        return
    
    grid = viz_data['grid']
    rows, cols = viz_data['dimensions']
    
    # Create figure
    fig = go.Figure()
    
    # Add slots to the grid
    for y in range(rows):
        for x in range(cols):
            if grid[y][x]:
                slot = grid[y][x]
                
                # Color based on occupancy
                color = '#ff6b6b' if slot['is_occupied'] else '#51cf66'
                
                # Add rectangle for slot
                fig.add_shape(
                    type="rect",
                    x0=x, y0=y,
                    x1=x + 0.9, y1=y + 0.9,
                    fillcolor=color,
                    line=dict(color="white", width=2),
                )
                
                # Add text label
                fig.add_annotation(
                    x=x + 0.45, y=y + 0.45,
                    text=f"{slot['slot_number']}",
                    showarrow=False,
                    font=dict(size=12, color="white", family="Arial Black"),
                )
    
    # Add stairs indicator
    fig.add_shape(
        type="rect",
        x0=-0.5, y0=-0.5,
        x1=0.3, y1=0.3,
        fillcolor='#ffd43b',
        line=dict(color="black", width=2),
    )
    
    fig.add_annotation(
        x=-0.1, y=-0.1,
        text="🚶<br>STAIRS",
        showarrow=False,
        font=dict(size=10, color="black"),
    )
    
    # Update layout
    fig.update_layout(
        title=f"{viz_data['floor_name']} - Parking Layout",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1, cols]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1, rows],
            scaleanchor="x",
            scaleratio=1
        ),
        plot_bgcolor='rgba(240, 242, 246, 0.8)',
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    st.plotly_chart(fig, use_container_width=True, key=f"parking_grid_floor_{floor_number}")
    
    # Legend
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟢 **Vacant Slot**")
    with col2:
        st.markdown("🔴 **Occupied Slot**")
    with col3:
        st.markdown("🟡 **Stairs Location**")


def render_dashboard():
    """Render the main dashboard with occupancy overview"""
    st.subheader("📊 Real-Time Parking Dashboard")
    
    summary = st.session_state.manager.get_occupancy_summary()
    
    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Slots",
            summary['total_slots'],
            delta=None
        )
    
    with col2:
        st.metric(
            "Occupied",
            summary['occupied_slots'],
            delta=f"{summary['overall_occupancy_rate']}%"
        )
    
    with col3:
        st.metric(
            "Vacant",
            summary['vacant_slots'],
            delta=None,
            delta_color="inverse"
        )
    
    with col4:
        occupancy = summary['overall_occupancy_rate']
        if occupancy >= 80:
            status = "🔴 High"
        elif occupancy >= 50:
            status = "🟡 Moderate"
        else:
            status = "🟢 Low"
        
        st.metric(
            "Rush Level",
            status,
            delta=None
        )
    
    st.markdown("---")
    
#pie chart for overall occupancy
    fig = go.Figure(data=[go.Pie(
        labels=['Vacant', 'Occupied'],
        values=[summary['vacant_slots'], summary['occupied_slots']],
        hole=0.6,
        marker_colors=['#51cf66', '#ff6b6b']
    )])

    

    # Floor-wise occupancy
    st.subheader("Floor-wise Availability")
    
    floor_cols = st.columns(len(summary['floors']))
    
    for idx, floor in enumerate(summary['floors']):
        with floor_cols[idx]:
            st.markdown(f"### {floor['floor_name']}")
            
            # Create donut chart for occupancy
            fig = go.Figure(data=[go.Pie(
                labels=['Vacant', 'Occupied'],
                values=[floor['vacant_slots'], floor['occupied_slots']],
                hole=0.6,
                marker_colors=['#51cf66', '#ff6b6b']
            )])
            
            fig.update_layout(
                showlegend=False,
                height=200,
                margin=dict(l=0, r=0, t=0, b=0),
                annotations=[dict(
                    text=f"{floor['vacant_slots']}<br>Vacant",
                    x=0.5, y=0.5,
                    font_size=16,
                    showarrow=False
                )]
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"floor_chart_{idx}")
            
            st.markdown(f"""
                <div class="metric-card">
                    <strong>{floor['vehicle_type']}</strong><br>
                    Total: {floor['total_slots']} slots<br>
                    Occupancy: {floor['occupancy_rate']}%
                </div>
            """, unsafe_allow_html=True)


def render_park_vehicle():
    """Render vehicle parking interface"""
    st.subheader("🚗 Park Your Vehicle")

    # 🔄 Loader (only inside Park Vehicle page)
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

    vehicle_number = st.session_state.get("park_vehicle_number", "").strip()

    # Live validation indicator
    if vehicle_number:
        if is_valid_vehicle_number(vehicle_number):
            st.success("✅ Vehicle number format is valid")
        else:
            st.error("❌ Invalid format (e.g., GJ27BH8904)")


    
    with col2:
        vehicle_type = st.selectbox(
            "Vehicle Type",
            ["2-Wheeler", "4-Wheeler"],
            key="park_vehicle_type"
        )
    
    # Show available slots before parking
    if vehicle_type:
        st.markdown("### Available Slots")
        available_slots = st.session_state.manager.get_all_available_slots(vehicle_type)
        
        if available_slots:
            st.info(f"✅ {len(available_slots)} slots available for {vehicle_type}")

    # Show table of available slots
    st.markdown(
    "<p style='text-align:center; color:#9aa4b2; font-size:16px;'>"
    "ⓘ Slot will be assigned automatically based on nearest distance"
    "</p>",
    unsafe_allow_html=True
)

    if st.button(
        "🅿️ Find & Park in Best Slot",
        use_container_width=True,
        disabled=st.session_state.parking_in_progress
    ):
        st.session_state.parking_in_progress = True
        st.session_state.parking_success = None

        if not vehicle_number:
            st.error("❌ Please enter vehicle number")
            st.session_state.parking_in_progress = False

        elif not is_valid_vehicle_number(vehicle_number):
            st.error("❌ Invalid vehicle number format (e.g., GJ27BH8909)")
            st.session_state.parking_in_progress = False

        else:
            success, message, slot_info = st.session_state.manager.park_vehicle(
                vehicle_number,
                vehicle_type
            )

            if success:
                st.session_state.parking_success = {
                    "message": message,
                    "slot_id": slot_info["slot_id"],
                    "vehicle": vehicle_number,
                    "timestamp": time.time()   # 👈 store current time
                }
            else:
                st.error(message)

            st.session_state.parking_in_progress = False

        # ✅ Persistent success card
    if st.session_state.parking_success:
        data = st.session_state.parking_success
        elapsed = time.time() - data["timestamp"]

        if elapsed < 20:   # 👈 show only for 20 seconds
            st.markdown(f"""
                <div class="success-box">
                    <h2>✅ Vehicle parked successfully</h2>
                    <h3>Assigned Slot: {data['slot_id']}</h3>
                    <p><strong>Vehicle:</strong> {data['vehicle']}</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # auto clear after 20 seconds
            st.session_state.parking_success = None



def render_exit_vehicle():
    st.subheader("🚪 Exit Vehicle")

    st.text_input(
        "Vehicle Registration Number",
        placeholder="e.g., GJ01AB1234",
        key="exit_vehicle_number",
        on_change=to_uppercase,
        args=("exit_vehicle_number",),
    )

    vehicle_number = st.session_state.get("exit_vehicle_number", "").strip()

    # 🔄 Show loader ONLY while exiting
    # 🛡️ Safety reset (important with auto-refresh)
    if st.session_state.get("exit_in_progress") and not st.session_state.get("exit_success"):
        st.info("🔄 Processing exit...")
    elif st.session_state.get("exit_in_progress"):
        st.session_state.exit_in_progress = False


    if st.button(
        "🚗 Exit Parking",
        use_container_width=True,
        disabled=st.session_state.get("exit_in_progress", False),
    ):
        if not vehicle_number:
            st.session_state.exit_error = "❌ Please enter vehicle number"
            return

        # Start exit
        st.session_state.exit_in_progress = True
        st.session_state.exit_error = None  # 🔥 clear old error

        success, data = st.session_state.manager.exit_vehicle(vehicle_number)

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


            # 🔥 clear input + errors
            st.session_state.exit_error = None
            st.session_state.exit_in_progress = False
            st.session_state.pop("exit_vehicle_number", None)

            st.rerun()

        else:
            st.session_state.exit_in_progress = False
            st.session_state.exit_error = data  # data contains error message
        
        # ❌ Show error ONLY if no success
    if st.session_state.exit_error and not st.session_state.exit_success:
        st.error(st.session_state.exit_error)




    # ✅ SUCCESS CARD (20 seconds)
    if st.session_state.get("exit_success"):
        data = st.session_state.exit_success
        elapsed = time.time() - data["timestamp"]

        if elapsed < 20:
            components.html(
                f"""
                <style>
                    .success-box {{
                        background: linear-gradient(
                            135deg,
                            rgba(34, 197, 94, 0.35),
                            rgba(22, 163, 74, 0.25)
                        );
                        border: 2px solid rgba(34, 197, 94, 0.75);
                        border-left: 8px solid #22c55e;
                        color: #eafff2;
                        padding: 1.6rem 2rem;
                        border-radius: 18px;
                        font-family: Arial, sans-serif;
                    }}

                    .success-box h2 {{
                        font-size: 26px;
                        margin-bottom: 12px;
                    }}

                    .success-box p {{
                        font-size: 16px;
                        margin: 6px 0;
                    }}

                    .success-box strong {{
                        color: #bbf7d0;
                    }}
                </style>

                <div class="success-box">
                    <h2>✅ Exit Successful</h2>

                    <p>
                        Slot <strong>{data['slot_id']}</strong> released<br>
                        Duration: <strong>{data['duration']} min</strong>
                    </p>

                    <p><strong>Entry Time:</strong><br>{data['entry_time']}</p>
                    <p><strong>Exit Time:</strong><br>{data['exit_time']}</p>
                </div>
                """,
                height=280
            )

        else:
            st.session_state.exit_success = None






def render_rush_prediction():
    """Render rush hour prediction analysis"""
    st.subheader("📈 Rush Hour Prediction")
    
    rush_data = st.session_state.manager.predict_rush_hours()
    
    # Current hour prediction
    if rush_data['current_hour_prediction']:
        current = rush_data['current_hour_prediction']
        st.markdown(f"""
            <div class="info-box">
                <h3>Current Hour ({current['time_label']})</h3>
                <h2>{current['rush_level']}</h2>
                <p><strong>Expected Occupancy:</strong> {current['avg_occupancy']}%</p>
                <p><em>Based on {current['data_points']} historical data points</em></p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show predictions
    tab1, tab2 = st.tabs([f"📅 Today ({rush_data['day_name']})", "📊 Overall Trends"])
    
    with tab1:
        if rush_data['today_predictions']:
            df = pd.DataFrame(rush_data['today_predictions'])
            
            # Create line chart
            fig = px.line(
                df,
                x='time_label',
                y='avg_occupancy',
                title=f"Expected Parking Occupancy - {rush_data['day_name']}",
                labels={
                    'time_label': 'Time of Day',
                    'avg_occupancy': 'Expected Occupancy (%)'
                },
                markers=True
            )
            
            # Add color zones
            fig.add_hrect(y0=80, y1=100, fillcolor="red", opacity=0.1, 
                         annotation_text="High Rush", annotation_position="right")
            fig.add_hrect(y0=50, y1=80, fillcolor="yellow", opacity=0.1,
                         annotation_text="Moderate Rush", annotation_position="right")
            fig.add_hrect(y0=0, y1=50, fillcolor="green", opacity=0.1,
                         annotation_text="Low Rush", annotation_position="right")
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, key="rush_prediction_today")
            
            # Show table
            st.markdown("### Hourly Breakdown")
            display_df = df[['time_label', 'avg_occupancy', 'rush_level']].copy()
            display_df.columns = ['Time Slot', 'Expected Occupancy (%)', 'Rush Level']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("Not enough historical data for today. Keep using the system to build predictions!")
    
    with tab2:
        if rush_data['overall_predictions']:
            df = pd.DataFrame(rush_data['overall_predictions'])
            
            fig = px.bar(
                df,
                x='time_label',
                y='avg_occupancy',
                title="Average Parking Occupancy by Hour (All Days)",
                labels={
                    'time_label': 'Time of Day',
                    'avg_occupancy': 'Average Occupancy (%)'
                },
                color='avg_occupancy',
                color_continuous_scale=['green', 'yellow', 'red']
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, key="rush_prediction_overall")
        else:
            st.info("Not enough historical data yet. Keep using the system to build predictions!")


def render_parking_layout():
    """Render all parking floor layouts"""
    st.subheader("🗺️ Parking Layout Visualization")
    
    floor_tabs = st.tabs([
        "Ground Floor (2W)",
        "Basement 1 (2W)",
        "Basement 2 (4W)"
    ])
    
    for idx, tab in enumerate(floor_tabs):
        with tab:
            render_parking_grid(idx)


def render_statistics():
    """Render parking statistics and history"""
    st.subheader("📊 Statistics & History")

    stats = st.session_state.manager.get_statistics()

    if not stats["recent_bookings"]:
        st.info("No parking history yet")
        return

    df = pd.DataFrame(stats["recent_bookings"])

    # -------------------------
    # FORMAT ENTRY & EXIT TIME
    # -------------------------
    def format_datetime(val):
        if pd.isna(val) or val is None:
            return "—"
        dt = pd.to_datetime(val)
        return f"{dt.strftime('%H:%M:%S')}\n{dt.strftime('%d-%m-%Y')}"

    df["entry_time"] = df["entry_time"].apply(format_datetime)
    df["exit_time"] = df["exit_time"].apply(format_datetime)

    # -------------------------
    # FORMAT DURATION (INT ONLY)
    # -------------------------
    def format_duration(val):
        if pd.isna(val):
            return "—"
        return int(round(val))

    df["duration_minutes"] = df["duration_minutes"].apply(format_duration)

    # Rename columns
    df = df[
        [
            "slot_id",
            "vehicle_number",
            "vehicle_type",
            "entry_time",
            "exit_time",
            "duration_minutes",
            "status",
        ]
    ]

    df.columns = [
        "Slot",
        "Vehicle",
        "Type",
        "Entry Time",
        "Exit Time",
        "Duration (min)",
        "Status",
    ]

    # -------------------------
    # STATUS COLORING
    # -------------------------
    def highlight_status(val):
        if val == "Active":
            return "background-color:#d4edda;color:#155724;font-weight:600;"
        else:
            return "background-color:#f8d7da;color:#721c24;font-weight:600;"

    styled_df = df.style.map(highlight_status, subset=["Status"])

    st.dataframe(styled_df, use_container_width=True, hide_index=True)




def main():
    """Main application entry point"""
    render_header()
    
    # Sidebar navigation
    st.sidebar.title("🚗 Navigation")
    
    menu_options = [
        "🏠 Dashboard",
        "🅿️ Park Vehicle",
        "🚪 Exit Vehicle",
        "🗺️ Parking Layout",
        "📈 Rush Prediction",
        "📊 Statistics"
    ]
    
    choice = st.sidebar.radio("Select Option", menu_options)
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
    
    # Admin options
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Admin Options")

    if not st.session_state.admin_authenticated:
        admin_pass = st.sidebar.text_input(
            "🔐 Admin Password",
            type="password"
        )

        if st.sidebar.button("Login as Admin"):
            if hashlib.sha256(admin_pass.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
                st.session_state.admin_authenticated = True
                st.sidebar.success("✅ Admin access granted")
                st.rerun()
            else:
                st.sidebar.error("❌ Incorrect password")
    else:
        st.sidebar.success("🟢 Admin Mode Enabled")

        if st.sidebar.button("↩️ Undo Last Parking", use_container_width=True):
            success, message = st.session_state.manager.undo_last_parking()
            if success:
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.error(message)

        if st.sidebar.button("🔄 Reset Database", use_container_width=True):
            if st.sidebar.checkbox("⚠️ Confirm Reset"):
                st.session_state.manager.db.reset_database()
                st.sidebar.success("Database reset successfully!")
                st.rerun()

        if st.sidebar.button("🔒 Logout Admin"):
            st.session_state.admin_authenticated = False
            st.sidebar.info("Logged out")
            st.rerun()

    
    # Current time display in sidebar

    now = datetime.now()

    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%d-%m-%Y")

    st.sidebar.markdown(
    f"""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2);
    padding:1px;
    border-radius:18px;
    text-align:center;
    margin-top:12px;
    box-shadow:0 6px 18px rgba(0,0,0,0.35);">

    <div style="
        font-size:22px;
        font-weight:650;
        color:white;
        letter-spacing:1px;
        display:flex;
        justify-content:center;
        align-items:center;
        gap:10px;">
        ⏰ {time_str}
    </div>

    <div style="
        font-size:22px;
        font-weight:650;
        color:white;
        letter-spacing:1px;
        margin-top:6px;
        display:flex;
        justify-content:center;
        align-items:center;
        gap:10px;">
        📅 {date_str}
    </div>


    </div>
    """,
    unsafe_allow_html=True
    )




    
    # Main content area
    if choice == "🏠 Dashboard":
        render_dashboard()
    
    elif choice == "🅿️ Park Vehicle":
        render_park_vehicle()
    
    elif choice == "🚪 Exit Vehicle":
        render_exit_vehicle()
    
    elif choice == "🗺️ Parking Layout":
        render_parking_layout()
    
    elif choice == "📈 Rush Prediction":
        render_rush_prediction()
    
    elif choice == "📊 Statistics":
        render_statistics()


if __name__ == "__main__":
    main()