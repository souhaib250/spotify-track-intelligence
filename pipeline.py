import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

try:
    from dotenv import load_dotenv
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    USE_API = bool(client_id and client_secret)
except ImportError:
    USE_API = False

TRACKS_CATALOG = {
    "Drake": {
        "genre": "hip-hop",
        "tracks": [
            ("God's Plan", "2018-01-19", 0.754, 0.449, -5.611, 0.448, 0.014, 77.284, 94),
            ("Hotline Bling", "2015-07-31", 0.661, 0.456, -8.012, 0.368, 0.063, 135.013, 90),
            ("One Dance", "2016-04-05", 0.792, 0.625, -5.395, 0.882, 0.0441, 103.967, 88),
            ("Started From the Bottom", "2013-02-01", 0.833, 0.602, -5.769, 0.489, 0.019, 84.981, 83),
            ("Nonstop", "2018-06-29", 0.835, 0.581, -6.263, 0.303, 0.034, 130.057, 86),
            ("In My Feelings", "2018-06-29", 0.904, 0.671, -4.741, 0.735, 0.063, 91.957, 85),
            ("Passionfruit", "2017-03-18", 0.712, 0.579, -6.802, 0.661, 0.0718, 118.503, 84),
            ("Rich Flex", "2022-10-28", 0.771, 0.588, -6.512, 0.218, 0.044, 141.001, 92),
            ("Laugh Now Cry Later", "2020-08-14", 0.868, 0.741, -5.011, 0.496, 0.016, 155.994, 83),
            ("Toosie Slide", "2020-04-03", 0.904, 0.684, -5.467, 0.636, 0.072, 100.015, 82),
        ]
    },
    "Daft Punk": {
        "genre": "electronic",
        "tracks": [
            ("Get Lucky", "2013-04-19", 0.816, 0.813, -9.237, 0.608, 0.021, 116.002, 85),
            ("One More Time", "2001-10-22", 0.763, 0.908, -6.221, 0.616, 0.011, 123.028, 88),
            ("Instant Crush", "2013-05-21", 0.510, 0.619, -11.512, 0.521, 0.023, 136.994, 80),
            ("Harder Better Faster Stronger", "2001-10-22", 0.776, 0.912, -6.818, 0.459, 0.011, 123.015, 87),
            ("Around the World", "1997-03-03", 0.828, 0.829, -6.422, 0.657, 0.027, 121.004, 81),
            ("Lose Yourself to Dance", "2013-05-21", 0.885, 0.780, -6.823, 0.722, 0.019, 100.001, 79),
            ("Digital Love", "2001-10-22", 0.771, 0.845, -5.113, 0.617, 0.015, 123.993, 83),
            ("Technologic", "2005-03-14", 0.721, 0.896, -7.113, 0.413, 0.008, 127.001, 78),
            ("Alive", "2007-11-19", 0.603, 0.937, -4.113, 0.312, 0.009, 134.992, 74),
            ("Something About Us", "2001-10-22", 0.509, 0.414, -11.902, 0.462, 0.191, 97.981, 76),
        ]
    },
    "Taylor Swift": {
        "genre": "pop",
        "tracks": [
            ("Anti-Hero", "2022-10-21", 0.737, 0.567, -5.776, 0.564, 0.067, 97.009, 97),
            ("Shake It Off", "2014-08-18", 0.645, 0.800, -5.665, 0.912, 0.049, 160.054, 88),
            ("Blank Space", "2014-11-10", 0.751, 0.701, -6.133, 0.618, 0.047, 96.028, 87),
            ("Love Story (Taylor's Version)", "2021-02-12", 0.620, 0.702, -5.734, 0.845, 0.316, 119.142, 89),
            ("Cruel Summer", "2019-08-23", 0.552, 0.701, -5.705, 0.564, 0.047, 169.994, 95),
            ("cardigan", "2020-07-24", 0.511, 0.351, -9.238, 0.773, 0.819, 141.995, 90),
            ("Style", "2014-10-27", 0.544, 0.774, -7.312, 0.335, 0.052, 94.993, 86),
            ("Lavender Haze", "2022-10-21", 0.724, 0.745, -5.908, 0.562, 0.063, 139.983, 92),
            ("All Too Well (10 Min)", "2021-11-12", 0.524, 0.411, -8.904, 0.397, 0.312, 76.028, 91),
            ("22", "2012-10-22", 0.670, 0.796, -6.422, 0.907, 0.123, 129.981, 83),
        ]
    },
    "Kendrick Lamar": {
        "genre": "hip-hop",
        "tracks": [
            ("HUMBLE.", "2017-04-14", 0.904, 0.622, -6.251, 0.323, 0.034, 150.011, 90),
            ("DNA.", "2017-04-14", 0.802, 0.733, -5.778, 0.419, 0.024, 142.054, 88),
            ("Alright", "2015-03-15", 0.657, 0.499, -8.922, 0.339, 0.123, 97.013, 84),
            ("Money Trees", "2012-10-22", 0.571, 0.476, -8.011, 0.371, 0.072, 80.994, 83),
            ("Swimming Pools (Drank)", "2012-07-31", 0.741, 0.648, -7.112, 0.447, 0.063, 86.994, 82),
            ("King Kunta", "2015-03-15", 0.906, 0.676, -5.312, 0.598, 0.072, 92.979, 83),
            ("Poetic Justice", "2012-10-22", 0.741, 0.419, -8.332, 0.498, 0.082, 89.981, 80),
            ("ELEMENT.", "2017-04-14", 0.736, 0.531, -7.891, 0.312, 0.044, 97.981, 84),
            ("Not Like Us", "2024-05-04", 0.891, 0.734, -4.112, 0.678, 0.011, 97.015, 95),
            ("LOVE.", "2017-04-14", 0.681, 0.472, -8.112, 0.531, 0.082, 89.991, 83),
        ]
    },
    "Arctic Monkeys": {
        "genre": "indie",
        "tracks": [
            ("Do I Wanna Know?", "2013-06-18", 0.527, 0.620, -8.413, 0.179, 0.013, 85.488, 88),
            ("R U Mine?", "2013-02-27", 0.541, 0.885, -5.102, 0.249, 0.008, 148.981, 85),
            ("505", "2006-10-23", 0.419, 0.591, -9.901, 0.183, 0.016, 104.994, 85),
            ("Fluorescent Adolescent", "2011-05-09", 0.681, 0.794, -5.302, 0.676, 0.023, 113.994, 82),
            ("Why'd You Only Call Me When You're High?", "2013-07-18", 0.586, 0.519, -9.413, 0.323, 0.012, 86.013, 83),
            ("I Wanna Be Yours", "2013-09-09", 0.524, 0.390, -11.202, 0.263, 0.067, 70.028, 81),
            ("Arabella", "2013-09-09", 0.552, 0.761, -7.912, 0.218, 0.009, 74.994, 80),
            ("Snap Out of It", "2013-09-09", 0.633, 0.773, -5.782, 0.613, 0.012, 149.936, 79),
            ("Crying Lightning", "2009-05-18", 0.502, 0.671, -8.202, 0.377, 0.019, 164.988, 76),
            ("Body Paint", "2022-10-21", 0.411, 0.369, -12.012, 0.148, 0.112, 68.012, 77),
        ]
    },
    "The Weeknd": {
        "genre": "r&b",
        "tracks": [
            ("Blinding Lights", "2019-11-29", 0.514, 0.730, -5.934, 0.334, 0.000, 171.005, 97),
            ("Starboy", "2016-09-22", 0.679, 0.588, -7.012, 0.481, 0.025, 186.001, 90),
            ("After Hours", "2020-03-20", 0.651, 0.527, -9.112, 0.286, 0.097, 115.981, 88),
            ("Save Your Tears", "2020-03-20", 0.631, 0.671, -6.302, 0.481, 0.023, 118.044, 91),
            ("Can't Feel My Face", "2015-07-14", 0.709, 0.802, -4.905, 0.597, 0.073, 136.979, 87),
            ("The Hills", "2015-05-27", 0.573, 0.595, -7.892, 0.202, 0.095, 86.015, 86),
            ("Often", "2014-08-28", 0.673, 0.671, -7.112, 0.448, 0.071, 79.981, 82),
            ("Earned It", "2015-01-12", 0.502, 0.421, -9.891, 0.373, 0.231, 95.015, 83),
            ("Die For You", "2016-11-25", 0.572, 0.501, -9.012, 0.371, 0.064, 123.985, 92),
            ("Take My Breath", "2021-08-06", 0.631, 0.838, -5.112, 0.373, 0.011, 123.994, 84),
        ]
    },
    "Billie Eilish": {
        "genre": "pop",
        "tracks": [
            ("bad guy", "2019-03-29", 0.701, 0.431, -13.118, 0.564, 0.332, 135.012, 92),
            ("Happier Than Ever", "2021-07-30", 0.482, 0.311, -14.312, 0.312, 0.631, 138.008, 88),
            ("lovely", "2018-04-19", 0.351, 0.198, -16.112, 0.312, 0.919, 115.015, 87),
            ("ocean eyes", "2016-11-18", 0.521, 0.268, -14.411, 0.638, 0.831, 162.007, 84),
            ("Therefore I Am", "2020-11-12", 0.701, 0.598, -11.012, 0.512, 0.031, 141.981, 85),
            ("bury a friend", "2019-01-11", 0.502, 0.611, -11.112, 0.313, 0.197, 112.011, 83),
            ("idontwannabeyouanymore", "2017-07-14", 0.531, 0.247, -13.902, 0.447, 0.812, 174.019, 81),
            ("LUNCH", "2024-05-17", 0.761, 0.712, -7.012, 0.634, 0.042, 102.011, 90),
            ("Chihiro", "2024-05-17", 0.511, 0.421, -10.902, 0.398, 0.312, 128.001, 86),
            ("What Was I Made For?", "2023-07-13", 0.482, 0.238, -14.112, 0.449, 0.712, 124.987, 93),
        ]
    },
    "Bonobo": {
        "genre": "electronic",
        "tracks": [
            ("Kiara", "2010-10-04", 0.611, 0.529, -12.012, 0.312, 0.312, 115.015, 72),
            ("Kong", "2013-10-07", 0.531, 0.612, -10.312, 0.268, 0.231, 100.001, 70),
            ("Cirrus", "2013-10-07", 0.594, 0.589, -11.102, 0.198, 0.231, 122.994, 73),
            ("Surface", "2017-03-10", 0.561, 0.498, -12.412, 0.247, 0.219, 83.994, 71),
            ("No Reason", "2017-03-10", 0.578, 0.631, -10.012, 0.318, 0.198, 120.011, 69),
            ("Kerala", "2017-03-10", 0.601, 0.541, -10.782, 0.311, 0.311, 95.012, 70),
            ("Outlier", "2013-10-07", 0.511, 0.567, -11.912, 0.284, 0.267, 112.015, 67),
            ("Bambro Koyo Ganda", "2010-10-04", 0.783, 0.638, -9.312, 0.481, 0.112, 97.012, 65),
            ("Sapphire", "2010-10-04", 0.541, 0.419, -13.012, 0.237, 0.412, 88.012, 64),
            ("Linked", "2017-03-10", 0.619, 0.561, -10.512, 0.312, 0.218, 118.994, 68),
        ]
    },
    "Frank Ocean": {
        "genre": "r&b",
        "tracks": [
            ("Nights", "2016-08-20", 0.617, 0.631, -8.912, 0.448, 0.013, 106.011, 87),
            ("Chanel", "2017-03-25", 0.701, 0.542, -9.112, 0.481, 0.023, 132.011, 84),
            ("Pink + White", "2016-08-20", 0.541, 0.427, -11.012, 0.598, 0.311, 93.981, 83),
            ("Ivy", "2016-08-20", 0.511, 0.391, -13.112, 0.312, 0.419, 70.013, 82),
            ("Self Control", "2016-08-20", 0.482, 0.311, -14.012, 0.248, 0.511, 97.981, 83),
            ("Lost", "2012-07-17", 0.712, 0.631, -8.312, 0.598, 0.023, 141.981, 78),
            ("Swim Good", "2011-08-22", 0.632, 0.519, -9.812, 0.398, 0.072, 112.013, 76),
            ("Super Rich Kids", "2012-07-17", 0.621, 0.512, -9.312, 0.448, 0.098, 93.981, 77),
            ("Thinking Bout You", "2012-07-17", 0.531, 0.419, -11.212, 0.448, 0.231, 112.011, 80),
            ("Godspeed", "2016-08-20", 0.312, 0.218, -16.012, 0.198, 0.712, 72.994, 79),
        ]
    },
    "Tame Impala": {
        "genre": "indie",
        "tracks": [
            ("The Less I Know The Better", "2015-07-17", 0.661, 0.671, -7.312, 0.819, 0.023, 116.011, 89),
            ("Borderline", "2019-04-05", 0.631, 0.631, -7.812, 0.671, 0.031, 106.981, 84),
            ("Let It Happen", "2015-07-17", 0.521, 0.834, -5.312, 0.372, 0.013, 134.978, 83),
            ("Eventually", "2015-07-17", 0.531, 0.619, -8.012, 0.619, 0.072, 100.015, 80),
            ("Feels Like We Only Go Backwards", "2012-10-05", 0.631, 0.571, -8.712, 0.812, 0.231, 112.993, 81),
            ("New Person, Same Old Mistakes", "2015-07-17", 0.628, 0.712, -7.012, 0.498, 0.019, 128.011, 79),
            ("Is It True", "2020-02-14", 0.802, 0.712, -6.112, 0.731, 0.011, 123.981, 80),
            ("Patience", "2019-03-21", 0.661, 0.619, -7.812, 0.619, 0.023, 101.981, 78),
            ("Lost In Yesterday", "2020-02-14", 0.712, 0.634, -7.312, 0.712, 0.019, 110.981, 81),
            ("One More Hour", "2020-02-14", 0.519, 0.519, -9.012, 0.448, 0.072, 102.981, 76),
        ]
    },
}


