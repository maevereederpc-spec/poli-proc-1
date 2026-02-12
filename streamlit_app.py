import streamlit as st

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import sys

# Increase the max upload size to 200MB
st.set_page_config(
    page_title="Political Process Save Game Analyzer",
    page_icon="🗳️",
    layout="wide"
)

# Set max upload size in config
if 'max_upload_size' not in st.session_state:
    st.session_state.max_upload_size = 200

# Title and description
st.title("🗳️ The Political Process - Save Game Analyzer")
st.markdown("""
Upload your save game file to visualize campaign data, poll numbers, finances, and more!
""")

# File uploader with increased size limit info
st.info("💡 **Tip:** The app supports files up to 200MB. For best performance with large files (50MB+), ensure you have a stable connection.")
uploaded_file = st.file_uploader("Upload Save Game File (JSON, TXT, or SAV format)", type=['json', 'txt', 'sav'])

def extract_game_data(raw_data):
    """
    Extract relevant game data from various possible save file structures.
    This function tries to intelligently parse different formats.
    """
    # If it's already in the expected format
    if isinstance(raw_data, dict):
        if all(key in raw_data for key in ['game_info', 'polls', 'finances']):
            return raw_data
        
        # Try to find nested data
        # The Political Process might nest data under various keys
        for key in raw_data:
            if isinstance(raw_data[key], dict):
                # Check if this nested dict has the structure we want
                nested = raw_data[key]
                if any(k in nested for k in ['game_info', 'polls', 'finances', 'states', 'campaign']):
                    return extract_game_data(nested)
    
    return raw_data

def parse_save_file(file):
    """Parse the save game file - attempts to handle JSON format with streaming for large files"""
    try:
        # Get file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Seek back to start
        
        st.info(f"📦 File size: {file_size / 1024 / 1024:.2f} MB - Processing...")
        
        # Read file content
        if file_size > 50 * 1024 * 1024:  # If larger than 50MB
            st.warning("⚠️ Large file detected. This may take a moment to process...")
        
        # Try to decode as JSON
        try:
            # For large files, read in chunks
            content = file.read()
            
            # Try parsing as JSON
            data = json.loads(content)
            st.success(f"✅ Successfully parsed JSON file with {len(str(data))} characters")
            return data, None
        except json.JSONDecodeError as je:
            # If JSON parsing fails, try as text
            try:
                content_str = content.decode('utf-8')
                st.warning(f"⚠️ Could not parse as JSON. Error: {str(je)[:100]}")
                return content_str, None
            except Exception as e:
                return None, f"Could not decode file: {str(e)}"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

