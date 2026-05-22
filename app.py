import os
import gdown

if not os.path.exists("similarity.pkl"):
    url = "https://drive.google.com/uc?id=1yawrT4i5lK4QFSzGRY2IzjuRmRzwHAGL"
    gdown.download(url, "similarity.pkl", quiet=False)

import streamlit as st
import pickle
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Setup retry session
session = requests.Session()
retry = Retry(connect=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Function to fetch poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c2195863612d32682d6e417834ab8c74&language=en-US"
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Poster"
    except Exception:
        return "https://via.placeholder.com/500x750.png?text=Error"

# Recommendation function
def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:  # top 5
        movie_id = movies.iloc[i[0]]['movie_id']  # ✅ safer than dot notation
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]]['title'])

    return recommended_movie_names, recommended_movie_posters


# Streamlit UI
st.header('🎬 Movie Recommender System')

# Load data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button("Show Recommendation"):
    names, posters = recommend(selected_movie)

    if names:  # ✅ only display if found
        cols = st.columns(5)
        for i in range(len(names)):
            with cols[i]:
                st.image(posters[i], use_container_width=True)
                st.markdown(
                    f"<p style='text-align: center; font-weight: bold;'>{names[i]}</p>",
                    unsafe_allow_html=True
                )
    else:
        st.warning("Movie not found in the dataset.")
