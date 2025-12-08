"""
☄️ Meteorite Landing System - Dashboard
Tema: Space/Meteor dengan Globe 3D Interaktif
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Load from .env for local
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
    .stApp {
        background: linear-gradient(180deg, #0a0a1a 0%, #1a1a3a 50%, #0d0d2b 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12122a 0%, #1e1e4a 100%);
        border-right: 2px solid #ff6b35;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0ff;
    }
    
    h1, h2, h3 {
        color: #ff6b35 !important;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
    }
    
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
    
    hr {
        border-color: #ff6b35 !important;
        box-shadow: 0 0 10px rgba(255, 107, 53, 0.3);
    }
    
    .stMarkdown, p, span {
        color: #d0d0ff;
    }
    
    .stDataFrame {
        border: 1px solid #ff6b35;
        border-radius: 10px;
    }
    
    .stSelectbox > div > div {
        background-color: #1a1a3a;
        border-color: #ff6b35;
    }
    
    .stRadio > div {
        background: transparent;
    }
    
    .stAlert {
        background-color: rgba(255, 107, 53, 0.1);
        border: 1px solid #ff6b35;
        color: #e0e0ff;
    }
    
    .meteor-header {
        background: linear-gradient(90deg, #ff6b35, #ff8c5a, #ffad7a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LAZY LOAD SUPABASE - Initialize only when needed
# ============================================================================
@st.cache_resource
def get_supabase():
    """Lazy load Supabase client"""
    try:
        from supabase import create_client
        
        url = st.secrets.get("SUPABASE_URL") if "SUPABASE_URL" in st.secrets else os.getenv("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_ANON_KEY") if "SUPABASE_ANON_KEY" in st.secrets else os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            return None
        
        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Failed to initialize Supabase: {str(e)}")
        return None

@st.cache_data(ttl=300)
def fetch_data(table_name, limit=None):
    """Fetch data from Supabase"""
    try:
        supabase = get_supabase()
        if not supabase:
            return pd.DataFrame()
        
        query = supabase.table(table_name).select("*")
        if limit:
            query = query.limit(limit)
        response = query.execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.warning(f"⚠️ Could not fetch {table_name}: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_table_count(table_name):
    """Get total count of records"""
    try:
        supabase = get_supabase()
        if not supabase:
            return 0
        
        response = supabase.table(table_name).select("*", count="exact").execute()
        return response.count if response.count else 0
    except:
        return 0

def apply_meteor_theme(fig):
    """Apply meteor theme to plotly figures"""
    fig.update_layout(
        paper_bgcolor='rgba(26, 26, 58, 0.8)',
        plot_bgcolor='rgba(26, 26, 58, 0.8)',
        font=dict(color='#d0d0ff'),
        title_text='',
        title_font=dict(color='#ff6b35'),
        legend=dict(bgcolor='rgba(26, 26, 58, 0.8)', font=dict(color='#d0d0ff')),
        xaxis=dict(gridcolor='rgba(255, 107, 53, 0.2)', tickfont=dict(color='#a0a0ff')),
        yaxis=dict(gridcolor='rgba(255, 107, 53, 0.2)', tickfont=dict(color='#a0a0ff'))
    )
    return fig

# ============================================================================
# SIDEBAR
# ============================================================================
st.sidebar.markdown("""
<h1 style='text-align: center; color: #ff6b35; font-size: 1.8rem; font-weight: bold;'>
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
try:
    meteorites_count = get_table_count("meteorites")
    st.sidebar.metric("Total Meteorites", f"{meteorites_count:,}")
