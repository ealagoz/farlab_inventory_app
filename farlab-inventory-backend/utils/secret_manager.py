# Update farlab-inventory-backend/utils/secret_manager.py
import os
from pathlib import Path
from typing import Optional
from .logging_config import get_logger

# Get a logger for this module
logger = get_logger(__name__)


class SecretManager:
    def __init__(self, secrets_file: Optional[str] = None):
        self._secrets_loaded = False

        # Determine the secrets file path with Docker-friendly defaults
        if secrets_file:
            self.secrets_file = Path(secrets_file)
        else:
            # Check environment variable first
            env_path = os.environ.get('SECRETS_FILE')
            if env_path:
                self.secrets_file = Path(env_path)
            else:
                # Docker-friendly paths - try in order
                possible_paths = [
                    # Path('/app/secrets/secrets.txt'),  # Docker mount point
                    # Path('/tmp/secrets/secrets.txt'),  # Alternative mount
                    Path('/run/secrets/postgres_secret'),    # Docker secrets
                    Path('/run/secrets/admin_secret'),       # Docker secrets
                    Path('/run/secrets/secret_key'),         # Docker secrets
                    Path('./secrets/secrets.txt'),     # Local development
                    Path('../secrets/secrets.txt'),    # From backend dir
                ]

                self.secrets_file = None
                for path in possible_paths:
                    if path.exists():
                        self.secrets_file = path
                        break

                # If no existing file found, default to Docker path
                if self.secrets_file is None:
                    self.secrets_file = Path('/app/secrets/secrets.txt')

    def load_secrets(self) -> None:
        """Load secrets from Docker secret files or consolidated file"""
        if self._secrets_loaded:
            logger.debug("Secrets already loaded, skipping...")
            return

        # Try Docker secrets first (individual files)
        docker_secrets = {
            'POSTGRES_PASSWORD': '/run/secrets/postgres_secret',
            'ADMIN_PASSWORD': '/run/secrets/admin_secret',
            'SECRET_KEY': '/run/secrets/secret_key'
        }

        secrets_loaded = 0
        for env_var, secret_path in docker_secrets.items():
            if os.path.exists(secret_path):
                try:
                    with open(secret_path, 'r', encoding='utf-8') as f:
                        value = f.read().strip()
                        if value and env_var not in os.environ:
                            os.environ[env_var] = value
                            secrets_loaded += 1
                            logger.debug(f"Loaded secret: {env_var}")
                except Exception as e:
                    logger.error(f"Error reading secret file {env_var}: {e}")

        if secrets_loaded > 0:
            logger.info(f"Loaded {secrets_loaded} Docker secrets")
            self._secrets_loaded = True
            return

        # Fallback to consolidated secrets file
        if not self.secrets_file.exists():
            logger.warning(
                "No secret files found (this is normal for development)")
            return

        try:
            logger.warning("Reading consolidated secrets file")

            with open(self.secrets_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.strip().split('\n')

                for _line_num, line in enumerate(lines, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Parse key=value pairs
                    if '=' not in line:
                        continue

                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    if not key or not value:
                        continue

                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
                        secrets_loaded += 1

            if secrets_loaded > 0:
                logger.info(f"Loaded {secrets_loaded} secrets from file")
            self._secrets_loaded = True

        except Exception as e:
            logger.error(f"Full error details: {str(e)}")

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret value by key"""
        if not self._secrets_loaded:
            self.load_secrets()
        return os.environ.get(key, default)


# Create a global instance
secret_manager = SecretManager()
