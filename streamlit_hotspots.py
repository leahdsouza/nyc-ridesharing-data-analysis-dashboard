#!/usr/bin/env python3
"""
NYC Ridesharing Hotspots - Interactive Streamlit Dashboard
=========================================================

Interactive dashboard for visualizing NYC ride hotspots with filtering,
clustering, and detailed analysis capabilities.

Author: Data Science Assistant
Date: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from folium import plugins
import seaborn as sns
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="NYC Ridesharing Hotspots",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the data for better performance."""
    try:
        user_summary = pd.read_csv('user_summary.csv')
        ride_summary = pd.read_csv('ride_summary.csv')
        return user_summary, ride_summary
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}")
        st.stop()

def create_hotspot_map(ride_data, selected_weeks=None, selected_type=None, cluster_size=50):
    """Create an interactive map with ride hotspots."""
    
    # Filter data based on selections
    filtered_data = ride_data.copy()
    
    if selected_weeks:
        filtered_data = filtered_data[filtered_data['week_index'].isin(selected_weeks)]
    
    if selected_type and selected_type != 'All':
        filtered_data = filtered_data[filtered_data['type'] == selected_type.lower()]
    
    # Create base map centered on NYC
    m = folium.Map(
        location=[40.7128, -74.0060],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Create separate layer groups for better organization
    origins_group = folium.FeatureGroup(name='🔵 Pickup Locations (Origins)', show=True)
    destinations_group = folium.FeatureGroup(name='🔴 Drop-off Locations (Destinations)', show=True)
    heatmap_group = folium.FeatureGroup(name='🔥 Ride Density Heatmap', show=True)
    
    # Add origins (blue markers) - PICKUP LOCATIONS
    origins = filtered_data[filtered_data['type'] == 'origin']
    if not origins.empty:
        for idx, row in origins.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['long']],
                radius=max(3, min(15, row['ride_count'] / 5)),  # Size based on ride count
                popup=f"""
                <div style='font-family: Arial; width: 200px;'>
                    <h3 style='color: #1f77b4; margin: 0;'> PICKUP LOCATION</h3>
                    <hr style='margin: 5px 0;'>
                    <b>Customer ID:</b> {row['customer_id']}<br>
                    <b>Week:</b> {row['week_index']}<br>
                    <b>Total Rides:</b> {row['ride_count']}<br>
                    <b>Coordinates:</b> {row['lat']:.4f}, {row['long']:.4f}
                </div>
                """,
                color='#1f77b4',  # Blue color
                fill=True,
                fillOpacity=0.7,
                weight=2
            ).add_to(origins_group)
    
    # Add destinations (red markers) - DROP-OFF LOCATIONS
    destinations = filtered_data[filtered_data['type'] == 'destination']
    if not destinations.empty:
        for idx, row in destinations.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['long']],
                radius=max(3, min(15, row['ride_count'] / 5)),
                popup=f"""
                <div style='font-family: Arial; width: 200px;'>
                    <h3 style='color: #d62728; margin: 0;'>🏁 DROP-OFF LOCATION</h3>
                    <hr style='margin: 5px 0;'>
                    <b>Customer ID:</b> {row['customer_id']}<br>
                    <b>Week:</b> {row['week_index']}<br>
                    <b>Total Rides:</b> {row['ride_count']}<br>
                    <b>Coordinates:</b> {row['lat']:.4f}, {row['long']:.4f}
                </div>
                """,
                color='#d62728',  # Red color
                fill=True,
                fillOpacity=0.7,
                weight=2
            ).add_to(destinations_group)
    
    # Add heatmap layer
    if not filtered_data.empty:
        heat_data = [[row['lat'], row['long'], row['ride_count']] 
                    for idx, row in filtered_data.iterrows()]
        plugins.HeatMap(
            heat_data, 
            name="Ride Density",
            min_opacity=0.2,
            max_zoom=18,
            radius=20,
            blur=15,
            gradient={0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red'}
        ).add_to(heatmap_group)
    
    # Add clustering for better performance
    if len(filtered_data) > cluster_size:
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        # Add markers to cluster
        for idx, row in filtered_data.iterrows():
            if row['type'] == 'origin':
                color = '#1f77b4'
                icon = 'car'
                label = 'Pickup'
            else:
                color = '#d62728'
                icon = 'flag'
                label = 'Drop-off'
                
            folium.Marker(
                [row['lat'], row['long']],
                popup=f"""
                <div style='font-family: Arial;'>
                    <h4 style='color: {color}; margin: 0;'>{label} Location</h4>
                    <b>Rides:</b> {row['ride_count']}
                </div>
                """,
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(marker_cluster)
    
    # Add all groups to map
    origins_group.add_to(m)
    destinations_group.add_to(m)
    heatmap_group.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def create_ride_distribution_chart(ride_data, selected_weeks=None, selected_type=None):
    """Create interactive charts for ride distribution analysis."""
    
    # Filter data
    filtered_data = ride_data.copy()
    if selected_weeks:
        filtered_data = filtered_data[filtered_data['week_index'].isin(selected_weeks)]
    if selected_type and selected_type != 'All':
        filtered_data = filtered_data[filtered_data['type'] == selected_type.lower()]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Rides by Week', 'Rides by Type', 'Top Locations', 'Ride Count Distribution'),
        specs=[[{"type": "bar"}, {"type": "pie"}],
               [{"type": "bar"}, {"type": "histogram"}]]
    )
    
    # 1. Rides by Week
    weekly_rides = filtered_data.groupby('week_index')['ride_count'].sum().reset_index()
    fig.add_trace(
        go.Bar(x=weekly_rides['week_index'], y=weekly_rides['ride_count'], 
               name='Weekly Rides', marker_color='lightblue'),
        row=1, col=1
    )
    
    # 2. Rides by Type
    type_counts = filtered_data['type'].value_counts()
    fig.add_trace(
        go.Pie(labels=type_counts.index, values=type_counts.values, 
               name='Ride Types', marker_colors=['blue', 'red']),
        row=1, col=2
    )
    
    # 3. Top Locations (by ride count)
    top_locations = filtered_data.groupby(['lat', 'long'])['ride_count'].sum().nlargest(10)
    location_labels = [f"({lat:.3f}, {lon:.3f})" for lat, lon in top_locations.index]
    fig.add_trace(
        go.Bar(x=location_labels, y=top_locations.values, 
               name='Top Locations', marker_color='green'),
        row=2, col=1
    )
    
    # 4. Ride Count Distribution
    fig.add_trace(
        go.Histogram(x=filtered_data['ride_count'], nbinsx=20, 
                    name='Ride Count Distribution', marker_color='orange'),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="Ride Distribution Analysis",
        title_x=0.5
    )
    
    # Update axes
    fig.update_xaxes(title_text="Week", row=1, col=1)
    fig.update_yaxes(title_text="Ride Count", row=1, col=1)
    fig.update_xaxes(title_text="Location", row=2, col=1)
    fig.update_yaxes(title_text="Ride Count", row=2, col=1)
    fig.update_xaxes(title_text="Ride Count", row=2, col=2)
    fig.update_yaxes(title_text="Frequency", row=2, col=2)
    
    return fig

def create_user_analysis_chart(user_data, selected_weeks=None):
    """Create user analysis charts."""
    
    # Filter users based on their activity weeks
    if selected_weeks:
        active_users = user_data[
            (user_data['first_week'] <= max(selected_weeks)) & 
            (user_data['last_week'] >= min(selected_weeks))
        ]
    else:
        active_users = user_data
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Rides per User Distribution', 'Weekly Rides Distribution', 
                       'Distance vs Weekly Rides', 'User Activity Timeline'),
        specs=[[{"type": "histogram"}, {"type": "histogram"}],
               [{"type": "scatter"}, {"type": "bar"}]]
    )
    
    # 1. Rides per User Distribution
    fig.add_trace(
        go.Histogram(x=active_users['total_rides'], nbinsx=20, 
                    name='Total Rides', marker_color='lightblue'),
        row=1, col=1
    )
    
    # 2. Weekly Rides Distribution
    fig.add_trace(
        go.Histogram(x=active_users['weekly_rides'], nbinsx=20, 
                    name='Weekly Rides', marker_color='lightgreen'),
        row=1, col=2
    )
    
    # 3. Distance vs Weekly Rides Scatter
    fig.add_trace(
        go.Scatter(x=active_users['weekly_rides'], y=active_users['avg_distance_miles'],
                  mode='markers', name='Users', 
                  marker=dict(size=8, color=active_users['total_rides'], 
                            colorscale='Viridis', showscale=True,
                            colorbar=dict(title="Total Rides"))),
        row=2, col=1
    )
    
    # 4. User Activity Timeline
    user_activity = active_users.groupby('first_week').size().reset_index(name='new_users')
    fig.add_trace(
        go.Bar(x=user_activity['first_week'], y=user_activity['new_users'],
               name='New Users', marker_color='purple'),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="User Analysis",
        title_x=0.5
    )
    
    # Update axes
    fig.update_xaxes(title_text="Total Rides", row=1, col=1)
    fig.update_yaxes(title_text="Number of Users", row=1, col=1)
    fig.update_xaxes(title_text="Weekly Rides", row=1, col=2)
    fig.update_yaxes(title_text="Number of Users", row=1, col=2)
    fig.update_xaxes(title_text="Weekly Rides", row=2, col=1)
    fig.update_yaxes(title_text="Average Distance (miles)", row=2, col=1)
    fig.update_xaxes(title_text="Week", row=2, col=2)
    fig.update_yaxes(title_text="New Users", row=2, col=2)
    
    return fig

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🚗 NYC Ridesharing Hotspots Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading data...'):
        user_data, ride_data = load_data()
    
    # Sidebar controls
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # Week selection
    available_weeks = sorted(ride_data['week_index'].unique())
    selected_weeks = st.sidebar.multiselect(
        "Select Weeks to Analyze",
        options=available_weeks,
        default=available_weeks[:10] if len(available_weeks) > 10 else available_weeks,
        help="Choose which weeks to include in the analysis"
    )
    
    # Type selection
    ride_types = ['All', 'Pickup Locations (Origins)', 'Drop-off Locations (Destinations)']
    selected_type = st.sidebar.selectbox(
        "📍 Select Location Type",
        options=ride_types,
        index=0,
        help="Filter by pickup locations (origins) or drop-off locations (destinations)"
    )
    
    # Convert selection to data format
    if selected_type == 'Pickup Locations (Origins)':
        selected_type = 'origin'
    elif selected_type == 'Drop-off Locations (Destinations)':
        selected_type = 'destination'
    else:
        selected_type = 'All'
    
    # Clustering option
    cluster_size = st.sidebar.slider(
        "🗂️ Map Clustering Threshold",
        min_value=10,
        max_value=200,
        value=50,
        help="When there are more than this many markers, they will be grouped into clusters for better performance and readability"
    )
    
    # Add explanation for clustering
    with st.sidebar.expander("ℹ️ About Clustering"):
        st.markdown("""
        **What is Clustering?**
        - Groups nearby markers together when there are too many to display clearly
        - Shows numbers like "15" meaning 15 rides in that area
        - Improves map performance and readability
        
        **Threshold Settings:**
        - **Low (10-20)**: See individual markers, good for detailed analysis
        - **Medium (50)**: Balanced view, good for general analysis  
        - **High (100+)**: Only major hotspots, good for strategic overview
        """)
    
    # Analysis type selection
    analysis_type = st.sidebar.radio(
        "Analysis Focus",
        options=["Hotspots Map", "Distribution Analysis", "User Analysis", "All Views"],
        index=0
    )
    
    # Key metrics
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Key Metrics")
    
    # Filter data for metrics
    filtered_ride_data = ride_data.copy()
    if selected_weeks:
        filtered_ride_data = filtered_ride_data[filtered_ride_data['week_index'].isin(selected_weeks)]
    if selected_type and selected_type != 'All':
        filtered_ride_data = filtered_ride_data[filtered_ride_data['type'] == selected_type.lower()]
    
    total_rides = filtered_ride_data['ride_count'].sum()
    unique_locations = filtered_ride_data[['lat', 'long']].drop_duplicates().shape[0]
    avg_rides_per_location = filtered_ride_data['ride_count'].mean()
    
    st.sidebar.metric("Total Rides", f"{total_rides:,}")
    st.sidebar.metric("Unique Locations", f"{unique_locations:,}")
    st.sidebar.metric("Avg Rides/Location", f"{avg_rides_per_location:.1f}")
    
    # Main content area
    if analysis_type in ["Hotspots Map", "All Views"]:

        
        # Add explanation box
        with st.expander("📖 How to Read This Map", expanded=True):
            st.markdown("""
            **Map Legend & Understanding:**
            - 🔵 **Blue Circles** = **Pickup Locations** (where customers start their rides)
            - 🔴 **Red Circles** = **Drop-off Locations** (where customers end their rides)
            - 🔥 **Heatmap Overlay** = **High-density areas** (more rides = hotter colors)
            - **Circle Size** = **Ride Frequency** (bigger circles = more rides at that location)
            
            **Layer Controls (top-right):**
            - Toggle different layers on/off
            - Show/hide pickup locations, drop-off locations, or heatmap
            - Use clustering when you have many points
            
            **Marketing Insights:**
            - **Residential areas** typically have more blue (pickup) markers
            - **Commercial areas** typically have more red (drop-off) markers
            - **Hotspots** show the most popular ride locations
            - **Size differences** reveal which locations are most frequently used
            """)
        
        # Create and display map
        with st.spinner('Generating interactive map...'):
            hotspot_map = create_hotspot_map(
                ride_data, 
                selected_weeks, 
                selected_type, 
                cluster_size
            )
            
            # Display map
            map_data = st_folium(hotspot_map, width=1200, height=600)
            
            # Show selected point info
            if map_data['last_object_clicked_popup']:
                st.info(f"Selected: {map_data['last_object_clicked_popup']}")
        
        # Add summary statistics for the map
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            origins_count = len(filtered_ride_data[filtered_ride_data['type'] == 'origin'])
            st.metric("Pickup Locations", f"{origins_count:,}")
        
        with col2:
            destinations_count = len(filtered_ride_data[filtered_ride_data['type'] == 'destination'])
            st.metric("Drop-off Locations", f"{destinations_count:,}")
        
        with col3:
            unique_origins = filtered_ride_data[filtered_ride_data['type'] == 'origin'][['lat', 'long']].drop_duplicates().shape[0]
            st.metric("Unique Pickup Spots", f"{unique_origins:,}")
        
        with col4:
            unique_destinations = filtered_ride_data[filtered_ride_data['type'] == 'destination'][['lat', 'long']].drop_duplicates().shape[0]
            st.metric("Unique Drop-off Spots", f"{unique_destinations:,}")
    
    if analysis_type in ["Distribution Analysis", "All Views"]:
        st.header("📈 Ride Distribution Analysis")
        
        # Create distribution charts
        dist_fig = create_ride_distribution_chart(ride_data, selected_weeks, selected_type)
        st.plotly_chart(dist_fig, use_container_width=True)
    
    if analysis_type in ["User Analysis", "All Views"]:
        st.header("👥 User Analysis")
        
        # Create user analysis charts
        user_fig = create_user_analysis_chart(user_data, selected_weeks)
        st.plotly_chart(user_fig, use_container_width=True)
    
    
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>NYC Ridesharing Hotspots Dashboard | Built with Streamlit & Plotly</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
