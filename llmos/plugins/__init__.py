"""
Plugin System - Extensible tool packs for domain-specific capabilities
"""

from typing import Dict, Any, Callable
from pathlib import Path
import importlib.util
import inspect


class PluginLoader:
    """
    Plugin loader for dynamic tool registration
    Allows domain-specific tools without hardcoding
    """

    def __init__(self, plugin_dir: Path):
        self.plugin_dir = Path(plugin_dir)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        self.tools: Dict[str, Callable] = {}

    def load_plugins(self):
        """Scan plugin directory and load all Python modules"""
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue  # Skip __init__.py and private files

            self._load_plugin(plugin_file)

    def _load_plugin(self, plugin_file: Path):
        """Load a single plugin file"""
        # Import the module
        spec = importlib.util.spec_from_file_location(
            plugin_file.stem,
            plugin_file
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find all functions decorated with @llm_tool
            for name, obj in inspect.getmembers(module):
                if hasattr(obj, '_is_llm_tool'):
                    self.tools[obj._tool_name] = obj
                    print(f"  ✓ Loaded tool: {obj._tool_name}")

    def get_tool(self, name: str) -> Callable:
        """Get a tool by name"""
        return self.tools.get(name)

    def list_tools(self) -> list:
        """List all available tools"""
        return list(self.tools.keys())


def llm_tool(name: str, description: str, schema: Dict[str, Any]):
    """
    Decorator to mark a function as an LLM tool

    Args:
        name: Tool name
        description: Tool description
        schema: JSON schema for tool parameters

    Example:
        @llm_tool("calculate", "Perform calculations", {"expression": str})
        async def calculate(expression: str):
            return eval(expression)
    """
    def decorator(func):
        func._is_llm_tool = True
        func._tool_name = name
        func._tool_description = description
        func._tool_schema = schema
        return func

    return decorator
