# StreamFlix — FastAPI + SQLAlchemy starter

A small Netflix-style **movie catalog** demo built with FastAPI, SQLAlchemy, SQLite, Jinja2, CSS, and JavaScript. It imports movie metadata from TMDB when you provide an API key. It does **not** provide movie streaming or scrape MX Player/Netflix.

## Project layout

```text
netflix-clone/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── movie_api.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

`movies.db` is created automatically when the app starts; it is not checked into the project.

## Run locally

### 1. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install packages

```bash
python -m pip install -r requirements.txt
```

### 3. Configure TMDB (optional)

Get an API key from TMDB, then put it in `.env`:

```env
TMDB_API_KEY=your_real_api_key_here
```

The application loads `.env` automatically through Uvicorn's `--env-file` option. The API key is optional until you want to import titles.

### 4. Start the app

```bash
uvicorn app.main:app --reload --env-file .env
```

Open <http://127.0.0.1:8000>. API documentation is at <http://127.0.0.1:8000/docs>, and the health endpoint is <http://127.0.0.1:8000/health>.

### 5. Import movie metadata

After adding the key and restarting the server, click **Refresh titles** on the homepage, or call the endpoint from a terminal:

```bash
curl -X POST http://127.0.0.1:8000/api/movies/sync
```

The catalog is stored in `movies.db`, so imported metadata remains available locally between runs.

## Current features

- Responsive dark movie-catalog homepage
- Search titles already stored in the local catalog
- SQLAlchemy `Movie` model and automatic SQLite table creation
- `GET /api/movies` to list local records
- `POST /api/movies/sync` to import/update popular TMDB metadata
- `GET /health` health-check endpoint

## Good next steps

1. Add user accounts and password hashing.
2. Add a personal watchlist model linked to users.
3. Add movie-detail pages and genre filters.
4. Add pagination and more TMDB endpoints.
5. Add tests, migrations (Alembic), and production configuration before deployment.

## Notes

- TMDB metadata and poster images are supplied by TMDB. Review TMDB's current API terms and attribution requirements before public deployment.
- Do not commit `.env` or expose the API key in frontend JavaScript.
- This project is a catalog UI, not an authorized streaming service.
