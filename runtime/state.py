# -*- coding: utf-8 -*-
# 文件位置：runtime/state.py
# 作用：保存会话状态（变量表、当前意图、最近回复）

from __future__ import annotations               # 未来注解
from dataclasses import dataclass, field         # 数据类
from typing import Dict                          # 字典类型

@dataclass
class ConversationState:
    current_intent: str = ""                     # 当前意图名（由 LLM 或 goto 设置）
    vars: Dict[str, str] = field(default_factory=dict)  # 变量表（set 动作使用）
    last_reply: str = ""                         # 最近一次回复文本（reply 动作写入）

    def set_var(self, key: str, value: str) -> None:
        """设置一个变量到状态表。"""
        self.vars[key] = value

    def get_var(self, key: str, default: str = "") -> str:
        """读取变量，不存在返回默认值。"""
        return self.vars.get(key, default)
