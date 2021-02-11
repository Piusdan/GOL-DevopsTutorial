from azure.cosmos import CosmosClient, DatabaseProxy
from azure.storage.blob import BlobServiceClient


class FlaskBlobServiceClient(BlobServiceClient):
    @staticmethod
    def init_app(app) -> BlobServiceClient:
        blob_service = BlobServiceClient(account_url=app.config["BLOB_STORAGE_ENDPOINT"], credential=app.config["BLOB_STORAGE_KEY"])
        return blob_service


class FlaskCosmosClient(CosmosClient):
    @staticmethod
    def init_app(app) -> DatabaseProxy:
        cosmos =CosmosClient(url=app.config["COSMOS_ACCOUNT_ENDPOINT"], credential=app.config["COSMOS_ACCOUNT_KEY"])
        db = cosmos.create_database_if_not_exists(id=app.config["DATABASE_NAME"])
        return db