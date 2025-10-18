from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from routes.api_routes import api_bp

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
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting Emotion Map Server...")
    print("📍 Server running at: http://localhost:5000")
    print("📊 API available at: http://localhost:5000/api/")
    app.run(debug=True, port=5000, host='0.0.0.0')