#  -*- coding: utf-8 -*-
#文件位置：runtime/actions.py
#承载解释器执行的“动作”实现。例如reply/set/goto
#为了简单，reply支持{var}模版替换
from __future__ import annotations  #未来注释
from typing import Dict #类型提示
from runtime.state import ConversationState #导入会话状态

def render_template(text: str, vars: Dict[str, str]) -> str:
    """非严格模版替代，把{key}替换为vars【key】。这是简化实现，避免引入jinja2以减少依赖"""
    #逐个变量替换
    for k, v in vars.item():
        text = text.replace("{" + k + "}", str(v))
    return text

def do_reply(state: ConversationState, text: str) -> str:
    """执行reply：渲染模版并保存到state.last_reply，然后返回文本"""
    rendered = render_template(text, state.vars)
    state.last_reply = rendered
    return rendered

def do_set(state: ConversationState, key: str, value: str) -> None:
    """执行set：将变量写入状态"""
    state.set_var(key, value)

def do_goto(state: ConversationState, intent_name: str) -> None:
    """执行goto：切换当前意图"""
    state.current_intent = intent_name