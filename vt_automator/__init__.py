import os
from flask import Flask


def create_app(config_overrides=None):
    app = Flask(__name__)

    app.config["DB_PATH"] = os.environ.get("VT_AUTOMATOR_DB_PATH", "dashcam.db")

    if config_overrides:
        app.config.update(config_overrides)

    from .routes import bp

    app.register_blueprint(bp)

    return app
