# Template Docker Stack

Canonical template repository for authoring bespoke and third-party Docker Compose stacks adhering to the **Homelab Systems Lifecycle (HSL)** and **ADR 0025** container deployment standards.

---

## 1. Stack Conventions & Repository Hygiene

Every bespoke stack initialized from this template abides by the following rules:

1. **Naming Standard:** Stack repository names must strictly follow lowercase alphanumeric kebab-case:
   `^[a-z0-9]+(-[a-z0-9]+)*$` (e.g. `openobserve`, `monitoring-agent`).
2. **Directory Footprint:**
   * `compose.yml`: Primary orchestration specification referencing pre-built image coordinates.
   * `config/`: Read-only host configuration templates mounted into containers (`:ro`).
   * `Dockerfile`: Source recipe for bespoke microservices compiled during CI.
   * `.env.example`: Non-sensitive environment variable declarations.
   * `.github/workflows/ci.yml`: Automated GitHub Actions linting pipeline.
3. **Immutable Runtimes:** Production target hosts pull pre-compiled container images from registries (GHCR/local). Production nodes shall not run container build toolchains.
4. **Versioning & Tagging:** Tag releases using Semantic Versioning (`vMAJOR.MINOR.PATCH`). Ansible deploys explicitly pinned release tags.

---

## 2. Local Development Workflow (SDP)

1. **Initialize Stack:** Create a new repository from this template on GitHub or locally under `~/src/github.com/mnaatjes/<stack-name>/`.
2. **Configure Environment:**
   ```bash
   cp .env.example .env
   ```
3. **Verify Compose Configuration:**
   ```bash
   docker compose config
   ```
4. **Start Local Development Stack:**
   ```bash
   docker compose up -d
   ```
5. **Inspect Health & Logs:**
   ```bash
   docker compose ps
   docker compose logs -f
   ```

---

## 3. Production Deployment via `homelab-ops` (HSL)

Once a stack version is tagged (`git tag v1.0.0 && git push origin v1.0.0`), register the stack in `homelab-ops`:
1. Declare stack parameters in `group_vars/all/compose_stacks.yml`.
2. Add vaulted credentials to `group_vars/all/vault.yml` under `vault_stack_secrets.<stack-name>`.
3. Deploy to authorized target nodes:
   ```bash
   ansible-playbook -i inventory.ini playbooks/deploy_stack.yml -e "stack=<stack-name>"
   ```
