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
Upload your save game file to visualize political career data, city statistics, and historical trends!
""")

# File uploader with increased size limit info
st.info("💡 **Tip:** The app supports files up to 200MB. For best performance with large files (50MB+), ensure you have a stable connection.")
uploaded_file = st.file_uploader("Upload Save Game File (JSON format)", type=['json', 'txt', 'sav'])

def parse_tpp_save(file):
    """Parse The Political Process save file"""
    try:
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        st.info(f"📦 File size: {file_size / 1024 / 1024:.2f} MB - Processing...")
        
        if file_size > 50 * 1024 * 1024:
            st.warning("⚠️ Large file detected. This may take a moment to process...")
        
        content = file.read()
        
        try:
            data = json.loads(content)
            st.success(f"✅ Successfully parsed Political Process save file!")
            return data, None
        except json.JSONDecodeError as je:
            # Try to handle truncated JSON
            try:
                content_str = content.decode('utf-8')
                # Find the last complete JSON structure
                last_brace = content_str.rfind('}')
                if last_brace > 0:
                    truncated_json = content_str[:last_brace + 1]
                    data = json.loads(truncated_json)
                    st.warning(f"⚠️ File appears truncated. Parsed partial data successfully.")
                    return data, None
            except:
                pass
            return None, f"Could not parse JSON: {str(je)[:200]}"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"

def extract_player_info(data):
    """Extract player information from save data"""
    try:
        player = data.get('player', [])
        if isinstance(player, list) and len(player) > 0:
            # Based on the structure seen, extract key indices
            return {
                'party': player[0] if len(player) > 0 else 'Unknown',
                'name': f"{player[4]} {player[5]}" if len(player) > 5 else 'Unknown',
                'ideology_left': player[6] if len(player) > 6 else 'Unknown',
                'ideology_right': player[7] if len(player) > 7 else 'Unknown',
            }
        return {}
    except:
        return {}

def extract_city_stats(data):
    """Extract city statistics from save data"""
    return data.get('cityStats', {})

def extract_historical_data(city_stats):
    """Extract historical data arrays for trending"""
    historical = city_stats.get('historicData', {})
    return historical

if uploaded_file is not None:
    with st.spinner('Processing save file...'):
        data, error = parse_tpp_save(uploaded_file)
        
        if error:
            st.error(f"❌ Error: {error}")
            st.stop()
        
        # Extract game information
        player_info = extract_player_info(data)
        city_stats = extract_city_stats(data)
        historical_data = extract_historical_data(city_stats)
        
        # Show what was found
        with st.expander("🔍 Debug: Data found in save file"):
            st.write("**Top-level keys:**", list(data.keys())[:20] if isinstance(data, dict) else "Data is not a dictionary")
            if city_stats:
                st.write("**City name:**", city_stats.get('name', 'Unknown'))
                st.write("**Game year:**", data.get('currentYear', 'Unknown'))
                st.write("**City population:**", f"{city_stats.get('pop', 0):,.0f}")
        
        # Display game info
        st.header("📋 Game Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Your Name", player_info.get('name', 'N/A'))
        with col2:
            st.metric("Party", player_info.get('party', 'N/A'))
        with col3:
            st.metric("Game Year", data.get('currentYear', 'N/A'))
        with col4:
            st.metric("City", city_stats.get('name', 'N/A'))
        
        # Tabs for different visualizations
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Demographics", "💰 Economy", "🎓 Education", "👮 Crime & Justice", "📈 Historical Trends"])
        
        with tab1:
            st.header("Demographics & Population")
            
            if city_stats:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Population", f"{city_stats.get('pop', 0):,.0f}")
                    st.metric("Under 18", f"{city_stats.get('under18', 0):,.0f}")
                    st.metric("Over 65", f"{city_stats.get('over65', 0):,.0f}")
                
                with col2:
                    st.metric("Democrats", f"{city_stats.get('demPop', 0) * 100:.1f}%")
                    st.metric("Republicans", f"{city_stats.get('repPop', 0) * 100:.1f}%")
                    st.metric("Independents", f"{city_stats.get('indPop', 0) * 100:.1f}%")
                
                with col3:
                    st.metric("Registered Voters", f"{city_stats.get('regVoters', 0) * 100:.1f}%")
                    st.metric("General Turnout", f"{city_stats.get('generalTurnout', 0) * 100:.1f}%")
                    st.metric("Midterm Turnout", f"{city_stats.get('midTermTurnout', 0) * 100:.1f}%")
                
                # Racial demographics
                st.subheader("Racial/Ethnic Demographics")
                demo_data = {
                    'Group': ['Caucasian', 'African American', 'Hispanic', 'Asian', 'Native American', 'Mixed', 'Middle Eastern'],
                    'Percentage': [
                        city_stats.get('caucasian', 0),
                        city_stats.get('african', 0),
                        city_stats.get('hispanic', 0),
                        city_stats.get('asian', 0),
                        city_stats.get('native', 0),
                        city_stats.get('mixed', 0),
                        city_stats.get('midEast', 0)
                    ]
                }
                df_demo = pd.DataFrame(demo_data)
                fig = px.pie(df_demo, values='Percentage', names='Group', title='Racial/Ethnic Composition')
                st.plotly_chart(fig, use_container_width=True)
                
                # Political affiliation
                st.subheader("Political Affiliation")
                pol_data = pd.DataFrame({
                    'Party': ['Democrat', 'Republican', 'Independent'],
                    'Percentage': [
                        city_stats.get('demPop', 0) * 100,
                        city_stats.get('repPop', 0) * 100,
                        city_stats.get('indPop', 0) * 100
                    ]
                })
                fig2 = px.bar(pol_data, x='Party', y='Percentage', 
                             color='Party',
                             color_discrete_map={'Democrat': '#1f77b4', 'Republican': '#ff7f0e', 'Independent': '#2ca02c'},
                             title='Political Party Distribution')
                st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            st.header("Economic Indicators")
            
            if city_stats:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Per Capita Income", f"${city_stats.get('perCapitaIncome', 0):,.2f}")
                with col2:
                    st.metric("Post-Tax Income", f"${city_stats.get('postTaxIncome', 0):,.2f}")
                with col3:
                    st.metric("Unemployment Rate", f"{city_stats.get('unemployment', 0):.2f}%")
                with col4:
                    st.metric("Poverty Rate", f"{city_stats.get('belowPoverty', 0):.2f}%")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Labor Force", f"{city_stats.get('laborForce', 0):,.0f}")
                    st.metric("Unemployed", f"{city_stats.get('unemployNum', 0):,.0f}")
                with col2:
                    st.metric("Minimum Wage", f"${city_stats.get('minWage', 0):.2f}/hr")
                    st.metric("Minimum Wage Jobs", f"{city_stats.get('minWageJob', 0):,.0f}")
                
                # Tax revenue breakdown
                st.subheader("City Finances")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Tax Revenue", f"${city_stats.get('totTaxRevenue', 0):,.0f}")
                with col2:
                    st.metric("City Treasury", f"${city_stats.get('treasury', 0):,.0f}")
                with col3:
                    st.metric("General Expenditure", f"${city_stats.get('genExpenditure', 0):,.0f}")
                
                # Tax breakdown
                st.subheader("Tax Revenue Sources")
                tax_data = pd.DataFrame({
                    'Source': ['Property Tax (City)', 'Property Tax (School)', 'Sales Tax', 'Income Tax', 'Other'],
                    'Amount': [
                        city_stats.get('cityPropTaxRev', 0),
                        city_stats.get('schoolPropTaxRev', 0),
                        city_stats.get('salesTaxRev', 0),
                        city_stats.get('incomeTaxRev', 0),
                        city_stats.get('totTaxRevenue', 0) - (
                            city_stats.get('cityPropTaxRev', 0) +
                            city_stats.get('schoolPropTaxRev', 0) +
                            city_stats.get('salesTaxRev', 0) +
                            city_stats.get('incomeTaxRev', 0)
                        )
                    ]
                })
                fig = px.bar(tax_data, x='Source', y='Amount', title='Tax Revenue by Source')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.header("Education Statistics")
            
            if city_stats:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Students", f"{city_stats.get('students', 0):,.0f}")
                    st.metric("High School Students", f"{city_stats.get('highSchoolStudents', 0):,.0f}")
                with col2:
                    st.metric("Academic Score", f"{city_stats.get('academicScore', 0):.2f}")
                    st.metric("Dropout Rate", f"{city_stats.get('totDropoutRate', 0) * 100:.2f}%")
                with col3:
                    st.metric("Education Budget", f"${city_stats.get('eduAdminBudget', 0):,.0f}")
                    st.metric("Teacher Pay Rate", f"{city_stats.get('teachPayRate', 1):.2f}x")
                
                # Education attainment
                st.subheader("Adult Education Levels")
                edu_data = pd.DataFrame({
                    'Level': ['No School', 'High School', 'Some College', 'Bachelor\'s', 'Graduate'],
                    'Percentage': [
                        city_stats.get('noSchoolEd', 0) * 100,
                        city_stats.get('highSchoolEd', 0) * 100,
                        city_stats.get('collegeEd', 0) * 100,
                        city_stats.get('bachelorEd', 0) * 100,
                        city_stats.get('gradEd', 0) * 100
                    ]
                })
                fig = px.bar(edu_data, x='Level', y='Percentage', title='Educational Attainment')
                st.plotly_chart(fig, use_container_width=True)
                
                # Teacher stats
                st.subheader("Teaching Staff")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Bachelor's Degree Teachers", f"{city_stats.get('bachTeachers', 0):,.0f}")
                    st.metric("Their Budget", f"${city_stats.get('bachTeachBudget', 0):,.0f}")
                with col2:
                    st.metric("Master's Degree Teachers", f"{city_stats.get('masterTeachers', 0):,.0f}")
                    st.metric("Their Budget", f"${city_stats.get('masterTeachBudget', 0):,.0f}")
        
        with tab4:
            st.header("Crime & Justice System")
            
            if city_stats:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Crime Rate", f"{city_stats.get('totalCrime', 0) * 100:.2f}%")
                with col2:
                    st.metric("Violent Crime", f"{city_stats.get('vCrimeRate', 0) * 100:.2f}%")
                with col3:
                    st.metric("Property Crime", f"{city_stats.get('pCrimeRate', 0) * 100:.2f}%")
                with col4:
                    st.metric("Drug Crime", f"{city_stats.get('dCrimeRate', 0) * 100:.2f}%")
                
                # Police force
                st.subheader("Law Enforcement")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Police Officers", f"{city_stats.get('police', 0):,.0f}")
                    st.metric("Police Budget", f"${city_stats.get('policeBudget', 0):,.0f}")
                with col2:
                    st.metric("Total Prisoners", f"{city_stats.get('vPrisoners', 0) + city_stats.get('pPrisoners', 0) + city_stats.get('dPrisoners', 0):,.0f}")
                    st.metric("Jail Budget", f"${city_stats.get('jailBudget', 0):,.0f}")
                with col3:
                    st.metric("Violent Prisoners", f"{city_stats.get('vPrisoners', 0):,.0f}")
                    st.metric("Drug Prisoners", f"{city_stats.get('dPrisoners', 0):,.0f}")
                
                # Crime breakdown
                st.subheader("Crime Types Breakdown")
                crime_data = pd.DataFrame({
                    'Type': ['Violent', 'Property', 'Drug', 'Other'],
                    'Rate': [
                        city_stats.get('vCrimeRate', 0) * 100,
                        city_stats.get('pCrimeRate', 0) * 100,
                        city_stats.get('dCrimeRate', 0) * 100,
                        city_stats.get('oCrimeRate', 0) * 100
                    ]
                })
                fig = px.bar(crime_data, x='Type', y='Rate', title='Crime Rates by Type (%)')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab5:
            st.header("Historical Trends")
            
            if historical_data:
                # Population trend
                if 'population' in historical_data:
                    df_pop = pd.DataFrame(historical_data['population'])
                    fig = px.line(df_pop, x='year', y='value', title='Population Growth Over Time',
                                 labels={'value': 'Population', 'year': 'Year'})
                    st.plotly_chart(fig, use_container_width=True)
                
                # Economic trends
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'perCapitaIncome' in historical_data:
                        df_income = pd.DataFrame(historical_data['perCapitaIncome'])
                        fig = px.line(df_income, x='year', y='value', 
                                     title='Per Capita Income Trend',
                                     labels={'value': 'Income ($)', 'year': 'Year'})
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'unemployment' in historical_data:
                        df_unemp = pd.DataFrame(historical_data['unemployment'])
                        fig = px.line(df_unemp, x='year', y='value',
                                     title='Unemployment Rate Trend',
                                     labels={'value': 'Rate (%)', 'year': 'Year'})
                        st.plotly_chart(fig, use_container_width=True)
                
                # Education trends
                if 'collegeNum' in historical_data and 'bachelorNum' in historical_data:
                    df_college = pd.DataFrame(historical_data['collegeNum'])
                    df_bach = pd.DataFrame(historical_data['bachelorNum'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df_college['year'], y=df_college['value'],
                                            mode='lines', name='Some College'))
                    fig.add_trace(go.Scatter(x=df_bach['year'], y=df_bach['value'],
                                            mode='lines', name='Bachelor\'s Degree'))
                    fig.update_layout(title='Education Attainment Trends',
                                    xaxis_title='Year',
                                    yaxis_title='Number of People')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Demographics trends
                if 'demPop' in historical_data:
                    df_dem = pd.DataFrame(historical_data['demPop'])
                    df_rep = pd.DataFrame(historical_data['repPop'])
                    df_ind = pd.DataFrame(historical_data['indPop'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df_dem['year'], y=[v*100 for v in df_dem['value']],
                                            mode='lines', name='Democrat', line=dict(color='#1f77b4')))
                    fig.add_trace(go.Scatter(x=df_rep['year'], y=[v*100 for v in df_rep['value']],
                                            mode='lines', name='Republican', line=dict(color='#ff7f0e')))
                    fig.add_trace(go.Scatter(x=df_ind['year'], y=[v*100 for v in df_ind['value']],
                                            mode='lines', name='Independent', line=dict(color='#2ca02c')))
                    fig.update_layout(title='Political Affiliation Trends',
                                    xaxis_title='Year',
                                    yaxis_title='Percentage (%)')
                    st.plotly_chart(fig, use_container_width=True)
        
        # Export functionality
        st.header("📥 Export Data")
        if st.button("Download City Stats as CSV"):
            if city_stats:
                # Flatten the city stats dict for CSV
                flat_stats = {}
                for key, value in city_stats.items():
                    if not isinstance(value, (dict, list)):
                        flat_stats[key] = value
                
                df_export = pd.DataFrame([flat_stats])
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="political_process_city_stats.csv",
                    mime="text/csv"
                )

else:
    st.info("📊 Upload your Political Process save file to begin analysis!")
    st.markdown("""
    ### What you'll see:
    - **Demographics**: Population breakdown by party, race, age
    - **Economy**: Income, unemployment, taxes, and city budget
    - **Education**: Student stats, teacher data, academic performance
    - **Crime & Justice**: Crime rates, police force, prison population
    - **Historical Trends**: Charts showing how your city has evolved over time
    
    The app will automatically parse your save file and extract all the relevant data!
    """)

st.markdown("---")
st.markdown("*Political Process Save Game Analyzer - Built with Streamlit*")
