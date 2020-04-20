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

    def get_envs(required_envs):
        res = dict()
        for key in required_envs:
            val = os.getenv(key)
            if not val:
                return None, Error(f'{key} is not defined on env')._asdict()

            res[key] = val

        return res, None

    required_envs = ['SES_AWS_REGION', 'SES_SENDER_EMAIL']
    envs, err = get_envs(required_envs)
    if err:
        return to_json(err)

    client = boto3.client('ses', region_name=envs['SES_AWS_REGION'])

    return ""
