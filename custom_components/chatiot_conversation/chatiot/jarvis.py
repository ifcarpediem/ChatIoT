# 测试暂定使用本地server（fastapi构建），发送query，返回response
# 后续修改为Intergation内部
import requests
from .logs_chatiot import _logger
import asyncio

url = "http://192.168.0.127:10024/ask"

def ask(query):
    _logger.debug(f"jarvis.py: ask: query: {query}")
    try:
        res = requests.post(url, json={"query": query})
        _logger.debug(f"jarvis.py: ask: res: {res}")
        return res.json()["response"]
    except Exception as e:
        _logger.error(f"jarvis.py: ask: error: {e}")
        return "Error"

async def test_1(test_str):
    _logger.debug(f"jarvis.py: test_1: test_str: {test_str}")
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, ask, test_str)
        _logger.debug(f"jarvis.py: test_1: result: {result}")
        return result
    except Exception as e:
        _logger.error(f"jarvis.py: test_1: error: {e}")
        return "Error"

if __name__ == "__main__":
    while True:
        test_str = input("Input: ")
        if test_str == "exit":
            break
        print(test_1(test_str))