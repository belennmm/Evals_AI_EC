"""Adaptador de Promptfoo para el flujo real de la arquitectura centralizada."""

import json
from pathlib import Path
import sys
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

# Cargar el entorno antes de importar módulos que leen variables al inicializarse.
load_dotenv(PROJECT_ROOT / ".env", override=False)

from agents import Runner
from agents.items import ToolCallItem
from centralized.manager_agent import create_manager


def call_api(prompt: str, options: dict, context: dict) -> dict:
    manager = create_manager()
    started = perf_counter()
    result = Runner.run_sync(manager, prompt)
    latency_ms = (perf_counter() - started) * 1000
    tool_calls = [
        {"agent": item.agent.name, "call": item.to_input_item()}
        for item in result.new_items
        if isinstance(item, ToolCallItem)
    ]
    return {
        "output": result.final_output,
        "metadata": {
            "tool_calls": tool_calls,
            "tool_calls_scope": "manager_run_items",
            "last_agent": result.last_agent.name,
            "latency_ms": latency_ms,
        },
    }


if __name__ == "__main__":
    for question in (
        "cuál es el peso máximo",
        "Quiero agendar una cita para mañana a las 10",
    ):
        print(json.dumps({"question": question, **call_api(question, {}, {})},
                         ensure_ascii=False, indent=2))
