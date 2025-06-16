import pickle
import numpy as np
import pandas as pd
import requests
import spotipy
from scipy.spatial.distance import cosine
from sklearn.feature_extraction.text import TfidfVectorizer
from spotipy import SpotifyClientCredentials

from app.resource.server import Client_id, Client_secret, youtube_api
import os



def recommend_songs(input_features, badSongList):
    if badSongList is None:
        badSongList = []
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

        # input_features에서 value만 추출
        input_features = [value for _, value in input_features.items()]

        # Get the recommendations (KNN 기반 4곡)
        distances, indices = loaded_model.kneighbors([input_features])

        bad_song_set = {(song['name'], song['artist']) for song in badSongList}
        recommendations = []
        used_indices = set()
        # KNN 기반 추천
        for i in indices[0]:
            if len(recommendations) == 4:
                break
            title = loaded_df.iloc[i]['track_name']
            artist = loaded_df.iloc[i]['track_artist']
            if (title, artist) in bad_song_set:
                continue
            song = search_song(title, artist)
            if song is not None:
                recommendations.append(song)
                used_indices.add(i)

        # 전체 DB에서 badSongList, 이미 추천된 곡을 제외하고 랜덤 1곡 추천
        exclude_set = set((song['name'], song['artist']) for song in badSongList)
        exclude_set.update((song['name'], song['artist']) for song in recommendations)
        candidates = loaded_df[~loaded_df.apply(lambda row: (row['track_name'], row['track_artist']) in exclude_set, axis=1)]
        # 랜덤 추천에서 유튜브 링크가 있는 곡만 추가
        if not candidates.empty:
            # 여러 번 시도해서 유튜브 링크가 있는 곡을 찾음
            for _ in range(len(candidates)):
                random_row = candidates.sample(1).iloc[0]
                random_song = search_song(random_row['track_name'], random_row['track_artist'])
                if random_song is not None:
                    recommendations.append(random_song)
                    break

        # 만약 추천 곡이 5곡이 안 되면, KNN/랜덤 후보에서 반복해서 곡을 추가
        # (유튜브 링크가 있는 곡만)
        for i in indices[0]:
            if len(recommendations) == 5:
                break
            if i in used_indices:
                continue
            title = loaded_df.iloc[i]['track_name']
            artist = loaded_df.iloc[i]['track_artist']
            if (title, artist) in bad_song_set:
                continue
            song = search_song(title, artist)
            if song is not None and song not in recommendations:
                recommendations.append(song)

        # 그래도 5곡이 안 되면 전체 DB에서 반복해서 채움
        if len(recommendations) < 5:
            for idx, row in loaded_df.iterrows():
                if len(recommendations) == 5:
                    break
                if (row['track_name'], row['track_artist']) in exclude_set:
                    continue
                song = search_song(row['track_name'], row['track_artist'])
                if song is not None and song not in recommendations:
                    recommendations.append(song)

        mean_similarity = calculate_mean_similarity(input_features, indices[0], loaded_df)

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
        song_uri = get_youtube_url(song_title, artist_name)
        if not song_uri:
            return None  # 유튜브 링크 없으면 추천에서 제외
        song_info = {
            "name": track["name"],
            "type": "RECOMMENDED",
            "isLiked": 0,
            "imagePath": track["album"]["images"][0]["url"],
            "artist": ", ".join(artist["name"] for artist in track["artists"]),
            "songURI": song_uri
        }
        return song_info
    else:
        return None

def get_youtube_url(song_title, artist_name):
    request_url = (
        f"https://www.googleapis.com/youtube/v3/search?"
        f"part=snippet&maxResults=1&q={song_title}+{artist_name}&key={youtube_api}"
    )
    response = requests.get(request_url)
    response_json = response.json()
    video_id = response_json['items'][0]['id']['videoId']
    return f"https://www.youtube.com/watch?v={video_id}"