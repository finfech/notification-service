import os
import json
from collections import namedtuple
from typing import NamedTuple, List

import boto3
from botocore.exceptions import ClientError

ALLOWED_TYPES = ['email']
CHARSET = "UTF-8"


RequestPayload = namedtuple(
    'RequestPayload', ['type', 'to', 'subject', 'html', 'text'])
Error = namedtuple('ApiError', 'msg')


class UndefinedEnvsError(Exception):
    def __init__(self, keys):
        self.keys = keys

    def __str__(self):
        return f'{self.keys} is undefined on env'


class PayloadParseError(ValueError):
    pass


class Config(NamedTuple):
    ses_aws_region: str
    ses_sender_email: str


class Payload(NamedTuple):
    to: str
    subject: str
    html: str
    text: str


def to_json(obj):
    return json.dumps(obj)


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
        body = event['Records'][0]['body']
    except Exception:
        raise PayloadParseError()

    return Payload(
        to=body['to'],
        subject=body['subject'],
        html=body['html'],
        text=body['text'],
    )


def handler(event, context):
    cfg = get_configs_by_env()
    msg = parse_message_payload(event)

    message_body = json.loads(event['Records'][0]['body'])

    try:
        req_payload = RequestPayload(**message_body)
    except TypeError as ex:
        return to_json(Error('invalid request payload ' + str(ex))._asdict())

    client = boto3.client('ses', region_name=envs['SES_AWS_REGION'])
    try:
        client.send_email(
            Destination={'ToAddresses': [req_payload.to]},
            Message={
                'Body': {
                    'Html': {'Charset': CHARSET, 'Data': req_payload.html},
                    'Text': {'Charset': CHARSET, 'Data': req_payload.text},
                },
                'Subject': {'Charset': CHARSET, 'Data': req_payload.subject}},
            Source=envs['SES_SENDER_EMAIL'],
        )
    except ClientError as ex:
        return to_json(Error(str(ex))._asdict())

    return None
