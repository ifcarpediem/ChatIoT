from openai import OpenAI
from tenacity import retry, stop_after_attempt
import httpx

class OpenAILLM():
    def __init__(self, model: str, config: dict):
        if "openai" not in config["llm_service"]["llm_models"][model]["format"]:
            raise ValueError("Model format is not supported by OpenAI API")
        self.api_key = config["llm_service"]["llm_models"][model]['api_key']
        self.model = model
        self.temperature = config["llm_service"]["llm_models"][model]['temperature']
        self.max_tokens = config["llm_service"]["llm_models"][model]['max_tokens']
        if 'base_url' in config["llm_service"]["llm_models"][model]:
            self.base_url = config["llm_service"]["llm_models"][model]['base_url']
            self.client = OpenAI(
                base_url = self.base_url, 
                api_key = self.api_key,
                http_client = httpx.Client(
                    base_url = self.base_url,
                    follow_redirects = True
                )
            )
        else:
            self.base_url = None
            self.client = OpenAI(
                api_key = self.api_key
            )
    
    @retry(stop=stop_after_attempt(6))
    def chat_completion_json_v1(self, messages: list[dict], response_format='json_object') -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format= {"type": response_format},
        )
        return response
    
    @retry(stop=stop_after_attempt(6))
    def chat_completion_text_v1(self, messages: list[dict]) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format= {"type": "text"},
        )
        return response
    
if __name__ == '__main__':
    import yaml
    config = yaml.safe_load(open('./configs/config.yaml'))
    llm = OpenAILLM('gpt-4-turbo', config)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is capital of France?"},
    ]
    response = llm.chat_completion_text_v1(messages)
    print(response)



