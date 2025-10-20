# Real-Time AI Emotion Map Project
## Progress Tracker & Handoff Document

**Project Repository:** https://github.com/vixtor-e86/emotion-map-project  
**Last Updated:** October 18, 2025  
**Current Status:** Backend 60% Complete | Frontend 0% Complete

---

## 📊 OVERALL PROGRESS

```
[████████████░░░░░░░░] 60% Complete

✅ COMPLETED (60%)
├── Project Setup & Infrastructure
├── Database Schema & Manager
├── Configuration System
├── API Endpoints (5/5)
├── Flask Application Core
└── Git/GitHub Integration

🔄 IN PROGRESS (0%)
└── (Nothing currently in progress)

⏳ PENDING (40%)
├── Data Collection (News API, Reddit, RSS) - Assigned to teammates
├── Sentiment Analysis
├── Location Extraction
├── Data Aggregation
├── Background Scheduler
├── Frontend (HTML, CSS, JavaScript)
└── Testing & Deployment
```

---

## ✅ COMPLETED TASKS

### 1. Development Environment Setup
**Status:** ✅ Complete  
**Files Created:**
- Virtual environment with UV (`.venv/`)
- `requirements.txt` with all dependencies
- `.gitignore` (blocks .venv, .env, .db files)
- `.env` (environment variables)

**Dependencies Installed:**
```
Flask==3.0.0
Flask-CORS==4.0.0
pandas (latest)
vaderSentiment==3.3.2
praw==7.7.1
feedparser==6.0.10
APScheduler==3.10.4
python-dotenv==1.0.0
requests==2.31.0
geopy (latest)
```

**Note:** spaCy installation skipped (requires C++ Build Tools) - using geopy instead

---

### 2. Project Structure
**Status:** ✅ Complete

```
emotion-map-project/
├── backend/
│   ├── app.py                     ✅ Main Flask application
│   ├── config.py                  ✅ Configuration management
│   ├── database/
│   │   ├── init_db.py            ✅ Database initialization
│   │   └── db_manager.py         ✅ Database operations
│   ├── routes/
│   │   └── api_routes.py         ✅ API endpoints
│   ├── data_collection/          ⏳ Empty (teammates working)
│   ├── processing/               ⏳ Empty (next phase)
│   └── scheduler/                ⏳ Empty (next phase)
├── frontend/
│   ├── templates/
│   │   └── index.html            ✅ Basic placeholder
│   ├── static/
│   │   ├── css/                  ⏳ Empty
│   │   └── js/                   ⏳ Empty
├── tests/                         ⏳ Empty
├── .env                          ✅ Environment variables
├── .gitignore                    ✅ Git ignore rules
├── requirements.txt              ✅ Dependencies list
└── emotion_map.db                ✅ SQLite database
```

---

### 3. Database Schema
**Status:** ✅ Complete  
**File:** `backend/database/init_db.py`

**Table 1: raw_posts**
```sql
Columns:
- id (PRIMARY KEY)
- text (post content)
- source (News/Reddit/RSS)
- timestamp (when collected)
- city, country, continent (location)
- sentiment (positive/negative/neutral)
- sentiment_score (-1 to 1)

Indexes:
- idx_raw_posts_timestamp
- idx_raw_posts_country
```

**Table 2: aggregated_sentiment**
```sql
Columns:
- id (PRIMARY KEY)
- location_name (country/city name)
- location_type (continent/country/city)
- timestamp (when aggregated)
- positive_count, negative_count, neutral_count
- total_posts
- dominant_sentiment
- avg_sentiment_score

Indexes:
- idx_aggregated_location
```

---

### 4. Database Manager
**Status:** ✅ Complete  
**File:** `backend/database/db_manager.py`

**Functions Implemented:**
1. `insert_raw_post()` - Save individual posts
2. `insert_aggregated_data()` - Save location summaries
3. `get_map_data(zoom_level, hours)` - Get data for map visualization
4. `get_location_details(location_name)` - Get details for one location
5. `get_global_stats()` - Get overall statistics
6. `cleanup_old_data(days)` - Delete old data

