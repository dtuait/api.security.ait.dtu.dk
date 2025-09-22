"""Proxy module for the upstream authtoken 0003 migration."""

from importlib import import_module

Migration = import_module(
    "rest_framework.authtoken.migrations.0003_tokenproxy"
).Migration

__all__ = ["Migration"]
