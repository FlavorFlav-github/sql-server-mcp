import os
import yaml
from typing import List, Dict

def load_server_configs(config_path: str = "config/servers.yml") -> List[Dict]:
    """Load and resolve server configurations from YAML."""
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    servers = raw.get("servers", [])
    resolved = []
    for srv in servers:
        srv_copy = srv.copy()
        # Substitute environment vars if referenced
        for k, v in srv_copy.items():
            if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                env_var = v.strip("${}")
                srv_copy[k] = os.getenv(env_var)
        resolved.append(srv_copy)

    return resolved