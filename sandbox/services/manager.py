import docker
from typing import List, cast
from docker.models.containers import Container
from sandbox.models.command import CommandResult, SandboxInfo

class SandboxManager:
    """Manages isolated Docker environments for executing bash commands."""
    
    def __init__(self) -> None:
        self.client = docker.from_env()

    def create_sandbox(self, image: str = "ubuntu:22.04", name_prefix: str = "prosec-sandbox-") -> str:
        """Create a new isolated sandbox container."""
        container = self.client.containers.run(
            image,
            command="/bin/bash",
            detach=True,
            tty=True,
            name=f"{name_prefix}{id(self)}"
        )
        if container.id is None:
            raise RuntimeError("Failed to retrieve container ID")
        return str(container.id)

    def execute_command(self, container_id: str, command: str) -> CommandResult:
        """Execute a bash command within a specific container."""
        container = cast(Container, self.client.containers.get(container_id))
        exit_code, output = container.exec_run(["/bin/bash", "-c", command])
        
        return CommandResult(
            exit_code=int(exit_code),
            output=output.decode("utf-8") if isinstance(output, bytes) else str(output)
        )

    def run_mitigation(self, target_container_id: str, commands: List[str]) -> List[CommandResult]:
        """Execute a sequence of mitigation commands against a target."""
        return [self.execute_command(target_container_id, cmd) for cmd in commands]

    def stop_sandbox(self, container_id: str) -> None:
        """Stop and remove a sandbox container."""
        container = cast(Container, self.client.containers.get(container_id))
        container.stop()
        container.remove()

    def get_info(self, container_id: str) -> SandboxInfo:
        """Retrieve details about a sandbox container."""
        container = cast(Container, self.client.containers.get(container_id))
        return SandboxInfo(
            id=str(container.id),
            name=str(container.name),
            status=str(container.status),
            image=str(container.image.tags[0]) if container.image.tags else "unknown"
        )
