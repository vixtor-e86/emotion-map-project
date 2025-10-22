# PulseNet - Project Status & Quick Reference
**Team Development Guide**

**Last Updated:** October 20, 2025  
**Current Progress:** 62% Complete  
**Project Lead:** Victor

---

## 🎯 PROJECT OVERVIEW

**PulseNet** = Real-time global emotion map showing how the world feels right now.

**What it does:**
- Collects posts from Twitter, Reddit, News, RSS feeds
- AI analyzes emotions: **Joy, Anger, Sadness, Hope, Calmness**
- Shows emotions on a **3D spinning Earth**
- Updates automatically every 60 minutes

---

## 📁 CURRENT PROJECT STRUCTURE

```
emotion-map-project/
│
├── backend/                          
│   ├── app.py                        ✅ Flask server (port 5000)
│   ├── config.py                     ✅ Configuration with API keys
│   │
│   ├── data_collection/              ✅ Data collectors (80% complete)
│   │   ├── rss_collector.py         ✅ WORKING (733 posts/run)
│   │   ├── reddit_collector.py      ✅ WORKING (175 posts/run)
│   │   ├── news_collector.py        ✅ WORKING (500+ posts/run)
│   │   └── twitter_collector.py     ⏳ PENDING (strategy ready)
│   │
│   ├── processing/                   ⏳ Processing layer (30% complete)
│   │   ├── emotion_analyzer.py      ⏳ TO BE CREATED
│   │   ├── location_extractor.py    ⏳ TO BE CREATED
│   │   └── aggregator.py            ⏳ TO BE CREATED
│   │
│   ├── database/                     ✅ Database (ready for migration)
│   │   ├── init_db.py               ✅ Original schema
│   │   ├── migrate_to_emotions.py   🔄 CREATED (needs to run)
│   │   └── db_manager.py            🔄 NEEDS METHOD UPDATES
│   │
│   ├── scheduler/                    🔄 Background tasks (40% complete)
│   │   └── background_tasks.py      🔄 PARTIAL (only RSS)
│   │
│   └── routes/                       ✅ API endpoints (complete)
│       └── api_routes.py            ✅ 7 ENDPOINTS READY
│
├── frontend/                         ⏳ Frontend (0% complete)
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
├── tests/                            ⏳ Testing (0% complete)
│
├── .env                             ✅ Environment variables configured
├── .gitignore                       ✅ Git ignore rules
├── requirements.txt                 ✅ Python dependencies
├── README.md                        ⏳ NEEDS UPDATE
└── emotion_map.db                   ✅ SQLite (1,400+ posts)
```

**Legend:**
- ✅ Complete and working
- 🔄 Partially complete / needs updates
- ⏳ Not started / pending
- 📁 Empty folder

---

## 📊 CURRENT STATUS

### Data Collection: 80% Complete ✅

**Working Collectors:**
1. **RSS Feeds** - 733 posts per run (15/20 sources working)
2. **Reddit** - 175 posts per run (54 subreddits)
3. **News API** - 500+ posts per run (32 countries)
4. **Twitter** - Pending (Grok API strategy ready)

**Total in Database:** 1,400+ posts  
**Countries Covered:** 40+  
**Update Frequency:** Every 60 minutes (configured)

### Database: 70% Complete 🔄

**Current State:**
- ✅ Original schema with sentiment (positive/negative/neutral)
- ✅ 1,400+ posts collected
- 🔄 Migration script created for 5-emotion system
- ⏳ Needs migration to be run
- ⏳ db_manager.py needs 3 new methods

**5 Emotions:** Joy, Anger, Sadness, Hope, Calmness

### API Endpoints: 100% Complete ✅

**Base URL:** `http://localhost:5000/api`

**Available Endpoints:**
1. `GET /api/health` - Health check
2. `GET /api/map-data/<zoom_level>` - Map visualization data
3. `GET /api/location/<name>` - Location details
4. `GET /api/stats` - Global statistics
5. `GET /api/emotions` - Emotion breakdown
6. `GET /api/search` - Search posts
7. `GET /api/trends` - Time-series data (placeholder)

