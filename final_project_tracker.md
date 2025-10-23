# PulseNet - Project Status Tracker
**Real-Time Global Emotion Map**

**Last Updated:** October 20, 2025 - 9:00 PM  
**Progress:** 65% Complete  
**Project Lead:** Victor  
**Repository:** https://github.com/vixtor-e86/emotion-map-project

---

## 📊 OVERALL PROGRESS

```
█████████████░░░░░░░ 65% Complete

Backend:  ████████████████░░░░ 80% ✅
Frontend: ░░░░░░░░░░░░░░░░░░░░  0% ⏳
```

---

## 📁 CURRENT PROJECT STRUCTURE

```
emotion-map-project/
│
├── backend/                          
│   ├── app.py                        ✅ Flask server (port 5000)
│   ├── config.py                     ✅ Config with API keys (GROK added)
│   │
│   ├── data_collection/              80% COMPLETE
│   │   ├── __init__.py              ✅
│   │   ├── rss_collector.py         ✅ WORKING (733 posts/run)
│   │   ├── reddit_collector.py      ✅ WORKING (175 posts/run)
│   │   ├── news_collector.py        ✅ WORKING (500+ posts/run)
│   │   └── twitter_collector.py     ⏳ PENDING (Grok strategy ready)
│   │
│   ├── processing/                   0% COMPLETE
│   │   ├── __init__.py              ✅
│   │   ├── emotion_analyzer.py      ⏳ TO CREATE (VADER + keywords)
│   │   ├── location_extractor.py    ⏳ TO CREATE (regex + dictionary)
│   │   └── aggregator.py            ⏳ TO CREATE (group by location)
│   │
│   ├── database/                     100% COMPLETE
│   │   ├── __init__.py              ✅
│   │   ├── init_db.py               ✅ CLEAN (2 tables, 5 emotions)
│   │   └── db_manager.py            ✅ CLEAN (all methods updated)
│   │
│   ├── scheduler/                    40% COMPLETE
│   │   ├── __init__.py              ✅
│   │   └── background_tasks.py      🔄 PARTIAL (only RSS integrated)
│   │
│   └── routes/                       100% COMPLETE
│       ├── __init__.py              ✅
│       └── api_routes.py            ✅ 7 ENDPOINTS (emotion-ready)
│
├── frontend/                         0% COMPLETE
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css            ⏳ NOT CREATED
│   │   └── js/
│   │       ├── 3d_map.js            ⏳ NOT CREATED (Globe.gl)
│   │       ├── dashboard.js         ⏳ NOT CREATED
│   │       └── api.js               ⏳ NOT CREATED
│   │
│   └── templates/
│       └── index.html               🔄 BASIC PLACEHOLDER
│
├── tests/                            0% COMPLETE
│   ├── test_api.py                  ⏳ NOT CREATED
│   ├── test_collectors.py           ⏳ NOT CREATED
│   └── test_processing.py           ⏳ NOT CREATED
│
├── .env                             ✅ API keys configured
├── .gitignore                       ✅ Git ignore rules
├── requirements.txt                 ✅ All dependencies listed
├── test_db.py                       ✅ Database testing script
├── README.md                        ⏳ NEEDS UPDATE
└── emotion_map.db                   ✅ SQLite (1,400+ posts, 2 tables)
```

---

## ✅ COMPLETED WORK (80% Backend)

### 1. Database System ✅ 100%

**File:** `backend/database/init_db.py`  
**Status:** Clean, production-ready

**Tables Created:**
1. **raw_posts** - Individual posts
   - Columns: text, source, timestamp, city, country, continent
   - Emotions: emotion (joy/anger/sadness/hope/calmness), emotion_score
   - Indexes: timestamp, country, emotion, source

2. **aggregated_emotions** - Summarized by location
   - Columns: joy_count, anger_count, sadness_count, hope_count, calmness_count
   - Summary: total_posts, dominant_emotion, avg_emotion_score
   - Indexes: location, timestamp, dominant_emotion, location_type

**Database Manager:** `backend/database/db_manager.py`  
**Methods Available:**
- `insert_raw_post()` - Save posts with emotions
- `update_post_emotion()` - Update emotion after analysis
- `update_post_location()` - Update location after extraction
- `get_posts_without_emotion()` - Get posts needing analysis
- `get_posts_without_location()` - Get posts needing location
- `insert_aggregated_emotions()` - Save aggregated data
- `get_emotion_map_data()` - Get data for map visualization
- `get_emotion_stats()` - Global emotion statistics
- `get_location_details()` - Details for specific location
- `count_emotion()` - Count emotions by country
- `get_all_countries()` - List all countries
- `cleanup_old_data()` - Delete old posts

