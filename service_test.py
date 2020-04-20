import os
import json

from unittest import TestCase

from service import handler


def to_json(obj):
    return json.dumps(obj)


class HandlerUnitTest(TestCase):
    def setUp(self):
        os.environ.clear()

    def test_expected_return_error_not_defined_aws_region_env(self):
        expected = to_json({"msg": "SES_AWS_REGION is not defined on env"})
        actual = handler({}, None)

        self.assertEqual(expected, actual)

    def test_expected_return_error_not_defined_sender_email_env(self):
        os.environ['SES_AWS_REGION'] = 'test'

        expected = to_json({"msg": "SES_SENDER_EMAIL is not defined on env"})
        actual = handler({}, None)

        self.assertEqual(expected, actual)

    def test_expected_return_error_invalid_request_payload(self):
        os.environ['SES_SENDER_EMAIL'] = 'sender@gmail.com'
        os.environ['SES_AWS_REGION'] = 'test'

        fake_event = {
            'message': {
                'Body': {
                    'to': 'gyuhwan.a.kim@gmail.com',
                    'subject': "title",
                    'html': "fasdfasdf Hello html",
                    'text': "tthis is a text"
                }
            }
        }

        expected = to_json(
            {'msg': "invalid request payload __new__() missing 1 required positional argument: 'type'"})
        actual = handler(fake_event, None)

        self.assertEqual(expected, actual)
