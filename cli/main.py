# -*- coding: utf-8 -*-
# 文件位置：cli/main.py
# 命令行入口：提供 repl 子命令，用于加载 DSL、接入(真|假)LLM、循环对话。

from __future__ import annotations                              # 未来注解
import pathlib                                                  # 读文件路径
import sys                                                      # 退出时使用
import typer                                                    # 命令行库
from rich.console import Console                                # 美化输出
from dsl.parser import parse_program                            # 解析 DSL
from runtime.executor import Interpreter                        # 执行器
from runtime.state import ConversationState                     # 会话状态
from intent.llm_client import OpenAICompatRouter                # 真实/伪路由

# 创建 Typer 应用
app = typer.Typer(add_completion=False)  # 关闭自动补全以简化依赖
console = Console()                      # rich 控制台

@app.command()
def repl(
    script: str = typer.Option(..., help="DSL 脚本文件路径，如 samples/logistics.dsl")
):
    """
    交互 REPL：
    1) 读取 DSL 脚本，构建解释器
    2) 使用 LLM 路由意图
    3) 根据意图进入对应状态，匹配规则并给出回复
    4) 用户输入 'exit' 退出
    """
    # 将字符串路径转为 Path 对象
    path = pathlib.Path(script)
    if not path.exists():
        console.print(f"[red]脚本不存在：{path}[/red]")
        raise typer.Exit(code=1)

    # 读取脚本文本
    text = path.read_text(encoding="utf-8")
    # 解析为 Program(AST)
    program = parse_program(text)
    # 创建解释器
    interpreter = Interpreter(program)
    # 创建会话状态
    state = ConversationState()
    # 创建 LLM 路由（内置自动 fallback 到 Mock）
    router = OpenAICompatRouter()

    console.print("[green]DSL 已加载。输入你的问题，输入 'exit' 退出。[/green]")

    # 交互循环
    while True:
        # 提示符
        user = console.input("[bold cyan]你：[/bold cyan]").strip()
        # 判定退出
        if user.lower() in {"exit", "quit", "q"}:
            console.print("[yellow]已退出。[/yellow]")
            break

        # 第一步：让 LLM 给出“顶层意图”
        intent = router.route(user)
        # 把当前意图写入状态
        state.current_intent = intent

        # 第二步：执行一步解释（匹配规则→动作）
        reply = interpreter.step(state, user)

        # 第三步：输出结果
        console.print(f"[bold magenta]机器人：[/bold magenta]{reply}")

# 允许 python -m cli.main 直接运行
if __name__ == "__main__":
    app()