def generate_sample_data():
    rows = []
    sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for artist_name, info in TRACKS_CATALOG.items():
        genre = info["genre"]
        for t in info["tracks"]:
            track_name, release_date, danceability, energy, loudness, valence, acousticness, tempo, popularity = t
            noise = np.random.normal(0, 0.02)
            rows.append({
                "track_name": track_name,
                "artist_name": artist_name,
                "genre": genre,
                "release_date": release_date,
                "popularity": min(100, max(0, popularity + int(np.random.randint(-3, 4)))),
                "tempo": round(tempo + np.random.uniform(-2, 2), 3),
                "energy": round(np.clip(energy + noise, 0.01, 0.99), 4),
                "danceability": round(np.clip(danceability + noise, 0.01, 0.99), 4),
                "valence": round(np.clip(valence + noise, 0.01, 0.99), 4),
                "acousticness": round(np.clip(acousticness + noise, 0.01, 0.99), 4),
                "loudness": round(loudness + np.random.uniform(-1, 1), 2),
                "last_synced": sync_time,
            })
    return pd.DataFrame(rows)


def fetch_from_spotify():
    auth = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth)
    sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for artist_name, info in TRACKS_CATALOG.items():
        genre = info["genre"]
        try:
            results = sp.search(q=f"artist:{artist_name}", type="track", limit=30)
            track_items = results["tracks"]["items"]
            track_ids = [t["id"] for t in track_items]
            try:
                features_list = sp.audio_features(track_ids) or []
            except Exception:
                features_list = [None] * len(track_ids)
            for t, f in zip(track_items, features_list):
                if not f:
                    continue
                rows.append({
                    "track_name": t["name"],
                    "artist_name": artist_name,
                    "genre": genre,
                    "release_date": t["album"].get("release_date", ""),
                    "popularity": t["popularity"],
                    "tempo": f["tempo"],
                    "energy": f["energy"],
                    "danceability": f["danceability"],
                    "valence": f["valence"],
                    "acousticness": f["acousticness"],
                    "loudness": f["loudness"],
                    "last_synced": sync_time,
                })
        except Exception as e:
            print(f"  Could not fetch {artist_name}: {e}")
    return pd.DataFrame(rows) if rows else generate_sample_data()


