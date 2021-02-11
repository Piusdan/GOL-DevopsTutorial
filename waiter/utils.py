from dataclasses import asdict

from flask import Flask

from waiter.config import ApplicationConfig


def allowed_image(filename: str, app: Flask):

    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def create_app(import_name, config: ApplicationConfig):
    app = Flask(import_name)
    app.config.from_mapping(asdict(config))
    return app