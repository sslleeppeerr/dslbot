# -*- coding: utf-8 -*-
# 文件位置：runtime/actions.py
# 作用：执行器使用的动作实现（reply/set/goto），含最简模板替换 {var}

from __future__ import annotations
from typing import Dict
from runtime.state import ConversationState

def render_template(text: str, vars: Dict[str, str]) -> str:
    """非常简化的模板替换：把 {key} 替换为 vars[key]（若无则不替换）。"""
    for k, v in vars.items():                       # 遍历状态变量
        text = text.replace("{" + k + "}", str(v))  # 逐个替换
    return text

def do_reply(state: ConversationState, text: str) -> str:
    """执行 reply：渲染模板 -> 记录到 last_reply -> 返回文本。"""
    rendered = render_template(text, state.vars)    # 模板替换
    state.last_reply = rendered                     # 记录最近回复
    return rendered                                 # 给解释器返回

def do_set(state: ConversationState, key: str, value: str) -> None:
    """执行 set：向变量表写入键值。"""
    state.set_var(key, value)

def do_goto(state: ConversationState, intent_name: str) -> None:
    """执行 goto：切换当前意图。"""
    state.current_intent = intent_name
