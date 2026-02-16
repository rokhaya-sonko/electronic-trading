"""
Electronic Trading Lab - Core Library

A comprehensive Python library for electronic trading analysis.
"""

__version__ = "1.0.0"

# Import main modules for easier access
from . import utils
from . import liquidity
from . import tca
from . import execution_algos
from . import risk
from . import models

__all__ = [
    'utils',
    'liquidity',
    'tca',
    'execution_algos',
    'risk',
    'models'
]
