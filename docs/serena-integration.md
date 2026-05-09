# Serena Integration

## Decision

Serena should be embedded as an optional Java symbol backend, not copied into this repository.

Our project remains responsible for Java + Protobuf RPC semantics:

- Proto service / rpc / message / field graph.
- Proto request / response impact analysis.
- RPC-to-Java implementation mapping.
- Framework, MyBatis, DB, MQ, and config semantics.
- Claude Code / Codex context pack generation.

Serena is responsible for IDE-grade Java symbol facts:

- Symbol overview.
- Symbol lookup.
- Declarations.
- Implementations.
- Referencing symbols.
- Diagnostics.

## Why Not Vendor Serena Source

Serena is MIT licensed, so vendoring is legally possible when preserving the license notice. But dependency-style embedding is cleaner:

- Easier upgrades.
- Smaller repository.
- Clearer ownership boundary.
- Lower risk of drifting from upstream.
- Easier fallback when Serena is unavailable.

## Runtime Shape

```text
Code Context Agent
  -> Proto Analyzer                 owned here
  -> Framework / RPC Analyzer        owned here
  -> Java Analyzer                   lightweight fallback
  -> Serena Backend                  optional richer Java symbols
  -> Graph Store
  -> Context Pack Generator
```

## Serena Installation

Use Serena's official installation path:

```bash
uv tool install -p 3.13 serena-agent@latest --prerelease=allow
serena init
```

Then start Serena for a Java repository:

```bash
serena start-mcp-server --project /path/to/java-repo --context claude-code
```

## Integration Phases

### Phase 1: Sidecar Backend

Expose commands that describe Serena availability and the MCP launch command:

```bash
python3 -m codeagent.cli serena status /path/to/java-repo
python3 -m codeagent.cli serena plan AddAppealRequest
```

### Phase 2: MCP Client Adapter

Add a read-only MCP client inside Code Context Agent that can call:

- `get_symbols_overview`
- `find_symbol`
- `find_declaration`
- `find_implementations`
- `find_referencing_symbols`
- `get_diagnostics_for_file`

The adapter should normalize Serena output into our graph model.

### Phase 3: Graph Merge

Merge Serena facts into these edge types:

- `JavaMethod REFERENCES JavaMethod`
- `JavaMethod CALLS JavaMethod`
- `JavaClass IMPLEMENTS JavaInterface`
- `JavaMethod OVERRIDES JavaMethod`
- `JavaSymbol DECLARED_AT File`

Keep provenance metadata:

```json
{
  "source": "serena",
  "backend": "lsp|jetbrains",
  "confidence": 0.9
}
```

### Phase 4: Context Pack Fusion

When generating context packs:

- Use self-owned Proto facts as the source of truth for RPC contracts.
- Use Serena facts as the preferred source for Java references and implementations.
- Fall back to the lightweight Java analyzer when Serena is unavailable.

## Current Status

The repository currently includes a Serena integration entrypoint and planning commands. The actual MCP client adapter is intentionally left as the next implementation step.
