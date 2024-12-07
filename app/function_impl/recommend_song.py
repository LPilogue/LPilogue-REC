import pickle
import pandas as pd


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
            recommendations.append({'artist': loaded_df.iloc[i]['artist'], 'song': loaded_df.iloc[i]['song']})
        return recommendations
    except FileNotFoundError:
        print("Error: knn_model_with_data.pkl not found. Please run the KNN training code first.")
        return []