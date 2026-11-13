# Spotify Artist & Track Analytics

Personal data analytics project built to explore audio features across different music genres using the Spotify API.

The project collects track data (tempo, energy, danceability, valence, acousticness), stores everything into an SQLite database, groups songs by mood using K-Means clustering, and predicts popularity with a Random Forest model. There is also an interactive dashboard built with Streamlit and Plotly to visualize the results.

## Overview

- ETL pipeline: collects audio features using Spotipy (or generates a sample dataset of 100 tracks if no API keys are provided).
- SQL storage: SQLite database with tables for artists, tracks, and metadata using star schema and SQL queries (aggregations, GROUP BY, AVG).
- Machine Learning:
  - Unsupervised: K-Means clustering (k=4) to group tracks into 4 mood categories (High Energy, Chill Vibes, Acoustic Mood, Dark / Intense).
  - Supervised: Random Forest Regressor to predict track popularity from audio features.
- Dashboard: Streamlit web interface with genre filters, KPI metrics, mood distribution donut charts, and energy vs popularity scatter plots.

## Project Structure

```
spotify-analytics/
├── pipeline.py          # Data collection, SQLite table creation, SQL queries
├── model.py             # K-Means clustering and Random Forest regression
├── app.py               # Streamlit web dashboard
├── requirements.txt     # Python dependencies
├── .env.example         # Example file for Spotify credentials
└── data/
    ├── spotify.db       # SQLite database (generated)
    ├── tracks.csv       # Raw track data (generated)
    ├── tracks_clustered.csv
    └── model_meta.json
```

## How to Run

1. Clone the repository:
```bash
git clone https://github.com/souhaib250/spotify-track-intelligence.git
cd spotify-track-intelligence
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up Spotify API keys:
Copy `.env.example` to `.env` and fill in your keys:
```bash
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
```
If you skip this step, the script will automatically use the built-in dataset of 100 tracks.

4. Run the ETL pipeline:
```bash
python pipeline.py
```

5. Train the models:
```bash
python model.py
```

6. Launch the dashboard:
```bash
streamlit run app.py
```

## Tech Stack

- Python, Pandas, NumPy
- SQLite3
- Scikit-learn (KMeans, RandomForestRegressor)
- Streamlit, Plotly
- Spotipy
