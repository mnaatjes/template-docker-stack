# Template Docker Stack

Canonical **Copier template generator** for authoring bespoke and third-party Docker Compose stacks adhering to the **Homelab Systems Lifecycle (HSL)** and **ADR 0025 / ADR 0038** container deployment standards.

---

## 1. Quick Start: Generating a New Stack

Generate a new, production-ready stack in your development directory:

```bash
# Using Copier via uv or pipx:
copier copy gh:mnaatjes/template-docker-stack ~/src/github.com/mnaatjes/<new-stack-name>
```

### Interactive Prompts
1. `stack_name`: Lowercase kebab-case identifier (e.g. `openobserve`, `bizops-stack`).
2. `stack_description`: Purpose of the container stack.
3. `stack_type`:
   * `standalone_service`: Lightweight single container with config mount (e.g. Caddy, OpenObserve).
   * `orchestrated_stack`: Multi-container stack pulling external frontend SPA and backend API images over an internal network bridge.
4. `service_http_port`: External ingress port (e.g. `8080`).
5. `include_architecture_scaffold`: Provisions canonical Unified Process `architecture/` tree (`adr/`, `designs/`, `use-cases/`, `risk/`).
6. `include_diataxis_docs`: Provisions complete Diátaxis `docs/` tree (`tutorials/`, `how-to/`, `reference/`, `explanation/`).

---

## 2. Upstream Architecture & Maintenance

This repository functions under a **Dual-Plane Architecture** ([ADR 0038](https://github.com/mnaatjes/homelab-ops/blob/main/architecture/adr/0038_adopt_copier_for_docker_stack_authoring.md)):

* **Root Management Plane:** Contains non-templated developer tooling (`pyproject.toml`, `.pre-commit-config.yaml`, `tests/`) used exclusively to test template compilation across archetypes and maintain the generator.
* **Template Payload Plane (`template/`):** Contains the parameterized blueprint assets that are rendered and instantiated into downstream repositories.

### Running Upstream Tests
```bash
uv run pytest -v tests/
```

### Upstream Versioning
Version bumps and release tagging are managed via `bump-my-version`:
```bash
uv run bump-my-version bump minor
```
