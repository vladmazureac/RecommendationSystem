from flask import Blueprint, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestRegressor

# Definirea blueprint-ului
recommendation_blueprint = Blueprint('recommendation', __name__)

# Citirea datelor
movies = pd.read_csv("database/movie_data.csv")

from sklearn.neighbors import NearestNeighbors

# Preprocesarea datelor
tfidf = TfidfVectorizer(stop_words='english')
features = ['genres','production_companies','cast']
for feature in features:
    movies[feature] = movies[feature].fillna('').astype(str)
movies['combined_features'] = movies[features].apply(lambda x: ' '.join(x), axis=1)
tfidf_matrix = tfidf.fit_transform(movies['combined_features'])

# Inițializăm modelul KNN
knn_model = NearestNeighbors(n_neighbors=11, algorithm='auto', metric='cosine')
knn_model.fit(tfidf_matrix)

def get_movie_recommendation(movie_name, min_rating=6, knn_model=knn_model):
    movie_index = movies[movies['title'].str.contains(movie_name)].index
    if len(movie_index) == 0:
        return []
    movie_index = movie_index[0]
    
    # Folosim KNN pentru a găsi cele mai similare filme
    distances, indices = knn_model.kneighbors(tfidf_matrix[movie_index])
    
    recommended_movies = []
    for idx in indices.flatten():
        movie_info = movies.iloc[idx]
        
        # Verificăm dacă rating-ul filmului este mai mare sau egal cu rating-ul minim specificat
        if movie_info['vote_average'] >= min_rating:
            recommended_movie = {
                'title': movie_info['title'],
                'genres': eval(movie_info['genres']),  # Convertim lista de genuri la o listă reală
                'production_companies': eval(movie_info['production_companies']),  # Convertim lista de producători la o listă reală
                'production_countries': movie_info['production_countries'],
                'release_date': movie_info['release_date'],
                'runtime': f"{int(movie_info['runtime']) // 60}h {int(movie_info['runtime']) % 60}m",
                'vote_average': movie_info['vote_average'],
                'cast' : eval(movie_info['cast'])
            }
            recommended_movies.append(recommended_movie)
    
    return recommended_movies




def get_movies_by_preferences(genres, min_year, min_rating, knn_model=knn_model):
    # Filtrăm filmele după genuri, an și rating
    filtered_movies = movies[
        (movies['genres'].str.contains('|'.join(genres))) &
        (movies['release_date'].str.split('-').str[0].astype(int) >= min_year) &
        (movies['vote_average'] >= min_rating)
    ]
    
    # Inițializăm o listă goală pentru recomandările de filme
    recommended_movies = []
    
    # Parcurgem fiecare film filtrat
    for index, movie_info in filtered_movies.iterrows():
        recommended_movie = {
            'title': movie_info['title'],
            'genres': eval(movie_info['genres']),
            'production_companies': eval(movie_info['production_companies']),
            'production_countries': movie_info['production_countries'],
            'release_date': movie_info['release_date'],
            'runtime': f"{int(movie_info['runtime']) // 60}h {int(movie_info['runtime']) % 60}m",
            'vote_average': movie_info['vote_average'],
            'cast' : eval(movie_info['cast'])

        }
        
        # Adăugăm reprezentarea filmului la lista de recomandări
        recommended_movies.append(recommended_movie)
    
    return recommended_movies[:10]  # Returnăm primele 10 filme recomandate



def get_movies_by_rating(num_movies):
    
    # Sortăm DataFrame-ul de filme după rating în ordine descrescătoare
    sorted_movies = movies.sort_values(by='vote_average', ascending=False)
    
    # Selecționăm primele num_movies filme
    top_movies = sorted_movies.head(num_movies)
    
    # Inițializăm o listă goală pentru recomandările de filme
    recommended_movies = []
    
    # Parcurgem fiecare film din primele num_movies
    for index, movie_info in top_movies.iterrows():
        recommended_movie = {
            'title': movie_info['title'],
            'genres': eval(movie_info['genres']),
            'production_companies': eval(movie_info['production_companies']),
            'production_countries': movie_info['production_countries'],
            'release_date': movie_info['release_date'],
            'runtime': f"{int(movie_info['runtime']) // 60}h {int(movie_info['runtime']) % 60}m",
            'vote_average': movie_info['vote_average'],
            'cast' : eval(movie_info['cast'])

        }
        
        # Adăugăm reprezentarea filmului la lista de recomandări
        recommended_movies.append(recommended_movie)

    return recommended_movies




@recommendation_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        recommended_movies = get_movie_recommendation(movie_name)
        return render_template('recommendations.html', page_title="Filme asemănătoare cu " + movie_name, recommended_movies=recommended_movies)
    return render_template('index.html', page_title="Home")

@recommendation_blueprint.route('/recommendations_by_preferences', methods=['GET', 'POST'])
def recommendations_by_preferences():
    if request.method == 'POST':
        # Obținem preferințele utilizatorului din formular
        genres = request.form.getlist('genres')
        min_year = int(request.form['year'])
        min_rating = float(request.form['rating'])
        
        # Obținem recomandările de filme pe baza preferințelor utilizatorului
        recommended_movies = get_movies_by_preferences(genres, min_year, min_rating)
        
        # Returnăm o pagină care să afișeze recomandările
        return render_template('recommendations.html', page_title="Recomandările după Preferințe", recommended_movies=recommended_movies)
    
    # Dacă nu este o cerere POST, returnăm pagina de introducere a preferințelor
    return render_template('index.html', page_title="Preferences")

@recommendation_blueprint.route('/top_rated_movies', methods=['GET', 'POST'])
def recommendations_by_rating():
    if request.method == 'POST':
        # Obținem numărul dorit de filme din formular
        num_movies = int(request.form['number_of_movies'])
        
        # Obținem recomandările de filme cu cele mai mari ratinguri
        recommended_movies = get_movies_by_rating(num_movies)
        
        # Returnăm o pagină care să afișeze recomandările
        return render_template('recommendations.html', page_title="Filme cu cel mai mare rating", recommended_movies=recommended_movies)
    
    # Dacă nu este o cerere POST, returnăm pagina de introducere a numărului dorit de filme
    return render_template('index.html', page_title="Top Rated Movies")
