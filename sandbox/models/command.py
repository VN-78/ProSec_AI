from pydantic import BaseModel, Field
from typing import Optional

class CommandResult(BaseModel):
    """Represents the outcome of a bash command executed inside a sandbox."""
    
    command: str = Field(
        ..., 
        description="The exact bash command that was executed."
    )
    exit_code: int = Field(
        ..., 
        description="The exit code of the command. 0 indicates standard success."
    )
    output: str = Field(
        ..., 
        description="The combined stdout and stderr output from the execution."
    )
    internal_error: Optional[str] = Field(
        default=None, 
        description="Any Python-level exceptions caught during execution (e.g., container missing)."
    )

    @property
    def success(self) -> bool:
        """A computed property to quickly check if the command succeeded."""
        return self.exit_code == 0 and self.internal_error is None

class SandboxInfo(BaseModel):
    """Metadata about an active Docker sandbox."""
    id: str = Field(..., description="The full Docker container ID.")
    name: str = Field(..., description="The human-readable container name.")
    status: str = Field(..., description="Current status (e.g., 'running', 'exited').")
    image: str = Field(..., description="The image tag used to spin up the container.")