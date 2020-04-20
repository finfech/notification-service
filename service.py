import os
import json
from collections import namedtuple

import boto3

ALLOWED_TYPES = ['email']


RequestPayload = namedtuple('RequestPayload', ['type', 'to', 'subject'])
Error = namedtuple('ApiError', 'msg')


def handler(event, context):
    def to_json(obj):
        return json.dumps(obj)

    required_envs = ['AWS_REGION', 'SENDER_EMAIL']

    envs = dict()
    for env in required_envs:
        val = os.getenv(env)
        if not val:
            return to_json(Error(f'{env} is not defined on env')._asdict())
        envs[env] = val

    client = boto3.client('ses', region_name=envs['AWS_REGION'])

    return ""
