from langchain.tools import tool
import io, contextlib

@tool("python_repl")
def python_repl(code: str) -> str:
    """Run small Python snippets in an isolated namespace. Returns stdout/last value."""
    ns = {}
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            result = eval(code, {}, ns) if ("__" not in code and "\n" not in code) else None
            if result is None:
                exec(code, {}, ns)
        out = buf.getvalue()
        if result is not None:
            out += repr(result)
        return out.strip() or "<no output>"
    except Exception as e:
        return f"Python REPL error: {e}"
