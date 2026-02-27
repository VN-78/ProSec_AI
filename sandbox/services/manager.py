import docker
from docker.errors import APIError, NotFound, DockerException
from docker.client import DockerClient
from typing import List, Optional, Dict
import uuid

# Assuming you have these models defined in sandbox/models/command.py
from sandbox.models.command import CommandResult, SandboxInfo

class SandboxManager:
    """Manages isolated Docker environments for executing bash commands and hosting targets."""
    
    client: DockerClient
    
    def __init__(self) -> None:
        try:
            self.client = docker.from_env()
        except DockerException as e:
            raise RuntimeError(f"Failed to connect to Docker daemon. Is it running? Error: {e}")

    def create_sandbox(
        self,   
        image: str = "ubuntu:22.04", 
        command: Optional[str] = None, 
        name: Optional[str] = None,
        ports: Optional[Dict[str, int]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        privileged: bool = False
    ) -> str:
        """
        Create a new isolated sandbox container with explicit networking and volume configs.
        """
        container_name = name or f"prosec-sandbox-{uuid.uuid4().hex[:8]}"
        
        try:
            container = self.client.containers.run(
                image,
                command=command,
                detach=True,
                name=container_name,
                ports=ports,
                volumes=volumes,
                privileged=privileged,
                # tty=True is usually only needed if keeping an interactive bash session open
                tty=True if command == "/bin/bash" else False 
            )
            return str(container.id)
            
        except APIError as e:
            # Catches issues like port collisions or name conflicts
            raise RuntimeError(f"Docker API Error during container creation: {e}")

    def execute_command(self, container_id: str, command: str) -> CommandResult:
        """Execute a bash command within a specific container."""
        try:
            container = self.client.containers.get(container_id)
            exit_code, output = container.exec_run(["/bin/bash", "-c", command])
            
            return CommandResult(
                command=command,  # <- Added this
                exit_code=int(exit_code),
                output=output.decode("utf-8").strip() if isinstance(output, bytes) else str(output).strip()
            )
        except NotFound:
            return CommandResult(
                command=command,
                exit_code=-1,
                output="",
                internal_error=f"Container with ID {container_id} not found."
            )
        except Exception as e:
            return CommandResult(
                command=command,
                exit_code=-1,
                output="",
                internal_error=f"Execution failed: {str(e)}"
            )

    def run_mitigation(self, target_container_id: str, commands: List[str]) -> List[CommandResult]:
        """Execute a sequence of mitigation commands against a target."""
        results: List[CommandResult] = []
        for cmd in commands:
            result = self.execute_command(target_container_id, cmd)
            results.append(result)
            # If a critical mitigation fails, you might want to break or log heavily here
            if result.exit_code != 0:
                print(f"[!] Mitigation command failed: {cmd} -> {result.output}")
        return results

    def stop_sandbox(self, container_id: str) -> None:
        """Stop and explicitly remove a sandbox container to free resources."""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            container.remove(v=True, force=True) # Ensure associated anonymous volumes are removed
        except NotFound:
            pass # Already gone

    def get_info(self, container_id: str) -> SandboxInfo:
        """Retrieve details about a sandbox container."""
        try:
            container = self.client.containers.get(container_id)
            
            # Safely narrow the types to avoid OptionalMemberAccess errors
            image_name = "unknown"
            if container.image and container.image.tags:
                image_name = str(container.image.tags[0])
                
            return SandboxInfo(
                id=str(container.id),
                name=str(container.name),
                status=str(container.status),
                image=image_name
            )
        except NotFound:
            raise ValueError(f"Container with ID {container_id} not found.")