import os
import json
from collections import namedtuple

import boto3
from botocore.exceptions import ClientError

ALLOWED_TYPES = ['email']
CHARSET = "UTF-8"


RequestPayload = namedtuple(
    'RequestPayload', ['type', 'to', 'subject', 'html', 'text'])
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
