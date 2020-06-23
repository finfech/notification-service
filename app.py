import os
import json

from typing import NamedTuple, List

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


class Config(NamedTuple):
    ses_aws_region: str
    ses_sender_email: str


class Payload(NamedTuple):
    to: str
    subject: str
    html: str
    text: str


REQUIRED_ENVS = ['SES_AWS_REGION', 'SES_SENDER_EMAIL']


def get_configs_by_env() -> Config:
    envs = dict()
    undefined_envs = list()

    for key in REQUIRED_ENVS:
        val = os.getenv(key)
        if not val:
            undefined_envs.append(key)
            continue

        envs[key] = val

    if undefined_envs:
        raise UndefinedEnvsError(undefined_envs)

    return Config(
        ses_aws_region=envs['SES_AWS_REGION'],
        ses_sender_email=envs['SES_SENDER_EMAIL'],
    )


def parse_message_payload(event: dict) -> Payload:
    try:
        json_str = event['Records'][0]['body']
        body = json.loads(json_str)
    except Exception:
        raise PayloadParseError()

    REQUIRED_FIELDS = ['to', 'subject', 'html', 'text']

    missing_fields = []
    for field in REQUIRED_FIELDS:
        if field not in body:
            missing_fields.append(field)

    if missing_fields:
        raise PayloadMissingFieldsError(missing_fields)

    return Payload(
        to=body['to'],
        subject=body['subject'],
        html=body['html'],
        text=body['text'],
    )


def send_email(cfg: Config, msg: Payload) -> None:
    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name=cfg.ses_aws_region)
    try:
        client.send_email(
            Destination={'ToAddresses': [msg.to]},
            Message={
                'Body': {
                    'Html': {'Charset': CHARSET, 'Data': msg.html},
                    'Text': {'Charset': CHARSET, 'Data': msg.text},
                },
                'Subject': {'Charset': CHARSET, 'Data': msg.subject}},
            Source=cfg.ses_sender_email,
        )
    except ClientError as ex:
        raise ex


def handler(event, context) -> None:
    cfg = get_configs_by_env()
    msg = parse_message_payload(event)

    send_email(cfg, msg)
