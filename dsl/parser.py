#-*- coding: utf-8 -*-
#文件位置：dsl/parser.py
#作用：加载Lark语法，解析DSL文本为抽象语法树（AST）并做最小结构化转换
from __future__ import annotations   #未来注解特性，允许向前引用
from dataclasses import dataclass   #用于简介定义数据类
from typing import List, Union  #类型提示
from lark import Lark, Transformer, v_args  #Lark解析器工具
import pathlib  #读取grammar.lark文件

#定义数据类：表示DSL的结构化结果
@dataclass
class Condition:    # 条件统一结构
    kind: str   #‘intent’/‘contains’/‘always’
    value: str  #对应的值，如意图名、关键词或空串

@dataclass
class Action:   #动作统一结构
    kind: str   #‘reply’/‘set’/‘goto’
    key: str    #对于set是变量名：对于reply/goto可为空串
    value: str  #对于reply是回复内容，对于set是值，对于goto是目标意图名

@dataclass
class Rule:    #规则：当...则... 
    condition: Condition    #条件
    action: Action  #动作

@dataclass
class IntentDef:    #意图定义
    name: str   #意图名称
    rules: List[Rule]   #规则列表

@dataclass
class Program:  #整个程序
    intents: List[IntentDef]    #所有意图

#定义Lark的Transformer：把解析树转换为上面的数据类
@v_args(inline=True)    #让回调函数的参数更直接
class DSLTransformer(Transformer):
    def start(self, *stmts):    #顶层start收集多个语句
        intents = [s for s in stmts]    #语句都是IntentDef
        return Program(intents=intents)
    
    def intent_def(self, _kw, name, _lbrace, *rules):
        rules_list = list(rules)
        return IntentDef(name=str(name),rules=rules_list)
    
    def rule(self, _when, cond, _them, act, _semi): #when condition then action；
        return Rule(condition=cond, action=act)
    
    def condition(self, *args): #复合分支：intent==NAME|contains “str”|always
        #Lark已经将tokens传入，我们依据关键字判断
        text = " ".join(str(a) for a in args)   #调试用
        #结构：【“intent”，“==”，NAME】或【“contains”，STRING】或【“always”】
        if len(args) == 3 and str(args[0]) == "intent" and str(args[1]) == "==":
            return Condition(kind="intent", value=str(args[2]))
        if len(args) == 2 and str(args[0]) == "contains":
            #args【1】是字符串的token，形如“\”快递\“”，需要去除引号
            return Condition(kind="contains", value=args[1][1:-1])
        if len(args) ==1 and str(args[0]) == "always":
            return Condition(kind="always", value="")
        raise ValueError(f"无法识别的条件：{text}")
    
    def action(self, *args):
        #可能形态
        #【“reply”，STRING】
        #【“set”， NAME， “=”， STRING】
        #【“goto”， NAME】
        if len(args) == 2 and str(args[0]) == "reply":
            return Action(kind="reply", key="", value=args[1][1:-1])
        if len(args) == 4 and str(args[0]) == "set" and str(args[2]) == "=":
            return Action(kind="set", key=str(args[1]), value=args[3][1:-1])
        if len(args) == 2 and str(args[0]) == "goto":
            return Action(kind="goto", key="", value=str(args[1]))
        raise ValueError(f"无法识别的动作：{args}")

#构建Lark解析器实例（加载grammar.lark）
def load_parser() -> Lark:
    #定位语法文件路径：当前文件所在目录/dsl/grammar.lark
    grammar_path = pathlib.Path(__file__).with_name("grammar.lark")
    #读取语法内容为字符串
    grammar = grammar_path.read_text(encoding="utf-8")
    #创建Lark实例，lalr算法更高效
    return Lark(grammar, start="start", parser="lalr")

#对外的解析函数：输入DLS文本，返回Program数据结构
def parse_program(text: str) -> Program:
    #获取解析器
    parser = load_parser()
    #解析得到的解析树
    tree = parser.parse(text)
    #用Transformer转换为数据类
    program = DSLTransformer().transform(tree)
    #返回Program对象
    return program