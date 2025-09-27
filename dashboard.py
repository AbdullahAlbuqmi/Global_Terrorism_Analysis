import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import re

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Advanced CSV Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS STYLING ====================
st.markdown("""
<style>
    /* Main background styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    
    /* Card-like containers */
    .custom-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        border-left: 5px solid #3498db;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(45deg, #3498db, #2ecc71);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Header styling */
    .main-header {
        color: white;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #3498db, #2c3e50);
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(45deg, #3498db, #2980b9);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    /* Success message */
    .success-msg {
        background: linear-gradient(45deg, #2ecc71, #27ae60);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    
    /* Warning message */
    .warning-msg {
        background: linear-gradient(45deg, #f39c12, #e67e22);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR CONFIGURATION ====================
st.sidebar.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="color: black; margin: 0;">🌐 Data Analysis</h1>
    <p style="color: #ecf0f1; margin: 5px 0 20px 0;">Advanced CSV Analytics</p>
</div>
""", unsafe_allow_html=True)

PAGES = {
    "📤 Upload Data": "upload",
    "👀 Data Preview": "preview", 
    "📊 Data Summary": "summary",
    "📈 Data Analysis": "analysis",
    "🗺️ Map & Heatmap": "map"
}

page = st.sidebar.radio("All Pages", list(PAGES.keys()))

# ==================== MAIN HEADER ====================
st.markdown("""
<div class="main-header">
    <h1>📊 A Data-Driven Analysis of Worldwide Terrorism Trends</h1>
    <p></p>
</div>
""", unsafe_allow_html=True)

# ==================== FILE UPLOAD SECTION ====================
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.file_uploaded = False