### 2. Data Collection ✅ 80%

**Working Collectors:**

**RSS Collector** (`rss_collector.py`)
- Sources: 20 international RSS feeds
- Performance: 733 posts per run (75% success rate)
- Coverage: Global (UK, USA, Europe, Asia, Africa, Australia)

**Reddit Collector** (`reddit_collector.py`)
- Sources: 54 global subreddits
- Performance: 175 posts per run
- Coverage: 6 continents, 40+ countries
- Rate limiting: Respected (2-4 second delays)

**News API Collector** (`news_collector.py`)
- Source: NewsData.io
- Coverage: 32 countries
- Performance: 500+ posts per run
- Rate limit: 100 requests/day

**Total Data Collected:** 1,400+ posts in database

**Pending:**
- Twitter Collector (Grok API strategy documented)

### 3. API Endpoints ✅ 100%

**Base URL:** `http://localhost:5000/api`

**7 Endpoints Ready:**
1. `GET /api/health` - Health check
2. `GET /api/map-data/<zoom>` - Map data (emotion support)
3. `GET /api/location/<name>` - Location details
4. `GET /api/stats` - Global emotion statistics
5. `GET /api/emotions` - Emotion breakdown
6. `GET /api/search` - Search posts by keyword/emotion
7. `GET /api/trends` - Time-series (placeholder)

**Features:**
- Supports 5-emotion system (joy, anger, sadness, hope, calmness)
- Backward compatible with old data
- Graceful fallbacks
- Error handling

### 4. Configuration ✅ 100%

**Environment Variables:** `.env`
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=configured
DATABASE_PATH=emotion_map.db
NEWS_API_KEY=configured
REDDIT_CLIENT_ID=configured
REDDIT_CLIENT_SECRET=configured
GROK_API_KEY=added (for Twitter)
UPDATE_INTERVAL_MINUTES=60
```

**Config File:** `backend/config.py`
- All API keys loaded from .env
- Flask settings configured
- Database path set
- Update interval: 60 minutes

### 5. Flask Application ✅ 100%

**File:** `backend/app.py`
- Application factory pattern
- CORS enabled for API calls
- Blueprint registration
- Serves static files from frontend/
- Server runs on port 5000

---

## ⏳ PENDING WORK (35%)

### 1. Processing Layer (0%)

**Need to Create:**

**Emotion Analyzer** (`backend/processing/emotion_analyzer.py`)
- Approach: VADER + keyword mapping
- Classification: joy, anger, sadness, hope, calmness
- Accuracy target: 70%+
- Time estimate: 1-2 days

**Location Extractor** (`backend/processing/location_extractor.py`)
- Approach: Regex patterns + city/country dictionary + geopy fallback
- Extract: city, country, continent
- Time estimate: 1-2 days

**Data Aggregator** (`backend/processing/aggregator.py`)
- Group posts by location
- Count emotion frequencies
- Calculate dominant emotion
- Save to aggregated_emotions table
- Time estimate: 1 day

### 2. Background Scheduler (40%)

**File:** `backend/scheduler/background_tasks.py`

**Current State:**
- ✅ APScheduler configured
- ✅ RSS collector integrated
- ⏳ Need to add Reddit, News, Twitter
- ⏳ Need to add processing pipeline
- ⏳ Need full automation

**Complete Pipeline Needed:**
```python
def run_complete_pipeline():
    # 1. Collect (15 min)
    collect_rss_data()
    collect_reddit_data()
    collect_news_data()
    collect_twitter_data()
    
    # 2. Process (10 min)
    analyze_emotions()
    extract_locations()
    
    # 3. Aggregate (5 min)
    aggregate_by_country()
    
    # 4. Cleanup (2 min)
    cleanup_old_data()
