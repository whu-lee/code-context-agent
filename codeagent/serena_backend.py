from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


SERENA_INSTALL_COMMAND = [
    "uv",
    "tool",
    "install",
    "-p",
    "3.13",
    "serena-agent@latest",
    "--prerelease=allow",
]

SERENA_INIT_COMMAND = ["serena", "init"]


@dataclass(frozen=True)
class SerenaStatus:
    available: bool
    executable: str | None
    project: str
    install_command: list[str]
    init_command: list[str]
    start_command: list[str]
    useful_tools: list[str]

    def as_dict(self) -> dict:
        return {
            "available": self.available,
            "executable": self.executable,
            "project": self.project,
            "install_command": self.install_command,
            "init_command": self.init_command,
            "start_command": self.start_command,
            "useful_tools": self.useful_tools,
        }


def serena_status(project: Path, context: str = "claude-code") -> SerenaStatus:
    executable = shutil.which("serena")
    project_path = str(project.resolve())
    return SerenaStatus(
        available=bool(executable),
        executable=executable,
        project=project_path,
        install_command=SERENA_INSTALL_COMMAND,
        init_command=SERENA_INIT_COMMAND,
        start_command=build_start_command(project, context=context),
        useful_tools=[
            "get_symbols_overview",
            "find_symbol",
            "find_declaration",
            "find_implementations",
            "find_referencing_symbols",
            "get_diagnostics_for_file",
        ],
    )


def build_start_command(project: Path, context: str = "claude-code") -> list[str]:
    return [
        "serena",
        "start-mcp-server",
        "--project",
        str(project.resolve()),
        "--context",
        context,
    ]


def enrichment_plan(symbol: str) -> dict:
    return {
        "symbol": symbol,
        "serena_queries": [
            {
                "tool": "find_symbol",
                "args": {
                    "name_path_pattern": symbol,
                    "substring_matching": True,
                    "depth": 1,
                },
                "purpose": "Locate matching Java symbols and immediate children.",
            },
            {
                "tool": "find_referencing_symbols",
                "args": {
                    "name_path": symbol,
                    "relative_path": "<fill from find_symbol result>",
                },
                "purpose": "Find symbol-level references to merge into graph edges.",
            },
            {
                "tool": "find_implementations",
                "args": {
                    "name_path": symbol,
                    "relative_path": "<fill from find_symbol result>",
                },
                "purpose": "Resolve interface-to-implementation and override relationships.",
            },
        ],
        "merge_targets": [
            "JavaMethod CALLS JavaMethod",
            "JavaClass IMPLEMENTS JavaInterface",
            "JavaMethod OVERRIDES JavaMethod",
            "JavaMethod REFERENCES JavaMethod",
        ],
    }