if PAGES[page] == "upload":
    st.markdown("""
    <div class="custom-card">
        <h2>📂 Upload Your CSV File</h2>
        <p>Upload a CSV file to begin analyzing your data. The dashboard supports various data analysis features including statistics, visualization, and mapping.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        uploaded_file = st.file_uploader("", type=["csv"], key="file_uploader")
        
        if uploaded_file:
            try:
                st.session_state.df = pd.read_csv(uploaded_file)
                st.session_state.file_uploaded = True
                
                st.markdown(f"""
                <div class="success-msg">
                    <h3>File Uploaded Successfully!</h3>
                    <p><strong>Filename:</strong> {uploaded_file.name}</p>
                    <p><strong>Shape:</strong> {st.session_state.df.shape[0]} rows × {st.session_state.df.shape[1]} columns</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show quick preview
                with st.expander("🔍 Quick Data Preview", expanded=True):
                    st.dataframe(st.session_state.df.head(10))
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

# ==================== DATA PROCESSING ====================
if st.session_state.df is not None:
    df = st.session_state.df
    
    # ==================== DATA PREVIEW PAGE ====================
    if PAGES[page] == "preview":
        st.markdown("""
        <div class="custom-card">
            <h2>Data Preview</h2>
            <p>Explore your dataset with interactive preview options.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.subheader("📋 Data Controls")
            show_rows = st.slider("Number of rows to display", 5, 100, 20)
            show_columns = st.multiselect("Select columns to display", 
                                        df.columns.tolist(), 
                                        default=df.columns.tolist()[:min(8, len(df.columns))])
        
        with col2:
            st.subheader("📊 Data Table")
            if show_columns:
                st.dataframe(df[show_columns].head(show_rows), use_container_width=True)
            else:
                st.warning("Please select at least one column to display.")
        
        # Data information
        with st.expander("🔍 Dataset Information", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Rows", df.shape[0])
            with col2:
                st.metric("Total Columns", df.shape[1])
            with col3:
                st.metric("Missing Values", df.isnull().sum().sum())
            
            # Column types
            st.subheader("Column Data Types")
            dtype_df = pd.DataFrame({
                'Column': df.columns,
                'Data Type': df.dtypes,
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum()
            })
            st.dataframe(dtype_df, use_container_width=True)

    # ==================== DATA SUMMARY PAGE ====================
    elif PAGES[page] == "summary":
        st.markdown("""
        <div class="custom-card">
            <h2>📊 Comprehensive Data Summary</h2>
            <p>Detailed statistical analysis and dataset overview.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key Metrics
        st.subheader("📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", f"{df.shape[0]:,}")
        with col2:
            st.metric("Total Features", df.shape[1])
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        with col4:
            st.metric("Duplicate Rows", df.duplicated().sum())
        
        # Statistical Summary
        st.subheader("📋 Statistical Summary")
        st.dataframe(df.describe(), use_container_width=True)
        
        # Detailed Data Description
        st.subheader("🔍 Detailed Data Description")
        
        # Define numerical and categorical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Numerical columns
        if numerical_cols:
            st.write("#### Numerical Columns Analysis")
            for col in numerical_cols:
                with st.expander(f"📐 {col} - Numerical Analysis"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Basic Statistics:**")
                        stats = df[col].describe()
                        st.write(stats)
                    with col2:
                        st.write(f"**Additional Info:**")
                        st.write(f"Skewness: {df[col].skew():.4f}")
                        st.write(f"Kurtosis: {df[col].kurtosis():.4f}")
                        st.write(f"Variance: {df[col].var():.4f}")
        
        # Categorical columns
        if categorical_cols:
            st.write("#### Categorical Columns Analysis")
            for col in categorical_cols:
                with st.expander(f"📊 {col} - Categorical Analysis"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Value Counts (Top 10):**")
                        value_counts = df[col].value_counts().head(10)
                        st.write(value_counts)
                    with col2:
                        st.write(f"**Unique Values:** {df[col].nunique()}")
                        st.write(f"**Most Frequent:** {df[col].mode().iloc[0] if not df[col].mode().empty else 'N/A'}")
        
        # Missing Values Analysis
        st.subheader("Missing Values Analysis")
        missing_data = df.isnull().sum()
        missing_percent = (missing_data / len(df)) * 100
        
        missing_df = pd.DataFrame({
            'Column': df.columns,
            'Missing Values': missing_data,
            'Missing Percentage': missing_percent
        }).sort_values('Missing Values', ascending=False)
        
        st.dataframe(missing_df[missing_df['Missing Values'] > 0], use_container_width=True)
        
        if missing_df['Missing Values'].sum() == 0:
            st.success("No missing values found in the dataset!")

    # ==================== DATA ANALYSIS PAGE ====================
    elif PAGES[page] == "analysis":
        st.markdown("""
        <div class="custom-card">
            <h2>📈 Advanced Data Analysis</h2>
            <p>Interactive visualizations and correlation analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Define numerical and categorical columns for this page
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Visualization Type Selection
        st.subheader("Select Visualization Type")
        viz_type = st.selectbox("Choose visualization type", 
                               ["Histogram", "Scatter Plot", "Bar Chart", "Pie Chart", 
                                "Box Plot", "Line Chart", "Heatmap", "Violin Plot"])
        
        # Main visualization area
        if viz_type == "Histogram":
            st.subheader("Histogram")
            col1, col2 = st.columns(2)
            with col1:
                if numerical_cols:
                    selected_col = st.selectbox("Select numerical column", numerical_cols, key="hist_num")
                    if selected_col:
                        fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col}",
                                         nbins=50, color_discrete_sequence=['#3498db'])
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("ℹ️ No numerical columns available for histogram.")
            
            with col2:
                if categorical_cols:
                    selected_cat_col = st.selectbox("Select categorical column for histogram", categorical_cols, key="hist_cat")
                    if selected_cat_col:
                        value_counts = df[selected_cat_col].value_counts().head(20)
                        fig = px.bar(x=value_counts.index, y=value_counts.values, 
                                   title=f"Value Counts for {selected_cat_col}",
                                   color=value_counts.values, color_continuous_scale='viridis')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("ℹ️ No categorical columns available for bar chart.")
        
        elif viz_type == "Scatter Plot":
            st.subheader("Scatter Plot")
            if len(numerical_cols) >= 2:
                col1, col2, col3 = st.columns(3)
                with col1:
                    x_col = st.selectbox("X-axis", numerical_cols, key="scatter_x")
                with col2:
                    y_col = st.selectbox("Y-axis", numerical_cols, key="scatter_y")
                with col3:
                    color_col = st.selectbox("Color by", ["None"] + numerical_cols + categorical_cols, key="scatter_color")
                
                if x_col and y_col:
                    if color_col != "None":
                        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, 
                                       title=f"Scatter Plot: {x_col} vs {y_col}")
                    else:
                        fig = px.scatter(df, x=x_col, y=y_col, title=f"Scatter Plot: {x_col} vs {y_col}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Need at least 2 numerical columns for scatter plot.")
        
        elif viz_type == "Bar Chart":
            st.subheader("Bar Chart")
            if categorical_cols:
                col1, col2 = st.columns(2)
                with col1:
                    cat_col = st.selectbox("Select categorical column", categorical_cols, key="bar_cat")
                with col2:
                    if numerical_cols:
                        num_col = st.selectbox("Select numerical column (for aggregation)", ["Count"] + numerical_cols, key="bar_num")
                
                if cat_col:
                    if num_col == "Count":
                        value_counts = df[cat_col].value_counts().head(20)
                        fig = px.bar(x=value_counts.index, y=value_counts.values, 
                                   title=f"Bar Chart of {cat_col}",
                                   labels={'x': cat_col, 'y': 'Count'})
                    else:
                        agg_data = df.groupby(cat_col)[num_col].mean().sort_values(ascending=False).head(20)
                        fig = px.bar(x=agg_data.index, y=agg_data.values,
                                   title=f"Average {num_col} by {cat_col}",
                                   labels={'x': cat_col, 'y': f'Average {num_col}'})
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(" No categorical columns available for bar chart.")
        
        elif viz_type == "Pie Chart":
            st.subheader("Pie Chart")
            if categorical_cols:
                pie_col = st.selectbox("Select categorical column", categorical_cols, key="pie_cat")
                if pie_col:
                    value_counts = df[pie_col].value_counts().head(10)
                    fig = px.pie(values=value_counts.values, names=value_counts.index,
                               title=f"Pie Chart of {pie_col}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No categorical columns available for pie chart.")
        
        elif viz_type == "Box Plot":
            st.subheader("Box Plot")
            if numerical_cols:
                col1, col2 = st.columns(2)
                with col1:
                    num_col = st.selectbox("Select numerical column", numerical_cols, key="box_num")
                with col2:
                    cat_col = st.selectbox("Group by (optional)", ["None"] + categorical_cols, key="box_cat")
                
                if num_col:
                    if cat_col != "None":
                        fig = px.box(df, x=cat_col, y=num_col, title=f"Box Plot of {num_col} by {cat_col}")
                    else:
                        fig = px.box(df, y=num_col, title=f"Box Plot of {num_col}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numerical columns available for box plot.")
        
        elif viz_type == "Line Chart":
            st.subheader("Line Chart")
            if len(numerical_cols) >= 1:
                col1, col2 = st.columns(2)
                with col1:
                    num_col = st.selectbox("Select numerical column", numerical_cols, key="line_num")
                with col2:
                    if categorical_cols:
                        group_col = st.selectbox("Group by", ["None"] + categorical_cols, key="line_group")
                
                if num_col:
                    if group_col != "None":
                        fig = px.line(df, x=df.index, y=num_col, color=group_col,
                                    title=f"Line Chart of {num_col} grouped by {group_col}")
                    else:
                        fig = px.line(df, x=df.index, y=num_col, title=f"Line Chart of {num_col}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹNo numerical columns available for line chart.")
        
        elif viz_type == "Heatmap":
            st.subheader("Correlation Heatmap")
            if len(numerical_cols) > 1:
                corr_matrix = df[numerical_cols].corr()
                fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                              color_continuous_scale='RdBu_r', title="Correlation Matrix Heatmap")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough numerical columns for correlation heatmap.")
        
        elif viz_type == "Violin Plot":
            st.subheader("🎻 Violin Plot")
            if numerical_cols and categorical_cols:
                col1, col2 = st.columns(2)
                with col1:
                    num_col = st.selectbox("Select numerical column", numerical_cols, key="violin_num")
                with col2:
                    cat_col = st.selectbox("Select categorical column", categorical_cols, key="violin_cat")
                
                if num_col and cat_col:
                    fig = px.violin(df, x=cat_col, y=num_col, title=f"Violin Plot of {num_col} by {cat_col}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(" Need both numerical and categorical columns for violin plot.")
                
         # ==================== MAP & HEATMAP PAGE ====================
    elif PAGES[page] == "map":
        st.markdown("""
        <div class="custom-card">
            <h2>🗺️ Map & Heatmap</h2>
            <p>Interactive geographic scatter plot and heatmap using Plotly.</p>
        </div>
        """, unsafe_allow_html=True)

        # ✅ Check for latitude/longitude columns
        lat_col, lon_col = None, None
        for c in df.columns:
            if c.lower() in ["latitude", "lat"]:
                lat_col = c
            if c.lower() in ["longitude", "long", "lng", "lon"]:
                lon_col = c

        if lat_col and lon_col:
            df_map = df.copy()
            df_map[lat_col] = pd.to_numeric(df_map[lat_col], errors="coerce")
            df_map[lon_col] = pd.to_numeric(df_map[lon_col], errors="coerce")
            df_map = df_map.dropna(subset=[lat_col, lon_col])

            if not df_map.empty:
                # --- Scatter Map ---
                st.subheader("Scatter Map")
                fig_scatter = px.scatter_geo(
                    df_map,
                    lat=lat_col,
                    lon=lon_col,
                    hover_data=[c for c in df_map.columns if c not in [lat_col, lon_col]],
                    projection="natural earth",
                    opacity=0.7
                )
                fig_scatter.update_traces(marker=dict(size=5, color="red"))
                st.plotly_chart(fig_scatter, use_container_width=True)

                # --- Heatmap ---
                st.subheader("Heatmap")
                fig_heat = px.density_mapbox(
                    df_map,
                    lat=lat_col,
                    lon=lon_col,
                    radius=10,
                    center=dict(lat=df_map[lat_col].mean(),
                                lon=df_map[lon_col].mean()),
                    zoom=2,
                    mapbox_style="carto-positron"
                )
                st.plotly_chart(fig_heat, use_container_width=True)
            else:
                st.error(" No valid latitude/longitude found in your data.")
        else:
            st.error("⚠️ Data must contain latitude/longitude columns.")
            st.write("Example column names: `latitude`, `longitude`, `lat`, `long`, `lon`")



else:
    if PAGES[page] != "upload":
        st.markdown("""
        <div class="warning-msg">
            <h3> Data Required</h3>
            <p>Please upload a CSV file first to access the analysis features.</p>
            <p>Go to <strong>Upload Data</strong> in the sidebar to get started.</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    <p></p>
</div>
""", unsafe_allow_html=True)