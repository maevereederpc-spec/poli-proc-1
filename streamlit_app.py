import streamlit as st
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Page config with wine red theme
st.set_page_config(
    page_title="Political Process Analytics",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern wine red theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --wine-red: #722F37;
        --wine-red-light: #8B3A44;
        --wine-red-dark: #5A1F28;
        --wine-red-accent: #A04555;
        --dark-bg: #0E1117;
        --card-bg: #1E1E1E;
        --text-primary: #FAFAFA;
        --text-secondary: #B0B0B0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    h1 {
        background: linear-gradient(135deg, var(--wine-red) 0%, var(--wine-red-accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: var(--wine-red) !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--card-bg);
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 500;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--wine-red) 0%, var(--wine-red-accent) 100%);
        color: white !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--card-bg) 0%, var(--dark-bg) 100%);
        border-right: 2px solid var(--wine-red-dark);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--wine-red) 0%, var(--wine-red-accent) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(114, 47, 55, 0.4);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: var(--card-bg);
        border: 2px dashed var(--wine-red);
        border-radius: 10px;
        padding: 20px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--card-bg);
        border-radius: 8px;
        color: var(--text-primary) !important;
        font-weight: 500;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: var(--card-bg);
        border-left: 4px solid var(--wine-red);
        border-radius: 8px;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: var(--text-primary) !important;
        font-weight: 500;
    }
    
    .stRadio > div {
        background-color: var(--card-bg);
        padding: 15px;
        border-radius: 8px;
        border: 2px solid var(--wine-red-dark);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--wine-red-dark) 0%, var(--wine-red) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Wine red color palette for charts
WINE_COLORS = {
    'primary': '#722F37',
    'secondary': '#A04555',
    'accent': '#8B3A44',
    'light': '#C86B7A',
    'dark': '#5A1F28',
    'gradient': ['#722F37', '#8B3A44', '#A04555', '#C86B7A', '#E89BAA']
}

PARTY_COLORS = {
    'Democrat': '#1E88E5',
    'Republican': '#D32F2F', 
    'Independent': '#43A047'
}

# Title
st.markdown("<h1>🗳️ Political Process Analytics</h1>", unsafe_allow_html=True)
st.markdown("##### Advanced Political Career & City Management Dashboard")
st.markdown("---")

# File uploader
uploaded_file = st.file_uploader(
    "📁 Upload Your Save Game File",
    type=['json', 'txt', 'sav'],
    help="Upload your Political Process save file to visualize your political career data"
)

def parse_tpp_save(file):
    """Parse The Political Process save file"""
    try:
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        with st.spinner(f'⚙️ Processing {file_size / 1024 / 1024:.1f} MB file...'):
            content = file.read()
            
            try:
                data = json.loads(content)
                return data, None
            except json.JSONDecodeError:
                # Try to handle truncated JSON
                try:
                    content_str = content.decode('utf-8')
                    last_brace = content_str.rfind('}')
                    if last_brace > 0:
                        truncated_json = content_str[:last_brace + 1]
                        data = json.loads(truncated_json)
                        return data, None
                except:
                    pass
                return None, "Could not parse JSON file"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

def extract_state_data(data):
    """Extract state-level data from save"""
    try:
        player = data.get('player', [])
        # State data is typically in the player array
        for item in player:
            if isinstance(item, list) and len(item) > 0:
                if isinstance(item[0], dict) and 'state' in item[0]:
                    return item
        return []
    except:
        return []

