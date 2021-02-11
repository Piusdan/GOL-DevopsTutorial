import os
import tempfile
from dataclasses import dataclass


@dataclass
class ApplicationConfig():
    DATABASE_NAME: str = "waiter"
    AZURE_COSMOS_CONNECTION_STRING: str = os.environ.get("AZURE_COSMOS_CONNECTION_STRING")
    COSMOS_ACCOUNT_ENDPOINT: str = os.environ.get('COSMOS_ACCOUNT_ENDPOINT')
    COSMOS_ACCOUNT_KEY: str = os.environ.get('COSMOS_ACCOUNT_KEY')
    BLOB_STORAGE_ENDPOINT: str = os.environ.get("BLOB_STORAGE_ENDPOINT", "http://127.0.0.1:10000/devstoreaccount1")
    BLOB_STORAGE_KEY: str = os.environ.get("BLOB_STORAGE_KEY", "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==")
    IMAGE_UPLOADS: str = None
    ALLOWED_IMAGE_EXTENSIONS: [str] = None

    def __post_init__(self):
        self.ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]

        if self.IMAGE_UPLOADS is None:
            # create temporary directory to store image uploads
            self.IMAGE_UPLOADS = tempfile.mkdtemp()
