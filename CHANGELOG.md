# Changelog

## v1.0.0

Initial GitHub release of Code Context Agent.

### Added

- Repository scanner for Java, Proto, Maven, Gradle, XML, YAML, and properties files.
- Proto analyzer for packages, imports, messages, fields, enums, services, RPC methods, and request/response types.
- Java analyzer for classes, interfaces, enums, fields, methods, annotations, imports, inheritance, injection, and lightweight method calls.
- Maven POM analyzer for modules and dependency relationships.
- SQLite graph store with `files`, `nodes`, and `edges` tables.
- CLI commands:
  - `index`
  - `find-symbol`
  - `class-context`
  - `find-callers`
  - `find-callees`
  - `find-subclasses`
  - `trace`
  - `explain-rpc`
  - `find-message`
  - `impact-add-field`
  - `context`
  - `install-hook`
  - `serena status`
  - `serena plan`
- Optional Serena integration planning commands.
- Git post-merge hook installer for refreshing graph indexes after `git pull`.
- Technical design document for the MVP and roadmap.
