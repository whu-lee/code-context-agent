from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .models import AnalysisResult, Edge, Node, SourceFile


class GraphStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def close(self) -> None:
        self.conn.close()

    def init_schema(self) -> None:
        self.conn.executescript(
            """
            create table if not exists files (
              path text primary key,
              language text not null,
              sha256 text not null,
              module text,
              updated_at datetime default current_timestamp
            );

            create table if not exists nodes (
              id integer primary key autoincrement,
              type text not null,
              name text not null,
              qualified_name text not null unique,
              file_path text,
              start_line integer,
              end_line integer,
              metadata text not null default '{}'
            );

            create table if not exists edges (
              id integer primary key autoincrement,
              from_qn text not null,
              to_qn text not null,
              type text not null,
              metadata text not null default '{}',
              unique(from_qn, to_qn, type, metadata)
            );

            create index if not exists idx_nodes_type on nodes(type);
            create index if not exists idx_nodes_name on nodes(name);
            create index if not exists idx_edges_from on edges(from_qn, type);
            create index if not exists idx_edges_to on edges(to_qn, type);
            """
        )
        self.conn.commit()

    def clear(self) -> None:
        self.conn.executescript("delete from edges; delete from nodes; delete from files;")
        self.conn.commit()

    def upsert_files(self, files: Iterable[SourceFile]) -> None:
        self.conn.executemany(
            """
            insert into files(path, language, sha256, module)
            values (?, ?, ?, ?)
            on conflict(path) do update set
              language=excluded.language,
              sha256=excluded.sha256,
              module=excluded.module,
              updated_at=current_timestamp
            """,
            [(f.rel_path, f.language, f.sha256, f.module) for f in files],
        )
        self.conn.commit()

    def upsert_result(self, result: AnalysisResult) -> None:
        self.upsert_nodes(result.nodes)
        self.upsert_edges(result.edges)

    def upsert_nodes(self, nodes: Iterable[Node]) -> None:
        self.conn.executemany(
            """
            insert into nodes(type, name, qualified_name, file_path, start_line, end_line, metadata)
            values (?, ?, ?, ?, ?, ?, ?)
            on conflict(qualified_name) do update set
              type=excluded.type,
              name=excluded.name,
              file_path=excluded.file_path,
              start_line=excluded.start_line,
              end_line=excluded.end_line,
              metadata=excluded.metadata
            """,
            [
                (
                    n.type,
                    n.name,
                    n.qualified_name,
                    n.file_path,
                    n.start_line,
                    n.end_line,
                    json.dumps(n.metadata, ensure_ascii=False, sort_keys=True),
                )
                for n in nodes
            ],
        )
        self.conn.commit()

    def upsert_edges(self, edges: Iterable[Edge]) -> None:
        self.conn.executemany(
            """
            insert or ignore into edges(from_qn, to_qn, type, metadata)
            values (?, ?, ?, ?)
            """,
            [
                (
                    e.from_qn,
                    e.to_qn,
                    e.type,
                    json.dumps(e.metadata, ensure_ascii=False, sort_keys=True),
                )
                for e in edges
            ],
        )
        self.conn.commit()

    def find_nodes(self, term: str, types: tuple[str, ...] = ()) -> list[sqlite3.Row]:
        query = "select * from nodes where (name = ? or qualified_name like ?)"
        params: list[object] = [term, f"%{term}%"]
        if types:
            placeholders = ",".join("?" for _ in types)
            query += f" and type in ({placeholders})"
            params.extend(types)
        query += " order by case when name = ? then 0 else 1 end, type, qualified_name limit 50"
        params.append(term)
        return list(self.conn.execute(query, params))

    def get_node(self, qualified_name: str) -> sqlite3.Row | None:
        return self.conn.execute("select * from nodes where qualified_name = ?", (qualified_name,)).fetchone()

    def out_edges(self, qualified_name: str, edge_type: str | None = None) -> list[sqlite3.Row]:
        if edge_type:
            return list(self.conn.execute("select * from edges where from_qn = ? and type = ?", (qualified_name, edge_type)))
        return list(self.conn.execute("select * from edges where from_qn = ?", (qualified_name,)))

    def in_edges(self, qualified_name: str, edge_type: str | None = None) -> list[sqlite3.Row]:
        if edge_type:
            return list(self.conn.execute("select * from edges where to_qn = ? and type = ?", (qualified_name, edge_type)))
        return list(self.conn.execute("select * from edges where to_qn = ?", (qualified_name,)))

    def stats(self) -> dict[str, int]:
        return {
            "files": self.conn.execute("select count(*) from files").fetchone()[0],
            "nodes": self.conn.execute("select count(*) from nodes").fetchone()[0],
            "edges": self.conn.execute("select count(*) from edges").fetchone()[0],
        }
