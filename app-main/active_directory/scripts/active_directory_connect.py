# load modules
from dotenv import load_dotenv
import os
from typing import Optional, Tuple

from ldap3 import ALL, Connection, Server

# Load .env file
dotenv_path = '/usr/src/project/.devcontainer/.env'
load_dotenv(dotenv_path=dotenv_path)


def _get_clean_env(name: str) -> Optional[str]:
    """Return the environment variable stripped of whitespace or ``None``."""

    value = os.getenv(name)
    if value is None:
        return None

    stripped = value.strip()
    return stripped or None


def _get_float_env(name: str, default: float, *, minimum: float | None = None) -> float:
    """Return a float from the environment variable with optional clamping."""

    value = os.getenv(name)
    if value is None:
        result = default
    else:
        try:
            result = float(value)
        except (TypeError, ValueError):
            result = default

    if minimum is not None and result < minimum:
        return minimum
    return result


def _missing_config_message(missing: list[str]) -> str:
    formatted = ', '.join(sorted(missing))
    return (
        "Missing required Active Directory configuration: "
        f"{formatted}. Update the environment configuration and try again."
    )


def active_directory_connect() -> Tuple[Optional[Connection], str]:
    try:
        ad_username = _get_clean_env('ACTIVE_DIRECTORY_USERNAME')
        ad_password = _get_clean_env('ACTIVE_DIRECTORY_PASSWORD')
        ad_server = _get_clean_env('ACTIVE_DIRECTORY_SERVER')

        missing_variables = [
            name
            for name, value in {
                'ACTIVE_DIRECTORY_USERNAME': ad_username,
                'ACTIVE_DIRECTORY_PASSWORD': ad_password,
                'ACTIVE_DIRECTORY_SERVER': ad_server,
            }.items()
            if not value
        ]

        if missing_variables:
            return None, _missing_config_message(missing_variables)

        connect_timeout = _get_float_env(
            'ACTIVE_DIRECTORY_CONNECT_TIMEOUT',
            5.0,
            minimum=0.1,
        )
        receive_timeout = _get_float_env(
            'ACTIVE_DIRECTORY_RECEIVE_TIMEOUT',
            10.0,
            minimum=0.1,
        )

        server = Server(
            ad_server,
            use_ssl=True,
            get_info=ALL,
            connect_timeout=connect_timeout,
        )
        conn = Connection(
            server,
            ad_username,
            ad_password,
            receive_timeout=receive_timeout,
        )

        # Check if the connection is successful
        if not conn.bind():
            return None, "Failed to connect to Active Directory"

        return conn, "Successfully connected to Active Directory"
    except Exception as e:
        return None, f"Error connecting to Active Directory: {str(e)}"


def run():
    ad_connection_object, message = active_directory_connect()
    if message:
        print(message)


# if main
if __name__ == "__main__":
    run()
