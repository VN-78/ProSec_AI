# region imports
# import os
from drain3 import TemplateMiner # type: ignore
from drain3.template_miner_config import TemplateMinerConfig # type: ignore
from app.models.log import ParsedLogEvent
from typing import Dict, Any, cast

class LogParserService:
    """Service to parse raw system logs into structured templates using Drain3."""
    
    def __init__(self, persistence_dir: str = "app/db"):
        # Drain3 requires configuration to know how to mask variables
        self.config = TemplateMinerConfig()
        
        # We define custom Regex to strip IPs and Numbers before tree traversal
        self.config.profiling_enabled = False
        
        # Initialize the miner. (In production, you'd use FilePersistence 
        # to save the tree state so it doesn't reset on restart).
        self.miner = TemplateMiner(config=self.config)

    def parse_line(self, log_line: str) -> ParsedLogEvent:
        """Parses a single log line and returns a strict Pydantic model."""
        
        # Strip trailing newlines which can mess up the token count
        clean_line = log_line.strip()
        if not clean_line:
            raise ValueError("Empty log line provided.")

        # Drain processes the line
        raw_result = self.miner.add_log_message(clean_line) # type: ignore
        result = cast(Dict[str,Any], raw_result)  
        
        # 2. Safely extract and explicitly cast values to string for Pydantic
        cluster_id = str(result.get("cluster_id", "unknown"))
        template_mined = str(result.get("template_mined", ""))

        # Drain3 returns a dictionary. We map it to our Pydantic model.
        # result["template_mined"] looks like: "Failed password for <*> from <*> port <*>"
        
        # Note: Extracting exact parameters requires comparing the raw log 
        # to the template. Drain3 has a utility for this, or we can extract 
        # natively. For the prototype, we store the cluster ID and template.
        
        return ParsedLogEvent(
            raw_log=clean_line,
            event_id=cluster_id,
            template=template_mined,
            # You can write a regex diff here later to extract the exact IPs
            parameters=[] 
        )

    def get_cluster_state(self) -> int:
        """Returns the total number of unique templates discovered so far."""
        # The internal 'clusters' is likely a dict or dict_values. 
        # We tell Pylance to safely ignore this specific line's type check,
        # which is the standard practice for accessing untyped library internals.
        clusters = self.miner.drain.clusters  # type: ignore
        return len(clusters)  # type: ignore