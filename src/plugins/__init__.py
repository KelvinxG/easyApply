"""
Plugins Package

Contains extensible analyzer modules and plugin architecture for
custom keyword extraction and matching algorithms.
"""

from .base import BaseAnalyzer
from .registry import PluginRegistry

__all__ = ['BaseAnalyzer', 'PluginRegistry'] 