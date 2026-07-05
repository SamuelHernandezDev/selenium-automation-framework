"""
Legacy WebDriver factory wrapper.

Existing tests import from utils.driver. The implementation now delegates
to core.driver_factory so the project has one source of driver behavior.
"""

from core.driver_factory import create_driver


__all__ = ["create_driver"]
