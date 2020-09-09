import os
import json

from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError


class UndefinedEnvsError(Exception):
    def __init__(self, keys):
        self.keys = keys

    def __str__(self):
        return f'{self.keys} is undefined on env'


class PayloadParseError(ValueError):
    pass


class PayloadMissingFieldsError(ValueError):
    def __init__(self, keys):
        self.keys = keys

    def __str__(self):
        return f'{self.keys} is missing on json payload'


@dataclass
class Config:
    ses_aws_region: str
    ses_sender_email: str


@dataclass
class Req:
    type: str
    payload: str


REQUIRED_ENVS = ['SES_AWS_REGION', 'SES_SENDER_EMAIL']


def get_configs_by_env() -> Config:
    if undefined_envs := [env for env in REQUIRED_ENVS if os.getenv(env) is None]:
        raise UndefinedEnvsError(undefined_envs)

    return Config(
        ses_aws_region=os.getenv('SES_AWS_REGION'),
        ses_sender_email=os.getenv('SES_SENDER_EMAIL'),
    )


def parse_request(event: dict) -> Req:
    try:
        json_str = event['Records'][0]['body']
        body = json.loads(json_str)
    except Exception:
        raise PayloadParseError()

    REQUIRED_FIELDS = ['type', 'payload']
    if missing_fields := [field for field in REQUIRED_FIELDS if field not in body]:
        raise PayloadMissingFieldsError(missing_fields)

    return Req(body['type'], body['payload'])


CHARSET = "UTF-8"


def email_handler(cfg: Config, payload) -> None:
    try:
        to = list(payload['to']),
        subject = str(payload['subject']),
        html = str(payload['html']),
        text = str(payload['text']),
    except Exception:
        raise PayloadParseError()

    client = boto3.client('ses', region_name=cfg.ses_aws_region)
    try:
        client.send_email(
            Destination={'ToAddresses': to},
            Message={
                'Body': {
                    'Html': {'Charset': CHARSET, 'Data': html},
                    'Text': {'Charset': CHARSET, 'Data': text},
                },
                'Subject': {'Charset': CHARSET, 'Data': subject}},
            Source=cfg.ses_sender_email,
        )
    except ClientError as ex:
        raise ex


def sms_handler(cfg: Config, payload) -> None:
    pass


def slack_handler(cfg: Config, payload) -> None:
    pass


def handler(event, context) -> None:
    handlers = {
        'email': email_handler,
        'slack': slack_handler,
        'sms': sms_handler,
    }

    cfg = get_configs_by_env()
    req = parse_request(event)

    action = handlers.get(req.type)
    if action is None:
        raise Exception('Not support notification type')

    action(cfg, req.payload)