**Usage Example:**
```python
from backend.database.db_manager import db

# Insert a post
db.insert_raw_post(
    text="Great day in Paris!",
    source="Reddit",
    country="France",
    sentiment="positive",
    sentiment_score=0.8
)

# Get map data
data = db.get_map_data(zoom_level='country', hours=24)
```

---

### 5. Configuration System
**Status:** ✅ Complete  
**File:** `backend/config.py`

**Settings Managed:**
```python
- FLASK_DEBUG = True (development mode)
- DATABASE_PATH = 'emotion_map.db'
- UPDATE_INTERVAL_MINUTES = 60 (update every hour)
- API Keys (empty, teammates will add):
  - NEWS_API_KEY
  - REDDIT_CLIENT_ID
  - REDDIT_CLIENT_SECRET
- CORS_ORIGINS (for frontend API calls)
```

**Environment Variables (.env):**
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_PATH=emotion_map.db
UPDATE_INTERVAL_MINUTES=60
NEWS_API_KEY=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=EmotionMapBot/1.0
```

---

### 6. API Endpoints
**Status:** ✅ Complete (5/5)  
**File:** `backend/routes/api_routes.py`

#### Endpoint 1: Health Check
```
GET /api/health

Response:
{
    "status": "ok",
    "timestamp": "2025-10-18T12:00:00"
}
```

#### Endpoint 2: Map Data
```
GET /api/map-data/<zoom_level>?hours=24

Parameters:
- zoom_level: continent, country, or city
- hours: data from last N hours (default: 24)

Response:
{
    "locations": ["USA", "UK", "France"],
    "sentiment_scores": [0.6, -0.2, 0.4],
    "hover_text": ["USA: positive (1500 posts)", ...],
    "post_counts": [1500, 800, 600],
    "timestamp": "2025-10-18T12:00:00"
}
```

#### Endpoint 3: Location Details
```
GET /api/location/<location_name>

Response:
{
    "location": "United States",
    "total_posts": 1500,
    "positive_count": 900,
    "negative_count": 400,
    "neutral_count": 200,
    "dominant_sentiment": "positive",
    "avg_score": 0.65,
    "sample_posts": [...],
    "timestamp": "2025-10-18T12:00:00"
}
```

#### Endpoint 4: Global Statistics
```
GET /api/stats

Response:
{
    "total_posts": 25000,
    "avg_sentiment": 0.35,
    "countries_tracked": 45,
    "last_updated": "2025-10-18T12:00:00"
}
```

#### Endpoint 5: Trends
```
GET /api/trends?hours=24

Status: Placeholder (TODO)
```

---

### 7. Flask Application
**Status:** ✅ Complete  
**File:** `backend/app.py`

**Features:**
- Application factory pattern
- CORS enabled for API calls
- Blueprint registration (api_routes)
- Static files served from `frontend/static/`
- Templates served from `frontend/templates/`
- Debug mode enabled

**How to Run:**
```bash
python backend/app.py
```

**Server URLs:**
- Main: http://localhost:5000
- API: http://localhost:5000/api/

---

### 8. Git & GitHub Integration
**Status:** ✅ Complete

**Repository:** https://github.com/vixtor-e86/emotion-map-project

**Commits Made:**
1. "Initial project setup"
2. "Complete backend setup: database, API routes, Flask app"

**Team Access:**
Team members can clone and set up:
```bash
git clone https://github.com/vixtor-e86/emotion-map-project.git
cd emotion-map-project
uv venv
source .venv/Scripts/activate
uv pip install -r requirements.txt
uv pip install geopy
```

---

## ⏳ PENDING TASKS

### Phase 1: Data Collection (Teammates Working)
**Priority:** HIGH  
**Assigned To:** Teammates doing research

**Files to Create:**
1. `backend/data_collection/news_collector.py`
2. `backend/data_collection/reddit_collector.py`
3. `backend/data_collection/rss_collector.py`

**Requirements:**
- Get API keys for News API and Reddit
- Fetch data from respective sources
- Return standardized format
- Handle rate limits
- Call `db.insert_raw_post()` to save data

**Template Structure:**
```python
from backend.database.db_manager import db

