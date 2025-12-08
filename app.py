"""
☄️ Meteorite Landing System - Dashboard
Tema: Space/Meteor dengan Globe 3D Interaktif
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import os

# Load from .env for local, or st.secrets for Streamlit Cloud
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Page config
st.set_page_config(
    page_title="☄️ Meteorite Explorer",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - METEOR THEME
# ============================================================================
st.markdown("""
<style>
    /* Main background - space theme */
    .stApp {
        background: linear-gradient(180deg, #0a0a1a 0%, #1a1a3a 50%, #0d0d2b 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12122a 0%, #1e1e4a 100%);
        border-right: 2px solid #ff6b35;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0ff;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ff6b35 !important;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a3a 0%, #2a2a5a 100%);
        border: 1px solid #ff6b35;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 0 20px rgba(255, 107, 53, 0.2);
    }
    
    [data-testid="stMetricValue"] {
        color: #ff6b35 !important;
        font-size: 2rem !important;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0a0ff !important;
    }
    
    /* Divider */
    hr {
        border-color: #ff6b35 !important;
        box-shadow: 0 0 10px rgba(255, 107, 53, 0.3);
    }
    
    /* Text */
    .stMarkdown, p, span {
        color: #d0d0ff;
    }
    
    /* Dataframe */
    .stDataFrame {
        border: 1px solid #ff6b35;
        border-radius: 10px;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #1a1a3a;
        border-color: #ff6b35;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: transparent;
    }
    
    /* Info box */
    .stAlert {
        background-color: rgba(255, 107, 53, 0.1);
        border: 1px solid #ff6b35;
        color: #e0e0ff;
    }
    
    /* Meteor animation */
    @keyframes meteor {
        0% { transform: translateX(-100px) translateY(-100px); opacity: 1; }
        100% { transform: translateX(100vw) translateY(100vh); opacity: 0; }
    }
    
    .meteor-header {
        background: linear-gradient(90deg, #ff6b35, #ff8c5a, #ffad7a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 10px #ff6b35, 0 0 20px #ff6b35; }
        to { text-shadow: 0 0 20px #ff8c5a, 0 0 30px #ff8c5a, 0 0 40px #ffad7a; }
    }
    
    /* Stars background effect */
    .stars {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, white, transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), transparent),
            radial-gradient(1px 1px at 90px 40px, white, transparent),
            radial-gradient(2px 2px at 160px 120px, rgba(255,255,255,0.9), transparent);
        background-repeat: repeat;
        background-size: 200px 200px;
        opacity: 0.3;
        z-index: -1;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    # Load from .env file (prioritas utama)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    # Fallback hardcoded jika masih None
    if not url:
        url = "https://leyohmljepfigqgguwhc.supabase.co"
    if not key:
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxleW9obWxqZXBmaWdxZ2d1d2hjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0NTM5ODIsImV4cCI6MjA4MDAyOTk4Mn0.yuwg-Q-1H9gsqgczYXUOSC-0SqShNPsQa_jwzj-ALLw"
    
    return create_client(url, key)

supabase = init_supabase()

@st.cache_data(ttl=300)
def fetch_data(table_name, limit=None):
    try:
        query = supabase.table(table_name).select("*")
        if limit:
            query = query.limit(limit)
        response = query.execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_table_count(table_name):
    """Get total count of records in a table"""
    try:
        # Use count query instead of fetching all data
        response = supabase.table(table_name).select("*", count="exact").execute()
        return response.count
    except Exception as e:
        st.error(f"Error counting {table_name}: {e}")
        return 0

# Plotly theme for meteor
def apply_meteor_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(26, 26, 58, 0.8)',
        plot_bgcolor='rgba(26, 26, 58, 0.8)',
        font=dict(color='#d0d0ff'),
        title_text='',  # Hilangkan title undefined
        title_font=dict(color='#ff6b35'),
        legend=dict(bgcolor='rgba(26, 26, 58, 0.8)', font=dict(color='#d0d0ff')),
        xaxis=dict(gridcolor='rgba(255, 107, 53, 0.2)', tickfont=dict(color='#a0a0ff')),
        yaxis=dict(gridcolor='rgba(255, 107, 53, 0.2)', tickfont=dict(color='#a0a0ff'))
    )
    return fig

# Sidebar
st.sidebar.markdown("""
<h1 style='text-align: center; 
           color: #ff6b35; 
           font-size: 1.8rem; 
           font-weight: bold; 
           margin-top: -20px;
           margin-bottom: 10px;
           text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);'>
    ☄️☄️☄️<br>METEORITE<br>EXPLORER
</h1>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "🚀 Navigation",
    ["🏠 Home", "☄️ Meteorites", "🔬 Classifications", "🏛️ Museums", "📚 Research", "🌍 Globe Map"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛸 Quick Stats")
meteorites_count = get_table_count("meteorites")
st.sidebar.metric("Total Meteorites", f"{meteorites_count:,}")


# ============================================================================
# PAGE: HOME
# ============================================================================
if page == "🏠 Home":
    st.markdown('<p class="meteor-header">☄️ METEORITE EXPLORER</p>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #a0a0ff;'>Explore the Universe of Fallen Stars</h3>", unsafe_allow_html=True)
    
    meteorites = fetch_data("meteorites")
    classifications = fetch_data("meteorite_classifications")
    museums = fetch_data("museums")
    specimens = fetch_data("meteorite_specimens")
    studies = fetch_data("research_studies")
    
    st.markdown("---")
    
    # Animated metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        meteorites_total = get_table_count("meteorites")
        st.metric("☄️ Meteorites", f"{meteorites_total:,}")
    with col2:
        st.metric("🔬 Classifications", len(classifications))
    with col3:
        st.metric("🏛️ Museums", len(museums))
    with col4:
        specimens_total = get_table_count("meteorite_specimens")
        st.metric("💎 Specimens", f"{specimens_total:,}")
    with col5:
        studies_total = get_table_count("research_studies")
        st.metric("📚 Studies", f"{studies_total:,}")
    
    st.markdown("---")
    
    # Main charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌌 Meteorite Categories")
        if not meteorites.empty and not classifications.empty:
            merged = meteorites.merge(classifications, on="classification_id", how="left")
            if "category" in merged.columns:
                # Filter out null/NaN values
                cat_counts = merged["category"].dropna().value_counts().reset_index()
                cat_counts.columns = ["Category", "Count"]
                # Replace any remaining null with "Unknown"
                cat_counts["Category"] = cat_counts["Category"].fillna("Unknown")
                fig = px.pie(cat_counts, values="Count", names="Category", hole=0.5,
                           color_discrete_sequence=px.colors.sequential.Oranges_r)
                fig = apply_meteor_theme(fig)
                fig.update_traces(textfont_color='white', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🔥 Fall vs Found")
        fall_types = fetch_data("fall_types")
        if not meteorites.empty and not fall_types.empty:
            merged = meteorites.merge(fall_types, on="fall_type_id", how="left")
            if "fall_type_name" in merged.columns:
                # Filter out null/NaN values
                fall_counts = merged["fall_type_name"].dropna().value_counts().reset_index()
                fall_counts.columns = ["Type", "Count"]
                # Replace any remaining null with "Unknown"
                fall_counts["Type"] = fall_counts["Type"].fillna("Unknown")
                fig = px.pie(fall_counts, values="Count", names="Type", hole=0.5,
                           color_discrete_sequence=["#ff6b35", "#4ecdc4"])
                fig = apply_meteor_theme(fig)
                fig.update_traces(textfont_color='white', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
    
    # Timeline
    st.markdown("### 📅 Discovery Timeline")
    if not meteorites.empty and "year_discovered" in meteorites.columns:
        yearly = meteorites[meteorites["year_discovered"] > 1800].groupby("year_discovered").size().reset_index(name="count")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly["year_discovered"], y=yearly["count"],
            mode='lines', fill='tozeroy',
            line=dict(color='#ff6b35', width=2),
            fillcolor='rgba(255, 107, 53, 0.3)'
        ))
        fig = apply_meteor_theme(fig)
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Discoveries",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Mass stats
    st.markdown("### ⚖️ Mass Statistics")
    if not meteorites.empty and "mass_gram" in meteorites.columns:
        valid_mass = meteorites[meteorites["mass_gram"].notna() & (meteorites["mass_gram"] > 0)]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌍 Total Mass", f"{valid_mass['mass_gram'].sum() / 1000000:,.1f} tons")
        with col2:
            st.metric("📊 Average", f"{valid_mass['mass_gram'].mean():,.0f} g")
        with col3:
            st.metric("🏆 Largest", f"{valid_mass['mass_gram'].max() / 1000:,.0f} kg")
        with col4:
            st.metric("🔬 Smallest", f"{valid_mass['mass_gram'].min():.4f} g")

# ============================================================================
# PAGE: METEORITES
# ============================================================================
elif page == "☄️ Meteorites":
    st.markdown("# ☄️ Meteorite Database")
    
    meteorites = fetch_data("meteorites")
    classifications = fetch_data("meteorite_classifications")
    fall_types = fetch_data("fall_types")
    
    # Filters in sidebar
    st.sidebar.markdown("### 🎯 Filters")
    
    if not classifications.empty:
        categories = ["All"] + sorted(classifications["category"].dropna().unique().tolist())
        selected_cat = st.sidebar.selectbox("Category", categories)
    
    if not fall_types.empty:
        falls = ["All"] + fall_types["fall_type_name"].tolist()
        selected_fall = st.sidebar.selectbox("Fall Type", falls)
    
    year_range = st.sidebar.slider("Year Range", 800, 2023, (1900, 2023))
    
    # Apply filters
    filtered = meteorites.copy()
    if not meteorites.empty:
        if "year_discovered" in filtered.columns:
            filtered = filtered[(filtered["year_discovered"] >= year_range[0]) & 
                              (filtered["year_discovered"] <= year_range[1])]
        
        if selected_cat != "All" and not classifications.empty:
            cat_ids = classifications[classifications["category"] == selected_cat]["classification_id"].tolist()
            filtered = filtered[filtered["classification_id"].isin(cat_ids)]
        
        if selected_fall != "All" and not fall_types.empty:
            fall_id = fall_types[fall_types["fall_type_name"] == selected_fall]["fall_type_id"].values[0]
            filtered = filtered[filtered["fall_type_id"] == fall_id]
    
    st.metric("🎯 Filtered Results", f"{len(filtered):,}")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 By Classification Group")
        if not filtered.empty and not classifications.empty:
            merged = filtered.merge(classifications, on="classification_id", how="left")
            if "class_group" in merged.columns:
                group_counts = merged["class_group"].value_counts().head(10).reset_index()
                group_counts.columns = ["Group", "Count"]
                fig = px.bar(group_counts, x="Count", y="Group", orientation='h',
                           color="Count", color_continuous_scale="Oranges")
                fig = apply_meteor_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⚖️ Mass Distribution")
        if not filtered.empty and "mass_gram" in filtered.columns:
            valid_mass = filtered[filtered["mass_gram"].notna() & (filtered["mass_gram"] > 0)]
            
            if len(valid_mass) > 0:
                # Statistik ringkas
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("📊 Total", f"{len(valid_mass):,}")
                with col_b:
                    st.metric("⚖️ Rata-rata", f"{valid_mass['mass_gram'].mean()/1000:,.1f} kg")
                with col_c:
                    st.metric("🏆 Terberat", f"{valid_mass['mass_gram'].max()/1000:,.0f} kg")
                
                # Box plot dengan log scale - lebih jelas menunjukkan distribusi
                fig = go.Figure()
                fig.add_trace(go.Box(
                    y=valid_mass['mass_gram'],
                    name='Mass Distribution',
                    marker=dict(color='#ff6b35'),
                    boxmean='sd',  # Tampilkan mean dan std deviation
                    fillcolor='rgba(255, 107, 53, 0.5)',
                    line=dict(color='#ff6b35', width=2)
                ))
                
                fig = apply_meteor_theme(fig)
                fig.update_layout(
                    yaxis_title="Mass (gram) - Log Scale",
                    yaxis_type="log",
                    showlegend=False,
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Tidak ada data massa")
    
    # Top heaviest
    st.markdown("### 🏆 Top 15 Heaviest Meteorites")
    if not filtered.empty and "mass_gram" in filtered.columns:
        top15 = filtered.nlargest(15, "mass_gram")[["name", "mass_gram", "year_discovered"]]
        top15["mass_tons"] = top15["mass_gram"] / 1000000
        fig = px.bar(top15, x="name", y="mass_tons", color="mass_tons",
                    color_continuous_scale="YlOrRd",
                    labels={"mass_tons": "Mass (tons)", "name": ""})
        fig = apply_meteor_theme(fig)
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown("### 📋 Data Table")
    if not filtered.empty:
        display_df = filtered[["meteorite_id", "name", "mass_gram", "year_discovered"]].head(100)
        st.dataframe(display_df, use_container_width=True, height=400)


# ============================================================================
# PAGE: CLASSIFICATIONS
# ============================================================================
elif page == "🔬 Classifications":
    st.markdown("# 🔬 Meteorite Classifications")
    
    classifications = fetch_data("meteorite_classifications")
    meteorites = fetch_data("meteorites")
    
    if not classifications.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Total Classes", len(classifications))
        with col2:
            st.metric("📂 Groups", classifications["class_group"].nunique())
        with col3:
            st.metric("🏷️ Categories", classifications["category"].nunique())
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌌 By Category")
            cat_counts = classifications["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            fig = px.pie(cat_counts, values="Count", names="Category", hole=0.5,
                       color_discrete_sequence=px.colors.sequential.Plasma)
            fig = apply_meteor_theme(fig)
            fig.update_traces(textfont_color='white')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Top Class Groups")
            group_counts = classifications["class_group"].value_counts().head(12).reset_index()
            group_counts.columns = ["Group", "Count"]
            fig = px.bar(group_counts, x="Count", y="Group", orientation='h',
                       color="Count", color_continuous_scale="Oranges")
            fig = apply_meteor_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        
        # Treemap
        st.markdown("### 🗺️ Classification Hierarchy")
        fig = px.treemap(classifications, path=['category', 'class_group'], 
                        color_discrete_sequence=px.colors.sequential.Oranges)
        fig = apply_meteor_theme(fig)
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: MUSEUMS
# ============================================================================
elif page == "🏛️ Museums":
    st.markdown("# 🏛️ Museums & Collections")
    
    museums = fetch_data("museums")
    specimens = fetch_data("meteorite_specimens")
    countries = fetch_data("countries")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏛️ Museums", len(museums))
    with col2:
        specimens_total = get_table_count("meteorite_specimens")
        st.metric("💎 Specimens", f"{specimens_total:,}")
    with col3:
        if not specimens.empty and "specimen_mass_gram" in specimens.columns:
            total = specimens["specimen_mass_gram"].sum()
            st.metric("⚖️ Total Mass", f"{total/1000:,.1f} kg")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Specimens by Museum")
        if not specimens.empty and not museums.empty:
            merged = specimens.merge(museums, on="museum_id", how="left")
            counts = merged["museum_name"].value_counts().reset_index()
            counts.columns = ["Museum", "Specimens"]
            fig = px.bar(counts, x="Specimens", y="Museum", orientation='h',
                       color="Specimens", color_continuous_scale="Oranges")
            fig = apply_meteor_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 💎 Specimen Types")
        if not specimens.empty and "specimen_type" in specimens.columns:
            type_counts = specimens["specimen_type"].value_counts().reset_index()
            type_counts.columns = ["Type", "Count"]
            fig = px.pie(type_counts, values="Count", names="Type", hole=0.5,
                       color_discrete_sequence=px.colors.sequential.Sunset)
            fig = apply_meteor_theme(fig)
            fig.update_traces(textfont_color='white')
            st.plotly_chart(fig, use_container_width=True)
    
    # Condition gauge
    st.markdown("### 📈 Specimen Conditions")
    if not specimens.empty and "condition" in specimens.columns:
        cond_counts = specimens["condition"].value_counts().reset_index()
        cond_counts.columns = ["Condition", "Count"]
        colors = {"Excellent": "#2ecc71", "Good": "#3498db", "Fair": "#f39c12", "Poor": "#e74c3c"}
        fig = px.bar(cond_counts, x="Condition", y="Count", 
                    color="Condition", color_discrete_map=colors)
        fig = apply_meteor_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    # Museum cards
    st.markdown("### 🏛️ Museum Directory")
    if not museums.empty:
        for _, museum in museums.iterrows():
            with st.expander(f"🏛️ {museum['museum_name']}"):
                st.write(f"📍 **City:** {museum.get('city', 'N/A')}")
                st.write(f"📝 **Description:** {museum.get('description', 'N/A')}")

# ============================================================================
# PAGE: RESEARCH
# ============================================================================
elif page == "📚 Research":
    st.markdown("# 📚 Research & Expeditions")
    
    studies = fetch_data("research_studies")
    researchers = fetch_data("researchers")
    expeditions = fetch_data("discovery_expeditions")
    discoveries = fetch_data("meteorite_discoveries")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        studies_total = get_table_count("research_studies")
        st.metric("📚 Studies", f"{studies_total:,}")
    with col2:
        st.metric("👨‍🔬 Researchers", len(researchers))
    with col3:
        st.metric("🏕️ Expeditions", len(expeditions))
    with col4:
        discoveries_total = get_table_count("meteorite_discoveries")
        st.metric("🔍 Discoveries", f"{discoveries_total:,}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Study Status")
        if not studies.empty and "status" in studies.columns:
            status_counts = studies["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            colors = {"Published": "#2ecc71", "In Review": "#f39c12", "Completed": "#3498db", "Ongoing": "#9b59b6"}
            fig = px.pie(status_counts, values="Count", names="Status", hole=0.5,
                       color="Status", color_discrete_map=colors)
            fig = apply_meteor_theme(fig)
            fig.update_traces(textfont_color='white')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📅 Publications Timeline")
        if not studies.empty and "publication_year" in studies.columns:
            yearly = studies.groupby("publication_year").size().reset_index(name="count")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=yearly["publication_year"], y=yearly["count"],
                mode='lines+markers', line=dict(color='#ff6b35', width=3),
                marker=dict(size=8, color='#ff6b35')
            ))
            fig = apply_meteor_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
    
    # Top journals
    st.markdown("### 📰 Top Journals")
    if not studies.empty and "journal" in studies.columns:
        journal_counts = studies["journal"].value_counts().reset_index()
        journal_counts.columns = ["Journal", "Publications"]
        fig = px.bar(journal_counts, x="Publications", y="Journal", orientation='h',
                   color="Publications", color_continuous_scale="Oranges")
        fig = apply_meteor_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    # ===== BAGIAN BARU: METEORITE DISCOVERIES =====
    st.markdown("---")
    st.markdown("## 🔍 Meteorite Discoveries Analysis")
    st.markdown("##### Analisis Penemuan Meteorit dari Ekspedisi")
    
    if not discoveries.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔬 Discovery Methods")
            if "discovery_method" in discoveries.columns:
                method_counts = discoveries["discovery_method"].value_counts().reset_index()
                method_counts.columns = ["Method", "Count"]
                fig = px.pie(method_counts, values="Count", names="Method", hole=0.4,
                           color_discrete_sequence=px.colors.sequential.Sunset)
                fig = apply_meteor_theme(fig)
                fig.update_traces(textfont_color='white', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📍 Find Context")
            if "find_context" in discoveries.columns:
                context_counts = discoveries["find_context"].value_counts().reset_index()
                context_counts.columns = ["Context", "Count"]
                fig = px.bar(context_counts, x="Count", y="Context", orientation='h',
                           color="Count", color_continuous_scale="Plasma")
                fig = apply_meteor_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
        
        # Discovery Timeline
        st.markdown("### 📅 Discovery Timeline")
        if "discovery_date" in discoveries.columns:
            # Convert to datetime and extract year
            discoveries_timeline = discoveries.copy()
            discoveries_timeline["discovery_date"] = pd.to_datetime(discoveries_timeline["discovery_date"], errors='coerce')
            discoveries_timeline["year"] = discoveries_timeline["discovery_date"].dt.year
            
            # Filter valid years
            valid_years = discoveries_timeline[discoveries_timeline["year"].notna()]
            
            if not valid_years.empty:
                yearly_discoveries = valid_years.groupby("year").size().reset_index(name="count")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=yearly_discoveries["year"], 
                    y=yearly_discoveries["count"],
                    mode='lines+markers',
                    line=dict(color='#4ecdc4', width=3),
                    marker=dict(size=8, color='#4ecdc4'),
                    fill='tozeroy',
                    fillcolor='rgba(78, 205, 196, 0.2)'
                ))
                fig = apply_meteor_theme(fig)
                fig.update_layout(
                    xaxis_title="Tahun",
                    yaxis_title="Jumlah Penemuan",
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Discoveries per Expedition
        st.markdown("### 🏕️ Top Expeditions by Discoveries")
        if not expeditions.empty:
            # Merge discoveries with expeditions
            exp_disc = discoveries.merge(expeditions, on="expedition_id", how="left")
            if "expedition_name" in exp_disc.columns:
                exp_counts = exp_disc["expedition_name"].value_counts().head(10).reset_index()
                exp_counts.columns = ["Expedition", "Discoveries"]
                
                fig = px.bar(exp_counts, x="Discoveries", y="Expedition", orientation='h',
                           color="Discoveries", 
                           color_continuous_scale="Oranges",
                           labels={"Expedition": "Nama Ekspedisi", "Discoveries": "Jumlah Penemuan"})
                fig = apply_meteor_theme(fig)
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Data meteorite discoveries belum tersedia")
    
    st.markdown("---")
    
    # Researchers
    st.markdown("### 👨‍🔬 Research Team")
    if not researchers.empty:
        cols = st.columns(3)
        for i, (_, r) in enumerate(researchers.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a1a3a, #2a2a5a); 
                            padding: 15px; border-radius: 10px; margin: 5px 0;
                            border: 1px solid #ff6b35;">
                    <h4 style="color: #ff6b35; margin: 0;">{r['name']}</h4>
                    <p style="color: #a0a0ff; margin: 5px 0;">🔬 {r.get('specialization', 'N/A')}</p>
                    <p style="color: #808080; margin: 0; font-size: 0.8em;">🏫 {r.get('institution', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
    


# ============================================================================
# PAGE: GLOBE MAP (3D Interactive)
# ============================================================================
elif page == "🌍 Globe Map":
    st.markdown("# 🌍 Interactive Globe Map")
    st.markdown("### Explore Meteorite Landing Sites Around the World")
    
    locations = fetch_data("locations")
    meteorites = fetch_data("meteorites")
    
    if not locations.empty and not meteorites.empty:
        # Merge data
        merged = meteorites.merge(locations, on="location_id", how="left")
        valid_coords = merged.dropna(subset=["latitude", "longitude"])
        
        # Info total data available
        total_available = len(valid_coords)
        st.success(f"📊 Total data dengan koordinat: **{total_available:,} lokasi meteorit**")
        
        # Sample size slider dengan penjelasan
        col1, col2 = st.columns([3, 1])
        with col1:
            sample_size = st.slider(
                "🎯 Jumlah Lokasi yang Ditampilkan", 
                min_value=100, 
                max_value=min(5000, total_available),  # Max 5000 atau total data (yang lebih kecil)
                value=min(1000, total_available),  # Default 1000 atau total data
                step=100,
                help="Pilih berapa banyak lokasi meteorit yang ingin ditampilkan di globe. Semakin banyak = semakin lambat."
            )
        with col2:
            st.metric("Menampilkan", f"{sample_size:,}")
        
        # Sample data
        if len(valid_coords) > sample_size:
            sample = valid_coords.sample(sample_size, random_state=42)
        else:
            sample = valid_coords
        
        # Header di luar globe
        st.markdown("### ☄️ Meteorite Landing Sites - 3D Globe")
        
        # Prepare data untuk hover dengan informasi lengkap
        sample_display = sample.copy()
        
        # Format massa untuk display
        sample_display['mass_display'] = sample_display['mass_gram'].apply(
            lambda x: f"{x:,.2f} g ({x/1000:,.2f} kg)" if pd.notna(x) and x > 0 else "Unknown"
        )
        
        # Format tahun
        sample_display['year_display'] = sample_display['year_discovered'].apply(
            lambda x: str(int(x)) if pd.notna(x) else "Unknown"
        )
        
        # Siapkan customdata untuk hover (multiple columns)
        customdata = sample_display[[
            'name', 
            'mass_display', 
            'year_display',
            'latitude',
            'longitude'
        ]].values
        
        # 3D Globe using Plotly
        fig = go.Figure()
        
        # Add meteorite markers dengan emoji ☄️ dan hover detail
        fig.add_trace(go.Scattergeo(
            lon=sample["longitude"],
            lat=sample["latitude"],
            text=["☄️"] * len(sample),  # Emoji meteor sebagai label
            customdata=customdata,  # Data lengkap untuk hover
            hovertemplate=(
                "<b style='font-size:16px; color:#ff6b35;'>☄️ %{customdata[0]}</b><br>"
                "<br>"
                "⚖️ <b>Massa:</b> %{customdata[1]}<br>"
                "📅 <b>Tahun:</b> %{customdata[2]}<br>"
                "📍 <b>Koordinat:</b><br>"
                "   Lat: %{customdata[3]:.2f}°<br>"
                "   Lon: %{customdata[4]:.2f}°"
                "<extra></extra>"
            ),
            mode='text',
            textfont=dict(
                size=14,
                color='#ff6b35'
            ),
            showlegend=False
        ))
        
        # Globe layout (tanpa title di dalam)
        fig.update_layout(
            geo=dict(
                projection_type='orthographic',  # 3D Globe!
                showland=True,
                landcolor='rgb(40, 40, 80)',
                showocean=True,
                oceancolor='rgb(20, 20, 50)',
                showlakes=True,
                lakecolor='rgb(30, 30, 60)',
                showcountries=True,
                countrycolor='rgb(100, 100, 150)',
                showcoastlines=True,
                coastlinecolor='rgb(80, 80, 120)',
                bgcolor='rgba(10, 10, 26, 1)',
                projection_rotation=dict(lon=0, lat=20, roll=0)
            ),
            paper_bgcolor='rgba(10, 10, 26, 1)',
            plot_bgcolor='rgba(10, 10, 26, 1)',
            height=700,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Instruksi interaksi di bawah globe
        st.markdown("""
        <p style="text-align: center; color: #a0a0ff;">
        🖱️ <b>Drag to rotate</b> | 🔍 <b>Scroll to zoom</b> | 👆 <b>Hover ☄️ untuk detail</b>
        </p>
        """, unsafe_allow_html=True)
        
        
        st.markdown("---")
        
        # Statistics by terrain
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏔️ By Terrain Type")
            if "terrain_type" in locations.columns:
                terrain_counts = locations["terrain_type"].value_counts().reset_index()
                terrain_counts.columns = ["Terrain", "Count"]
                fig = px.bar(terrain_counts, x="Count", y="Terrain", orientation='h',
                           color="Count", color_continuous_scale="Oranges")
                fig = apply_meteor_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🌍 Geographic Distribution")
            # Latitude distribution
            fig = px.histogram(sample, x="latitude", nbins=36,
                             color_discrete_sequence=["#ff6b35"],
                             labels={"latitude": "Latitude"})
            fig = apply_meteor_theme(fig)
            fig.update_layout(title="Latitude Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap density
        st.markdown("### 🔥 Density Heatmap")
        
        # Opsi heatmap mode
        col_heat1, col_heat2, col_heat3 = st.columns([2, 2, 2])
        with col_heat1:
            heatmap_mode = st.radio(
                "📊 Mode Heatmap:",
                ["🔢 Berdasarkan Jumlah", "⚖️ Berdasarkan Massa"],
                help="Jumlah = semua meteorit sama intensitasnya | Massa = meteorit besar lebih terang"
            )
        with col_heat2:
            radius_heat = st.slider("🎯 Radius Titik", 5, 50, 25, step=5)
        with col_heat3:
            zoom_heat = st.slider("🔍 Zoom Level", 0, 3, 1)
        
        # Tentukan nilai z berdasarkan mode
        if heatmap_mode == "🔢 Berdasarkan Jumlah":
            # Semua titik punya intensitas sama = 1 (jadi semua terlihat)
            z_values = [1] * len(sample)
            colorscale_heat = 'Hot'
        else:
            # Berdasarkan massa (log scale agar lebih merata)
            import numpy as np
            mass_values = sample["mass_gram"].fillna(1).values
            # Gunakan log scale agar perbedaan tidak terlalu ekstrem
            z_values = np.log10(mass_values + 1)  # +1 untuk avoid log(0)
            colorscale_heat = 'Plasma'
        
        fig = go.Figure(go.Densitymapbox(
            lat=sample["latitude"],
            lon=sample["longitude"],
            z=z_values,
            radius=radius_heat,  # Dinamis dari slider
            colorscale=colorscale_heat,
            showscale=True,
            colorbar=dict(
                title="Intensitas" if heatmap_mode == "🔢 Berdasarkan Jumlah" else "Log(Mass)",
                titlefont=dict(color='#d0d0ff'),
                tickfont=dict(color='#d0d0ff')
            )
        ))
        
        fig.update_layout(
            mapbox=dict(
                style='carto-darkmatter',
                center=dict(lat=20, lon=0),
                zoom=zoom_heat  # Dinamis dari slider
            ),
            height=600,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(10, 10, 26, 1)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Penjelasan
        if heatmap_mode == "🔢 Berdasarkan Jumlah":
            st.info("💡 **Mode Jumlah**: Semua meteorit memiliki intensitas yang sama. Area dengan banyak meteorit akan terlihat lebih terang.")
        else:
            st.info("💡 **Mode Massa**: Meteorit dengan massa lebih besar akan terlihat lebih terang (skala logaritmik).")

# ============================================================================
# FOOTER
# ============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; color: #808080; font-size: 0.8em;">
    <p>Data: NASA Meteorite Landings</p>
    <p>Powered by Supabase & Streamlit</p>
</div>
""", unsafe_allow_html=True)
