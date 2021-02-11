from waiter.api_schemas import ImageProperties


class ImageRetriver():
    @classmethod
    def get_image(cls, id=None) -> [ImageProperties]:
        raise NotImplementedError("%s Not Implemented" % cls.__name__ )