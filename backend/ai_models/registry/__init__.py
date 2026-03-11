# sura_smart/ai_models/registry/__init__.py
"""
Sura Smart Model Registry Module
TRD Section 7.2: CI/CD Pipeline with Model Versioning
TRD Section 10.4: Quarterly Algorithm Retraining
"""

# NOTE: MLFlow is intentionally NOT imported here at package level.
# Import directly when needed:
#   from ai_models.registry.mlflow_registry import ModelRegistry

__all__ = ['ModelRegistry']
__version__ = '1.0.0'