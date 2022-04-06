import os


class Config:
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
    DELAY_SECONDS = 60
    DATE_PERIOD_LIMIT = 90 * 24 * 60 * 60 # 90 days

    API_KEY = os.environ.get('API_KEY')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

    S3_BACKET_ID = 's3-backet'
    S3_ENDPOINT_URL = 'https://storage.yandexcloud.net'
    S3_SERVICE_NAME = 's3'
