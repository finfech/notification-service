import os
import json

from unittest import TestCase

from service import handler, UndefinedEnvsError, REQUIRED_ENVS, Config, get_configs_by_env


def to_json(obj):
    return json.dumps(obj)


class GetConfigsByEnvUnitTest(TestCase):
    def setUp(self):
        os.environ.clear()

    def test_expected_configs(self):
        expected_region = 'test-region'
        expected_sender_email = 'test@test.com'

        os.environ['SES_AWS_REGION'] = expected_region
        os.environ['SES_SENDER_EMAIL'] = expected_sender_email

        expected = Config(
            ses_aws_region=expected_region,
            ses_sender_email=expected_sender_email,
        )

        actual = get_configs_by_env()
        self.assertEqual(expected, actual)

    def test_expected_undefined_envs_error(self):
        expected = UndefinedEnvsError(REQUIRED_ENVS)
        with self.assertRaises(UndefinedEnvsError) as ctx:
            get_configs_by_env()

        self.assertEqual(str(expected), str(ctx.exception))


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
            'Records': [{
                'body': json.dumps({
                    'to': 'gyuhwan.a.kim@gmail.com',
                    'subject': "title",
                    'html': "fasdfasdf Hello html",
                    'text': "tthis is a text"
                })
            }]
        }

        expected = to_json(
            {'msg': "invalid request payload __new__() missing 1 required positional argument: 'type'"})
        actual = handler(fake_event, None)

        self.assertEqual(expected, actual)
