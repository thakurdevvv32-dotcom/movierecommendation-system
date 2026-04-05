let userHistory = [];

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Fetch available movies to populate the select dropdown
    try {
        const res = await fetch('/api/movies');
        const data = await res.json();
        
        const select = document.getElementById('movie-select');
        data.movies.forEach(movie => {
            const option = document.createElement('option');
            option.value = movie;
            option.textContent = movie;
            select.appendChild(option);
        });
    } catch (e) {
        console.error("Failed to load movies", e);
    }

    // 2. Add event listener to the "Add" button
    document.getElementById('add-btn').addEventListener('click', () => {
        const select = document.getElementById('movie-select');
        const selectedMovie = select.value;
        
        if (selectedMovie && !userHistory.includes(selectedMovie)) {
            userHistory.push(selectedMovie);
            renderHistory();
            fetchRecommendations();
            
            // Reset select
            select.value = '';
        }
    });
});

function renderHistory() {
    const container = document.getElementById('history-tags');
    container.innerHTML = '';
    
    if (userHistory.length === 0) {
        container.innerHTML = '<p class="empty-state">No movies added yet. Add some above to get recommendations!</p>';
        return;
    }
    
    userHistory.forEach((movie, index) => {
        const tag = document.createElement('div');
        tag.className = 'tag';
        tag.innerHTML = `
            <span>${movie}</span>
            <button onclick="removeMovie(${index})">&times;</button>
        `;
        container.appendChild(tag);
    });
}

function removeMovie(index) {
    userHistory.splice(index, 1);
    renderHistory();
    fetchRecommendations();
}

async function fetchRecommendations() {
    const recContainer = document.getElementById('recommendations-container');
    const cardsGrid = document.getElementById('movie-cards');
    
    if (userHistory.length === 0) {
        recContainer.style.display = 'none';
        return;
    }

    try {
        const res = await fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ history: userHistory })
        });
        
        const data = await res.json();
        
        if (data.recommendations && data.recommendations.length > 0) {
            recContainer.style.display = 'block';
            cardsGrid.innerHTML = '';
            
            data.recommendations.forEach((rec, i) => {
                const percentage = Math.round(rec.score * 100);
                
                const card = document.createElement('div');
                card.className = 'movie-card';
                card.style.animation = `fadeIn 0.4s ease forwards ${i * 0.1}s`;
                card.style.opacity = '0';
                
                card.innerHTML = `
                    <h4>${rec.title}</h4>
                    <p class="genre">${rec.genres}</p>
                    <span class="score">Match: ${percentage}%</span>
                `;
                
                cardsGrid.appendChild(card);
            });
        } else {
            recContainer.style.display = 'none';
        }
    } catch (e) {
        console.error("Failed to fetch recommendations", e);
    }
}
