#-*- coding: utf-8 -*-
#文件位置：runtime/state.py
#保存会话状态（变量名、当前意图等），便于执行器读写
from __future__ import annotations  #未来注解
from dataclasses import dataclass, field    #数据类
from typing import Dict #字典类型

@dataclass
class ConversationState:
    #当前意图名（由LLM或goto设置）
    current_intent: str = ""
    #变量表（set动作用）
    vars: Dict[str, str] = field(default_factory=dict)
    #最近一次回复文本（reply动作用）
    last_reply: str = ""

    def set_var(self, key: str, value: str) -> None:
        """设置一个变量到状态表"""
        self.vars[key] = value

    def get_var(self, key: str, default: str = ""):
        """读取变量，不存在则返回默认值"""
        return self.vars.get(key,default)
