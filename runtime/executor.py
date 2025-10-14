# -*- coding: utf-8 -*-
# 文件：runtime/executor.py
# 作用：解释器执行引擎（两阶段执行：先副作用，再回复）

from __future__ import annotations
from typing import Optional, List
from dsl.parser import Program, IntentDef, Rule, Condition, Action
from runtime.state import ConversationState
from runtime.actions import do_reply, do_set, do_goto

class Interpreter:
    """持有一个 Program（DSL AST），提供 step() 执行一轮对话。"""

    def __init__(self, program: Program) -> None:
        self.program = program
        # 建立意图索引，O(1) 获取 IntentDef
        self.intent_map = {i.name: i for i in program.intents}

    def _match_condition(self, cond: Condition, user_text: str, current_intent: str) -> bool:
        """判断单个条件是否满足。"""
        if cond.kind == "intent":
            return current_intent == cond.value
        if cond.kind == "contains":
            return cond.value in user_text
        if cond.kind == "always":
            return True
        return False

    def _run_action_effect(self, action: Action, state: ConversationState) -> None:
        """
        执行“无输出动作”的副作用（set/goto）。
        设计：在阶段一里仅做副作用，不返回字符串。
        """
        if action.kind == "set":
            do_set(state, action.key, action.value)
        elif action.kind == "goto":
            do_goto(state, action.value)
        # reply 不在这里执行

    def _run_action_reply(self, action: Action, state: ConversationState) -> Optional[str]:
        """
        执行“输出动作”（reply）。
        设计：阶段二里只要遇到第一条 reply 就返回本轮输出。
        """
        if action.kind == "reply":
            return do_reply(state, action.value)
        return None

    def step(self, state: ConversationState, user_text: str) -> str:
        """
        两阶段执行：
          阶段一：遍历所有匹配规则，先执行 set/goto 等“无输出副作用”，准备状态；
          阶段二：再次遍历匹配规则，命中第一条 reply 就返回；
          若没有任何 reply，则返回上次的 last_reply 或兜底提示。
        """
        # 获取当前意图
        intent: Optional[IntentDef] = self.intent_map.get(state.current_intent)
        if not intent:
            return "对不起，当前意图未定义。"

        # —— 阶段一：只做副作用（set/goto），允许多条规则叠加状态 ——
        for rule in intent.rules:
            if self._match_condition(rule.condition, user_text, state.current_intent):
                # 仅在副作用阶段处理 set/goto
                self._run_action_effect(rule.action, state)

        # —— 阶段二：找到第一条匹配的 reply 并返回 ——
        for rule in intent.rules:
            if self._match_condition(rule.condition, user_text, state.current_intent):
                out = self._run_action_reply(rule.action, state)
                if out is not None:               # 第一条 reply 就返回
                    return out

        # 若本轮没有新回复，但历史上有 last_reply，则返回它（轻度容错）
        if state.last_reply:
            return state.last_reply