def collect_news():
    # Fetch from News API
    # Parse response
    # Extract text, country
    # Save to database
    db.insert_raw_post(
        text=article_text,
        source="NewsAPI",
        country=country,
        # Will add sentiment later
    )
```

---

### Phase 2: Processing (Next After Frontend)
**Priority:** MEDIUM  
**Status:** Not Started

#### Task 2.1: Sentiment Analyzer
**File:** `backend/processing/sentiment_analyzer.py`

**Purpose:** Analyze text sentiment using VADER

**Function:**
```python
def analyze_sentiment(text):
    # Use vaderSentiment
    # Return: sentiment (positive/negative/neutral)
    # Return: score (-1 to 1)
    pass
```

#### Task 2.2: Location Extractor
**File:** `backend/processing/location_extractor.py`

**Purpose:** Extract location from text using geopy

**Function:**
```python
def extract_location(text):
    # Use geopy or regex
    # Map city -> country -> continent
    # Return: city, country, continent
    pass
```

#### Task 2.3: Data Aggregator
**File:** `backend/processing/aggregator.py`

**Purpose:** Aggregate raw posts by location

**Function:**
```python
def aggregate_by_location():
    # Group posts by country/city
    # Count positive/negative/neutral
    # Calculate average score
    # Determine dominant sentiment
    # Call db.insert_aggregated_data()
    pass
```

---

### Phase 3: Background Scheduler (After Processing)
**Priority:** MEDIUM  
**File:** `backend/scheduler/background_tasks.py`

**Purpose:** Run data pipeline every 60 minutes

**Structure:**
```python
from apscheduler.schedulers.background import BackgroundScheduler

def data_pipeline():
    # 1. Collect data (news, reddit, rss)
    # 2. Process (sentiment + location)
    # 3. Aggregate by location
    # 4. Save to database
    pass

scheduler = BackgroundScheduler()
scheduler.add_job(data_pipeline, 'interval', minutes=60)
scheduler.start()
```

---

### Phase 4: Frontend (NEXT - Starting Now!)
**Priority:** HIGH  
**Status:** About to Start

#### Task 4.1: HTML Structure
**File:** `frontend/templates/index.html`

**Components:**
- Header with title
- Map container (Plotly.js)
- Dashboard with statistics cards
- Location detail modal
- Controls (zoom level, time range)

#### Task 4.2: CSS Styling
**File:** `frontend/static/css/style.css`

**Design:**
- Color scheme: Green (positive) → Yellow (neutral) → Red (negative)
- Responsive layout
- Modern, clean design
- Animations and transitions

#### Task 4.3: JavaScript - Map
**File:** `frontend/static/js/map.js`

**Features:**
- Plotly.js choropleth map
- Color countries by sentiment
- Click handlers (show details)
- Auto-refresh every 60 minutes
- Zoom level changes

#### Task 4.4: JavaScript - API Calls
**File:** `frontend/static/js/api.js`

**Functions:**
- `fetchMapData(zoom_level)`
- `fetchLocationDetails(location)`
- `fetchStats()`
- `fetchTrends(hours)`

#### Task 4.5: JavaScript - Dashboard
**File:** `frontend/static/js/dashboard.js`

**Features:**
- Update statistics cards
- Display sample posts
- Show trends chart
- Time range filters

---

### Phase 5: Testing
**Priority:** MEDIUM  
**Status:** Not Started

**Files to Create:**
- `tests/test_api.py` - Test API endpoints
- `tests/test_collectors.py` - Test data collection
- `tests/test_processing.py` - Test sentiment/location

---

### Phase 6: Deployment
**Priority:** LOW (Final Step)  
**Status:** Not Started

**Options:**
- Heroku (free tier)
- PythonAnywhere
- DigitalOcean ($5/month)
- Railway.app

---

## 🔧 TECHNICAL NOTES

### Known Issues
1. **spaCy not installed** - Requires C++ Build Tools. Using geopy as alternative for now.
2. **No real data yet** - Database is empty until teammates provide API collectors
3. **Trends endpoint placeholder** - Needs time-series implementation

### Rate Limits to Consider
- **News API:** 100 requests/day (free tier)
- **Reddit API:** 60 requests/minute
- **Solution:** Update every 60 minutes to stay within limits

### Future Optimizations
- Add caching for API responses
- Implement database connection pooling
- Add Redis for real-time updates
- Compress large database queries

---

## 📝 IMPORTANT COMMANDS

### Start Development Server
```bash
cd emotion-map-project
source .venv/Scripts/activate  # or .venv\Scripts\activate on Windows
python backend/app.py
```

### Install Dependencies (New Team Member)
```bash
uv venv
source .venv/Scripts/activate
uv pip install -r requirements.txt
uv pip install geopy
```

### Initialize Database
```bash
python backend/database/init_db.py
```

### Git Workflow
```bash
git add .
git commit -m "Your message"
git push origin main
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:5000/api/health

