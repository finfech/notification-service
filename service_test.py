import os
import json

from unittest import TestCase

from service import handler


def to_json(obj):
    return json.dumps(obj)


class HandlerUnitTest(TestCase):
    def test_expected_return_error_not_defined_aws_region_env(self):
        expected = to_json({"msg": "SES_AWS_REGION is not defined on env"})
        actual = handler({}, None)

        self.assertEqual(expected, actual)

    def test_expected_return_error_not_defined_sender_email_env(self):
        os.environ['SES_AWS_REGION'] = 'test'

        expected = to_json({"msg": "SES_SENDER_EMAIL is not defined on env"})
        actual = handler({}, None)

        self.assertEqual(expected, actual)
