import os
import json

from unittest import TestCase

from app import handler, REQUIRED_ENVS
from app import Config, Payload
from app import UndefinedEnvsError, PayloadParseError, PayloadMissingFieldsError
from app import get_configs_by_env, parse_message_payload


class SendEmailUnitTest(TestCase):
    pass


class ParseMessagePayloadUnitTest(TestCase):
    def test_expected_payload_parse_error(self):
        invalid_event = {
            ''
        }

        with self.assertRaises(PayloadParseError) as ctx:
            parse_message_payload(invalid_event)

    def test_expected_payload_parse_error_when_invalid_json(self):
        invalid_event = {
            'Records': [{
                'body': "invalid json"
            }]
        }

        with self.assertRaises(PayloadParseError) as ctx:
            parse_message_payload(invalid_event)

    def test_expected_payload_parse_error_when_missing_field(self):
        invalid_event = {
            'Records': [{
                'body': json.dumps({
                    "to": "test to",
                    "text": "test text",
                })
            }]
        }

        expected = PayloadMissingFieldsError(['subject', 'html'])
        with self.assertRaises(PayloadMissingFieldsError) as ctx:
            parse_message_payload(invalid_event)

        self.assertEqual(str(expected), str(ctx.exception))

    def test_expected_parsed_payload(self):
        expected_to = "to@gmail.com"
        expected_subj = "subject test"
        expected_html = "test html"
        expected_text = "test text"

        fake_event = {
            'Records': [{
                'body': json.dumps({
                    "to": expected_to,
                    "subject": expected_subj,
                    "html": expected_html,
                    "text": expected_text,
                })
            }]
        }

        expected = Payload(to=expected_to, subject=expected_subj,
                           html=expected_html, text=expected_text)
        actual = parse_message_payload(fake_event)

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
