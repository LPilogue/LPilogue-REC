import pickle
import pandas as pd
import spotipy
from spotipy import SpotifyClientCredentials

from app.resource.server import Client_id, Client_secret


def recommend_songs(input_features):
    """
    Gets the top 5 recommendations using the KNN model.
    """
    try:
        # Load the model and DataFrame information
        loaded_data = pickle.load(open('../model_resource/knn_model_with_data.pkl', 'rb'))
        loaded_model = loaded_data['model']
        columns = loaded_data['dataframe_columns']
        data = loaded_data['dataframe_data']

        # Recreate the DataFrame from the stored information
        loaded_df = pd.DataFrame(data, columns=columns)

        # input_features에서 value만 추출
        input_features = [value for _, value in input_features.items()]

        # Get the recommendations
        distances, indices = loaded_model.kneighbors([input_features])

        recommendations = []
        for i in indices[0]:
            song = search_song(loaded_df.iloc[i]['song'], loaded_df.iloc[i]['artist'])
            recommendations.append(song)
        return recommendations
    except FileNotFoundError:
        print("Error: knn_model_with_data.pkl not found. Please run the KNN training code first.")
        return []


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
            "artist": ", ".join(artist["name"] for artist in track["artists"]),
            "filePath": track["album"]["images"][0]["url"]
        }
        return song_info
    else:
        return "Song not found."

# Example usage
song_title = "Shape of You"
artist_name = "Ed Sheeran"

song_info = search_song(song_title, artist_name)
if isinstance(song_info, dict):
    print(f"Title: {song_info['name']}")
    print(f"Artist: {song_info['artist']}")
    print(f"Album image: {song_info['filePath']}")

else:
    print(song_info)