import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

response = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Say hello in one sentence"}
    ]
)

print(response.content[0].text)