except:
    st.sidebar.metric("Total Meteorites", "Loading...")

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
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("☄️ Meteorites", f"{get_table_count('meteorites'):,}")
    with col2:
        st.metric("🔬 Classifications", len(classifications))
    with col3:
        st.metric("🏛️ Museums", len(museums))
    with col4:
        st.metric("💎 Specimens", f"{get_table_count('meteorite_specimens'):,}")
    with col5:
        st.metric("📚 Studies", f"{get_table_count('research_studies'):,}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌌 Meteorite Categories")
        if not meteorites.empty and not classifications.empty:
            try:
                merged = meteorites.merge(classifications, on="classification_id", how="left")
                if "category" in merged.columns:
                    cat_counts = merged["category"].dropna().value_counts().reset_index()
                    cat_counts.columns = ["Category", "Count"]
                    fig = px.pie(cat_counts, values="Count", names="Category", hole=0.5,
                               color_discrete_sequence=px.colors.sequential.Oranges_r)
                    fig = apply_meteor_theme(fig)
                    fig.update_traces(textfont_color='white', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.info("📊 No data available")
    
    with col2:
        st.markdown("### 🔥 Fall vs Found")
        fall_types = fetch_data("fall_types")
        if not meteorites.empty and not fall_types.empty:
            try:
                merged = meteorites.merge(fall_types, on="fall_type_id", how="left")
                if "fall_type_name" in merged.columns:
                    fall_counts = merged["fall_type_name"].dropna().value_counts().reset_index()
                    fall_counts.columns = ["Type", "Count"]
                    fig = px.pie(fall_counts, values="Count", names="Type", hole=0.5,
                               color_discrete_sequence=["#ff6b35", "#4ecdc4"])
                    fig = apply_meteor_theme(fig)
                    fig.update_traces(textfont_color='white', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.info("📊 No data available")
    
    st.markdown("### 📅 Discovery Timeline")
    if not meteorites.empty and "year_discovered" in meteorites.columns:
        try:
            yearly = meteorites[meteorites["year_discovered"] > 1800].groupby("year_discovered").size().reset_index(name="count")
            if not yearly.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=yearly["year_discovered"], y=yearly["count"],
                    mode='lines', fill='tozeroy',
                    line=dict(color='#ff6b35', width=2),
                    fillcolor='rgba(255, 107, 53, 0.3)'
                ))
                fig = apply_meteor_theme(fig)
                fig.update_layout(xaxis_title="Year", yaxis_title="Discoveries", height=400)
                st.plotly_chart(fig, use_container_width=True)
        except:
            pass
    
    st.markdown("### ⚖️ Mass Statistics")
    if not meteorites.empty and "mass_gram" in meteorites.columns:
        try:
            valid_mass = meteorites[meteorites["mass_gram"].notna() & (meteorites["mass_gram"] > 0)]
            if not valid_mass.empty:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🌍 Total Mass", f"{valid_mass['mass_gram'].sum() / 1000000:,.1f} tons")
                with col2:
                    st.metric("📊 Average", f"{valid_mass['mass_gram'].mean():,.0f} g")
                with col3:
                    st.metric("🏆 Largest", f"{valid_mass['mass_gram'].max() / 1000:,.0f} kg")
                with col4:
                    st.metric("🔬 Smallest", f"{valid_mass['mass_gram'].min():.4f} g")
        except:
            pass

