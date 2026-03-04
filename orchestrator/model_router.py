import os
from dotenv import load_dotenv
import anthropic
from openai import OpenAI
import replicate

load_dotenv()

anthropic_client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


MODEL_CONFIG = {
    "planner": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-0"
    },
    "coder": {
        "provider": "openai",
        "model": "gpt-4o"
    },
    "reviewer": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-0"
    },
    "fallback": {
        "provider": "replicate",
        "model": "meta/meta-llama-3-70b-instruct"
    }
}

class ModelRouter:

    def generate(self, role, prompt):

        config = MODEL_CONFIG[role]

        provider = config["provider"]
        model = config["model"]

        print(f"[MODEL ROUTER] role={role} provider={provider} model={model}")

        if provider == "anthropic":
            return self._call_claude(model, prompt)

        if provider == "openai":
            return self._call_openai(model, prompt)

        if provider == "replicate":
            return self._call_replicate(model, prompt)
            
    def _call_claude(self, model, prompt):

        response = anthropic_client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
        
    def _call_openai(self, model, prompt):

        response = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    def _call_replicate(self, model, prompt):

        output = replicate.run(
            model,
            input={"prompt": prompt}
        )

        return "".join(output)