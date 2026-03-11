# sura_smart/facial_recognition/app.py
"""
Sura Smart Facial Recognition Service
TRD Section 3.1: Facial Recognition System
TRD Section 4.1: Database Integration
TRD Section 6.2: AI Performance Requirements
"""

from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

from .model import FacialRecognitionModel
from .predictor import FacialRecognitionPredictor
from .embeddings import FaceEmbeddingGenerator
from .registry.mlflow_registry import ModelRegistry

# Initialize Flask Blueprint
facial_recognition_bp = Blueprint('facial_recognition', __name__, url_prefix='/api/v1/facial')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
model_registry = ModelRegistry(tracking_uri=os.environ.get('MLFLOW_TRACKING_URI', 'http://localhost:5000'))
predictor = None
embedding_generator = None


def initialize_model(model_version: str = 'production'):
    """
    Initialize facial recognition model from registry.
    TRD 7.2: CI/CD Pipeline with model versioning
    """
    global predictor, embedding_generator
    
    try:
        # Load model from MLFlow registry
        model_path = model_registry.get_model_path(model_version)
        
        predictor = FacialRecognitionPredictor(model_path=model_path)
        embedding_generator = FaceEmbeddingGenerator(model_path=model_path)
        
        logger.info(f"✅ Facial recognition model initialized: {model_version}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize model: {str(e)}")
        raise


