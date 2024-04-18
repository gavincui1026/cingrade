import logging
import boto3
from botocore.exceptions import ClientError

from src.config.manager import settings
from src.models.db.upload import Upload
from src.models.schemas.upload import UploadCreate
from src.repository.crud.base import BaseCRUDRepository


class UploadRepository(BaseCRUDRepository):
    async def create_presigned_post(self,
                              user_id: int,
                              upload:UploadCreate,
                              bucket_name=settings.AWS_BUCKET_NAME,
                              fields=None,
                              conditions=None,
                              expiration=3600):
        """Generate a presigned URL S3 POST request to upload a file

        :param bucket_name: string
        :param object_name: string
        :param fields: Dictionary of prefilled form fields
        :param conditions: List of conditions to include in the policy
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Dictionary with the following keys:
            url: URL to post to
            fields: Dictionary of form fields and values to submit with the POST
        :return: None if error.
        """
        # Generate a presigned URL for the S3 object
        s3_client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_BUCKET_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )
        try:
            response = s3_client.generate_presigned_post(bucket_name,
                                                         upload.md5 + "." + upload.ext,
                                                         Fields=fields,
                                                         Conditions=conditions,
                                                         ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None

        # The response contains the presigned URL and required fields
        upload=Upload(
            account_id=user_id,
            md5=upload.md5,
            ext=upload.ext,
        )
        self.async_session.add(upload)
        await self.async_session.commit()
        await self.async_session.refresh(upload)
        return response