### Processing Layer: 30% Complete ⏳

**Needs Creation:**
- Emotion Analyzer (VADER + keyword mapping)
- Location Extractor (regex + dictionary)
- Data Aggregator (group by country/continent)

### Frontend: 0% Complete ⏳

**Required Components:**
- 3D Globe visualization (Globe.gl library)
- Emotion meter dashboard
- Statistics cards
- Interactive controls
- Mobile responsive design

---

## 🔌 API DOCUMENTATION

### 1. Health Check
```
GET /api/health

Response:
{
    "status": "ok",
    "timestamp": "2025-10-20T18:00:00Z"
}
```

### 2. Map Data
```
GET /api/map-data/country?hours=24

Parameters:
- zoom_level: continent | country | city
- hours: data from last N hours (default: 24)

Response:
{
    "locations": ["USA", "France", "Nigeria", ...],
    "emotions": ["joy", "anger", "sadness", ...],
    "emotion_scores": [0.8, 0.6, 0.4, ...],
    "joy_counts": [500, 200, 150, ...],
    "anger_counts": [100, 300, 50, ...],
    "sadness_counts": [50, 100, 200, ...],
    "hope_counts": [200, 150, 100, ...],
    "calmness_counts": [150, 250, 500, ...],
    "post_counts": [1000, 1000, 1000, ...],
    "timestamp": "2025-10-20T18:00:00Z"
}
```

### 3. Global Statistics
```
GET /api/stats

Response:
{
    "total_posts": 1400,
    "joy_percentage": 35.0,
    "anger_percentage": 20.0,
    "sadness_percentage": 15.0,
    "hope_percentage": 18.0,
    "calmness_percentage": 12.0,
    "dominant_emotion": "joy",
    "countries_tracked": 45,
    "last_updated": "2025-10-20T18:00:00Z"
}
```

### 4. Location Details
```
GET /api/location/USA

Response:
{
    "location": "United States",
    "total_posts": 1000,
    "joy_count": 350,
    "anger_count": 200,
    "sadness_count": 150,
    "hope_count": 180,
    "calmness_count": 120,
    "dominant_emotion": "joy",
    "sample_posts": [...],
    "timestamp": "2025-10-20T18:00:00Z"
}
```

### 5. Emotion Breakdown
```
GET /api/emotions?location=USA

Response:
{
    "location": "USA",
    "emotions": {
        "joy": 350,
        "anger": 200,
        "sadness": 150,
        "hope": 180,
        "calmness": 120
    },
    "dominant": "joy",
    "total_posts": 1000
}
```

### 6. Search Posts
```
GET /api/search?query=climate&emotion=sadness&limit=50

Response:
{
    "query": "climate",
    "emotion_filter": "sadness",
    "results": [...],
    "count": 45
}
```

### 7. Trends (Coming Soon)
```
GET /api/trends?hours=24

Response:
{
    "timestamps": [],
    "emotion_data": {...},
    "message": "Implementation pending"
}
```

---

## 🎨 DESIGN SPECIFICATIONS

### Color Palette (5 Emotions)
```css
Joy:      #FFC107  (Yellow/Gold)
Anger:    #F44336  (Red)
Sadness:  #9C27B0  (Purple)
Hope:     #4CAF50  (Green)
Calmness: #2196F3  (Blue)

Background: #f5f5f5
Dark Mode:  #1a1a2e
Text:       #333333
```

