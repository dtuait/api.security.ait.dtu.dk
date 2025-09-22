"""Proxy module for the upstream authtoken 0004 migration."""

from importlib import import_module

Migration = import_module(
    "rest_framework.authtoken.migrations.0004_alter_tokenproxy_options"
).Migration

__all__ = ["Migration"]
