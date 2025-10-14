# -*- coding: utf-8 -*-
# 文件：run_repl.py
# 运行：python run_repl.py samples/logistics.dsl

from __future__ import annotations
import sys
import pathlib

# —— 保证能导入本项目包 ——
ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dsl.parser import parse_program
from runtime.executor import Interpreter
from runtime.state import ConversationState
from intent.llm_client import OpenAICompatRouter

# （可选）保证控制台 UTF-8 输出，避免中文乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def main(argv=None) -> None:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print("用法: python run_repl.py <DSL脚本路径>")
        sys.exit(2)

    path = pathlib.Path(argv[0])
    if not path.exists():
        print(f"脚本不存在: {path}")
        sys.exit(1)

    # 解析 DSL -> AST
    program = parse_program(path.read_text(encoding="utf-8"))
    # 创建解释器和会话状态
    interpreter = Interpreter(program)
    state = ConversationState()
    # LLM 路由（无 Key 自动走 Mock）
    router = OpenAICompatRouter()

    print("DSL 已加载。输入你的问题，输入 'exit' 退出。")

    while True:
        try:
            user = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出。")
            break

        if user.lower() in {"exit", "quit", "q"}:
            print("已退出。")
            break

        # —— 意图“黏住”：非 fallback 才更新；fallback 不覆盖当前意图 ——
        routed_intent = router.route(user)         # 本轮路由结果
        if routed_intent != "fallback":            # 只在明确识别出意图时才切换
            state.current_intent = routed_intent
        if not state.current_intent:               # 首次还没意图时兜底
            state.current_intent = "fallback"

        # —— 两阶段执行在解释器中完成，这里只要调用一步即可 ——
        reply = interpreter.step(state, user)
        print(f"机器人：{reply}")

if __name__ == "__main__":
    main()