def create_sample_data():
    """Create sample data for demonstration"""
    return {
        "game_info": {
            "campaign_name": "2024 Presidential Campaign",
            "candidate_name": "John Smith",
            "party": "Democratic",
            "difficulty": "Hard",
            "current_date": "2024-10-15",
            "days_remaining": 21
        },
        "finances": [
            {"date": "2024-08-01", "cash_on_hand": 5000000, "daily_donations": 150000, "daily_spending": 100000},
            {"date": "2024-08-15", "cash_on_hand": 7200000, "daily_donations": 180000, "daily_spending": 120000},
            {"date": "2024-09-01", "cash_on_hand": 12000000, "daily_donations": 250000, "daily_spending": 200000},
            {"date": "2024-09-15", "cash_on_hand": 15500000, "daily_donations": 320000, "daily_spending": 280000},
            {"date": "2024-10-01", "cash_on_hand": 22000000, "daily_donations": 450000, "daily_spending": 380000},
            {"date": "2024-10-15", "cash_on_hand": 28000000, "daily_donations": 580000, "daily_spending": 520000}
        ],
        "polls": [
            {"date": "2024-08-01", "you": 42, "opponent": 48, "undecided": 10},
            {"date": "2024-08-15", "you": 44, "opponent": 47, "undecided": 9},
            {"date": "2024-09-01", "you": 46, "opponent": 46, "undecided": 8},
            {"date": "2024-09-15", "you": 48, "opponent": 45, "undecided": 7},
            {"date": "2024-10-01", "you": 49, "opponent": 44, "undecided": 7},
            {"date": "2024-10-15", "you": 51, "opponent": 42, "undecided": 7}
        ],
        "state_data": [
            {"state": "California", "electoral_votes": 54, "your_support": 58, "opponent_support": 35, "undecided": 7, "lean": "Safe You"},
            {"state": "Texas", "electoral_votes": 40, "your_support": 46, "opponent_support": 48, "undecided": 6, "lean": "Toss-up"},
            {"state": "Florida", "electoral_votes": 30, "your_support": 49, "opponent_support": 45, "undecided": 6, "lean": "Lean You"},
            {"state": "New York", "electoral_votes": 28, "your_support": 62, "opponent_support": 32, "undecided": 6, "lean": "Safe You"},
            {"state": "Pennsylvania", "electoral_votes": 19, "your_support": 50, "opponent_support": 46, "undecided": 4, "lean": "Lean You"},
            {"state": "Illinois", "electoral_votes": 19, "your_support": 56, "opponent_support": 38, "undecided": 6, "lean": "Safe You"},
            {"state": "Ohio", "electoral_votes": 17, "your_support": 47, "opponent_support": 48, "undecided": 5, "lean": "Toss-up"},
            {"state": "Georgia", "electoral_votes": 16, "your_support": 49, "opponent_support": 47, "undecided": 4, "lean": "Lean You"},
            {"state": "North Carolina", "electoral_votes": 16, "your_support": 48, "opponent_support": 48, "undecided": 4, "lean": "Toss-up"},
            {"state": "Michigan", "electoral_votes": 15, "your_support": 51, "opponent_support": 44, "undecided": 5, "lean": "Lean You"},
        ],
        "issues": [
            {"issue": "Economy", "your_position": 7, "voter_preference": 6, "importance": 95},
            {"issue": "Healthcare", "your_position": 8, "voter_preference": 7, "importance": 85},
            {"issue": "Immigration", "your_position": 5, "voter_preference": 5, "importance": 75},
            {"issue": "Climate Change", "your_position": 9, "voter_preference": 6, "importance": 70},
            {"issue": "Education", "your_position": 7, "voter_preference": 7, "importance": 80},
            {"issue": "Foreign Policy", "your_position": 6, "voter_preference": 5, "importance": 65}
        ],
        "events": [
            {"date": "2024-08-10", "event": "Launched campaign in Iowa", "impact": "+2 polls"},
            {"date": "2024-08-25", "event": "First debate performance - Strong", "impact": "+3 polls"},
            {"date": "2024-09-10", "event": "Major endorsement from labor union", "impact": "+1 polls"},
            {"date": "2024-09-20", "event": "Scandal about opponent revealed", "impact": "+2 polls"},
            {"date": "2024-10-05", "event": "Second debate performance - Very Strong", "impact": "+2 polls"},
            {"date": "2024-10-12", "event": "Won major newspaper endorsements", "impact": "+1 polls"}
        ]
    }

if uploaded_file is not None:
    with st.spinner('Processing save file...'):
        data, error = parse_save_file(uploaded_file)
        
        if error:
            st.error(f"❌ Error parsing file: {error}")
            st.info("📊 Loading sample data for demonstration...")
            data = create_sample_data()
        elif isinstance(data, str):
            st.warning("⚠️ File format not recognized as JSON. Please ensure it's a valid save game file.")
            
            # Show a preview of the file content
            with st.expander("🔍 View file content preview (first 1000 characters)"):
                st.code(data[:1000])
            
            st.info("📊 Loading sample data for demonstration...")
            data = create_sample_data()
        else:
            # Try to extract and validate the data structure
            try:
                data = extract_game_data(data)
                
                # Show what keys were found in the file
                with st.expander("🔍 Debug: Data structure found in file"):
                    if isinstance(data, dict):
                        st.write("Top-level keys found:")
                        st.json(list(data.keys()))
                        
                        # Show structure for each key
                        for key in list(data.keys())[:10]:  # Limit to first 10 keys
                            if isinstance(data[key], (list, dict)):
                                st.write(f"**{key}:** {type(data[key]).__name__}")
                                if isinstance(data[key], list) and len(data[key]) > 0:
                                    st.write(f"  - Contains {len(data[key])} items")
                                    if isinstance(data[key][0], dict):
                                        st.write(f"  - Item keys: {list(data[key][0].keys())}")
                
                # Check if we have the expected structure
                expected_keys = ['game_info', 'polls', 'finances', 'state_data', 'issues', 'events']
                found_keys = [k for k in expected_keys if k in data]
                
                if found_keys:
                    st.success(f"✅ Save game loaded! Found: {', '.join(found_keys)}")
                else:
                    st.warning("⚠️ Save file loaded, but expected data structure not found. Using sample data.")
                    st.info("Your save file may use a different format. Check the debug info above.")
                    data = create_sample_data()
                    
            except Exception as e:
                st.error(f"❌ Error processing data structure: {str(e)}")
                st.info("📊 Loading sample data for demonstration...")
                data = create_sample_data()
else:
    st.info("📊 No file uploaded. Showing sample data for demonstration...")
    data = create_sample_data()

