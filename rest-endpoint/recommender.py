import ssl
import os
import time
import pandas as pd
import pickle
from flask import Flask, request, jsonify


app = Flask(__name__)


last_mod_time = None
rules = None


def get_file_data(filename):
    global last_mod_time
    global rules
    
    current_mod_time = os.path.getmtime(filename)

    if last_mod_time is None or current_mod_time > last_mod_time:
        with open(filename, "rb") as f:
            rules = pickle.load(f)
        last_mod_time = current_mod_time

def playlists_recommendation(client_songs):
    """
    Recommends existing playlists given a list of songs
    
    Parameters:
    client_songs (list): list of songs coming from the request

    Returns:
    list: playlist ids
    """
    
    global rules

    ssl._create_default_https_context = ssl._create_unverified_context
    url = os.environ["DS_URL"]
    playlists = pd.read_csv(url)

    # Recover songs unique identifiers from their names
    song_uris = playlists[playlists['track_name'].isin(client_songs)]['track_uri'].drop_duplicates().tolist()

    # One-hot encoding of playlists dataframe
    playlists['value'] = 1
    playlists = playlists.pivot_table(index='pid', columns='track_uri', values='value', fill_value=0)
    playlists = playlists.astype(bool)
    
    applicable_rules = rules[rules['antecedents'].apply(lambda x: set(x).issubset(set(song_uris)))]
    recommended_songs = list(set().union(*applicable_rules['consequents']))
    recommended_playlists = playlists[playlists[recommended_songs].any(axis=1).tolist()].index.tolist()

    return recommended_playlists

@app.route('/api/recommend', methods=["POST"])
def recommend():
    """
    This endpoint responds to playlist recommendation requests
    """

    get_file_data("/ml-data/rules.pickle")

    data = request.json
    recommended_playlists = playlists_recommendation(data["songs"])
    version = os.environ["IMAGE_VERSION"]
    model_date = time.ctime(last_mod_time)

    return jsonify({"playlist_ids": recommended_playlists,
                    "version": version,
                    "model_date": model_date}), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0")