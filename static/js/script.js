const grid = document.querySelector("#movie-grid");
const statusMessage = document.querySelector("#status-message");
const movieCount = document.querySelector("#movie-count");
const searchInput = document.querySelector("#movie-search");
const syncButton = document.querySelector("#sync-button");

let allMovies = [];
let currentMovie = null;
let hlsInstance = null;

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);
}

function posterUrl(path) {
  return path ? `https://image.tmdb.org/t/p/w500${path}` : "";
}

function renderMovies(movies) {
  movieCount.textContent = `${movies.length} ${movies.length === 1 ? "title" : "titles"}`;
  if (!movies.length) {
    grid.innerHTML = `
      <div class="empty-state">
        <strong>No movie data yet.</strong><br>
        Add a valid <code>TMDB_API_KEY</code> to your local <code>.env</code> file, restart the server,
        and click <strong>Refresh titles</strong> to import popular movie metadata.
      </div>`;
    return;
  }

  grid.innerHTML = movies.map((movie) => {
    const poster = posterUrl(movie.poster_path);
    const year = movie.release_date ? String(movie.release_date).slice(0, 4) : "Year unknown";
    const rating = Number(movie.vote_average || 0).toFixed(1);
    
    return `
      <article class="movie-card" onclick="openModal(${escapeHtml(JSON.stringify(movie))})" style="cursor: pointer;">
        <div class="poster-frame">
          ${poster
            ? `<img src="${escapeHtml(poster)}" alt="Poster for ${escapeHtml(movie.title)}" loading="lazy" onerror="this.remove(); this.parentElement.insertAdjacentHTML('afterbegin', '<div class=&quot;poster-placeholder&quot;>SF</div>')">`
            : `<div class="poster-placeholder">SF</div>`}
          <span class="rating">★ ${escapeHtml(rating)}</span>
        </div>
        <h3 class="movie-title" title="${escapeHtml(movie.title)}">${escapeHtml(movie.title)}</h3>
        <p class="movie-meta">${escapeHtml(year)}</p>
      </article>`;
  }).join("");
}

async function loadMovies() {
  statusMessage.textContent = "Loading your movie catalog…";
  try {
    const response = await fetch("/api/movies");
    if (!response.ok) throw new Error("Could not load the movie catalog.");
    allMovies = await response.json();
    statusMessage.textContent = allMovies.length ? "" : "Your local catalog is ready to be populated.";
    renderMovies(allMovies);
  } catch (error) {
    statusMessage.textContent = "Could not connect to the app. Check that the FastAPI server is running.";
    movieCount.textContent = "Unavailable";
  }
}

async function syncMovies() {
  syncButton.disabled = true;
  syncButton.textContent = "Refreshing…";
  statusMessage.textContent = "Fetching popular movie metadata from TMDB…";
  try {
    const response = await fetch("/api/movies/sync", { method: "POST" });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || "Movie refresh failed.");
    await loadMovies();
    statusMessage.textContent = `${result.imported} movie records refreshed.`;
  } catch (error) {
    statusMessage.textContent = error.message || "Movie refresh failed. Check your API key and connection.";
  } finally {
    syncButton.disabled = false;
    syncButton.textContent = "Refresh titles";
  }
}

searchInput.addEventListener("input", () => {
  const query = searchInput.value.trim().toLowerCase();
  renderMovies(allMovies.filter((movie) => String(movie.title).toLowerCase().includes(query)));
});
syncButton.addEventListener("click", syncMovies);
loadMovies();

// --- Modal Logic ---
function openModal(movie) {
    currentMovie = movie;
    const modal = document.getElementById('movieModal');
    
    document.getElementById('modal-title').innerText = movie.title;
    document.getElementById('modal-overview').innerText = movie.overview || "No overview available.";
    document.getElementById('modal-rating').innerText = `⭐ ${movie.vote_average}`;
    document.getElementById('modal-date').innerText = movie.release_date || "Release date not available";
    
    const backdropPath = movie.backdrop_path || movie.poster_path;
    if (backdropPath) {
        document.getElementById('modal-backdrop-img').src = `https://image.tmdb.org/t/p/w1280${backdropPath}`;
    } else {
        document.getElementById('modal-backdrop-img').src = 'https://via.placeholder.com/800x300?text=No+Image';
    }

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('movieModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

function playMovie() {
    if (!currentMovie) return;
    closeModal(); 
    
    const videoModal = document.getElementById('videoPlayerModal');
    const iframePlayer = document.getElementById('videoPlayer');
    
    videoModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    
    // vidsrc.cc का इस्तेमाल करें, यह ज्यादा मूवीज सपोर्ट करता है
    const streamUrl = `https://player.xxiku.com/embed/movie/${currentMovie.tmdb_id}`;
    iframePlayer.src = streamUrl;
}

function closeVideoPlayer() {
    const videoModal = document.getElementById('videoPlayerModal');
    const iframePlayer = document.getElementById('videoPlayer');
    
    iframePlayer.src = ""; 
    videoModal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}