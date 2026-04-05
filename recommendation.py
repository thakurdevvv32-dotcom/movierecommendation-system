import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import argparse

def create_recommendator(data_path):
    # 1. Load a dataset containing movie titles and genres
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: Dataset {data_path} not found.")
        return None, None, None
    
    if 'title' not in df.columns or 'genres' not in df.columns:
        print("Error: Dataset must contain 'title' and 'genres' columns.")
        return None, None, None

    # 2. Preprocess the data using pandas (fill empty genres)
    df['genres'] = df['genres'].fillna('')
    
    # 3. Convert text features (genres) into numerical vectors using TF-IDF from scikit-learn
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['genres'])
    
    # 4. Compute similarity between movies using cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Create a mapping from title to index for fast lookup
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()
    
    return df, cosine_sim, indices

# 5. Recommend top 5 similar movies based on user history of choices
def get_recommendations(history, df, cosine_sim, indices, top_n=5):
    import numpy as np
    
    # Initialize an array of zeros for the scores
    avg_sim_scores = np.zeros(len(cosine_sim))
    
    valid_movies = 0
    for title in history:
        if title in indices:
            idx = indices[title]
            if isinstance(idx, pd.Series):
               idx = idx.iloc[0]
            avg_sim_scores += cosine_sim[idx]
            valid_movies += 1
            
    if valid_movies == 0:
        return
        
    avg_sim_scores = avg_sim_scores / valid_movies
    
    # Get pairwise similarity scores combining all choices
    sim_scores = list(enumerate(avg_sim_scores))
    
    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Filter out movies that the user has already chosen
    history_indices = []
    for title in history:
        name_idx = indices.get(title)
        if name_idx is not None:
             if isinstance(name_idx, pd.Series):
                 history_indices.extend(name_idx.tolist())
             else:
                 history_indices.append(name_idx)
                 
    sim_scores = [x for x in sim_scores if x[0] not in history_indices]
    
    # Get the scores of the most similar movies
    sim_scores = sim_scores[:top_n]
    movie_indices = [i[0] for i in sim_scores]
    
    # 6. Display recommended movie names clearly
    label = f"'{history[-1]}'" if len(history) == 1 else f"{', '.join(history)}"
    print(f"\nBecause you liked {label}, we recommend:")
    print("-" * 40)
    for i, idx in enumerate(movie_indices, 1):
        print(f"{i}. {df['title'].iloc[idx]} (Genres: {df['genres'].iloc[idx]})")
    print("-" * 40)

def main():
    dataset_path = "movies.csv"
    print(f"Loading data from {dataset_path}...")
    df, cosine_sim, indices = create_recommendator(dataset_path)
    
    if df is not None:
        print("\nHere are some available movies in the dataset:")
        print(", ".join(df['title'].tolist()[:15]))
        
        user_history = []
        
        while True:
            movie_title = input("\nEnter a movie title exactly as it appears above (or 'q' to quit): ").strip()
            if movie_title.lower() == 'q':
                break
                
            if movie_title not in indices:
                print(f"Sorry, '{movie_title}' is not in the database.")
                continue
                
            user_history.append(movie_title)
            
            get_recommendations(user_history, df, cosine_sim, indices)

if __name__ == "__main__":
    main()
