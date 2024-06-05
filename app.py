import streamlit as st
import pickle
import pandas as pd
import requests
import time
import base64

# Streamlit App Configuration
st.set_page_config(page_title="Movie Recommender", page_icon="")


def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = f'''
    <style>
    @keyframes moveBackground {{
        from {{
            background-position: 0% 0%;
        }}
        to {{
            background-position: 100% 100%;
        }}
    }}

    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        animation: moveBackground 7.5s linear infinite; /* Background animation */
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_background('bgimg.jpg')


# Rest of the code remains the same...

def fetch_poster(movie_id, max_retries=3):
    retries = 0
    while retries < 50:
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
            data = requests.get(url)
            data = data.json()
            poster_path = data['poster_path']
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        except Exception as e:
            retries += 1
            time.sleep(0.1)  # Wait for a second before retrying
    st.error(f"Failed to fetch poster for movie ID {movie_id} after {max_retries} attempts.")
    return None


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters


similarity = pickle.load(open('similarity.pkl', 'rb'))

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Layout and Styling
st.markdown("""
<style>
body {
  font-family: sans-serif;
  background: linear-gradient(to right, #f7cac9 0%, #ffe2c5 50%, #f7cac9 100%);  /* Colorful background gradient */
  margin: 0;
  padding: 0;
}

.app-title {
  text-align: center;
  font-size: 2.5em;
  margin: 20px 0;
  color: #333;
}

.movie-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  margin: 20px 0;
}

.movie {
  display: flex;
  align-items: center;
  margin-bottom: 20px; /* Add margin between movies */
}

.movie-poster {
  width: 200px;
  height: 300px;
  margin-right: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  border-radius: 5px;
}

.movie-title {
  font-size: 1.5em;
  font-weight: bold;
  margin: 0;
  color: #FFFFFF;  /* Bright color for text */
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<h1 class='app-title'>Movie Recommender</h1>", unsafe_allow_html=True)

selected_movie_name = st.selectbox('Select a Movie',
                                   movies['title'].values)

if st.button('Recommend'):
    names, poster = recommend(selected_movie_name)

    st.markdown("<div class='movie-container'>", unsafe_allow_html=True)
    for i in range(len(names)):
        st.markdown(f"""
        <div class="movie">
          <img class="movie-poster" src="{poster[i]}" alt="{names[i]}">
          <p class="movie-title">{names[i]}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