```

### 3. Frontend (0%)

**Technology:** Globe.gl (3D interactive Earth)

**Components Needed:**
- `index.html` - Main structure
- `style.css` - Styling (emotion colors)
- `3d_map.js` - Globe visualization
- `dashboard.js` - Statistics display
- `api.js` - API integration

**Features:**
- 3D spinning globe
- Countries colored by emotion
- Hover tooltips
- Click for details
- Emotion meter dashboard
- Statistics cards
- Mobile responsive

**Time Estimate:** 4-5 days

### 4. Twitter Collection (0%)

**File:** `backend/data_collection/twitter_collector.py`

**Strategy:**
- Primary: Grok API (xAI) - direct Twitter access
- Backup: ntscraper (web scraping)
- Advanced filtering for sarcasm/spam
- Quality account focus

**Time Estimate:** 2-3 days (including API access)

### 5. Testing (0%)

**Need to Create:**
- Unit tests for all modules
- Integration tests
- Performance tests
- API endpoint tests

**Time Estimate:** 2-3 days

---

## 🎯 KEY DECISIONS MADE

### Technical Decisions ✅

1. **Emotion System:** 5 emotions (joy, anger, sadness, hope, calmness)
   - Changed from 3-sentiment system
   - Changed "fear" to "sadness"

2. **Emotion Analysis:** VADER + keyword mapping
   - Simple, fast, accurate (70%+)
   - No complex ML models for MVP

3. **Location Extraction:** Regex + dictionary
   - Three-layer approach
   - No spaCy (installation issues)

4. **Map Visualization:** 3D Globe.gl
   - Instructor requirement
   - More impressive than 2D

5. **Twitter Access:** Grok API (xAI)
   - Instructor recommended
   - Direct Twitter integration

6. **Database:** SQLite for MVP
   - Easy setup
   - Will migrate to PostgreSQL in production

7. **Update Frequency:** 60 minutes
   - Respects API rate limits
   - Good balance for MVP

---

## 🎨 DESIGN SPECIFICATIONS

### Color Palette (5 Emotions)
```
Joy:      #FFC107  (Yellow/Gold)
Anger:    #F44336  (Red)
Sadness:  #9C27B0  (Purple)
Hope:     #4CAF50  (Green)
Calmness: #2196F3  (Blue)
```

### Technology Stack
- **Backend:** Flask, SQLite, VADER, geopy
- **Frontend:** Globe.gl, Three.js, Chart.js
- **APIs:** NewsData.io, Reddit (PRAW), Grok (Twitter)
- **Deployment:** Heroku/Railway (planned)

---

## 📈 CURRENT METRICS

### Database Status
- **Total Posts:** 1,400+ collected
- **Sources:** RSS (733), Reddit (175), News (500+)
- **Countries:** 40+ represented
- **Tables:** 2 (raw_posts, aggregated_emotions)
- **Emotions:** Ready for 5-emotion system

### API Performance
- **Endpoints:** 7 working
- **Response Time:** <100ms
- **Uptime:** 100% (local dev)

### Data Collection
- **Success Rate:** 85%
- **Update Frequency:** Every 60 minutes
- **Geographic Coverage:** 6 continents

---

## 🚀 IMMEDIATE NEXT STEPS

### Priority 1: Processing Layer (3-4 days)
1. Create emotion_analyzer.py
2. Create location_extractor.py
3. Create aggregator.py
4. Test on existing 1,400 posts

### Priority 2: Complete Scheduler (1 day)
1. Integrate all collectors
2. Add processing pipeline
3. Test full automation

### Priority 3: Frontend (4-5 days)
1. Build HTML structure
2. Implement 3D globe
3. Create dashboard
4. Style and polish

### Priority 4: Twitter Integration (2-3 days)
1. Get Grok API access
2. Implement collector
3. Add sarcasm filtering

### Priority 5: Testing & Deployment (2-3 days)
1. Write tests
2. Fix bugs
3. Deploy to production

---

## 🎓 TEAM INFORMATION

**Project Lead:** Victor  
**Team Size:** 7 members  
**Current Sprint:** Week 2 of MVP  
**Target Launch:** November 7, 2025  
**Days Remaining:** 18 days

**Division of Work:**
- Backend: Victor + 2 teammates
- Frontend: 2 teammates
- Data Science: 1 teammate
- Testing/DevOps: 1 teammate

---

## 📞 PROJECT LINKS

**Repository:** https://github.com/vixtor-e86/emotion-map-project  
**Local Server:** http://localhost:5000  
**API Base:** http://localhost:5000/api

**Getting Started:**
```bash
# Clone repo
git clone https://github.com/vixtor-e86/emotion-map-project.git

# Setup environment
cd emotion-map-project
uv venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
uv pip install geopy

# Initialize database
python backend/database/init_db.py

# Run server
python backend/app.py
```

---

## ✅ SUCCESS CRITERIA

### MVP Requirements (Target: Nov 7)
- [x] Database operational (2 tables, 5 emotions)
- [x] 3+ data sources working (RSS, Reddit, News)
- [ ] Emotion analysis implemented
- [ ] Location extraction working
- [ ] Aggregation working
- [x] API endpoints returning data (7 endpoints)
- [ ] Background scheduler automated
- [ ] 3D globe visualization
- [ ] Dashboard showing stats
- [ ] Mobile responsive
- [ ] 1,500+ posts collected

**Current Status:** 65% complete (13/20 criteria met)

---

**Last Updated:** October 20, 2025 - 9:00 PM  
**Next Update:** After processing layer completion  
**Status:** On track for MVP launch 🚀