import ast
import subprocess
import os

# === Step 1: 提取函数调用关系 ===

class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls = {}
        self.current_func = None

    def visit_FunctionDef(self, node):
        self.current_func = node.name
        self.calls[self.current_func] = []
        self.generic_visit(node)
        self.current_func = None

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and self.current_func:
            self.calls[self.current_func].append(node.func.id)
        self.generic_visit(node)

def extract_function_calls(code: str):
    tree = ast.parse(code)
    visitor = FunctionCallVisitor()
    visitor.visit(tree)
    return visitor.calls


# === Step 2: 生成 PlantUML 脚本 ===

def generate_plantuml_script(call_map: dict) -> str:
    lines = ["@startuml", "skinparam ArrowColor Blue"]
    for caller, callees in call_map.items():
        for callee in callees:
            lines.append(f"{caller} --> {callee}")
    lines.append("@enduml")
    return "\n".join(lines)


# === Step 3: 写入 .puml 文件并渲染为 PNG ===

def save_plantuml_script(script: str, filename: str = "diagram.puml"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(script)

def render_plantuml_image(puml_file: str):
    # 你需要安装 Java 并下载 plantuml.jar：https://plantuml.com/download
    cmd = ["java", "-jar", "plantuml.jar", puml_file]
    subprocess.run(cmd, check=True)


# === 示例：运行完整流程 ===

if __name__ == "__main__":
    python_code = """
def main():
    data = load_data()
    processed = process_data(data)
    save_results(processed)

def load_data():
    return []

def process_data(data):
    return data

def save_results(data):
    print("Saved!")
"""

    call_map = extract_function_calls(python_code)
    plantuml_script = generate_plantuml_script(call_map)
    save_plantuml_script(plantuml_script, "diagram.puml")
    print("✅ PlantUML 脚本已保存为 diagram.puml")

    try:
        render_plantuml_image("diagram.puml")
        print("✅ 图像已生成为 diagram.png")
    except Exception as e:
        print("⚠️ 图像渲染失败，请确保已安装 Java 并下载 plantuml.jar")
        print(e)
