import os
import json

from unittest import TestCase

from app import REQUIRED_ENVS, parse_request
from app import Config, Req
from app import UndefinedEnvsError, PayloadParseError, PayloadMissingFieldsError
from app import get_configs_by_env


class SendEmailUnitTest(TestCase):
    pass


class ParseRequestUnitTest(TestCase):
    def test_expected_req_parse_error(self):
        invalid_event = {
            ''
        }

        with self.assertRaises(PayloadParseError) as ctx:
            parse_request(invalid_event)

    def test_expected_req_parse_error_when_invalid_json(self):
        invalid_event = {
            'Records': [{
                'body': "invalid json"
            }]
        }

        with self.assertRaises(PayloadParseError) as ctx:
            parse_request(invalid_event)

    def test_expected_req_parse_error_when_missing_field(self):
        invalid_event = {
            'Records': [{
                'body': json.dumps({
                    "type": "email",
                })
            }]
        }

        expected = PayloadMissingFieldsError(['payload'])
        with self.assertRaises(PayloadMissingFieldsError) as ctx:
            parse_request(invalid_event)

        self.assertEqual(str(expected), str(ctx.exception))

    def test_expected_parsed_req(self):
        expected_type = "email"
        expected_payload = "payload"

        fake_event = {
            'Records': [{
                'body': json.dumps({
                    "type": expected_type,
                    "payload": expected_payload,
                })
            }]
        }

        expected = Req(type=expected_type, payload=expected_payload)
        actual = parse_request(fake_event)

        self.assertEqual(expected, actual)


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

    def test_expected_undefined_envs_error_single(self):
        os.environ['SES_AWS_REGION'] = 'test region'

        expected = UndefinedEnvsError(['SES_SENDER_EMAIL'])
        with self.assertRaises(UndefinedEnvsError) as ctx:
            get_configs_by_env()

        self.assertEqual(str(expected), str(ctx.exception))

    def test_expected_undefined_envs_error(self):
        expected = UndefinedEnvsError(REQUIRED_ENVS)
        with self.assertRaises(UndefinedEnvsError) as ctx:
            get_configs_by_env()

        self.assertEqual(str(expected), str(ctx.exception))
