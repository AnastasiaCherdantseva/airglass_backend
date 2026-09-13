# check_defaults.py
import ast
from pathlib import Path

for path in Path("app/models").rglob("*.py"):
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Проверить, есть ли default= и server_default=
            has_default = False
            has_server_default = False
            for kw in node.keywords:
                if kw.arg == "default":
                    has_default = True
                if kw.arg == "server_default":
                    has_server_default = True
            
            if has_default and not has_server_default:
                print(f"❌ {path}:{node.lineno} — default без server_default")