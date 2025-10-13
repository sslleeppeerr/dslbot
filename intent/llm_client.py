# -*- coding: utf-8 -*-
#文件位置：intent/llm_client.py
#真实LLM适配层，若没有API key，会自动退回Mock

from __future__ import annotations  #未来注解
import os   #读取环境变量
import requests #HTTP请求
from typing import Optional #类型提示
from intent.mock_llm import MockLLMRouter #备用路由

class OpenAICompatRouter:
    """
    一个最小可用的OPENAI兼容路由器：
    读取OPENAI_API_KEY和OPENAI_BASE_URL
    调用chat.completions接口，让模型产出意图名
    若失败则回退到Mock
    """

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model
        self.mock = MockLLMRouter()

    def route(self, text: str) -> str:
        #没有key直接走mock
        if not self.api_key:
            return self.mock.route(text)
        
        try:
            #构造请求体（OpenAI Chat Completions兼容）
            url = f"{self.base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content":(
                            "You are a router. Output ONLY one word intent among: "
                            "logistics, refund, campus, fallback" 
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                "temperature": 0.0,
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            #解析模型输出模版
            content = data["choices"][0]["message"]["content"].strip().lower()
            #简单清洗为合法集合之一
            if content in {"logistics", "refund", "campus"}:
                return content
            return "fallback"
        except Exception:
            #任何异常都回退到Mock
            return self.mock.route(text)