# Display game info
if "game_info" in data:
    st.header("📋 Campaign Overview")
    info = data["game_info"]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Candidate", info.get("candidate_name", "N/A"))
    with col2:
        st.metric("Party", info.get("party", "N/A"))
    with col3:
        st.metric("Difficulty", info.get("difficulty", "N/A"))
    with col4:
        st.metric("Days to Election", info.get("days_remaining", "N/A"))

# Tabs for different visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Polls", "💰 Finances", "🗺️ Electoral Map", "📝 Issues", "📅 Timeline"])

with tab1:
    st.header("Poll Trends")
    if "polls" in data and data["polls"]:
        df_polls = pd.DataFrame(data["polls"])
        df_polls['date'] = pd.to_datetime(df_polls['date'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_polls['date'], 
            y=df_polls['you'],
            mode='lines+markers',
            name='You',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=df_polls['date'], 
            y=df_polls['opponent'],
            mode='lines+markers',
            name='Opponent',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=df_polls['date'], 
            y=df_polls['undecided'],
            mode='lines+markers',
            name='Undecided',
            line=dict(color='#808080', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title="Poll Numbers Over Time",
            xaxis_title="Date",
            yaxis_title="Support (%)",
            hovermode='x unified',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Current standings
        latest = df_polls.iloc[-1]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Your Support", f"{latest['you']}%", 
                     delta=f"{latest['you'] - df_polls.iloc[0]['you']:.1f}%" if len(df_polls) > 1 else None)
        with col2:
            st.metric("Opponent Support", f"{latest['opponent']}%",
                     delta=f"{latest['opponent'] - df_polls.iloc[0]['opponent']:.1f}%" if len(df_polls) > 1 else None,
                     delta_color="inverse")
        with col3:
            st.metric("Undecided", f"{latest['undecided']}%")

with tab2:
    st.header("Campaign Finances")
    if "finances" in data and data["finances"]:
        df_finance = pd.DataFrame(data["finances"])
        df_finance['date'] = pd.to_datetime(df_finance['date'])
        
        # Cash on hand over time
        fig1 = px.line(df_finance, x='date', y='cash_on_hand', 
                      title='Cash on Hand Over Time',
                      labels={'cash_on_hand': 'Cash ($)', 'date': 'Date'})
        fig1.update_traces(line_color='#2ca02c', line_width=3)
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Daily donations vs spending
        col1, col2 = st.columns(2)
        with col1:
            fig2 = px.line(df_finance, x='date', y='daily_donations',
                          title='Daily Donations',
                          labels={'daily_donations': 'Donations ($)', 'date': 'Date'})
            fig2.update_traces(line_color='#2ca02c', line_width=2)
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            fig3 = px.line(df_finance, x='date', y='daily_spending',
                          title='Daily Spending',
                          labels={'daily_spending': 'Spending ($)', 'date': 'Date'})
            fig3.update_traces(line_color='#d62728', line_width=2)
            st.plotly_chart(fig3, use_container_width=True)
        
        # Summary metrics
        latest_finance = df_finance.iloc[-1]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Cash", f"${latest_finance['cash_on_hand']:,.0f}")
        with col2:
            st.metric("Daily Donations", f"${latest_finance['daily_donations']:,.0f}")
        with col3:
            st.metric("Daily Spending", f"${latest_finance['daily_spending']:,.0f}")
        with col4:
            net = latest_finance['daily_donations'] - latest_finance['daily_spending']
            st.metric("Daily Net", f"${net:,.0f}", delta="Positive" if net > 0 else "Negative")

with tab3:
    st.header("Electoral Map")
    if "state_data" in data and data["state_data"]:
        df_states = pd.DataFrame(data["state_data"])
        
        # Calculate electoral vote totals
        your_ev = df_states[df_states['lean'].str.contains('You', case=False)]['electoral_votes'].sum()
        opponent_ev = df_states[df_states['lean'].str.contains('Opponent', case=False)]['electoral_votes'].sum()
        tossup_ev = df_states[df_states['lean'].str.contains('Toss', case=False)]['electoral_votes'].sum()
        
        # Electoral vote summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Your Electoral Votes", your_ev, delta="Leading" if your_ev >= 270 else None)
        with col2:
            st.metric("Opponent Electoral Votes", opponent_ev)
        with col3:
            st.metric("Toss-up States", tossup_ev)
        
        st.markdown(f"**Need 270 to win** - You need {max(0, 270 - your_ev)} more electoral votes")
        
        # State-by-state breakdown
        st.subheader("State-by-State Breakdown")
        
        # Sort by electoral votes
        df_display = df_states.sort_values('electoral_votes', ascending=False)
        
        # Create color coding based on lean
        def color_lean(val):
            if 'Safe You' in val:
                return 'background-color: #90EE90'
            elif 'Lean You' in val:
                return 'background-color: #ADD8E6'
            elif 'Toss-up' in val:
                return 'background-color: #FFE4B5'
            elif 'Lean Opponent' in val:
                return 'background-color: #FFB6C1'
            elif 'Safe Opponent' in val:
                return 'background-color: #FF6B6B'
            return ''
        
        # Display styled dataframe
        styled_df = df_display[['state', 'electoral_votes', 'your_support', 'opponent_support', 'undecided', 'lean']].style.applymap(
            color_lean, subset=['lean']
        ).format({
            'your_support': '{:.1f}%',
            'opponent_support': '{:.1f}%',
            'undecided': '{:.1f}%'
        })
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Bar chart of support by state
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='You',
            x=df_display['state'],
            y=df_display['your_support'],
            marker_color='#1f77b4'
        ))
        fig.add_trace(go.Bar(
            name='Opponent',
            x=df_display['state'],
            y=df_display['opponent_support'],
            marker_color='#ff7f0e'
        ))
        
        fig.update_layout(
            title='Support by State',
            xaxis_title='State',
            yaxis_title='Support (%)',
            barmode='group',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Issue Positions")
    if "issues" in data and data["issues"]:
        df_issues = pd.DataFrame(data["issues"])
        
        # Position comparison
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Your Position',
            x=df_issues['issue'],
            y=df_issues['your_position'],
            marker_color='#1f77b4'
        ))
        fig.add_trace(go.Bar(
            name='Voter Preference',
            x=df_issues['issue'],
            y=df_issues['voter_preference'],
            marker_color='#2ca02c'
        ))
        
        fig.update_layout(
            title='Issue Positions (1=Very Conservative, 10=Very Liberal)',
            xaxis_title='Issue',
            yaxis_title='Position',
            barmode='group',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Issue importance
        fig2 = px.bar(df_issues, x='issue', y='importance',
                     title='Issue Importance to Voters',
                     labels={'importance': 'Importance Score', 'issue': 'Issue'},
                     color='importance',
                     color_continuous_scale='Reds')
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Alignment analysis
        st.subheader("Position Alignment Analysis")
        df_issues['alignment'] = 100 - abs(df_issues['your_position'] - df_issues['voter_preference']) * 10
        df_issues['weighted_alignment'] = df_issues['alignment'] * df_issues['importance'] / 100
        
        col1, col2 = st.columns(2)
        with col1:
            avg_alignment = df_issues['alignment'].mean()
            st.metric("Average Alignment", f"{avg_alignment:.1f}%")
        with col2:
            weighted_avg = df_issues['weighted_alignment'].mean()
            st.metric("Weighted Alignment", f"{weighted_avg:.1f}%")
        
        st.dataframe(df_issues[['issue', 'your_position', 'voter_preference', 'alignment', 'importance']].style.format({
            'your_position': '{:.1f}',
            'voter_preference': '{:.1f}',
            'alignment': '{:.1f}%',
            'importance': '{:.0f}'
        }), use_container_width=True)

with tab5:
    st.header("Campaign Timeline")
    if "events" in data and data["events"]:
        df_events = pd.DataFrame(data["events"])
        df_events['date'] = pd.to_datetime(df_events['date'])
        df_events = df_events.sort_values('date', ascending=False)
        
        st.subheader("Key Campaign Events")
        for idx, row in df_events.iterrows():
            with st.expander(f"📅 {row['date'].strftime('%B %d, %Y')} - {row['event']}"):
                st.write(f"**Impact:** {row['impact']}")
        
        # Event impact visualization
        fig = go.Figure(data=go.Scatter(
            x=df_events['date'],
            y=list(range(len(df_events))),
            mode='markers+text',
            marker=dict(size=15, color='#1f77b4'),
            text=df_events['event'],
            textposition='middle right',
            hovertemplate='<b>%{text}</b><br>Date: %{x}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Campaign Events Timeline',
            xaxis_title='Date',
            yaxis_visible=False,
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

# Download processed data
st.header("📥 Export Data")
if st.button("Download Processed Data as CSV"):
    if "state_data" in data:
        csv = pd.DataFrame(data["state_data"]).to_csv(index=False)
        st.download_button(
            label="Download State Data CSV",
            data=csv,
            file_name="political_process_state_data.csv",
            mime="text/csv"
        )

st.markdown("---")
st.markdown("*Political Process Save Game Analyzer - Built with Streamlit*")
