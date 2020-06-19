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


class Config(NamedTuple):
    ses_aws_region: str
    ses_sender_email: str


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


def get_envs(required_envs):
    res = dict()
    for key in required_envs:
        val = os.getenv(key)
        if not val:
            return None, Error(f'{key} is not defined on env')._asdict()

        res[key] = val

    return res, None


def handler(event, context):
    required_envs = ['SES_AWS_REGION', 'SES_SENDER_EMAIL']
    envs, err = get_envs(required_envs)
    if err:
        return to_json(err)

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

    return ""
