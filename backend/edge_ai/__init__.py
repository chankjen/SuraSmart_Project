# sura_smart/edge_ai/__init__.py
"""
Edge AI Module for Sura Smart
TRD Section 4.3.1: Edge AI Processing
"""

from .model_converter import EdgeModelConverter
from .edge_inference import EdgeInferenceEngine

__all__ = ['EdgeModelConverter', 'EdgeInferenceEngine']