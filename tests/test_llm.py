"""Mock-only LLM configuration tests; never load the real .env or call the API."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import llm


class LLMTests(unittest.TestCase):
    def setUp(self):
        self.dotenv = patch("llm.load_dotenv")
        self.dotenv.start()
        self.addCleanup(self.dotenv.stop)
        self.env = patch.dict(os.environ, {"ARK_API_KEY": "test-only-fake-key"}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_defaults_and_secret_repr(self):
        config = llm.load_llm_config()
        self.assertEqual(config.model, llm.DEFAULT_MODEL)
        self.assertNotIn("test-only-fake-key", repr(config))

    def test_missing_key(self):
        os.environ.pop("ARK_API_KEY")
        with self.assertRaises(llm.LLMConfigurationError):
            llm.load_llm_config()

    def test_invalid_configuration(self):
        for key, value in (("ARK_TIMEOUT_SECONDS", "nan"), ("ARK_TIMEOUT_SECONDS", "0"),
                           ("ARK_MAX_RETRIES", "-1"), ("ARK_MAX_RETRIES", "a"),
                           ("ARK_MODEL", ""), ("ARK_BASE_URL", "http://example.invalid")):
            with self.subTest(key=key, value=value), patch.dict(os.environ, {key: value}):
                with self.assertRaises(llm.LLMConfigurationError):
                    llm.load_llm_config()

    def test_sdk_and_langchain_use_same_config(self):
        config = llm.load_llm_config()
        with patch("openai.OpenAI") as sdk, patch("langchain_openai.ChatOpenAI") as chat:
            llm.get_llm_client(config)
            llm.get_chat_model(config=config)
            self.assertEqual(sdk.call_args.kwargs["base_url"], chat.call_args.kwargs["base_url"])
            self.assertEqual(sdk.call_args.kwargs["api_key"], chat.call_args.kwargs["api_key"])
            self.assertEqual(chat.call_args.kwargs["model"], config.model)

    def test_generate_answer_success_and_empty_response(self):
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="response"))])
        with patch("llm.get_llm_client") as factory:
            factory.return_value.__enter__.return_value = client
            self.assertEqual(llm.generate_answer("input"), "response")
            client.chat.completions.create.return_value = SimpleNamespace(choices=[])
            with self.assertRaises(llm.LLMRequestError):
                llm.generate_answer("input")

    def test_api_error_is_sanitized(self):
        from openai import APIError
        client = Mock()
        client.chat.completions.create.side_effect = APIError("private server text", Mock(), body=None)
        with patch("llm.get_llm_client") as factory:
            factory.return_value.__enter__.return_value = client
            with self.assertRaises(llm.LLMRequestError) as caught:
                llm.generate_answer("input")
            self.assertNotIn("private server text", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