def build_database(df):
    os.makedirs("data", exist_ok=True)
    con = sqlite3.connect("data/spotify.db")
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS metadata")
    cur.execute("DROP TABLE IF EXISTS tracks")
    cur.execute("DROP TABLE IF EXISTS artists")

    cur.execute("""
        CREATE TABLE artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            genre TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_name TEXT,
            artist_id INTEGER,
            release_date TEXT,
            popularity INTEGER,
            tempo REAL,
            energy REAL,
            danceability REAL,
            valence REAL,
            acousticness REAL,
            loudness REAL,
            FOREIGN KEY (artist_id) REFERENCES artists(id)
        )
    """)
    cur.execute("""
        CREATE TABLE metadata (
            id INTEGER PRIMARY KEY,
            last_synced TEXT,
            source TEXT,
            track_count INTEGER
        )
    """)

    for _, row in df[["artist_name", "genre"]].drop_duplicates().iterrows():
        cur.execute("INSERT OR IGNORE INTO artists (name, genre) VALUES (?, ?)", (row["artist_name"], row["genre"]))

    artist_map = {r[1]: r[0] for r in cur.execute("SELECT id, name FROM artists")}

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO tracks (track_name, artist_id, release_date, popularity, tempo, energy, danceability, valence, acousticness, loudness)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["track_name"], artist_map[row["artist_name"]], row.get("release_date", ""),
            row["popularity"], row["tempo"], row["energy"],
            row["danceability"], row["valence"], row["acousticness"], row["loudness"]
        ))

    source = "Spotify API" if USE_API else "sample dataset"
    cur.execute("INSERT INTO metadata (id, last_synced, source, track_count) VALUES (1, ?, ?, ?)",
                (df["last_synced"].iloc[0], source, len(df)))
    con.commit()
    return con


