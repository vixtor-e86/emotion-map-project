from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from routes.api_routes import api_bp
import atexit
from scheduler.background_task import start_scheduler

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
    app = create_app()
    print("🚀 Starting Emotion Map Server...")
    print("📍 Server running at: http://localhost:5000")
    print("📊 API available at: http://localhost:5000/api/health")
    app.run(debug=True, port=5000, host='0.0.0.0')
    
    print("\n>>> Starting background data collection scheduler...")
    scheduler = start_scheduler()
    
    # Register shutdown handler
    atexit.register(shutdown_scheduler)
    
    print("\n>>> Background scheduler is running!")
    print(">>> Collecting data every 60 minutes from:")
    print("    - RSS Feeds")
    print("    - News API")
    print("    - Reddit")
    print("="*60 + "\n")
    
    # Run Flask app
    try:
        app.run(debug=True, port=5000, host='0.0.0.0')
    except KeyboardInterrupt:
        print("\n>>> Server stopped by user")
        shutdown_scheduler()