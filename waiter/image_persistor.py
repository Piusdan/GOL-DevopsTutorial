import logging
import json
from dataclasses import asdict

from azure.core.exceptions import ResourceExistsError
from azure.cosmos import DatabaseProxy, PartitionKey
from azure.storage.blob import BlobServiceClient

from waiter.api_schemas import PersistImageRequest, ImageProperties, ImageFile

logger = logging.getLogger("ImagePersistor")
logger.setLevel(logging.INFO)


class ImagePersistor():
    def __init__(self, blob_service: BlobServiceClient, db: DatabaseProxy):
        try:
            self.blob_container = blob_service.create_container("images")
        except ResourceExistsError as exc:
            self.blob_container = blob_service.get_container_client(container="images")
        self.cosmos_container = db.create_container_if_not_exists(id="images",
                                                                  partition_key=PartitionKey(path="/image/path"))

    def persist_image(self, persist_req: PersistImageRequest) -> ImageProperties:
        # Create a blob client using the local file name as the name for the blob
        logger.info("\nUploading to Azure Storage as blob:\n\t" + persist_req.file.filename)

        # Upload the created file
        with open(persist_req.file.path, "rb") as data:
            blob = self.blob_container.upload_blob(name=str(persist_req.file.id), data=data,
                                                   metadata=persist_req.file.to_json())
        image = ImageProperties(
            attributes={},
            image=ImageFile(
                id=persist_req.file.id,
                filename=persist_req.file.filename,
                path=blob.url,
                local=False
            )

        )
        # save data in cosmos
        json_image = image.to_json()
        print(json_image)
        saved_images = self.cosmos_container.upsert_item(
            image.to_json()
        )

        logger.info("Uploaded %d images" % len(saved_images))

        # save to cosmos

        return image
