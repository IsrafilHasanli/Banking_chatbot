from functools import lru_cache

import boto3
from app.core.config import settings


@lru_cache
def get_cognito_client():
    return boto3.client(
        "cognito-idp",
        region_name=settings.AWS_REGION
    )


@lru_cache
def get_lambda_client():
    return boto3.client(
        "lambda",
        region_name=settings.AWS_REGION
    )


class LazyBoto3Client:
    def __init__(self, factory):
        self._factory = factory

    def __getattr__(self, item):
        return getattr(self._factory(), item)


client_cognito = LazyBoto3Client(get_cognito_client)
client_lambda = LazyBoto3Client(get_lambda_client)
