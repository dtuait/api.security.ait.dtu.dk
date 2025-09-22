"""Proxy module for the upstream authtoken 0001 migration."""

from importlib import import_module

Migration = import_module(
    "rest_framework.authtoken.migrations.0001_initial"
).Migration

__all__ = ["Migration"]
