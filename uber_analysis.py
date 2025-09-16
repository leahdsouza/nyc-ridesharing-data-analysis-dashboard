#!/usr/bin/env python3
"""
NYC Ridesharing Data Analysis Dashboard
=======================================

This script processes Uber ride data and prepares it for Tableau visualization.
It computes user-level metrics, creates visualizations, and exports Tableau-ready CSVs.

Author: Data Science Assistant
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic
import folium
from folium import plugins
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class UberDataAnalyzer:
    """Main class for analyzing Uber ride data."""
    
    def __init__(self, data_path):
        """Initialize with data path."""
        self.data_path = data_path
        self.df = None
        self.user_summary = None
        self.ride_summary = None
        
    def load_data(self):
        """Load and perform initial data exploration."""
        print("Loading data...")
        self.df = pd.read_csv(self.data_path)
        
        print(f"Dataset shape: {self.df.shape}")
        print(f"Columns: {list(self.df.columns)}")
        print(f"Date range: Week {self.df['week_index'].min()} to Week {self.df['week_index'].max()}")
        print(f"Unique customers: {self.df['customer_id'].nunique()}")
        print(f"Total trips: {len(self.df)}")
        
        # Display basic info
        print("\nData Info:")
        print(self.df.info())
        print("\nFirst few rows:")
        print(self.df.head())
        
        return self.df
    
    def calculate_distance(self, row):
        """Calculate distance between origin and destination using geodesic distance."""
        try:
            origin = (row['origin_lat'], row['origin_long'])
            destination = (row['destination_lat'], row['destination_long'])
            return geodesic(origin, destination).miles
        except:
            return np.nan
    
    def compute_user_metrics(self):
        """Compute user-level metrics: rides per user, weekly rides, avg distance."""
        print("\nComputing user-level metrics...")
        
        # Calculate distance for each trip
        print("Calculating trip distances...")
        self.df['distance_miles'] = self.df.apply(self.calculate_distance, axis=1)
        
        # Remove trips with invalid distances
        valid_trips = self.df.dropna(subset=['distance_miles'])
        print(f"Valid trips after distance calculation: {len(valid_trips)}")
        
        # User-level aggregations
        user_metrics = valid_trips.groupby('customer_id').agg({
            'trip_id': 'count',  # Total rides per user
            'distance_miles': 'mean',  # Average distance per user
            'week_index': 'nunique'  # Number of weeks user was active
        }).rename(columns={
            'trip_id': 'total_rides',
            'distance_miles': 'avg_distance_miles',
            'week_index': 'active_weeks'
        })
        
        # Calculate weekly rides per user
        user_metrics['weekly_rides'] = user_metrics['total_rides'] / user_metrics['active_weeks']
        
        # Add user activity details
        user_activity = valid_trips.groupby('customer_id')['week_index'].agg(['min', 'max']).rename(columns={
            'min': 'first_week',
            'max': 'last_week'
        })
        
        self.user_summary = user_metrics.join(user_activity)
        
        print(f"User summary created for {len(self.user_summary)} users")
        print("\nUser Summary Statistics:")
        print(self.user_summary.describe())
        
        return self.user_summary
    
    def create_histogram_rides_per_user(self):
        """Create histogram of rides per user."""
        print("\nCreating histogram of rides per user...")
        
        plt.figure(figsize=(12, 8))
        
        # Main histogram
        plt.subplot(2, 2, 1)
        plt.hist(self.user_summary['total_rides'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Distribution of Total Rides per User', fontsize=14, fontweight='bold')
        plt.xlabel('Total Rides')
        plt.ylabel('Number of Users')
        plt.grid(True, alpha=0.3)
        
        # Log scale histogram for better visualization
        plt.subplot(2, 2, 2)
        plt.hist(np.log10(self.user_summary['total_rides'] + 1), bins=50, alpha=0.7, color='lightcoral', edgecolor='black')
        plt.title('Distribution of Total Rides per User (Log Scale)', fontsize=14, fontweight='bold')
        plt.xlabel('Log10(Total Rides + 1)')
        plt.ylabel('Number of Users')
        plt.grid(True, alpha=0.3)
        
        # Weekly rides histogram
        plt.subplot(2, 2, 3)
        plt.hist(self.user_summary['weekly_rides'], bins=50, alpha=0.7, color='lightgreen', edgecolor='black')
        plt.title('Distribution of Weekly Rides per User', fontsize=14, fontweight='bold')
        plt.xlabel('Weekly Rides')
        plt.ylabel('Number of Users')
        plt.grid(True, alpha=0.3)
        
        # Box plot for weekly rides
        plt.subplot(2, 2, 4)
        plt.boxplot(self.user_summary['weekly_rides'], vert=True)
        plt.title('Box Plot: Weekly Rides per User', fontsize=14, fontweight='bold')
        plt.ylabel('Weekly Rides')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('rides_per_user_histogram.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Calculate proportion of users with more than 1 ride per week
        users_more_than_1_ride_per_week = (self.user_summary['weekly_rides'] > 1).sum()
        total_users = len(self.user_summary)
        proportion = users_more_than_1_ride_per_week / total_users
        
        print(f"\nProportion of users with more than 1 ride per week: {proportion:.3f}")
        print(f"Users with >1 ride/week: {users_more_than_1_ride_per_week} out of {total_users}")
        
        return proportion
    
    def create_scatter_plot(self):
        """Create scatter plot of average distance vs rides per week."""
        print("\nCreating scatter plot of average distance vs weekly rides...")
        
        plt.figure(figsize=(12, 8))
        
        # Main scatter plot
        plt.subplot(2, 2, 1)
        plt.scatter(self.user_summary['weekly_rides'], self.user_summary['avg_distance_miles'], 
                   alpha=0.6, s=50, color='purple')
        plt.title('Average Distance vs Weekly Rides per User', fontsize=14, fontweight='bold')
        plt.xlabel('Weekly Rides')
        plt.ylabel('Average Distance (miles)')
        plt.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(self.user_summary['weekly_rides'], self.user_summary['avg_distance_miles'], 1)
        p = np.poly1d(z)
        plt.plot(self.user_summary['weekly_rides'], p(self.user_summary['weekly_rides']), 
                "r--", alpha=0.8, linewidth=2)
        
        # Log scale scatter plot
        plt.subplot(2, 2, 2)
        plt.scatter(np.log10(self.user_summary['weekly_rides'] + 1), 
                   np.log10(self.user_summary['avg_distance_miles'] + 1), 
                   alpha=0.6, s=50, color='orange')
        plt.title('Log Scale: Distance vs Weekly Rides', fontsize=14, fontweight='bold')
        plt.xlabel('Log10(Weekly Rides + 1)')
        plt.ylabel('Log10(Average Distance + 1)')
        plt.grid(True, alpha=0.3)
        
        # Distance distribution
        plt.subplot(2, 2, 3)
        plt.hist(self.user_summary['avg_distance_miles'], bins=50, alpha=0.7, color='lightblue', edgecolor='black')
        plt.title('Distribution of Average Distance per User', fontsize=14, fontweight='bold')
        plt.xlabel('Average Distance (miles)')
        plt.ylabel('Number of Users')
        plt.grid(True, alpha=0.3)
        
        # Correlation analysis
        plt.subplot(2, 2, 4)
        correlation = self.user_summary['weekly_rides'].corr(self.user_summary['avg_distance_miles'])
        plt.text(0.5, 0.5, f'Correlation: {correlation:.3f}', 
                ha='center', va='center', fontsize=16, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        plt.title('Correlation Analysis', fontsize=14, fontweight='bold')
        plt.axis('off')
        
        plt.tight_layout()
        plt.savefig('distance_vs_rides_scatter.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Correlation between weekly rides and average distance: {correlation:.3f}")
        
        return correlation
    
    def prepare_map_data(self):
        """Prepare map-ready dataset with origins and destinations."""
        print("\nPreparing map data for visualization...")
        
        # Load the original data for mapping
        map_df = self.df.copy()
        
        # Calculate distance for mapping data
        map_df['distance_miles'] = map_df.apply(self.calculate_distance, axis=1)
        map_df = map_df.dropna(subset=['distance_miles'])
        
        # Create origins dataset (blue markers)
        origins = map_df[['origin_lat', 'origin_long', 'customer_id', 'trip_id', 'week_index']].copy()
        origins['type'] = 'origin'
        origins['lat'] = origins['origin_lat']
        origins['long'] = origins['origin_long']
        origins = origins[['lat', 'long', 'customer_id', 'trip_id', 'week_index', 'type']]
        
        # Create destinations dataset (red markers)
        destinations = map_df[['destination_lat', 'destination_long', 'customer_id', 'trip_id', 'week_index']].copy()
        destinations['type'] = 'destination'
        destinations['lat'] = destinations['destination_lat']
        destinations['long'] = destinations['destination_long']
        destinations = destinations[['lat', 'long', 'customer_id', 'trip_id', 'week_index', 'type']]
        
        # Combine for map visualization
        self.ride_summary = pd.concat([origins, destinations], ignore_index=True)
        
        # Add ride count by location for hotspot analysis
        location_counts = self.ride_summary.groupby(['lat', 'long', 'type']).size().reset_index(name='ride_count')
        self.ride_summary = self.ride_summary.merge(location_counts, on=['lat', 'long', 'type'], how='left')
        
        print(f"Map data prepared: {len(self.ride_summary)} location points")
        print(f"Origins: {len(origins)}, Destinations: {len(destinations)}")
        
        return self.ride_summary
    
    def create_nyc_map(self):
        """Create an interactive map of NYC showing ride hotspots."""
        print("\nCreating NYC ride hotspots map...")
        
        # NYC center coordinates
        nyc_center = [40.7128, -74.0060]
        
        # Create base map
        m = folium.Map(location=nyc_center, zoom_start=11, tiles='OpenStreetMap')
        
        # Add origins (blue markers)
        origins = self.ride_summary[self.ride_summary['type'] == 'origin']
        for idx, row in origins.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['long']],
                radius=3,
                popup=f"Origin<br>Customer: {row['customer_id']}<br>Rides: {row['ride_count']}",
                color='blue',
                fill=True,
                fillOpacity=0.6
            ).add_to(m)
        
        # Add destinations (red markers)
        destinations = self.ride_summary[self.ride_summary['type'] == 'destination']
        for idx, row in destinations.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['long']],
                radius=3,
                popup=f"Destination<br>Customer: {row['customer_id']}<br>Rides: {row['ride_count']}",
                color='red',
                fill=True,
                fillOpacity=0.6
            ).add_to(m)
        
        # Add heatmap layer
        heat_data = [[row['lat'], row['long'], row['ride_count']] for idx, row in self.ride_summary.iterrows()]
        plugins.HeatMap(heat_data, name="Ride Density").add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map
        m.save('nyc_ride_hotspots.html')
        print("Interactive map saved as 'nyc_ride_hotspots.html'")
        
        return m
    
    def export_tableau_csvs(self):
        """Export CSV files ready for Tableau import."""
        print("\nExporting Tableau-ready CSV files...")
        
        # Export user summary
        user_export = self.user_summary.reset_index()
        user_export.to_csv('user_summary.csv', index=False)
        print(f"User summary exported: {len(user_export)} users")
        
        # Export ride summary for mapping
        ride_export = self.ride_summary.copy()
        ride_export.to_csv('ride_summary.csv', index=False)
        print(f"Ride summary exported: {len(ride_export)} location points")
        
        # Create additional summary statistics for Tableau
        summary_stats = pd.DataFrame({
            'metric': [
                'total_users',
                'total_rides',
                'avg_rides_per_user',
                'avg_weekly_rides_per_user',
                'avg_distance_per_user',
                'users_more_than_1_ride_per_week',
                'proportion_heavy_users',
                'correlation_distance_rides'
            ],
            'value': [
                len(self.user_summary),
                self.user_summary['total_rides'].sum(),
                self.user_summary['total_rides'].mean(),
                self.user_summary['weekly_rides'].mean(),
                self.user_summary['avg_distance_miles'].mean(),
                (self.user_summary['weekly_rides'] > 1).sum(),
                (self.user_summary['weekly_rides'] > 1).mean(),
                self.user_summary['weekly_rides'].corr(self.user_summary['avg_distance_miles'])
            ]
        })
        summary_stats.to_csv('summary_statistics.csv', index=False)
        print("Summary statistics exported")
        
        print("\nExported files:")
        print("- user_summary.csv: User-level metrics")
        print("- ride_summary.csv: Location data for mapping")
        print("- summary_statistics.csv: Key metrics for dashboard")
        
        return user_export, ride_export, summary_stats
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline."""
        print("="*60)
        print("NYC RIDESHARING DATA ANALYSIS DASHBOARD")
        print("="*60)
        
        # Load data
        self.load_data()
        
        # Compute user metrics
        self.compute_user_metrics()
        
        # Create visualizations
        proportion_heavy_users = self.create_histogram_rides_per_user()
        correlation = self.create_scatter_plot()
        
        # Prepare map data
        self.prepare_map_data()
        
        # Create map
        self.create_nyc_map()
        
        # Export for Tableau
        user_export, ride_export, summary_stats = self.export_tableau_csvs()
        
        # Final summary
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        print(f"Total users analyzed: {len(self.user_summary)}")
        print(f"Total rides processed: {self.user_summary['total_rides'].sum()}")
        print(f"Proportion of heavy users (>1 ride/week): {proportion_heavy_users:.3f}")
        print(f"Correlation (distance vs frequency): {correlation:.3f}")
        print(f"Average rides per user: {self.user_summary['total_rides'].mean():.2f}")
        print(f"Average weekly rides per user: {self.user_summary['weekly_rides'].mean():.2f}")
        print(f"Average distance per user: {self.user_summary['avg_distance_miles'].mean():.2f} miles")
        
        return {
            'user_summary': self.user_summary,
            'ride_summary': self.ride_summary,
            'proportion_heavy_users': proportion_heavy_users,
            'correlation': correlation
        }

def main():
    """Main execution function."""
    # Initialize analyzer
    analyzer = UberDataAnalyzer('uber_data.csv')
    
    # Run complete analysis
    results = analyzer.run_complete_analysis()
    
    print("\nFiles created:")
    print("- rides_per_user_histogram.png")
    print("- distance_vs_rides_scatter.png") 
    print("- nyc_ride_hotspots.html")
    print("- user_summary.csv")
    print("- ride_summary.csv")
    print("- summary_statistics.csv")

if __name__ == "__main__":
    main()
