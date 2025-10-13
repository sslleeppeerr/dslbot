#-*- coding: utf-8 -*-
#文件位置：intent/mock_llm.py
#这是一个假意图识别器（不需要外网和API key）便于离线跑程序
#简单规则：根据包含关键词把用户输入映射到意图名称

from __future__ import annotations  #未来注解
from typing import List #类型提示

class MockLLMRouter:
    """
    伪LLM意图：
    如果包含‘快递’/‘物流’/‘包裹’ => intent 'logistics'
    如果包含‘退票’/‘改签’/‘退款’ => intent 'refund'
    如果包含‘选课’/‘成绩’/‘教务’ => intent 'campus'
    否则 => 'fallback'
    """

    def route(self, text: str) -> str:
        #全文小写，简化匹配
        low = text.lower()
        if any(k in low for k in ["快递", "物流", "包裹", "express", "parcel"]):
            return "logistics"
        if any(k in low for k in ["退票", "改签", "退款", "refund", "reschedule"]):
            return "refund"
        if any(k in low for k in ["选课", "成绩", "教务", "course", "grade", "registrar"]):
            return "campus"
        return "fallback"