#-*- coding: utf-8 -*-
#文件位置: runntime/executer.py
#解释器执行引擎；根据Program（AST）与当前会话状态，匹配规则并执行动作

from __future__ import annotations  #未来注解
from typing import Optional, List   #类型提示
from dsl.parser import Program, IntentDef, Rule, Condition, Action  #AST类型
from runtime.state import ConversationState #会话状态
from runtime.actions import do_reply, do_set, do_goto   #动作实现

class Interpreter:
    """解释器：持有一个Program（DSL AST），并提供step（）方法来给定用户输入与意图，执行一次规则匹配与动作"""
    
    def __init__(self, program, Program) -> None:
        #保存AST
        self.program = program
        #建立意图索引，便于快速按名称查意图
        self.intent_map = {i.name: i for i in program.intents}

    def _match_condition(self, cond: Condition, user_text: str, current_intent: str) ->bool:
        """
        内部方法：判断单个条件是否满足。
        - intent==NAME：当前意图名等于NAME
        - contents “xxx”：用户输入包含子串xxx（大小写不变，简化处理）
        - always：恒为真
        """
        if cond.kind == "intent":
            return current_intent == cond.value
        if cond.kind == "contains":
            return cond.value in user_text
        if cond.kind == "always":
            return True
        return False
    
    def _run_action(self, action: Action, state: ConversationState) -> Optional[str]:
       """
       内部方法：执行动作，返回可输出的回复文本（仅reply有输出）
       - reply“...”：渲染后返回文本
       - set k="v"：写入状态，不返回
       - goto NAME：更改当前意图，不返回
       """
       if action.kind == "reply":
           return do_reply(state, action.value)
       if action.kind == "set":
           return do_set(state, action.key, action.value)
           return None
       if action.kind == "goto":
           do_goto(state, action.value)
           return None
       raise ValueError(f"未知动作：{action.kind}")
    
    def step(self, state: ConversationState, user_text: str) -> Optional[str]:
        """
        对话执行第一步：
        1）根据state.current_intent找出意图定义
        2）遍历其规则，找到第一个条件匹配的rule
        3）执行动作，可能改变当前意图或返回回复
        """

        intent : Optional[IntentDef] = self.intent_map.get(state.current_intent)
        #若当前意图不存在于程序中，直接返回提示
        if not intent:
            return "对不起，当前意图未定义。"
        
        #遍历规则，匹配条件
        for rule in intent.rules:
            if self._match_condition(rule.condition, user_text, state.current_intent):

                result = self._run_action(rule.action, state)
                return result
        #未匹配到任何规则    
        return "抱歉，我不太明白你的意思。"

