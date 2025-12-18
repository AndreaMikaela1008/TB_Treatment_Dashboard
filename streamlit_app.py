# -*- coding: utf-8 -*-
"""
Tuberculosis Treatment Success Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import numpy as np

# ======================
# PAGE CONFIGURATION
# ======================
st.set_page_config(
    page_title="TB Treatment Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================
# SAMPLE DATA FUNCTION
# ======================
def create_sample_data():
    """Create sample data for testing"""
    countries = ['Philippines', 'India', 'USA', 'China', 'Brazil', 'Nigeria', 
                 'Russia', 'Indonesia', 'Pakistan', 'Bangladesh', 'South Africa',
                 'Vietnam', 'Thailand', 'Mexico', 'Egypt']
    years = list(range(2010, 2024))
    
    data = []
    for i in range(200):  # Create 200 rows
        country = np.random.choice(countries)
        year = np.random.choice(years)
        success_rate = np.random.uniform(60, 95)
        dropout_rate = 100 - success_rate + np.random.uniform(-10, 10)
        
        data.append({
            'country': country,
            'year': year,
            'region': np.random.choice(['Asia', 'Africa', 'Americas', 'Europe']),
            'treatment_success_rate': round(success_rate, 1),
            'dropout_rate': round(max(0, min(100, dropout_rate)), 1),
            'cases': np.random.randint(100, 5000),
            'clinic_type': np.random.choice(['Urban DOTS', 'Rural DOTS', 'Hospital', 'Health Center'])
        })
    
    return pd.DataFrame(data)

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    """Load data from file or create sample data"""
    # Try multiple possible file locations
    possible_paths = [
        "data/tb_data_cleaned.csv",
        "../Data/tb_data_cleaned.csv",
        "tb_data_cleaned.csv",
        "cleaned_tb_data.csv",
        "data/cleaned_tb_data.csv",
        r"C:\Users\user\OneDrive\3rd - 1st Sem\ITE3\TB_Treatment_Dashboard\Data\tb_data_cleaned.csv"
    ]
    
    for file_path in possible_paths:
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                st.sidebar.success(f"✅ Loaded: {os.path.basename(file_path)}")
                
                # Ensure required columns exist
                if 'treatment_success_rate' not in df.columns:
                    if 'success_rate' in df.columns:
                        df = df.rename(columns={'success_rate': 'treatment_success_rate'})
                
                if 'dropout_rate' not in df.columns and 'treatment_success_rate' in df.columns:
                    df['dropout_rate'] = 100 - df['treatment_success_rate']
                
                # Ensure year is integer
                if 'year' in df.columns:
                    df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)
                
                return df
            except Exception as e:
                continue
    
    # If no file found, create sample data
    st.sidebar.warning("📝 Using sample data (run cleaning script for real data)")
    return create_sample_data()

df = load_data()

# ======================
# SIDEBAR - FILTERS
# ======================
st.sidebar.title("🔍 FILTER CONTROLS")

# Show dataset info
st.sidebar.markdown(f"**Dataset:** {len(df)} rows, {len(df.columns)} columns")

# Year filter
if 'year' in df.columns:
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    selected_years = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
    df_filtered = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]
else:
    df_filtered = df
    st.sidebar.warning("No 'year' column found")

# Country filter
if 'country' in df_filtered.columns:
    countries = sorted(df_filtered['country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        countries,
        default=countries[:5] if len(countries) > 5 else countries
    )
    if selected_countries:
        df_filtered = df_filtered[df_filtered['country'].isin(selected_countries)]

# Metric selection
metric_options = ['treatment_success_rate', 'dropout_rate']
if all(col in df_filtered.columns for col in metric_options):
    selected_metric = st.sidebar.radio(
        "Select Metric to Display",
        metric_options,
        format_func=lambda x: x.replace('_', ' ').title()
    )
else:
    selected_metric = 'treatment_success_rate' if 'treatment_success_rate' in df_filtered.columns else df_filtered.columns[0]

# ======================
# MAIN DASHBOARD
# ======================
st.title("🩺 Tuberculosis Treatment Success Dashboard")
st.markdown("**Visualizing completion vs. dropout rates in DOTS clinics worldwide**")

# ======================
# ROW 1: KEY METRICS
# ======================
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_success = df_filtered['treatment_success_rate'].mean() if 'treatment_success_rate' in df_filtered.columns else 0
    st.metric("Average Success Rate", f"{avg_success:.1f}%", 
              delta=f"{(avg_success - 75):+.1f}%" if avg_success > 0 else None)

with col2:
    avg_dropout = df_filtered['dropout_rate'].mean() if 'dropout_rate' in df_filtered.columns else 0
    st.metric("Average Dropout Rate", f"{avg_dropout:.1f}%",
              delta=f"{(avg_dropout - 25):+.1f}%" if avg_dropout > 0 else None,
              delta_color="inverse")

with col3:
    country_count = df_filtered['country'].nunique() if 'country' in df_filtered.columns else 0
    st.metric("Countries", country_count)

with col4:
    year_range = f"{selected_years[0]}-{selected_years[1]}" if 'year' in df.columns else "N/A"
    st.metric("Year Range", year_range)

st.divider()

# ======================
# ROW 2: VISUALIZATION 1 - LINE CHART
# ======================
st.subheader("📈 Treatment Success Trend Over Time")

if 'year' in df_filtered.columns and len(df_filtered) > 0 and selected_metric in df_filtered.columns:
    # Group by year for trend
    yearly_avg = df_filtered.groupby('year')[selected_metric].mean().reset_index()
    
    fig1 = px.line(
        yearly_avg,
        x='year',
        y=selected_metric,
        title=f"Average {selected_metric.replace('_', ' ').title()} Trend ({selected_years[0]}-{selected_years[1]})",
        markers=True,
        line_shape='spline'
    )
    fig1.update_layout(
        xaxis_title="Year",
        yaxis_title=selected_metric.replace('_', ' ').title() + " (%)",
        hovermode='x unified'
    )
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("Select a metric and ensure data has year information to show trends")

# ======================
# ROW 3: VISUALIZATION 2 - BAR CHARTS
# ======================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏆 Top Performing Countries")
    if 'country' in df_filtered.columns and 'treatment_success_rate' in df_filtered.columns:
        top_countries = df_filtered.groupby('country')['treatment_success_rate'].mean().nlargest(10).reset_index()
        fig2 = px.bar(
            top_countries,
            x='treatment_success_rate',
            y='country',
            orientation='h',
            color='treatment_success_rate',
            title="Top 10 Countries by Success Rate",
            color_continuous_scale='Greens',
            labels={'treatment_success_rate': 'Success Rate (%)', 'country': ''}
        )
        fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

with col_right:
    st.subheader("📉 Countries Needing Improvement")
    if 'country' in df_filtered.columns and 'treatment_success_rate' in df_filtered.columns:
        bottom_countries = df_filtered.groupby('country')['treatment_success_rate'].mean().nsmallest(10).reset_index()
        fig3 = px.bar(
            bottom_countries,
            x='treatment_success_rate',
            y='country',
            orientation='h',
            color='treatment_success_rate',
            title="10 Countries with Lowest Success Rates",
            color_continuous_scale='Reds',
            labels={'treatment_success_rate': 'Success Rate (%)', 'country': ''}
        )
        fig3.update_layout(yaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig3, use_container_width=True)

# ======================
# ROW 4: VISUALIZATION 3 - PIE CHART & DATA
# ======================
st.subheader("📊 Distribution Overview")

col1_pie, col2_pie = st.columns(2)

with col1_pie:
    if len(df_filtered) > 0 and 'treatment_success_rate' in df_filtered.columns:
        avg_success = df_filtered['treatment_success_rate'].mean()
        avg_dropout = df_filtered['dropout_rate'].mean() if 'dropout_rate' in df_filtered.columns else 100 - avg_success
        
        fig4 = px.pie(
            names=['Successful Treatments', 'Dropouts'],
            values=[avg_success, avg_dropout],
            title=f"Treatment Outcomes: {selected_years[0]}-{selected_years[1]}",
            color=['Successful Treatments', 'Dropouts'],
            color_discrete_map={'Successful Treatments': '#2E8B57', 'Dropouts': '#DC143C'},
            hole=0.4  # Donut chart
        )
        fig4.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig4, use_container_width=True)

with col2_pie:
    st.subheader("📋 Filtered Data View")
    
    # Add download button
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name=f"tb_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Show data table
    st.dataframe(
        df_filtered.head(15),
        use_container_width=True,
        hide_index=True,
        column_config={
            'treatment_success_rate': st.column_config.ProgressColumn(
                "Success Rate",
                help="Treatment success rate",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            )
        }
    )
    if len(df_filtered) > 15:
        st.caption(f"Showing 15 of {len(df_filtered)} rows")

# ======================
# ADDITIONAL FEATURES
# ======================
st.divider()
st.subheader("🔍 Detailed Analysis")

# Correlation heatmap if we have numeric columns
numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 1:
    st.write("**Correlation Matrix:**")
    corr_matrix = df_filtered[numeric_cols].corr()
    fig5 = px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu',
        title="Correlation Between Variables"
    )
    st.plotly_chart(fig5, use_container_width=True)

# ======================
# FOOTER - DATA SOURCE
# ======================
st.divider()
st.caption(f"""
**Data Source:** World Health Organization (WHO) Global Tuberculosis Programme  
**Dashboard Created By:** Andrea Mikaela Algara | Health Informatics ITE3 Project  
**Last Updated:** {datetime.now().strftime("%B %d, %Y")} | **Total Records:** {len(df_filtered):,}
""")

# ======================
# DEBUG INFO (Hidden by default)
# ======================
with st.sidebar.expander("ℹ️ Debug Info"):
    st.write(f"Data shape: {df.shape}")
    st.write(f"Filtered shape: {df_filtered.shape}")
    st.write("Columns:", list(df.columns))
    st.write(f"Selected metric: {selected_metric}")