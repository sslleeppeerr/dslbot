# -*- coding: utf-8 -*-
# 文件：intent/mock_llm.py
# 作用：离线路由（关键词），与“意图黏住”配合即可保证对话连贯。

from __future__ import annotations

class MockLLMRouter:
    def route(self, text: str) -> str:
        low = text.lower()
        # —— 物流关键词（可按需继续加）——
        if any(k in low for k in ["快递", "物流", "包裹", "单号", "express", "parcel"]):
            return "logistics"
        # —— 退改签关键词 —— 
        if any(k in low for k in ["退票", "改签", "退款", "refund", "reschedule"]):
            return "refund"
        # —— 校园教务关键词 —— 
        if any(k in low for k in ["选课", "成绩", "教务", "course", "grade", "registrar"]):
            return "campus"
        # 未识别 → fallback（注意：入口会“黏住”不覆盖现有意图）
        return "fallback"
