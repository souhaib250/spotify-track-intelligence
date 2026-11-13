import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

df = pd.read_csv("data/tracks.csv")

features = ["energy", "danceability", "valence", "acousticness", "tempo"]
X = df[features].copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(X_scaled)

centers = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), columns=features)

scores = {}
for i, row in centers.iterrows():
    scores[i] = {
        "high_energy": row["energy"] * 0.5 + row["danceability"] * 0.3 - row["acousticness"] * 0.2,
        "acoustic": row["acousticness"] * 0.6 - row["energy"] * 0.2 + row["valence"] * 0.1,
        "dark": -row["valence"] * 0.5 - row["acousticness"] * 0.1 + row["energy"] * 0.2,
        "chill": row["valence"] * 0.3 + row["acousticness"] * 0.1 - row["energy"] * 0.3,
    }

mood_map = {}
used = set()
priority = ["high_energy", "acoustic", "dark", "chill"]
label_names = {
    "high_energy": "High Energy",
    "acoustic": "Acoustic Mood",
    "dark": "Dark / Intense",
    "chill": "Chill Vibes",
}

for mood_key in priority:
    candidates = [i for i in scores if i not in mood_map.values()]
    if not candidates:
        break
    best_cluster = max(candidates, key=lambda i: scores[i][mood_key])
    mood_map[mood_key] = best_cluster

cluster_to_label = {v: label_names[k] for k, v in mood_map.items()}
remaining = [i for i in range(4) if i not in cluster_to_label]
remaining_labels = [l for l in label_names.values() if l not in cluster_to_label.values()]
for i, lbl in zip(remaining, remaining_labels):
    cluster_to_label[i] = lbl

df["mood"] = df["cluster"].map(cluster_to_label)

print("Cluster distribution:")
print(df["mood"].value_counts())
print("\nCluster centers (original scale):")
print(centers.round(3))

X_model = df[features]
y = df["popularity"]

X_train, X_test, y_train, y_test = train_test_split(X_model, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)
r2 = r2_score(y_test, preds)
mae = mean_absolute_error(y_test, preds)

print(f"\nRandomForest -> R2: {r2:.3f}  |  MAE: {mae:.2f}")

importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
print("\nFeature importances:")
print(importances.round(4))

df.to_csv("data/tracks_clustered.csv", index=False)

import json, os
os.makedirs("data", exist_ok=True)
meta = {"r2": round(r2, 3), "mae": round(mae, 2)}
with open("data/model_meta.json", "w") as f:
    json.dump(meta, f)

print(f"\nSaved -> data/tracks_clustered.csv + data/model_meta.json")
