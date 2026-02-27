# ProSec AI Sandbox Management

This document provides instructions for managing the isolated Docker sandboxes used by ProSec AI. We use a **Decoupled Logging Architecture**, ensuring the AI host is safely separated from the vulnerable target.

## 1. Vulnerable SSH Sandbox Architecture

The `vulnerable-ssh` image provides an Ubuntu-based environment with an intentionally weak configuration (`root:password`). 

**How it works:**
Instead of relying on fragile internal logging daemons like `rsyslog` inside the container, this image forces the `sshd` process to write authentication logs directly to `/var/log/auth.log`. We then use Docker Volume Mounts to synchronize this file directly to the host machine. 

```text
+-----------------------------+          +-------------------------------+
| Docker Container (Target)   |          | Host Machine (AI Engine)      |
|                             |          |                               |
|  sshd -E /var/log/auth.log  |--[SYNC]->|  .../sandbox/data/logs/       |
|                             |          |         auth.log              |
+-----------------------------+          +-------------------------------+
```

## 2. Building the Image

From the project root:
Bash

`docker build -t vulnerable-ssh ./sandbox/infra/vulnerable_ssh/`

## 3. Running the Sandbox

To start the container and properly map the logging directories to your host machine, use the following command.

Note: Update the host path -v if you move the repository.
Bash
```
docker run -d \
  --name test-vulnerable-ssh \
  -p 2222:22 \
  --privileged \
  -v ~/VN_78/Programming/Personal/Projects/amd-hackthon/code/ProSec_AI/sandbox/data/logs:/var/log \
  vulnerable-ssh
```

    -d: Runs in detached mode.

    -p 2222:22: Maps the container's SSH port to 2222 on the host.

    --privileged: Grants the container required permissions for network manipulation (required for automated iptables blocking later).

    -v: Mounts the container's log directory directly to the host filesystem.

## Accessing the Sandbox via SSH

To generate normal traffic or simulate an attack, connect from your host:
Bash

`ssh root@localhost -p 2222`

# Password: password

## 4. Viewing System Logs

Because of the volume mount architecture, you do not need to execute commands inside the container to view the logs. The logs are streamed in real-time to your local repository.

To monitor authentication attempts (successful logins, brute force failures):
Bash

`tail -f ~/VN_78/Programming/Personal/Projects/amd-hackthon/code/ProSec_AI/sandbox/data/logs/auth.log`

## 6. Cleaning Up

Always stop and remove containers after use to free up resources and reset the log state.
Bash

`docker rm -f test-vulnerable-ssh`

(Using -f forces the stop and removal in one command).




# How to use this new Manager

Now, when your Python orchestrator spins up the target, you can pass the exact configuration we defined in our architecture. Here is how you initialize the vulnerable-ssh sandbox using this updated manager:
Python

from sandbox.services.manager import SandboxManager

manager = SandboxManager()

# Define your Arch host path and the container path
``` 
log_volume = {
    '/home/vn-78/VN_78/Programming/Personal/Projects/amd-hackthon/code/ProSec_AI/sandbox/data/logs': {
        'bind': '/var/log',
        'mode': 'rw'
    }
}

container_id = manager.create_sandbox(
    image="vulnerable-ssh",
    name="test-vulnerable-ssh",
    ports={'22/tcp': 2222},
    volumes=log_volume,
    privileged=True
)

print(f"Target running! ID: {container_id}") 
 ```

This properly sets up the target, exposes the log file to your host, and gives the container the network privileges required for your Tier 2 execution module to inject iptables rules later.