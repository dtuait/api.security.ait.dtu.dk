"""Proxy module for the upstream authtoken 0002 migration."""

from importlib import import_module

Migration = import_module(
    "rest_framework.authtoken.migrations.0002_auto_20160226_1747"
).Migration

__all__ = ["Migration"]