# ============================================================================
# PAGE: METEORITES
# ============================================================================
elif page == "☄️ Meteorites":
    st.markdown("# ☄️ Meteorite Database")
    
    meteorites = fetch_data("meteorites")
    classifications = fetch_data("meteorite_classifications")
    fall_types = fetch_data("fall_types")
    
    if not meteorites.empty:
        st.sidebar.markdown("### 🎯 Filters")
        
        selected_cat = "All"
        selected_fall = "All"
        
        if not classifications.empty:
            categories = ["All"] + sorted(classifications["category"].dropna().unique().tolist())
            selected_cat = st.sidebar.selectbox("Category", categories)
        
        if not fall_types.empty:
            falls = ["All"] + fall_types["fall_type_name"].tolist()
            selected_fall = st.sidebar.selectbox("Fall Type", falls)
        
        year_range = st.sidebar.slider("Year Range", 800, 2023, (1900, 2023))
        
        filtered = meteorites.copy()
        if "year_discovered" in filtered.columns:
            filtered = filtered[(filtered["year_discovered"] >= year_range[0]) & 
                              (filtered["year_discovered"] <= year_range[1])]
        
        if selected_cat != "All" and not classifications.empty:
            cat_ids = classifications[classifications["category"] == selected_cat]["classification_id"].tolist()
            filtered = filtered[filtered["classification_id"].isin(cat_ids)]
        
        if selected_fall != "All" and not fall_types.empty:
            try:
                fall_id = fall_types[fall_types["fall_type_name"] == selected_fall]["fall_type_id"].values[0]
                filtered = filtered[filtered["fall_type_id"] == fall_id]
            except:
                pass
        
        st.metric("🎯 Filtered Results", f"{len(filtered):,}")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 By Classification Group")
            if not filtered.empty and not classifications.empty:
                try:
                    merged = filtered.merge(classifications, on="classification_id", how="left")
                    if "class_group" in merged.columns:
                        group_counts = merged["class_group"].value_counts().head(10).reset_index()
                        group_counts.columns = ["Group", "Count"]
                        fig = px.bar(group_counts, x="Count", y="Group", orientation='h',
                                   color="Count", color_continuous_scale="Oranges")
                        fig = apply_meteor_theme(fig)
                        st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("No data available")
        
        with col2:
            st.markdown("### ⚖️ Mass Distribution")
            if not filtered.empty and "mass_gram" in filtered.columns:
                try:
                    valid_mass = filtered[filtered["mass_gram"].notna() & (filtered["mass_gram"] > 0)]
                    
                    if len(valid_mass) > 0:
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("📊 Total", f"{len(valid_mass):,}")
                        with col_b:
                            st.metric("⚖️ Rata-rata", f"{valid_mass['mass_gram'].mean()/1000:,.1f} kg")
                        with col_c:
                            st.metric("🏆 Terberat", f"{valid_mass['mass_gram'].max()/1000:,.0f} kg")
                        
                        fig = go.Figure()
                        fig.add_trace(go.Box(
                            y=valid_mass['mass_gram'],
                            name='Mass Distribution',
                            marker=dict(color='#ff6b35'),
                            boxmean='sd',
                            fillcolor='rgba(255, 107, 53, 0.5)',
                            line=dict(color='#ff6b35', width=2)
                        ))
                        
                        fig = apply_meteor_theme(fig)
                        fig.update_layout(yaxis_title="Mass (gram) - Log Scale", yaxis_type="log", showlegend=False, height=350)
                        st.plotly_chart(fig, use_container_width=True)
                except:
                    pass
        
        st.markdown("### 🏆 Top 15 Heaviest Meteorites")
        if not filtered.empty and "mass_gram" in filtered.columns:
            try:
                top15 = filtered.nlargest(15, "mass_gram")[["name", "mass_gram", "year_discovered"]]
                if not top15.empty:
                    top15["mass_tons"] = top15["mass_gram"] / 1000000
                    fig = px.bar(top15, x="name", y="mass_tons", color="mass_tons",
                                color_continuous_scale="YlOrRd",
                                labels={"mass_tons": "Mass (tons)", "name": ""})
                    fig = apply_meteor_theme(fig)
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
            except:
                pass
        
        st.markdown("### 📋 Data Table")
        if not filtered.empty:
            display_df = filtered[["name", "mass_gram", "year_discovered"]].head(100)
            st.dataframe(display_df, use_container_width=True, height=400)

# ============================================================================
# PAGE: CLASSIFICATIONS
# ============================================================================
elif page == "🔬 Classifications":
    st.markdown("# 🔬 Meteorite Classifications")
    
    classifications = fetch_data("meteorite_classifications")
    
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
            try:
                cat_counts = classifications["category"].value_counts().reset_index()
                cat_counts.columns = ["Category", "Count"]
                fig = px.pie(cat_counts, values="Count", names="Category", hole=0.5,
                           color_discrete_sequence=px.colors.sequential.Plasma)
                fig = apply_meteor_theme(fig)
                fig.update_traces(textfont_color='white')
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("No data available")
        
        with col2:
            st.markdown("### 📊 Top Class Groups")
            try:
                group_counts = classifications["class_group"].value_counts().head(12).reset_index()
                group_counts.columns = ["Group", "Count"]
                fig = px.bar(group_counts, x="Count", y="Group", orientation='h',
                           color="Count", color_continuous_scale="Oranges")
                fig = apply_meteor_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("No data available")
        
        st.markdown("### 🗺️ Classification Hierarchy")
        try:
            fig = px.treemap(classifications, path=['category', 'class_group'], 
                            color_discrete_sequence=px.colors.sequential.Oranges)
            fig = apply_meteor_theme(fig)
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("No data available")
    else:
        st.info("📊 No classification data available")