if uploaded_file is not None:
    data, error = parse_tpp_save(uploaded_file)
    
    if error:
        st.error(f"❌ {error}")
        st.stop()
    
    # Extract all data
    player = data.get('player', [])
    city_stats = data.get('cityStats', {})
    current_year = data.get('currentYear', 'Unknown')
    version = data.get('version', 'Unknown')
    state_data = extract_state_data(data)
    historical_data = city_stats.get('historicData', {})
    
    # Sidebar for level selection
    with st.sidebar:
        st.markdown("### 🎯 Data Scope")
        view_level = st.radio(
            "Select View Level:",
            ["🏛️ Local (City)", "🗺️ State", "🇺🇸 National"],
            help="Choose which geographic level to analyze"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        if city_stats:
            st.metric("Game Year", current_year)
            st.metric("City", city_stats.get('name', 'N/A'))
            st.metric("Population", f"{city_stats.get('pop', 0):,.0f}")
            st.metric("Version", version)
        
        st.markdown("---")
        st.markdown("### 🎨 Chart Style")
        chart_template = st.selectbox(
            "Chart Theme",
            ["plotly_dark", "plotly", "seaborn", "ggplot2"],
            index=0
        )
    
    # Success message
    st.success(f"✅ Successfully loaded save file from Year {current_year}")
    
    # Player info header
    player_name = f"{player[4]} {player[5]}" if len(player) > 5 else "Unknown"
    player_party = player[0] if len(player) > 0 else "Unknown"
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("👤 Player", player_name)
    with col2:
        st.metric("🎭 Party", player_party)
    with col3:
        st.metric("📅 Year", current_year)
    with col4:
        st.metric("🏙️ City", city_stats.get('name', 'N/A'))
    with col5:
        st.metric("👥 Population", f"{city_stats.get('pop', 0):,.0f}")
    
    st.markdown("---")
    
    # Main content based on view level
    if "Local" in view_level:
        st.markdown("## 🏛️ Local City Analysis")
        
        tabs = st.tabs(["📊 Demographics", "💰 Economy", "🎓 Education", "⚖️ Crime & Justice", "📈 Trends"])
        
        with tabs[0]:  # Demographics
            st.markdown("### Population & Voter Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Population", f"{city_stats.get('pop', 0):,.0f}")
                st.metric("Youth (<18)", f"{city_stats.get('under18', 0):,.0f}")
            with col2:
                st.metric("Seniors (65+)", f"{city_stats.get('over65', 0):,.0f}")
                st.metric("Labor Force", f"{city_stats.get('laborForce', 0):,.0f}")
            with col3:
                st.metric("Registered Voters", f"{city_stats.get('regVoters', 0) * 100:.1f}%")
                st.metric("General Turnout", f"{city_stats.get('generalTurnout', 0) * 100:.1f}%")
            with col4:
                st.metric("Midterm Turnout", f"{city_stats.get('midTermTurnout', 0) * 100:.1f}%")
                st.metric("District #", city_stats.get('districtNum', 'N/A'))
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Political Affiliation")
                pol_data = pd.DataFrame({
                    'Party': ['Democrat', 'Republican', 'Independent'],
                    'Percentage': [
                        city_stats.get('demPop', 0) * 100,
                        city_stats.get('repPop', 0) * 100,
                        city_stats.get('indPop', 0) * 100
                    ]
                })
                fig = px.bar(pol_data, x='Party', y='Percentage',
                            color='Party',
                            color_discrete_map=PARTY_COLORS,
                            template=chart_template)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Racial/Ethnic Composition")
                demo_data = pd.DataFrame({
                    'Group': ['Caucasian', 'African American', 'Hispanic', 'Asian', 'Native', 'Mixed', 'Mid East'],
                    'Percentage': [
                        city_stats.get('caucasian', 0),
                        city_stats.get('african', 0),
                        city_stats.get('hispanic', 0),
                        city_stats.get('asian', 0),
                        city_stats.get('native', 0),
                        city_stats.get('mixed', 0),
                        city_stats.get('midEast', 0)
                    ]
                })
                fig = px.pie(demo_data, values='Percentage', names='Group',
                            color_discrete_sequence=WINE_COLORS['gradient'],
                            template=chart_template)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tabs[1]:  # Economy
            st.markdown("### Economic Indicators & City Finances")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Per Capita Income", f"${city_stats.get('perCapitaIncome', 0):,.0f}")
            with col2:
                st.metric("Post-Tax Income", f"${city_stats.get('postTaxIncome', 0):,.0f}")
            with col3:
                unemployment = city_stats.get('unemployment', 0)
                st.metric("Unemployment", f"{unemployment:.2f}%")
            with col4:
                poverty = city_stats.get('belowPoverty', 0)
                st.metric("Poverty Rate", f"{poverty:.2f}%")
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Total Tax Revenue", f"${city_stats.get('totTaxRevenue', 0):,.0f}")
            with col2:
                st.metric("🏦 City Treasury", f"${city_stats.get('treasury', 0):,.0f}")
            with col3:
                st.metric("💸 Expenditure", f"${city_stats.get('genExpenditure', 0):,.0f}")
            
            st.markdown("---")
            st.markdown("#### Tax Revenue Breakdown")
            
            tax_sources = pd.DataFrame({
                'Source': ['Property (City)', 'Property (School)', 'Sales', 'Income', 'Other'],
                'Amount': [
                    city_stats.get('cityPropTaxRev', 0),
                    city_stats.get('schoolPropTaxRev', 0),
                    city_stats.get('salesTaxRev', 0),
                    city_stats.get('incomeTaxRev', 0),
                    max(0, city_stats.get('totTaxRevenue', 0) - (
                        city_stats.get('cityPropTaxRev', 0) +
                        city_stats.get('schoolPropTaxRev', 0) +
                        city_stats.get('salesTaxRev', 0) +
                        city_stats.get('incomeTaxRev', 0)
                    ))
                ]
            })
            
            fig = px.bar(tax_sources, x='Source', y='Amount',
                        color='Amount',
                        color_continuous_scale=[[0, WINE_COLORS['light']], [1, WINE_COLORS['dark']]],
                        template=chart_template)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tabs[2]:  # Education
            st.markdown("### Education System Performance")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📚 Total Students", f"{city_stats.get('students', 0):,.0f}")
            with col2:
                st.metric("📖 Academic Score", f"{city_stats.get('academicScore', 0):.1f}")
            with col3:
                dropout = city_stats.get('totDropoutRate', 0) * 100
                st.metric("🎓 Dropout Rate", f"{dropout:.2f}%")
            with col4:
                st.metric("💵 Education Budget", f"${city_stats.get('eduAdminBudget', 0):,.0f}")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Education Attainment Levels")
                edu_levels = pd.DataFrame({
                    'Level': ['No School', 'High School', 'Some College', 'Bachelor\'s', 'Graduate'],
                    'Percentage': [
                        city_stats.get('noSchoolEd', 0) * 100,
                        city_stats.get('highSchoolEd', 0) * 100,
                        city_stats.get('collegeEd', 0) * 100,
                        city_stats.get('bachelorEd', 0) * 100,
                        city_stats.get('gradEd', 0) * 100
                    ]
                })
                fig = px.bar(edu_levels, x='Level', y='Percentage',
                            color='Percentage',
                            color_continuous_scale=[[0, WINE_COLORS['light']], [1, WINE_COLORS['primary']]],
                            template=chart_template)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Teaching Staff Distribution")
                teacher_data = pd.DataFrame({
                    'Degree': ['Bachelor\'s', 'Master\'s', 'Support Staff'],
                    'Count': [
                        city_stats.get('bachTeachers', 0),
                        city_stats.get('masterTeachers', 0),
                        city_stats.get('teachAssist', 0)
                    ]
                })
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Staff Count',
                    x=teacher_data['Degree'],
                    y=teacher_data['Count'],
                    marker_color=WINE_COLORS['primary']
                ))
                fig.update_layout(
                    template=chart_template,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=400,
                    yaxis_title="Number of Staff"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tabs[3]:  # Crime & Justice
            st.markdown("### Public Safety & Justice System")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_crime = city_stats.get('totalCrime', 0) * 100
                st.metric("🚨 Total Crime Rate", f"{total_crime:.2f}%")
            with col2:
                st.metric("👮 Police Officers", f"{city_stats.get('police', 0):,.0f}")
            with col3:
                total_prisoners = (city_stats.get('vPrisoners', 0) + 
                                 city_stats.get('pPrisoners', 0) + 
                                 city_stats.get('dPrisoners', 0))
                st.metric("⛓️ Total Prisoners", f"{total_prisoners:,.0f}")
            with col4:
                st.metric("💰 Police Budget", f"${city_stats.get('policeBudget', 0):,.0f}")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Crime Rates by Category")
                crime_types = pd.DataFrame({
                    'Type': ['Violent', 'Property', 'Drug', 'Other'],
                    'Rate': [
                        city_stats.get('vCrimeRate', 0) * 100,
                        city_stats.get('pCrimeRate', 0) * 100,
                        city_stats.get('dCrimeRate', 0) * 100,
                        city_stats.get('oCrimeRate', 0) * 100
                    ]
                })
                fig = px.bar(crime_types, x='Type', y='Rate',
                            color='Rate',
                            color_continuous_scale=[[0, WINE_COLORS['light']], [1, WINE_COLORS['dark']]],
                            template=chart_template)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    height=400,
                    yaxis_title="Crime Rate (%)"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Prison Population")
                prison_data = pd.DataFrame({
                    'Category': ['Violent', 'Property', 'Drug', 'Other'],
                    'Prisoners': [
                        city_stats.get('vPrisoners', 0),
                        city_stats.get('pPrisoners', 0),
                        city_stats.get('dPrisoners', 0),
                        city_stats.get('oPrisoners', 0)
                    ]
                })
                fig = px.pie(prison_data, values='Prisoners', names='Category',
                            color_discrete_sequence=WINE_COLORS['gradient'],
                            template=chart_template)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tabs[4]:  # Trends
            st.markdown("### Historical Trends Analysis")
            
            if historical_data:
                # Population trend
                if 'population' in historical_data:
                    st.markdown("#### 📈 Population Growth")
                    df_pop = pd.DataFrame(historical_data['population'])
                    fig = px.area(df_pop, x='year', y='value',
                                 color_discrete_sequence=[WINE_COLORS['primary']],
                                 template=chart_template)
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="Year",
                        yaxis_title="Population",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'perCapitaIncome' in historical_data:
                        st.markdown("#### 💵 Income Trend")
                        df_income = pd.DataFrame(historical_data['perCapitaIncome'])
                        fig = px.line(df_income, x='year', y='value',
                                     markers=True,
                                     line_shape='spline',
                                     template=chart_template)
                        fig.update_traces(line_color=WINE_COLORS['primary'], line_width=3)
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis_title="Year",
                            yaxis_title="Per Capita Income ($)",
                            height=350
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'unemployment' in historical_data:
                        st.markdown("#### 📊 Unemployment Rate")
                        df_unemp = pd.DataFrame(historical_data['unemployment'])
                        fig = px.line(df_unemp, x='year', y='value',
                                     markers=True,
                                     line_shape='spline',
                                     template=chart_template)
                        fig.update_traces(line_color=WINE_COLORS['accent'], line_width=3)
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis_title="Year",
                            yaxis_title="Unemployment Rate (%)",
                            height=350
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    elif "State" in view_level:
        st.markdown("## 🗺️ State-Level Analysis")
        
        if state_data:
            st.markdown(f"### Analyzing {len(state_data)} States")
            
            # Convert state data to DataFrame
            df_states = pd.DataFrame(state_data)
            
            # Calculate aggregate metrics
            total_states = len(df_states)
            states_with_presence = len(df_states[df_states['nameRec'] > 0])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total States", total_states)
            with col2:
                st.metric("🏢 States with Presence", states_with_presence)
            with col3:
                st.metric("🎯 Field Offices", df_states['fieldOffice'].sum())
            with col4:
                avg_trust = df_states.apply(lambda x: x.get('trust', {}).get('democrat', {}).get('total', 0) if isinstance(x.get('trust'), dict) else 0, axis=1).mean()
                st.metric("📈 Avg Trust (Dem)", f"{avg_trust:.2f}")
            
            st.markdown("---")
            
            # Extract trust data
            df_states['dem_trust'] = df_states.apply(lambda x: x.get('trust', {}).get('democrat', {}).get('total', 0) if isinstance(x.get('trust'), dict) else 0, axis=1)
            df_states['rep_trust'] = df_states.apply(lambda x: x.get('trust', {}).get('republican', {}).get('total', 0) if isinstance(x.get('trust'), dict) else 0, axis=1)
            df_states['ind_trust'] = df_states.apply(lambda x: x.get('trust', {}).get('independent', {}).get('total', 0) if isinstance(x.get('trust'), dict) else 0, axis=1)
            
            # Display top states
            top_states = df_states.nlargest(10, 'nameRec')[['state', 'nameRec', 'fieldOffice', 'dem_trust', 'rep_trust', 'ind_trust']]
            
            st.markdown("#### Top 10 States by Name Recognition")
            fig = px.bar(top_states, x='state', y='nameRec',
                        color='nameRec',
                        color_continuous_scale=[[0, WINE_COLORS['light']], [1, WINE_COLORS['primary']]],
                        template=chart_template)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                height=400,
                xaxis_title="State",
                yaxis_title="Name Recognition"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No state-level data found in this save file")
    
    else:  # National view
        st.markdown("## 🇺🇸 National Analysis")
        
        st.info("📊 National-level statistics aggregated from all available data")
        
        if state_data:
            df_states = pd.DataFrame(state_data)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🗳️ Total States", len(df_states))
            with col2:
                st.metric("🏢 Total Field Offices", df_states['fieldOffice'].sum())
            with col3:
                total_trust = df_states.apply(lambda x: x.get('trust', {}).get('democrat', {}).get('total', 0) if isinstance(x.get('trust'), dict) else 0, axis=1).sum()
                st.metric("📊 Total Trust Score", f"{total_trust:,.0f}")

else:
    # Welcome screen
    st.markdown("""
    <div style='text-align: center; padding: 50px;'>
        <h2>Welcome to Political Process Analytics</h2>
        <p style='font-size: 1.2em; color: #B0B0B0;'>
            Upload your save file to unlock powerful insights
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #B0B0B0; padding: 20px;'>
    <small>Political Process Analytics Dashboard • Built with Streamlit & Plotly</small>
</div>
""", unsafe_allow_html=True)