### Visualization Library
**3D Globe:** Globe.gl (https://globe.gl/)
- Built on Three.js
- Interactive spinning Earth
- Color-coded by emotion
- Hover tooltips
- Click for details

---

## ⚙️ TECHNICAL REQUIREMENTS

### Backend Dependencies
```
Flask==3.0.0
Flask-CORS==4.0.0
pandas==2.3.3
vaderSentiment==3.3.2
praw==7.7.1
feedparser==6.0.10
APScheduler==3.10.4
python-dotenv==1.0.0
requests==2.31.0
geopy==2.4.1
```

### Frontend Dependencies (CDN)
```html
<!-- Globe.gl for 3D visualization -->
<script src="//unpkg.com/globe.gl"></script>

<!-- Chart.js for statistics -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

---

## 🚀 RUNNING THE PROJECT

### Start Backend Server
```bash
# Activate virtual environment
source .venv/Scripts/activate  # Mac/Linux
.venv\Scripts\activate         # Windows

# Run Flask server
python backend/app.py
```

**Server runs at:** http://localhost:5000

### Test APIs
```bash
# Health check
curl http://localhost:5000/api/health

# Get map data
curl http://localhost:5000/api/map-data/country

# Get statistics
curl http://localhost:5000/api/stats
```

---

## ✅ IMMEDIATE NEXT STEPS

### Phase 1: Complete Database Migration (1 hour)
1. Run migration script: `python backend/database/migrate_to_emotions.py`
2. Update `db_manager.py` with 3 new emotion methods
3. Test database operations

### Phase 2: Build Processing Layer (2-3 days)
1. Create `emotion_analyzer.py` (VADER + keywords)
2. Create `location_extractor.py` (regex + dictionary)
3. Create `aggregator.py` (group by location)
4. Test on existing 1,400 posts

### Phase 3: Complete Background Scheduler (1 day)
1. Integrate all collectors (RSS, Reddit, News)
2. Add processing pipeline (emotion + location)
3. Add aggregation step
4. Test full automation

### Phase 4: Build Frontend (4-5 days)
1. Create HTML structure
2. Implement 3D globe with Globe.gl
3. Build dashboard components
4. Style with CSS
5. Make responsive

### Phase 5: Testing & Deployment (2-3 days)
1. Unit tests for all modules
2. Integration testing
3. Performance optimization
4. Deploy to production

---

## 📋 DEVELOPMENT WORKFLOW

### Daily Development Cycle
```
1. Pull latest from GitHub
2. Activate virtual environment
3. Start Flask server
4. Make changes to code
5. Test locally
6. Commit and push to GitHub
```

### Git Commands
```bash
# Pull latest changes
git pull origin main

# Check status
git status

# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push origin main
```

---

## 🎯 SUCCESS CRITERIA (MVP)

### Backend (Currently 62%)
- [x] Database operational
- [x] 3 data sources working
- [ ] Emotion analysis implemented
- [ ] Location extraction working
- [ ] Aggregation working
- [x] API endpoints returning data
- [ ] Background scheduler fully automated

### Frontend (Currently 0%)
- [ ] 3D globe visualization working
- [ ] Emotion meter displaying stats
- [ ] Dashboard showing real data
- [ ] Interactive controls
- [ ] Mobile responsive
- [ ] Professional design

### System Performance
- [ ] Collect 2,000+ posts per hour
- [ ] 70%+ emotion accuracy
- [ ] 40+ countries mapped
- [ ] Page loads in < 3 seconds
- [ ] Updates every 60 minutes
- [ ] 99% uptime

---

## 📞 PROJECT INFORMATION

**Repository:** https://github.com/vixtor-e86/emotion-map-project  
**Project Lead:** Victor  
**Current Sprint:** Week 2 of MVP development  
**Target Launch:** November 7, 2025  
**Days Remaining:** 18 days

---

## 📚 KEY RESOURCES

**Documentation:**
- Globe.gl Examples: https://globe.gl/
- Flask Docs: https://flask.palletsprojects.com/
- VADER Sentiment: https://github.com/cjhutto/vaderSentiment
- Chart.js: https://www.chartjs.org/

**APIs Used:**
- NewsData.io: https://newsdata.io/
- Reddit (PRAW): https://praw.readthedocs.io/
- Grok (xAI): https://x.ai/

---

**Last Updated:** October 20, 2025 - 7:00 PM  
**Document Version:** 2.0 (Simplified)