# ============================================================================
# PAGE: MUSEUMS
# ============================================================================
elif page == "🏛️ Museums":
    st.markdown("# 🏛️ Museums & Collections")
    
    museums = fetch_data("museums")
    specimens = fetch_data("meteorite_specimens")
    
    if not museums.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏛️ Museums", len(museums))
        with col2:
            st.metric("💎 Specimens", f"{get_table_count('meteorite_specimens'):,}")
        with col3:
            if not specimens.empty and "specimen_mass_gram" in specimens.columns:
                try:
                    total = specimens["specimen_mass_gram"].sum()
                    st.metric("⚖️ Total Mass", f"{total/1000:,.1f} kg")
                except:
                    st.metric("⚖️ Total Mass", "N/A")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Specimens by Museum")
            if not specimens.empty and not museums.empty:
                try:
                    merged = specimens.merge(museums, on="museum_id", how="left")
                    counts = merged["museum_name"].value_counts().reset_index()
                    counts.columns = ["Museum", "Specimens"]
                    fig = px.bar(counts, x="Specimens", y="Museum", orientation='h',
                               color="Specimens", color_continuous_scale="Oranges")
                    fig = apply_meteor_theme(fig)
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("No data available")
        
        with col2:
            st.markdown("### 💎 Specimen Types")
            if not specimens.empty and "specimen_type" in specimens.columns:
                try:
                    type_counts = specimens["specimen_type"].value_counts().reset_index()
                    type_counts.columns = ["Type", "Count"]
                    fig = px.pie(type_counts, values="Count", names="Type", hole=0.5,
                               color_discrete_sequence=px.colors.sequential.Sunset)
                    fig = apply_meteor_theme(fig)
                    fig.update_traces(textfont_color='white')
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("No data available")
        
        st.markdown("### 🏛️ Museum Directory")
        for _, museum in museums.iterrows():
            with st.expander(f"🏛️ {museum['museum_name']}"):
                st.write(f"📍 **City:** {museum.get('city', 'N/A')}")
                st.write(f"📝 **Description:** {museum.get('description', 'N/A')}")
    else:
        st.info("📊 No museum data available")