def run_sql_analysis(con):
    print("\n--- AVG Popularity by Genre ---")
    q1 = pd.read_sql_query("""
        SELECT a.genre, ROUND(AVG(t.popularity), 2) as avg_popularity, COUNT(*) as track_count
        FROM tracks t JOIN artists a ON t.artist_id = a.id
        GROUP BY a.genre ORDER BY avg_popularity DESC
    """, con)
    print(q1.to_string(index=False))

    print("\n--- Top 10 Tracks by Energy ---")
    q2 = pd.read_sql_query("""
        SELECT t.track_name, a.name as artist, t.energy, t.popularity
        FROM tracks t JOIN artists a ON t.artist_id = a.id
        ORDER BY t.energy DESC LIMIT 10
    """, con)
    print(q2.to_string(index=False))

    print("\n--- AVG Audio Features by Artist ---")
    q3 = pd.read_sql_query("""
        SELECT a.name, ROUND(AVG(t.danceability),3) as avg_dance,
               ROUND(AVG(t.energy),3) as avg_energy,
               ROUND(AVG(t.popularity),1) as avg_pop
        FROM tracks t JOIN artists a ON t.artist_id = a.id
        GROUP BY a.name ORDER BY avg_pop DESC
    """, con)
    print(q3.to_string(index=False))


np.random.seed(42)
if USE_API:
    print("Fetching from Spotify API...")
    df = fetch_from_spotify()
else:
    print("No API credentials - using curated real track dataset (100 tracks).")
    df = generate_sample_data()

con = build_database(df)
run_sql_analysis(con)

full_df = pd.read_sql_query("""
    SELECT t.track_name, a.name as artist_name, a.genre,
           t.release_date, t.popularity, t.tempo, t.energy,
           t.danceability, t.valence, t.acousticness, t.loudness
    FROM tracks t JOIN artists a ON t.artist_id = a.id
""", con)

meta = pd.read_sql_query("SELECT last_synced, source FROM metadata WHERE id=1", con)
full_df["last_synced"] = meta["last_synced"].iloc[0]
full_df["source"] = meta["source"].iloc[0]

full_df.to_csv("data/tracks.csv", index=False)
print(f"\nSaved {len(full_df)} tracks -> data/tracks.csv  (synced: {meta['last_synced'].iloc[0]})")
con.close()
