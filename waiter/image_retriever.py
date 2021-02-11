from waiter.api_schemas import ImageProperties
from azure.cosmos import DatabaseProxy
import logging

logger = logging.getLogger("ImageRetriever")
class ImageRetriver():
    @classmethod
    def get_image(cls, db: DatabaseProxy,id=None) -> [ImageProperties]:
        container  = db.get_container_client("images")
        query = "SELECT c.id, c.attributes,c.created_at, c.image FROM c"
        items = [ImageProperties(**item) for item in container.query_items(query=query, enable_cross_partition_query=True)]

        return items