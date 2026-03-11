# sura_smart/facial_recognition/__init__.py
"""
Sura Smart Facial Recognition Module
TRD Section 3.1: Facial Recognition System
TRD Section 6.2: AI Performance Requirements
"""

# NOTE: Heavy ML imports (TensorFlow, OpenCV) are intentionally NOT imported
# here at the package level to avoid breaking Django startup. Import the
# specific classes directly from their modules when needed:
#   from ai_models.facial_recognition.model import FacialRecognitionModel
#   from ai_models.facial_recognition.predictor import FacialRecognitionPredictor

default_app_config = 'ai_models.facial_recognition.apps.FacialRecognitionConfig'

__version__ = '1.0.0'
__all__ = [
    'FacialRecognitionModel',
    'FacialRecognitionPredictor',
    'FacialRecognitionTrainer',
    'FaceEmbeddingGenerator',
]

# TRD 3.1.1: Minimum 98% accuracy rate
MODEL_ACCURACY_THRESHOLD = 0.98

# TRD 6.2.2: False positive rate < 0.5%
FALSE_POSITIVE_THRESHOLD = 0.005

# TRD 6.2.3: False negative rate < 2%
FALSE_NEGATIVE_THRESHOLD = 0.02

# TRD 6.2.4: Processing time < 5 seconds per image
PROCESSING_TIME_SLA = 5.0

# TRD 3.1.4: Bias variance threshold < 2%
BIAS_VARIANCE_THRESHOLD = 0.02