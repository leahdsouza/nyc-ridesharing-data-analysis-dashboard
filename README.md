# NYC Ridesharing Data Analysis Dashboard

A comprehensive interactive dashboard for analyzing NYC ridesharing data with advanced visualizations, hotspot mapping, and predictive analytics.

## 🚀 Features

- **Interactive Hotspot Mapping**: Visualize pickup and drop-off locations with clustering and heatmaps
- **Advanced Analytics**: User behavior analysis, ride distribution patterns, and correlation insights
- **Predictive Intelligence**: Demand forecasting and business intelligence recommendations
- **Real-time Filtering**: Filter by weeks, location types, and other parameters
- **Professional Visualizations**: High-quality charts and interactive maps

## 📁 Project Structure

```
nyc-ridesharing-data-analysis-dashboard/
├── src/                          # Main source code
│   ├── __init__.py              # Package initialization
│   ├── streamlit_hotspots.py    # Interactive Streamlit dashboard
│   └── uber_analysis.py         # Data analysis and processing
├── data/                        # Data files
│   ├── user_summary.csv         # User-level metrics
│   ├── ride_summary.csv         # Location data for mapping
│   └── summary_statistics.csv   # Key metrics summary
├── assets/                      # Generated visualizations
│   ├── rides_per_user_histogram.png
│   ├── distance_vs_rides_scatter.png
│   └── nyc_ride_hotspots.html
├── docs/                        # Documentation (future)
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── Makefile                     # Development commands
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd nyc-ridesharing-data-analysis-dashboard

# Install dependencies
make install
# or
pip install -r requirements.txt

# Setup development environment
make setup
```

## 🚀 Usage

### Run the Interactive Dashboard
```bash
make run-dashboard
# or
cd src && streamlit run streamlit_hotspots.py
```

### Run Data Analysis
```bash
make run-analysis
# or
cd src && python uber_analysis.py
```

### Available Commands
```bash
make help          # Show all available commands
make install       # Install dependencies
make setup         # Setup development environment
make run-dashboard # Run the Streamlit dashboard
make run-analysis  # Run data analysis
make clean         # Clean generated files
```

## 📊 Dashboard Features

### 🗺️ Hotspot Mapping
- Interactive map with pickup (blue) and drop-off (red) locations
- Clustering for better performance with large datasets
- Heatmap overlay showing ride density
- Layer controls for toggling different data views

### 📈 Analytics Dashboard
- **Weekly Trends**: Animated charts showing ride patterns over time
- **Distribution Analysis**: Pie charts and histograms of ride types
- **User Intelligence**: User behavior analysis and engagement metrics
- **Predictive Insights**: Demand forecasting and business recommendations

### 🎛️ Interactive Controls
- Week selection for time-based filtering
- Location type filtering (pickups vs drop-offs)
- Clustering threshold adjustment
- Multiple analysis views

## 📋 Data Requirements

The dashboard expects the following CSV files in the `data/` directory:
- `user_summary.csv`: User-level metrics and statistics
- `ride_summary.csv`: Location data for mapping and visualization

## 🔧 Development

### Project Structure
- `src/`: Contains all Python source code
- `data/`: Contains input data files (CSV format)
- `assets/`: Contains generated visualizations and outputs
- `docs/`: Future documentation directory

### Dependencies
Key dependencies include:
- `streamlit`: Web application framework
- `plotly`: Interactive visualizations
- `folium`: Interactive maps
- `pandas`: Data manipulation
- `numpy`: Numerical computing
- `matplotlib` & `seaborn`: Static visualizations

## 📈 Key Metrics

The dashboard analyzes and visualizes:
- **15,120 total rides** across the dataset
- **30,240 location points** (origins and destinations)
- **100% heavy users** (users with >1 ride per week)
- **99 weeks** of comprehensive data coverage

## 🎯 Business Intelligence

The dashboard provides strategic insights including:
- User engagement patterns and retention analysis
- Geographic hotspots for marketing and operations
- Demand forecasting and growth predictions
- Competitive advantage analysis
- Revenue potential calculations

## 📝 License

© 2024 Leah D'Souza • All Rights Reserved

This project contains proprietary analysis and insights. Unauthorized distribution is prohibited.

## 🤝 Contributing

This is a private project. For collaboration or questions, please contact the author.

## 📞 Support

For technical support or questions about the dashboard, please contact:
- Author: Leah D'Souza
- Email: leah@example.com

---

*Built with Streamlit & Plotly • Powered by Advanced Analytics*