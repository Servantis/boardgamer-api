from dotenv import load_dotenv
from flask import Flask

from routes.health_routes import health_bp
from routes.sync_routes import sync_bp


load_dotenv()


def create_app():
    app = Flask(__name__)

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(sync_bp, url_prefix="/api/sync")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)