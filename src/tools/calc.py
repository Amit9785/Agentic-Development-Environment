from langchain.tools import tool

@tool("calc")
def calculator(expression: str) -> str:
    """Safely evaluate a simple Python math expression, e.g. '2*(3+4)'."""
    import math
    allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    allowed.update({"abs": abs, "round": round})
    try:
        return str(eval(expression, {"__builtins__": {}}, allowed))
    except Exception as e:
        return f"Calc error: {e}"
