from flask import Flask
from app.web.routes import web_bp
from app.config import Config

def create_app():
    app = Flask(__name__, static_folder="web/static", template_folder="web/templates")
    app.config.from_object(Config)
    app.register_blueprint(web_bp)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
