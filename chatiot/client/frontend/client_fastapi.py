import sys
from pathlib import Path
cwd = Path.cwd()
sys.path.append(str(cwd))

from fastapi import FastAPI, HTTPException
from frontend.utils.logs import logger
from config import CONFIG
from backend.agents.jarvis import JARVIS
import asyncio

app = FastAPI()

@app.post("/ask")
async def ask(chat_request: dict) -> dict:
    try:
        query = chat_request["query"]
        logger.info(f"request: {query}")
        response, complete_flag = await JARVIS.run(query)
        return {"response": response, "complete_flag": complete_flag}
    except Exception as e:
        return {"response": str(e), "complete_flag": True}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("client_fastapi:app", host="0.0.0.0", port=10024, reload=True)