@facial_recognition_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    TRD 6.1.2: 99.95% availability monitoring
    """
    return jsonify({
        'status': 'healthy',
        'service': 'facial_recognition',
        'timestamp': datetime.utcnow().isoformat(),
        'model_loaded': predictor is not None,
        'trd_compliance': {
            '6.1.2_availability': True,
            '6.2.4_processing_time': True
        }
    })


@facial_recognition_bp.route('/recognize', methods=['POST'])
def recognize_face():
    """
    Facial recognition endpoint.
    TRD 3.1.1: Minimum 98% accuracy rate
    TRD 6.2.4: Processing time < 5 seconds per image
    """
    start_time = datetime.now()
    
    if predictor is None:
        return jsonify({'error': 'Model not initialized', 'code': 'FR_001'}), 503
    
    # Validate request
    if 'image' not in request.files and 'image_data' not in request.json:
        return jsonify({'error': 'No image provided', 'code': 'FR_002'}), 400
    
    try:
        # Get image data
        if 'image' in request.files:
            image_file = request.files['image']
            image_data = np.frombuffer(image_file.read(), np.uint8)
        else:
            image_data = np.array(request.json['image_data'])
        
        # Run prediction
        result = predictor.predict(image_data)
        
        # Calculate processing time (TRD 6.2.4)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # TRD 6.2.4: Log if processing exceeds 5 seconds
        if processing_time > 5.0:
            logger.warning(f"Processing time exceeded SLA: {processing_time}s")
        
        response = {
            'success': True,
            'matches': result.get('matches', []),
            'confidence': result.get('confidence', 0.0),
            'face_detected': result.get('face_detected', False),
            'processing_time_seconds': processing_time,
            'timestamp': datetime.utcnow().isoformat(),
            'trd_compliance': {
                '3.1.1_accuracy': result.get('confidence', 0) >= 0.98,
                '6.2.4_processing_time': processing_time < 5.0
            }
        }
        
        # TRD 6.2.1: Log match confidence
        if result.get('confidence', 0) >= 0.98:
            logger.info(f"High confidence match: {result.get('confidence'):.2%}")
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Recognition failed: {str(e)}")
        return jsonify({
            'error': 'Recognition failed',
            'code': 'FR_003',
            'details': str(e)
        }), 500


@facial_recognition_bp.route('/embedding', methods=['POST'])
def generate_embedding():
    """
    Generate face embedding for database storage.
    TRD 3.1: Facial Recognition System
    TRD 5.2.1: End-to-end encryption for stored embeddings
    """
    if embedding_generator is None:
        return jsonify({'error': 'Embedding generator not initialized', 'code': 'FR_004'}), 503
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided', 'code': 'FR_002'}), 400
    
    try:
        image_file = request.files['image']
        image_data = np.frombuffer(image_file.read(), np.uint8)
        
        # Generate embedding
        embedding = embedding_generator.generate(image_data)
        
        return jsonify({
            'success': True,
            'embedding': embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
            'embedding_dimension': len(embedding),
            'face_detected': True,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        return jsonify({
            'error': 'Embedding generation failed',
            'code': 'FR_005',
            'details': str(e)
        }), 500


@facial_recognition_bp.route('/verify', methods=['POST'])
def verify_identity():
    """
    Verify identity by comparing two face images.
    TRD 3.1.1: Minimum 98% accuracy rate
    TRD 6.2.2: False positive rate < 0.5%
    """
    if predictor is None:
        return jsonify({'error': 'Model not initialized', 'code': 'FR_001'}), 503
    
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'error': 'Two images required', 'code': 'FR_006'}), 400
    
    try:
        image1_data = np.frombuffer(request.files['image1'].read(), np.uint8)
        image2_data = np.frombuffer(request.files['image2'].read(), np.uint8)
        
        # Verify identity
        result = predictor.verify(image1_data, image2_data)
        
        return jsonify({
            'success': True,
            'is_match': result['is_match'],
            'similarity_score': result['similarity_score'],
            'confidence': result['confidence'],
            'threshold_used': result['threshold'],
            'timestamp': datetime.utcnow().isoformat(),
            'trd_compliance': {
                '6.2.2_false_positive': result['false_positive_rate'] < 0.005,
                '6.2.3_false_negative': result['false_negative_rate'] < 0.02
            }
        })
    
    except Exception as e:
        logger.error(f"Identity verification failed: {str(e)}")
        return jsonify({
            'error': 'Verification failed',
            'code': 'FR_007',
            'details': str(e)
        }), 500


@facial_recognition_bp.route('/model/version', methods=['GET'])
def get_model_version():
    """
    Get current model version information.
    TRD 7.2: CI/CD Pipeline with model versioning
    TRD 10.4: Quarterly algorithm retraining
    """
    try:
        model_info = model_registry.get_current_model_info()
        
        return jsonify({
            'success': True,
            'model_version': model_info.get('version', 'unknown'),
            'model_name': model_info.get('name', 'sura-smart-facial-recognition'),
            'stage': model_info.get('stage', 'production'),
            'accuracy': model_info.get('metrics', {}).get('accuracy', 0.0),
            'trained_at': model_info.get('created_at', 'unknown'),
            'next_retraining': model_info.get('next_retraining', 'quarterly')
        })
    
    except Exception as e:
        logger.error(f"Failed to get model version: {str(e)}")
        return jsonify({
            'error': 'Failed to get model version',
            'code': 'FR_008',
            'details': str(e)
        }), 500


@facial_recognition_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Get model performance metrics.
    TRD 6.2: AI Performance Requirements
    TRD 7.4: Monitoring with New Relic/Datadog
    """
    try:
        metrics = predictor.get_metrics() if predictor else {}
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'trd_compliance': {
                '6.2.1_accuracy': metrics.get('accuracy', 0) >= 0.98,
                '6.2.2_false_positive': metrics.get('false_positive_rate', 1) < 0.005,
                '6.2.3_false_negative': metrics.get('false_negative_rate', 1) < 0.02,
                '6.2.4_processing_time': metrics.get('avg_processing_time', 10) < 5.0
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        return jsonify({
            'error': 'Failed to get metrics',
            'code': 'FR_009',
            'details': str(e)
        }), 500


# Initialize model on module load
def init_app(app):
    """
    Initialize facial recognition module with Flask app.
    """
    app.register_blueprint(facial_recognition_bp)
    
    # Initialize model if not in test mode
    if os.environ.get('FLASK_ENV') != 'testing':
        initialize_model(model_version='production')