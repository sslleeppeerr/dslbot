# -*- coding: utf-8 -*-
# 文件位置：intent/llm_client.py
# 作用：OpenAI 兼容接口；若无 OPENAI_API_KEY 则自动回退到 Mock。

from __future__ import annotations
import os
from typing import Optional
try:
    import requests                       # 尝试导入 requests；没有也能跑（走 Mock）
except Exception:
    requests = None

from intent.mock_llm import MockLLMRouter

class OpenAICompatRouter:
    """
    最小可用的 OpenAI 兼容路由器：
      - 读取 OPENAI_API_KEY / OPENAI_BASE_URL
      - 调 /chat/completions 让模型输出一个 intent
      - 失败或无 Key 时回退到 Mock
    """

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
        self.model = model
        self.mock = MockLLMRouter()

    def route(self, text: str) -> str:
        if not self.api_key or not requests:      # 没有 Key 或没装 requests → 走 Mock
            return self.mock.route(text)
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
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
            content = (data["choices"][0]["message"]["content"]).strip().lower()
            if content in {"logistics", "refund", "campus"}:
                return content
            return "fallback"
        except Exception:
            return self.mock.route(text)
