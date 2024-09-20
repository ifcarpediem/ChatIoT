from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from providers.openai_api import OpenAILLM
from utils.config import CONFIG
from utils.logs import logger

model_list = ["gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo-0125", "gpt-4o-mini", "deepseek-chat", "moonshot-v1-8k"]
llm_1 = OpenAILLM("gpt-4-turbo", CONFIG.configs)
llm_2 = OpenAILLM("gpt-4o", CONFIG.configs)
llm_3 = OpenAILLM("gpt-4o-mini", CONFIG.configs)
llm_4 = OpenAILLM("gpt-3.5-turbo-0125", CONFIG.configs)
llm_5 = OpenAILLM("deepseek-chat", CONFIG.configs)
llm_6 = OpenAILLM("moonshot-v1-8k", CONFIG.configs)

# per M tokens
prices = {
    "gpt-4-turbo": (10, 30),
    "gpt-4o": (5, 15),
    "gpt-4o-mini": (0.15, 0.6),
    "gpt-3.5-turbo-0125": (0.5, 1.5),
    "deepseek-chat": (0.14, 0.28),
    "moonshot-v1-8k": (12 / 7.15, 12 / 7.15)
}

app = FastAPI()


class ChatRequest(BaseModel):
    model: str
    messages: list
    format: str

@app.post("/llm/ask")
async def ask(request: ChatRequest) -> dict:
    try:
        logger.info(f"request: {request}")
        if request.model not in model_list:
            raise HTTPException(status_code=400, detail="Unsupported model")
        if request.model == "gpt-4-turbo":
            if request.format == 'json':
                response = llm_1.chat_completion_json_v1(request.messages)
            elif request.format == 'text' or request.format == '':
                response = llm_1.chat_completion_text_v1(request.messages)
            else:
                raise HTTPException(status_code=400, detail="Unsupported response format")
        elif request.model == "gpt-4o":
            if request.format == 'json':
                response = llm_2.chat_completion_json_v1(request.messages)
            elif request.format == 'text' or request.format == '':
                response = llm_2.chat_completion_text_v1(request.messages)
            else:
                raise HTTPException(status_code=400, detail="Unsupported response format")
        elif request.model == "gpt-4o-mini":
            if request.format == 'json':
                response = llm_3.chat_completion_json_v1(request.messages)
            elif request.format == 'text' or request.format == '':
                response = llm_3.chat_completion_text_v1(request.messages)
            else:
                raise HTTPException(status_code=400, detail="Unsupported response format")
        elif request.model == "gpt-3.5-turbo-0125":
            if request.format == 'json':
                response = llm_4.chat_completion_json_v1(request.messages)
            elif request.format == 'text' or request.format == '':
                response = llm_4.chat_completion_text_v1(request.messages)
            else:
                raise HTTPException(status_code=400, detail="Unsupported response format")
        elif request.model == "deepseek-chat":
            if request.format == 'json':
                response = llm_5.chat_completion_json_v1(request.messages)
            elif request.format == 'text' or request.format == '':
                response = llm_5.chat_completion_text_v1(request.messages)
            else:
                raise HTTPException(status_code=400, detail="Unsupported response format")
        elif request.model == "moonshot-v1-8k":
            if request.format == 'json':
                response = llm_6.chat_completion_json_v1(request.messages)
            elif request.format == 'text' or request.format == '':
                response = llm_6.chat_completion_text_v1(request.messages)
            else:
                raise HTTPException(status_code=400, detail="Unsupported response format")
        logger.info(f"Response from {request.model}: {response}")
        rsp = response.choices[0].message.content
        usage = response.usage
        completion_tokens = usage.completion_tokens
        prompt_tokens = usage.prompt_tokens
        response_data = {
            "rsp": rsp,
            "completion_tokens": completion_tokens,
            "prompt_tokens": prompt_tokens,
            "cost": (completion_tokens * prices[request.model][0] + prompt_tokens * prices[request.model][1]) * 7.15 / 1e6
        }
        return response_data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=ve)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("llm_service_api:app", host="0.0.0.0", port=10000, reload=True, debug=True)