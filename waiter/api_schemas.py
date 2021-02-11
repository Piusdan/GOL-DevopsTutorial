import enum
import uuid
from dataclasses import dataclass, asdict, field
import datetime


class APIStatus(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class BaseSchema():
    def to_json(self): return asdict(self)


@dataclass
class ImageFile(BaseSchema):
    local: bool
    filename: str
    path: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_json(self):
        json_obj = asdict(self)
        json_obj["local"] = str(self.local)
        json_obj["id"] = str(self.id)
        json_obj["created_at"] = str(self.created_at)
        return json_obj

@dataclass
class ImageProperties(BaseSchema):
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    attributes: dict = field(default_factory=dict)
    image: ImageFile = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_json(self):
        json_obj = asdict(self)
        json_obj["id"] = str(self.id)
        json_obj["created_at"] = str(self.created_at)
        if self.image is not None or type(self.image):
            try:
                json_obj["image"] = self.image.to_json()
            except AttributeError as exc:
                pass
        return json_obj

@dataclass
class PersistImageRequest(BaseSchema):
    file: ImageFile
    request_id : uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self):
        return f"PersistImageRequest<filename={self.file.filename},path={self.file.path}, image_id={self.request_id}>"

    def to_json(self):
        return {
            "file": self.file.to_json(),
            "request_id": str(self.request_id)
        }

@dataclass
class APIError(BaseSchema):
    message: str
    description: str
    status_code: int = 400
    inner_error: [str] = field(default_factory=list)


@dataclass
class APISchema(BaseSchema):
    status: APIStatus
    status_code: int = 200
    data: [BaseSchema] = field(default_factory=list)
    errors: [APIError] = field(default_factory=list)

    def to_json(self):
        json_obj = {"status": self.status.value,
                    "data": [item.to_json() for item in self.data],
                    "errors": [error.to_json() for error in self.errors]
                    }
        return json_obj