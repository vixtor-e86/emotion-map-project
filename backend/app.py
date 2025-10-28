"""
app.py
------
Main Flask application with background scheduler integration.
"""

from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from routes.api_routes import api_bp
import atexit
from scheduler.background_task import start_scheduler

# Global scheduler instance
scheduler = None

def create_app(config_class=Config):
    """Application factory pattern."""
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    app.config.from_object(config_class)
    
    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Main route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    return app

def shutdown_scheduler():
    """Gracefully shutdown scheduler on app exit."""
    global scheduler
    if scheduler:
        print("\n>>> Stopping background scheduler...")
        scheduler.shutdown()
        print(">>> Scheduler stopped successfully!")

if __name__ == '__main__':
    # Create Flask app
    app = create_app()
    
    # ✅ FIX: Start the background scheduler
    print("🚀 Starting Emotion Map Server...")
    scheduler = start_scheduler()
    
    # ✅ FIX: Register cleanup function
    atexit.register(shutdown_scheduler)
    
    # Display server info
    print("\n📍 Server running at: http://localhost:5000")
    print("📊 API available at: http://localhost:5000/api/health")
    print("⚠️  Press CTRL+C to stop server and scheduler\n")
    
    # Run Flask app
    app.run(debug=True, port=5000, host='0.0.0.0')