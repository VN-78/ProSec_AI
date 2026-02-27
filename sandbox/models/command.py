from pydantic import BaseModel

class CommandResult(BaseModel):
    exit_code: int
    output: str

class SandboxInfo(BaseModel):
    id: str
    name: str
    status: str
    image: str
