import pickle

import numpy as np
import pandas as pd
import requests
import spotipy
from scipy.spatial.distance import cosine
from sklearn.feature_extraction.text import TfidfVectorizer
from spotipy import SpotifyClientCredentials

from app.resource.server import Client_id, Client_secret, youtube_api



def recommend_songs(input_features, badSongList):
    """
    Gets the top 5 recommendations using the KNN model.
    """
    try:
        # Load the model and DataFrame information
        loaded_data = pickle.load(open('model_resource/knn_model_with_data.pkl', 'rb'))
        loaded_model = loaded_data['model']
        columns = loaded_data['dataframe_columns']
        data = loaded_data['dataframe_data']

        # Recreate the DataFrame from the stored information
        loaded_df = pd.DataFrame(data, columns=columns)

        print(loaded_df.head())

        # input_features에서 value만 추출
        input_features = [value for _, value in input_features.items()]

        # Get the recommendations
        distances, indices = loaded_model.kneighbors([input_features])


        bad_song_set={(song['name'],song['artist']) for song in badSongList}
        recommendations = []
        for i in indices[0]:
            if len(recommendations)==5:
                break
            title=loaded_df.iloc[i]['track_name']
            artist=loaded_df.iloc[i]['track_artist']
            if (title,artist) in bad_song_set:
                continue
            song = search_song(title, artist)
            recommendations.append(song)

        mean_similarity = calculate_mean_similarity(input_features, indices[0], loaded_df)
        print(f"Mean similarity: {mean_similarity}")
        return recommendations
    except FileNotFoundError:
        print("Error: knn_model_with_data.pkl not found. Please run the KNN training code first.")
        return []

def calculate_mean_similarity(input_features, indices, df):
    similarities = []
    for i in indices:
        recommended_features = df.iloc[i].drop(['track_name', 'track_artist', 'lyrics']).values
        similarity = 1 - cosine(input_features, recommended_features)
        similarities.append(similarity)
    return np.mean(similarities)

def search_song(song_title, artist_name):
    # Set up Spotipy client
    client_credentials_manager = SpotifyClientCredentials(client_id=Client_id, client_secret=Client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    query = f"track:{song_title} artist:{artist_name}"
    results = sp.search(q=query, type="track", limit=1)


    if results['tracks']['items']:
        track = results['tracks']['items'][0]

        song_info = {
            "name": track["name"],
            "type": "RECOMMENDED",
            "isLiked": 0,
            "filePath": track["album"]["images"][0]["url"],
            "artist": ", ".join(artist["name"] for artist in track["artists"]),
            "songURI": get_youtube_url(song_title, artist_name)
        }
        return song_info
    else:
        return "Song not found."


def get_youtube_url(song_title, artist_name):
        request_url=f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={song_title}+{artist_name}&key={youtube_api}"
        response=requests.get(request_url)
        response_json=response.json()
        video_id=response_json['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
