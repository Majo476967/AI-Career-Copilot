from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


def get_llm_client():
    client = OpenAI(
        api_key=os.getenv("ARK_API_KEY"),
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )
    return client


def generate_answer(prompt):
    client = get_llm_client()

    response = client.chat.completions.create(
        model="doubao-1-5-lite-32k-250115",
        messages=[
            {"role": "system", "content": "你是一个专业的AI助手"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content