# Map data
curl http://localhost:5000/api/map-data/country

# Stats
curl http://localhost:5000/api/stats
```

---

## 🎯 NEXT STEPS (In Order)

1. **NOW:** Build Frontend (HTML, CSS, JavaScript with Plotly.js)
2. **After Frontend:** Create sentiment analyzer
3. **After Sentiment:** Create location extractor
4. **After Location:** Create data aggregator
5. **After Aggregator:** Integrate teammates' API collectors
6. **After Integration:** Set up background scheduler
7. **After Scheduler:** Testing
8. **Final:** Deployment

---

## 📞 HANDOFF INFORMATION

### For Continuing with Another AI/Person

**Context:**
- This is a Flask web application that visualizes global emotions on a map
- Backend is 60% complete
- Database schema and API are fully functional
- Frontend needs to be built next
- Data collection is being handled by teammates

**What to Ask For:**
"Continue building the Emotion Map project. We need to create the frontend with Plotly.js. The backend API is ready at /api/map-data/<zoom>, /api/stats, etc. Please create the HTML, CSS, and JavaScript files for an interactive world map that shows sentiment by country color (green=positive, red=negative)."

**Files to Focus On:**
- `frontend/templates/index.html`
- `frontend/static/css/style.css`
- `frontend/static/js/map.js`
- `frontend/static/js/api.js`
- `frontend/static/js/dashboard.js`

**API Endpoints Available:**
- GET /api/health
- GET /api/map-data/country
- GET /api/location/USA
- GET /api/stats

---

## 📊 COMPLETION CHECKLIST

### Backend
- [x] Project setup
- [x] Virtual environment
- [x] Dependencies installed
- [x] Database schema
- [x] Database manager
- [x] Configuration system
- [x] API endpoints (5/5)
- [x] Flask application
- [ ] Data collectors (teammates)
- [ ] Sentiment analyzer
- [ ] Location extractor
- [ ] Data aggregator
- [ ] Background scheduler

### Frontend
- [ ] HTML structure
- [ ] CSS styling
- [ ] Plotly.js map
- [ ] API integration
- [ ] Dashboard components
- [ ] Interactive features

### Testing & Deployment
- [ ] Unit tests
- [ ] Integration tests
- [ ] Deployment setup
- [ ] Documentation

---

**Total Progress: 60% Complete**  
**Estimated Time Remaining: 6-8 days**  
**Next Milestone: Frontend Complete (75%)**

---

*Last updated: October 18, 2025*  
*Project maintained by: Vixtor*  
*Repository: https://github.com/vixtor-e86/emotion-map-project*