# ============================================================================
# PAGE: RESEARCH
# ============================================================================
elif page == "📚 Research":
    st.markdown("# 📚 Research & Expeditions")
    
    studies = fetch_data("research_studies")
    researchers = fetch_data("researchers")
    expeditions = fetch_data("discovery_expeditions")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Studies", f"{get_table_count('research_studies'):,}")
    with col2:
        st.metric("👨‍🔬 Researchers", len(researchers))
    with col3:
        st.metric("🏕️ Expeditions", len(expeditions))
    
    st.markdown("---")
    
    if not studies.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Study Status")
            if "status" in studies.columns:
                try:
                    status_counts = studies["status"].value_counts().reset_index()
                    status_counts.columns = ["Status", "Count"]
                    colors = {"Published": "#2ecc71", "In Review": "#f39c12", "Completed": "#3498db", "Ongoing": "#9b59b6"}
                    fig = px.pie(status_counts, values="Count", names="Status", hole=0.5,
                               color="Status", color_discrete_map=colors)
                    fig = apply_meteor_theme(fig)
                    fig.update_traces(textfont_color='white')
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("No data available")
        
        with col2:
            st.markdown("### 📅 Publications Timeline")
            if "publication_year" in studies.columns:
                try:
                    yearly = studies.groupby("publication_year").size().reset_index(name="count")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=yearly["publication_year"], y=yearly["count"],
                        mode='lines+markers', line=dict(color='#ff6b35', width=3),
                        marker=dict(size=8, color='#ff6b35')
                    ))
                    fig = apply_meteor_theme(fig)
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("No data available")
        
        st.markdown("### 📰 Top Journals")
        if "journal" in studies.columns:
            try:
                journal_counts = studies["journal"].value_counts().reset_index()
                journal_counts.columns = ["Journal", "Publications"]
                fig = px.bar(journal_counts, x="Publications", y="Journal", orientation='h',
                           color="Publications", color_continuous_scale="Oranges")
                fig = apply_meteor_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("No data available")
    
    st.markdown("### 👨‍🔬 Research Team")
    if not researchers.empty:
        try:
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
        except:
            st.info("No researcher data available")
    
    # DIAGRAM METEORITE_DISCOVERIES - Meteorites Found per Expedition
    st.markdown("---")
    st.markdown("### 🏕️ Meteorites Found per Expedition")
    
    discoveries = fetch_data("meteorite_discoveries")
    
    if not discoveries.empty and not expeditions.empty:
        try:
            # Gabungkan discoveries dengan expeditions untuk mendapatkan nama ekspedisi
            disc_exp = discoveries.merge(expeditions, on="expedition_id", how="left")
            
            if "expedition_name" in disc_exp.columns:
                # Hitung jumlah meteorit per ekspedisi
                exp_counts = disc_exp.groupby("expedition_name").size().reset_index(name="meteorites_found")
                exp_counts = exp_counts.sort_values("meteorites_found", ascending=True)
                
                # Bar chart horizontal
                fig = px.bar(exp_counts, 
                           x="meteorites_found", 
                           y="expedition_name",
                           orientation='h',
                           color="meteorites_found",
                           color_continuous_scale="Reds",
                           labels={"meteorites_found": "Jumlah Meteorit", "expedition_name": "Ekspedisi"},
                           text="meteorites_found")
                
                fig = apply_meteor_theme(fig)
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                fig.update_layout(showlegend=False, height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Info box
                total_discovered = len(discoveries)
                avg_per_exp = total_discovered / len(expeditions) if len(expeditions) > 0 else 0
                most_productive = exp_counts.iloc[-1]  # Ekspedisi dengan penemuan terbanyak
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("📊 Total Penemuan", f"{total_discovered:,}")
                with col_b:
                    st.metric("📈 Rata-rata/Ekspedisi", f"{avg_per_exp:.1f}")
                with col_c:
                    st.metric("🏆 Paling Produktif", f"{most_productive['meteorites_found']}")
                
                st.info(f"🏕️ Ekspedisi paling produktif: **{most_productive['expedition_name']}** dengan **{most_productive['meteorites_found']}** meteorit ditemukan")
        except Exception as e:
            st.warning("⚠️ Data ekspedisi penemuan tidak tersedia")

# ============================================================================
# PAGE: GLOBE MAP
# ============================================================================
elif page == "🌍 Globe Map":
    st.markdown("# 🌍 Interactive Globe Map")
    st.markdown("### Explore Meteorite Landing Sites Around the World")
    
    locations = fetch_data("locations")
    meteorites = fetch_data("meteorites")
    
    if not locations.empty and not meteorites.empty:
        try:
            merged = meteorites.merge(locations, on="location_id", how="left")
            valid_coords = merged.dropna(subset=["latitude", "longitude"])
            
            if not valid_coords.empty:
                total_available = len(valid_coords)
                st.success(f"📊 Total data dengan koordinat: **{total_available:,} lokasi meteorit**")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    sample_size = st.slider(
                        "🎯 Jumlah Lokasi yang Ditampilkan", 
                        min_value=100, 
                        max_value=min(5000, total_available),
                        value=min(1000, total_available),
                        step=100
                    )
                with col2:
                    st.metric("Menampilkan", f"{sample_size:,}")
                
                if len(valid_coords) > sample_size:
                    sample = valid_coords.sample(sample_size, random_state=42)
                else:
                    sample = valid_coords
                
                st.markdown("### ☄️ Meteorite Landing Sites - 3D Globe")
                
                sample_display = sample.copy()
                sample_display['mass_display'] = sample_display['mass_gram'].apply(
                    lambda x: f"{x:,.2f} g ({x/1000:,.2f} kg)" if pd.notna(x) and x > 0 else "Unknown"
                )
                sample_display['year_display'] = sample_display['year_discovered'].apply(
                    lambda x: str(int(x)) if pd.notna(x) else "Unknown"
                )
                
                customdata = sample_display[['name', 'mass_display', 'year_display', 'latitude', 'longitude']].values
                
                fig = go.Figure()
                fig.add_trace(go.Scattergeo(
                    lon=sample["longitude"],
                    lat=sample["latitude"],
                    text=["☄️"] * len(sample),
                    customdata=customdata,
                    hovertemplate=(
                        "<b style='font-size:16px; color:#ff6b35;'>☄️ %{customdata[0]}</b><br>"
                        "⚖️ <b>Massa:</b> %{customdata[1]}<br>"
                        "📅 <b>Tahun:</b> %{customdata[2]}<br>"
                        "📍 <b>Lat:</b> %{customdata[3]:.2f}° <b>Lon:</b> %{customdata[4]:.2f}°"
                        "<extra></extra>"
                    ),
                    mode='text',
                    textfont=dict(size=14, color='#ff6b35'),
                    showlegend=False
                ))
                
                fig.update_layout(
                    geo=dict(
                        projection_type='orthographic',
                        showland=True,
                        landcolor='rgb(40, 40, 80)',
                        showocean=True,
                        oceancolor='rgb(20, 20, 50)',
                        showcountries=True,
                        countrycolor='rgb(100, 100, 150)',
                        bgcolor='rgba(10, 10, 26, 1)',
                        projection_rotation=dict(lon=0, lat=20, roll=0)
                    ),
                    paper_bgcolor='rgba(10, 10, 26, 1)',
                    height=700,
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("""
                <p style="text-align: center; color: #a0a0ff;">
                🖱️ <b>Drag to rotate</b> | 🔍 <b>Scroll to zoom</b> | 👆 <b>Hover ☄️ untuk detail</b>
                </p>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ No location data with valid coordinates")
        except Exception as e:
            st.error(f"❌ Error loading globe map: {str(e)}")
    else:
        st.error("❌ Could not load locations or meteorites data")

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
