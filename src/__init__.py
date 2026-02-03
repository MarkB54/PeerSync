"""
PeerSync - A P2P File Sharing System

This package provides a peer-to-peer file-sharing application with
dual-protocol communication (UDP for control, TCP for data transfer).
"""

__version__ = "1.0.0"
__author__ = "Mark Bastoulis"
__email__ = "mbastoulis@gmail.com"

from . import config
from . import utils

__all__ = ['config', 'utils']
