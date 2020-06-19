import os
import json

from unittest import TestCase

from service import handler, REQUIRED_ENVS
from service import Config, Payload
from service import UndefinedEnvsError, PayloadParseError
from service import get_configs_by_env, parse_message_payload


def to_json(obj):
    return json.dumps(obj)


class ParseMessagePayloadUnitTest(TestCase):
    def test_expected_payload_parse_error(self):
        invalid_event = {
            ''
        }

        with self.assertRaises(PayloadParseError) as ctx:
            parse_message_payload(invalid_event)

    def test_expected_parsed_payload(self):
        expected_to = "to@gmail.com"
        expected_subj = "subject test"
        expected_html = "test html"
        expected_text = "test text"

        fake_event = {
            'Records': [{
                'body': {
                    "to": expected_to,
                    "subject": expected_subj,
                    "html": expected_html,
                    "text": expected_text,
                }
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

    def test_expected_undefined_envs_error(self):
        expected = UndefinedEnvsError(REQUIRED_ENVS)
        with self.assertRaises(UndefinedEnvsError) as ctx:
            get_configs_by_env()

        self.assertEqual(str(expected), str(ctx.exception))


class HandlerUnitTest(TestCase):
    def setUp(self):
        os.environ.clear()

    # def test_expected_return_error_not_defined_sender_email_env(self):
    #     os.environ['SES_AWS_REGION'] = 'test'

    #     expected = to_json({"msg": "SES_SENDER_EMAIL is not defined on env"})
    #     actual = handler({}, None)

    #     self.assertEqual(expected, actual)
