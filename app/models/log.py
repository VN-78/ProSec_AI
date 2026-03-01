from pydantic import BaseModel, Field
from typing import List

class ParsedLogEvent(BaseModel):
    """The strictly typed output of a parsed system log."""
    
    raw_log: str = Field(
        ..., 
        description="The original raw log string."
    )
    event_id: str = Field(
        ..., 
        description="The unique cluster ID assigned by Drain (e.g., A001)."
    )
    template: str = Field(
        ..., 
        description="The structural log template with variables masked."
    )
    parameters: List[str] = Field(
        default_factory=list, 
        description="The dynamic variables extracted from the log (e.g., IPs, usernames)."
    )

    @property
    def is_ssh_failure(self) -> bool:
        """Helper to quickly flag known bad templates."""
        return "Failed password" in self.template