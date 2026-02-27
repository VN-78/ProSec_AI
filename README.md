# ProSec AI

Proactively preventing attacks and anomalies by monitoring system logs and switching to an AI-driven bash-execution model for real-time mitigation.

## Project Structure

- `app/`: Contains the AI agent communication logic and core services.
- `sandbox/`: Modularized Docker-based execution environment for isolated command execution.
  - `models/`: Pydantic data models for structured command results and container info.
  - `services/`: `SandboxManager` for interacting with Docker containers.
  - `infra/`: Dockerfiles for testing (e.g., vulnerable SSH server).

## Sandbox Usage

The Sandbox allows you to run bash commands in an isolated Docker container, preventing any impact on the host system.

### Prerequisites

- Docker installed and running.
- (Recommended) Current user added to the `docker` group to avoid `sudo`.

### Installation

```bash
uv add docker pydantic
```

### Basic Example

```python
from sandbox.services.manager import SandboxManager

# Initialize the manager
manager = SandboxManager()

# Create a target container (e.g., for testing)
# Ensure the image 'vulnerable-ssh' is built first.
# sudo docker build -t vulnerable-ssh sandbox/infra/vulnerable_ssh/

target_id = manager.create_sandbox(image="vulnerable-ssh")

# Execute a mitigation command (e.g., block an IP)
result = manager.execute_command(
    target_id, 
    "iptables -A INPUT -s 192.168.1.100 -j DROP"
)

print(f"Exit Code: {result.exit_code}")
print(f"Output: {result.output}")

# Cleanup
manager.stop_sandbox(target_id)
```

## Testing Environment (Vulnerable SSH)

To build the test target container:

```bash
sudo docker build -t vulnerable-ssh sandbox/infra/vulnerable_ssh/
```

This container is configured with a weak root password (`password`) and SSH enabled, making it a perfect target for simulating attacks and verifying AI-driven mitigations.
