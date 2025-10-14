
# -*- coding: utf-8 -*-
# 文件位置：dsl/parser.py
# 作用：手写一个极简 DSL 解析器（不依赖 Lark），解析为 AST 数据类。
# 支持的语法：
#   INTENT <NAME> { <RULE>+ }
#   RULE: when <condition> then <action> ;
#   condition: intent == <NAME> | contains "..." | always
#   action: reply "..." | set <NAME> = "..." | goto <NAME>

from __future__ import annotations              # 允许前向引用类型
from dataclasses import dataclass               # 简洁的数据类
from typing import List, Tuple                  # 类型标注
import re                                       # 正则，用于简单切词
import ast
# ========= AST 数据结构 =========

@dataclass
class Condition:
    kind: str            # 'intent' / 'contains' / 'always'
    value: str           # 对应值：意图名 / 关键词 / 空串

@dataclass
class Action:
    kind: str            # 'reply' / 'set' / 'goto'
    key: str             # 对 set：变量名；其它为空串
    value: str           # reply 的文本 / set 的值 / goto 的目标意图名

@dataclass
class Rule:
    condition: Condition # 条件
    action: Action       # 动作

@dataclass
class IntentDef:
    name: str            # 意图名
    rules: List[Rule]    # 该意图的规则集

@dataclass
class Program:
    intents: List[IntentDef]  # 所有意图

# ========= 简单的词法辅助 =========

# 提取字符串常量（双引号包裹，支持 \" 转义）的正则
STRING_RE = re.compile(r'"((?:\\.|[^"\\])*)"')
# 去掉注释：// 到行尾
LINE_COMMENT_RE = re.compile(r'//.*?$')
# 多个空白折叠为一个空格，便于匹配
WS_RE = re.compile(r'\s+')

def _strip_comments(line: str) -> str:
    """去除行内 // 注释。"""
    return LINE_COMMENT_RE.sub('', line)

def _unescape(s: str) -> str:
    """
    正确还原 DSL 字符串字面量：
    - 保留中文原样
    - 正确处理 \" \\n \\t 等转义
    """
    return ast.literal_eval(f'"{s}"')  # 让 Python 自己按字面量规则解析

# ========= 解析核心 =========

def parse_program(text: str) -> Program:
    """
    把完整 DSL 文本解析为 Program。
    解析策略：逐行扫描，匹配 INTENT 开始和结束（花括号成对），
    在块内部解析一行一条的规则（以分号 ; 结尾）。
    """
    lines = text.splitlines()                    # 逐行读取
    intents: List[IntentDef] = []               # 收集意图
    i = 0                                       # 行号指针

    while i < len(lines):
        raw = lines[i]                          # 取原始行
        line = _strip_comments(raw).strip()     # 去注释+两端空白
        i += 1                                  # 自增行号（下次读下一行）
        if not line:                            # 空行跳过
            continue

        # 期待 INTENT 开始：INTENT <NAME> {
        if line.startswith("INTENT"):
            # 用正则抓取名字和左花括号（允许空格）
            m = re.match(r'^INTENT\s+([A-Za-z_]\w*)\s*\{', line)
            if not m:                           # 不匹配就报错
                raise SyntaxError(f"INTENT 头部语法错误：{raw}")
            intent_name = m.group(1)            # 提取意图名
            rules: List[Rule] = []              # 新意图的规则列表

            # 如果本行除了 { 之后还有内容（严格起见不允许），我们也忽略
            # 继续读取直到遇到独立的 '}' 一行
            while i < len(lines):
                raw_rule = lines[i]             # 当前规则行原始内容
                line_rule = _strip_comments(raw_rule).strip()
                i += 1

                if not line_rule:               # 空行跳过
                    continue
                if line_rule == "}":            # 意图块结束
                    break

                # 规则必须以 ; 结尾
                if not line_rule.endswith(";"):
                    raise SyntaxError(f"规则缺少分号 ';'：{raw_rule}")
                # 去掉末尾分号
                stmt = line_rule[:-1].strip()

                # 规则形态：when <cond> then <action>
                if not stmt.lower().startswith("when "):
                    raise SyntaxError(f"规则应以 when 开头：{raw_rule}")
                # 按 then 分裂（只分一次）
                parts = re.split(r'\bthen\b', stmt, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) != 2:
                    raise SyntaxError(f"规则缺少 then：{raw_rule}")
                cond_text = parts[0].strip()[len("when "):].strip()
                act_text = parts[1].strip()

                cond = _parse_condition(cond_text)   # 解析条件
                act = _parse_action(act_text)        # 解析动作
                rules.append(Rule(condition=cond, action=act))  # 收集规则

            # 退出 while 时应已遇到 '}'，否则说明缺少右花括号
            else:
                raise SyntaxError(f"意图 {intent_name} 缺少右花括号 '}}'")

            intents.append(IntentDef(name=intent_name, rules=rules))  # 收集意图
            continue

        # 如果遇到非空行且不是 INTENT 开头，认为是语法错误
        raise SyntaxError(f"无法识别的语句：{raw}")

    return Program(intents=intents)              # 返回 AST

def _parse_condition(text: str) -> Condition:
    """
    解析条件：
      - intent == NAME
      - contains "xxx"
      - always
    大小写严格（按 DSL 样例）。
    """
    # intent == NAME
    m = re.match(r'^intent\s*==\s*([A-Za-z_]\w*)$', text)
    if m:
        return Condition(kind="intent", value=m.group(1))

    # contains "xxx"
    m = re.match(r'^contains\s*(".*")$', text)
    if m:
        s = m.group(1)
        m2 = STRING_RE.fullmatch(s)
        if not m2:
            raise SyntaxError(f"contains 的字符串不合法：{text}")
        return Condition(kind="contains", value=_unescape(m2.group(1)))

    # always
    if text == "always":
        return Condition(kind="always", value="")

    # 其它不合法
    raise SyntaxError(f"无法识别的条件：{text}")

def _parse_action(text: str) -> Action:
    """
    解析动作：
      - reply "xxx"
      - set name = "xxx"
      - goto NAME
    """
    # reply "xxx"
    m = re.match(r'^reply\s*(".*")$', text)
    if m:
        s = m.group(1)
        m2 = STRING_RE.fullmatch(s)
        if not m2:
            raise SyntaxError(f"reply 的字符串不合法：{text}")
        return Action(kind="reply", key="", value=_unescape(m2.group(1)))

    # set name = "xxx"
    m = re.match(r'^set\s+([A-Za-z_]\w*)\s*=\s*(".*")$', text)
    if m:
        key = m.group(1)
        s = m.group(2)
        m2 = STRING_RE.fullmatch(s)
        if not m2:
            raise SyntaxError(f"set 的值字符串不合法：{text}")
        return Action(kind="set", key=key, value=_unescape(m2.group(1)))

    # goto NAME
    m = re.match(r'^goto\s+([A-Za-z_]\w*)$', text)
    if m:
        return Action(kind="goto", key="", value=m.group(1))

    # 其它不合法
    raise SyntaxError(f"无法识别的动作：{text}")
