import os
import traceback

from flask import jsonify, request
from flask.views import MethodView
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

from waiter.azure_sdk import FlaskBlobServiceClient, FlaskCosmosClient
from waiter.utils import create_app
from waiter.api_schemas import APIStatus, APIError, APISchema, PersistImageRequest, ImageFile
from waiter.config import ApplicationConfig
from waiter.image_persistor import ImagePersistor
from waiter.image_retriever import ImageRetriver


class APIException(HTTPException):
    code = 400

app = create_app(__name__, config=ApplicationConfig())


blob_service = FlaskBlobServiceClient.init_app(app)
cosmos = FlaskCosmosClient.init_app(app)


@app.errorhandler(Exception)
def handle_api_exception(e):
    if isinstance(e, HTTPException):
        error = APIError(
            message=e.name,
            description=e.description,
            status_code=e.code,
            inner_error=traceback.format_exception_only(type(e), e)
        )
        status_code = e.code
    else:
        try:
            name = e.name
            description = e.description
            status_code = 500
        except Exception as esc:
            name = "Unknown Exception"
            description = "Server Encountered an Error Processing your request. Please try again after some time"
            status_code = 500
        error = APIError(
            message=name,
            description=description,
            status_code=status_code,
            inner_error=traceback.format_exception_only(type(e), e)
        )
    response = APISchema(
        status=APIStatus.FAILED,
        errors=[error],
        status_code=status_code
    )
    return jsonify(response.to_json()), response.status_code

class ImageAPI(MethodView):

    def get(self):
        # query image properties from cosmos
        try:
            images = ImageRetriver.get_image(db=cosmos)
            app.logger.info("Found %d images" % len(images))
            response = APISchema(
                status=APIStatus.SUCCESS,
                data=images
            )
        except Exception as exc:
            error = APIError(
                message="Failed to fetch image",
                description=str(exc)
            )
            response = APISchema(
                status=APIStatus.FAILED,
                errors=[error]
            )

        return jsonify(response.to_json()), response.status_code

    def post(self):
        # get image data
        # save image in cosmos
        # upload file to azure storage
        image = request.files.get("image", None)
        if image is None:
            raise APIException("Could not find image file to upload")
        filename = secure_filename(image.filename)
        image_file = ImageFile(
            local=True,
            filename=filename,
            path=os.path.join(app.config["IMAGE_UPLOADS"], filename)
        )
        # save image locally
        app.logger.info(f"Saving {image_file}")
        image.save(image_file.path)
        persist_req = PersistImageRequest(
            file=image_file
        )
        app.logger.info(f"Uploading {image_file}  to blob store")

        image_persistor = ImagePersistor(blob_service=blob_service, db=cosmos)
        try:
            image_persistor.persist_image(persist_req)
            response = APISchema(status=APIStatus.SUCCESS, status_code=201)
        except Exception as exc: raise

            # error = APIError(
            #     status_code=500,
            #     message="Failed to save image",
            #     description=str(exc)
            # )
            # response = APISchema(status=APIStatus.FAILED, errors=[error], status_code=500)

        return jsonify(response.to_json()), response.status_code


app.add_url_rule('/images/', view_func=ImageAPI.as_view('images'))

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")
