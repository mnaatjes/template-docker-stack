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
   * `.github/workflows/release.yml`: Automated container build and dual-tag publishing pipeline.
3. **Immutable Runtimes:** Production target hosts pull pre-compiled container images from registries (GHCR/local). Production nodes shall not run container build toolchains.
4. **Versioning & Tagging:** Tag releases using Semantic Versioning (`vMAJOR.MINOR.PATCH`). Ansible deploys explicitly pinned release tags.

---

## 2. Ansible Architecture & Production Deployment Standards

When developing stacks intended for deployment via `homelab-ops` Ansible automation, you **must** adhere to the following architecture rules:

### A. Volume Mounts & Data Separation (Dev vs. Prod)
* **Local Development (SDP):** Containers mount relative directories (e.g., `./data/logs:/var/log/app`) directly inside the local repository workspace.
* **Production Deployment (HSL):** Per ADR 0025, declarative code and mutable state are strictly decoupled:
  * Declarative code resides in: `/opt/homelab/<env>/compose/<stack-name>/`
  * Persistent data resides in: `/opt/homelab/<env>/data/<stack-name>/<service>/`
* **Pre-Creation & Permissions:** In `group_vars/all/compose_stacks.yml`, declare the required `data_dirs` for each service with explicit numeric `owner` (UID), `group` (GID), and octal `mode`. Ansible pre-creates these directories on the host with default POSIX ACLs *before* the container starts, preventing root-owned permission lockouts.

### B. Host Port Parameterization (Preventing Collisions)
* **Never hardcode static host ports** (e.g., `ports: ["8080:8080"]`).
* Always parameterize host port bindings with an environment variable fallback:
  ```yaml
  ports:
    - "${PORT:-8080}:8080"
  ```
* This allows Ansible to assign a unique host port (e.g., `PORT: 8081`) via `environment_variables` in `compose_stacks.yml` if multiple containers share the same manager or workstation host.

### C. Image Coordinate & Local Build Dual-Mode
* Enable both local building (`docker compose up --build`) and production image pulling (`pull: always`) using:
  ```yaml
  services:
    app:
      image: ${IMAGE_NAME:-ghcr.io/mnaatjes/<stack-name>:v1.0.0}
      build:
        context: .
        dockerfile: Dockerfile
  ```

### D. GitHub Container Registry (GHCR) Publishing & Visibility
* **Dual-Tag Requirement (KI-2610-01):** The release workflow (`.github/workflows/release.yml`) publishes both literal `v*` tags (`type=raw,value={{tag}}`) and semver normalized tags (`type=semver,pattern={{version}}`). This ensures Docker can pull exact `vX.Y.Z` tags without `manifest unknown` failures.
* **Public Visibility Requirement:** Upon initial creation on GitHub, navigate to **GitHub Profile** -> **Packages** -> **`<stack-name>`** -> **Package settings** -> **Danger Zone** and set visibility to **Public**. Unauthenticated fleet nodes cannot pull private container packages.

---

## 3. Local Development Workflow (SDP)

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

## 4. Production Deployment via `homelab-ops` (HSL)

Once a stack version is tagged and pushed:
```bash
git tag v1.0.0
git push origin v1.0.0
```

1. **Declare Stack in SSOT Catalog:** Add to `group_vars/all/compose_stacks.yml` in `homelab-ops`:
   ```yaml
   compose_stacks:
     <stack-name>:
       target_hosts: ["prd-mgr-01.lan"]
       environment: "prod"
       source_repo: "https://github.com/mnaatjes/<stack-name>.git"
       version: "v1.0.0"
       environment_variables:
         PORT: "8081"
       services:
         app:
           data_dirs:
             - path: "data"
               owner: 1000
               group: 1000
               mode: "0750"
       health_check:
         type: "http"
         url: "http://127.0.0.1:8081/"
         expected_status: 200
         timeout_seconds: 60
       pre_upgrade_backup:
         enabled: true
         command: ""
         retention_count: 5
   ```
2. **Validate Schema:**
   ```bash
   .venv/bin/pytest tests/unit/test_compose_stacks_schema.py
   ```
3. **Deploy to Fleet:**
   Deploy to Stage 4 Production (`bash scripts/deploy_prod.sh`) and execute the convergence playbook:
   ```bash
   cd /opt/homelab/prod/ops
   ansible-playbook -i inventory.ini playbooks/deploy_compose_stacks.yml
   ```
