# sura_smart/ai_models/voice_matching/__init__.py
"""
Sura Smart Voice Matching Module
TRD Section 3.2: Multimodal Recognition Engine
TRD Section 6.2: AI Performance Requirements
"""

# NOTE: Heavy ML imports (TensorFlow, librosa) are intentionally NOT imported here.
# Import directly from submodules when needed:
#   from ai_models.voice_matching.model import VoiceMatchingModel
#   from ai_models.voice_matching.predictor import VoiceMatchingPredictor

__version__ = '1.0.0'
__all__ = ['VoiceMatchingModel', 'VoiceMatchingPredictor']

# TRD 3.2: Voice pattern matching with 95%+ accuracy
VOICE_ACCURACY_THRESHOLD = 0.95

# TRD 6.2.4: Processing time < 5 seconds per audio clip
PROCESSING_TIME_SLA = 5.0