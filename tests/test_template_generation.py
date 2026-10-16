import subprocess
from pathlib import Path

import copier


def test_generate_standalone_service(tmp_path: Path):
    target = tmp_path / "standalone-test"
    template_root = Path(__file__).parent.parent

    copier.run_copy(
        src_path=str(template_root),
        dst_path=str(target),
        data={
            "stack_name": "sample-service",
            "stack_description": "A standalone test stack",
            "stack_type": "standalone_service",
            "service_http_port": 8090,
            "include_architecture_scaffold": True,
            "include_diataxis_docs": True,
        },
        defaults=True,
        unsafe=True,
    )

    assert (target / "compose.yml").is_file()
    assert (target / ".env.example").is_file()
    assert (target / "config" / "sample.conf").is_file()
    assert not (target / "config" / "nginx.conf").exists()
    assert (target / "architecture" / "adr" / "0001_initial_stack_architecture.md").is_file()
    assert (target / "docs" / "tutorials" / "getting_started.md").is_file()

    # Validate docker compose syntax
    compose_content = (target / "compose.yml").read_text()
    assert "sample-service" in compose_content
    assert "8090" in compose_content

    # Validate docker compose syntax validation
    subprocess.run(
        ["docker", "compose", "-f", str(target / "compose.yml"), "config", "--quiet"],
        check=True,
    )


def test_generate_orchestrated_stack(tmp_path: Path):
    target = tmp_path / "orchestrated-test"
    template_root = Path(__file__).parent.parent

    copier.run_copy(
        src_path=str(template_root),
        dst_path=str(target),
        data={
            "stack_name": "my-ops-platform",
            "stack_description": "Multi-container platform",
            "stack_type": "orchestrated_stack",
            "service_http_port": 8085,
            "include_architecture_scaffold": True,
            "include_diataxis_docs": True,
        },
        defaults=True,
        unsafe=True,
    )

    assert (target / "compose.yml").is_file()
    assert (target / "config" / "nginx.conf").is_file()
    assert (target / "docs" / "how-to" / "integrate_polyrepo_backend.md").is_file()
    assert (target / "docs" / "how-to" / "integrate_polyrepo_frontend.md").is_file()

    compose_content = (target / "compose.yml").read_text()
    assert "my-ops-platform-frontend" in compose_content
    assert "my-ops-platform-backend" in compose_content
    assert "my_ops_platform_net" in compose_content

    # Validate docker compose syntax validation
    subprocess.run(
        ["docker", "compose", "-f", str(target / "compose.yml"), "config", "--quiet"],
        check=True,
    )
