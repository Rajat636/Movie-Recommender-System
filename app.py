import streamlit as st
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def fetch_poster(movie_id):
    # URL for making the request
    url = 'https://api.themoviedb.org/3/movie/65?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US'

    # Retry with exponential backoff
    response = None
    for _ in range(3):  # Retry 3 times
        try:
            response = requests_retry_session().get(url)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            time.sleep(2 ** _)  # Exponential backoff: 2, 4, 8 seconds

    if response is not None:
        data = response.json()
        print(response.text)
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    else:
        print("Failed to fetch the poster.")
        return None



# method to recommend movies by calculating similarity from similarity matrix
def recommend(sel_movie):
    movie_index = movies[movies["title"] == sel_movie].index[0]
    similarity_scores = similarity[movie_index]
    movie_list = sorted(list(enumerate(similarity_scores)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movies_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movieId
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters


# loading pickle files having our database and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)  

similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommender System')

# Input box to take input from user
selected_movie = st.selectbox(
    'Enter movie for recommendations',
    movies['title'].values
)

# Button to recommend movies
if st.button('Recommend'):
    names, posters = recommend(selected_movie)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])



