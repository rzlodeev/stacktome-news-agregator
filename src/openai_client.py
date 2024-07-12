import requests
import json
import math
import logging

from requests import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIClient:
    MODEL_MAX_OUTPUT_TOKENS = {
        "gpt-4o": 2000,  # It's 2048 but we will left window
    }

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"

    def create_completion(self, messages: list, model: str = "gpt-4o", max_tokens: int = 2000) -> Response:
        """
        Create and return completion for OpenAI LLM model
        :param messages: Messages with system and user
        :param model: LLM model
        :param max_tokens:
        :return: OpenAI LLM answer
        """
        if not self.api_key:
            raise ValueError("API key must be set before making requests.")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "response_format": {
                "type": "json_object"
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return response
        elif response.status_code == 429:  # If given message exceeds openai token limit
            new_response = response
            while new_response.status_code == 429:
                logging.info('Articles list exceeds LLM token limit, splitting it by 2...')
                new_response = self.create_completion(messages[:len(messages)//2])
            return new_response

        else:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    def get_sentiment_score(self, articles: list[str], developer_mode=True) -> list[float]:
        """
        Get sentiment score for given articles from -1 to 1, where -1 is most negative and 1 is most positive.
        :param articles: List of articles to get score of
        :param developer_mode: Limits amount of articles given to LLM for developing
        :return: List of scores that follows articles list order
        """

        print(f"{len(articles)} articles given to calculate sentiment score")

        model = 'gpt-4o'
        #
        # # Split articles list, so it will fit in LLM token context window
        #
        # articles_amount = len(articles)
        #
        # if articles_amount > 200:  # LLM output token limit limit amount of articles we can proceed - 200 articles is slightly below 2048 tokens
        #     multiplier = math.ceil(articles_amount / (self.MODEL_MAX_OUTPUT_TOKENS.get(model) / 10))  # 1 score output is ~ 10 tokens
        # else:
        #     multiplier = 1
        #
        # if multiplier > 1:
        #     def split_list(a, n):
        #         """Splits list into n parts"""
        #         k, m = divmod(len(a), n)
        #         return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))
        #
        #     articles_list = list(split_list(articles, multiplier))
        # else:
        #     articles_list = [articles]  # If there is one part, put it in list so further code will see article list as one part
        #
        completion_answer_dict: dict = {}

        if developer_mode:
            message_content = articles[:10]
        else:
            message_content = articles[:100]  # We will proceed first 100 articles due to LLM output token limit

        openai_completion = self.create_completion(
            messages=[
                {
                    "role": "system",
                    "content": """
            You will be given a list of articles. Your goal is to provide a sentiment score for each article 
            from -1 to 1, where -1 is most negative and 1 is most positive. Response only with JSON.
            your answer will be parsed as JSON in downstream system. Example answer: \n
            {"0": -0.1453, "1": 0.2523, "2": 0.0014}. Make sure to proceed every article. Amount of items in 
            your output should be equal to amount of items in input.
            """
                },
                {
                    "role": "user",
                    "content": str(message_content)
                }],
            model=model
        )

        openai_completion = openai_completion.json().get('choices', [{}])[0].get('message', {}).get('content', '')

        try:
            completion_answer_dict.update(json.loads(openai_completion))
        except Exception as e:
            raise Exception

        if completion_answer_dict:
            return list(completion_answer_dict.values())


