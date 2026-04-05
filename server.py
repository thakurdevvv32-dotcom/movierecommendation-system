from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
import recommendation # Import our existing logic
import os

app = FastAPI(title="Movie Recommender API")

class RecommendationRequest(BaseModel):
    history: List[str]

# Create recommendator on startup
df, cosine_sim, indices = recommendation.create_recommendator('movies.csv')

@app.get("/api/movies")
def get_movies():
    if df is not None:
        return {"movies": df['title'].tolist()}
    return {"movies": []}

@app.post("/api/recommend")
def get_recommendations(req: RecommendationRequest):
    if df is None:
        return JSONResponse(status_code=500, content={"error": "Dataset not loaded"})
        
    history = req.history
    if not history:
        return {"recommendations": []}
    
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
        return {"recommendations": []}
        
    avg_sim_scores = avg_sim_scores / valid_movies
    sim_scores = list(enumerate(avg_sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    history_indices = []
    for title in history:
        name_idx = indices.get(title)
        if name_idx is not None:
             if isinstance(name_idx, pd.Series):
                 history_indices.extend(name_idx.tolist())
             else:
                 history_indices.append(name_idx)
                 
    # filter out already picked movies
    sim_scores = [x for x in sim_scores if x[0] not in history_indices]
    sim_scores = sim_scores[:5]
    
    results = []
    for sim in sim_scores:
        idx = sim[0]
        results.append({
            "title": str(df['title'].iloc[idx]),
            "genres": str(df['genres'].iloc[idx]),
            "score": float(sim[1])
        })
        
    return {"recommendations": results}

# Serve static files for the frontend
os.makedirs("public", exist_ok=True)
app.mount("/", StaticFiles(directory="public", html=True), name="public")
