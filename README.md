# dslbot (minimal, no Lark/Typer)

## 运行
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python run_repl.py samples/logistics.dsl
python run_repl.py samples/campus.dsl
python run_repl.py samples/refund.dsl