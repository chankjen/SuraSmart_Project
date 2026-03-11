# sura_smart/facial_recognition/embeddings.py
"""
Sura Smart Face Embedding Generator
TRD Section 3.1: Facial Recognition System
TRD Section 5.2.1: End-to-end Encryption for Stored Data
"""

import numpy as np
import tensorflow as tf
from typing import Union, List, Optional
from pathlib import Path
import logging
from datetime import datetime
from cryptography.fernet import Fernet
import os

logger = logging.getLogger(__name__)


class FaceEmbeddingGenerator:
    """
    Generates face embeddings for database storage and matching.
    
    TRD 3.1.1: Minimum 98% accuracy rate
    TRD 5.2.1: End-to-end encryption for stored embeddings
    TRD 6.2.4: Processing time < 5 seconds per image
    """
    
    def __init__(self, model_path: str, embedding_dimension: int = 512):
        """
        Initialize embedding generator.
        
        Args:
            model_path: Path to trained facial recognition model
            embedding_dimension: Dimension of output embedding (default: 512)
        """
        self.model_path = model_path
        self.embedding_dimension = embedding_dimension
        self.model = self._load_model()
        
        # TRD 5.2.1: Encryption for stored embeddings
        self.encryption_key = os.environ.get('EMBEDDING_ENCRYPTION_KEY', None)
        if self.encryption_key:
            self.cipher = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
        else:
            self.cipher = None
            logger.warning("⚠️  Embedding encryption not configured (TRD 5.2.1)")
    
    def _load_model(self) -> tf.keras.Model:
        """
        Load facial recognition model for embedding generation.
        TRD 3.1: Facial Recognition System
        """
        try:
            if self.model_path.endswith('.tflite'):
                # Edge AI model (TRD 4.3.1)
                self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
                return None
            else:
                # Standard Keras model
                model = tf.keras.models.load_model(self.model_path)
                logger.info(f"✅ Model loaded from {self.model_path}")
                return model
        except Exception as e:
            logger.error(f"❌ Failed to load model: {str(e)}")
            raise
    
    def preprocess_image(self, image_data: Union[np.ndarray, str, bytes]) -> np.ndarray:
        """
        Preprocess image for embedding generation.
        
        TRD 3.1.5: Support for low-quality images
        TRD 6.2.4: Efficient preprocessing (< 1 second)
        """
        import cv2
        
        # Load image
        if isinstance(image_data, str):
            # File path
            image = cv2.imread(image_data)
        elif isinstance(image_data, bytes):
            # Bytes data
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            # Already numpy array
            image = image_data
        
        if image is None:
            raise ValueError("Failed to load image")
        
        # Convert to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize to model input size
        target_size = (112, 112)  # Standard face recognition input size
        image = cv2.resize(image, target_size)
        
        # Normalize pixel values
        image = image.astype(np.float32)
        image = (image - 127.5) / 127.5  # Normalize to [-1, 1]
        
        # Expand dimensions for batch
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        
        return image
    
    def generate(self, image_data: Union[np.ndarray, str, bytes], 
                 encrypt: bool = True) -> np.ndarray:
        """
        Generate face embedding from image.
        
        TRD 3.1.1: Minimum 98% accuracy rate
        TRD 5.2.1: End-to-end encryption
        TRD 6.2.4: Processing time < 5 seconds
        """
        import time
        start_time = time.time()
        
        # Preprocess
        preprocessed = self.preprocess_image(image_data)
        
        # Generate embedding
        if hasattr(self, 'interpreter'):
            # TFLite model (Edge AI)
            self.interpreter.set_tensor(self.input_details[0]['index'], preprocessed)
            self.interpreter.invoke()
            embedding = self.interpreter.get_tensor(self.output_details[0]['index'])
        else:
            # Keras model
            embedding = self.model.predict(preprocessed, verbose=0)
        
        # Flatten embedding
        embedding = embedding.flatten()
        
        # Normalize embedding (L2 normalization)
        embedding = embedding / np.linalg.norm(embedding)
        
        # TRD 5.2.1: Encrypt embedding if requested
        if encrypt and self.cipher:
            embedding_bytes = embedding.astype(np.float32).tobytes()
            encrypted = self.cipher.encrypt(embedding_bytes)
            # Return as base64 string for storage
            import base64
            embedding = base64.b64encode(encrypted).decode()
        
        # Log processing time (TRD 6.2.4)
        processing_time = time.time() - start_time
        if processing_time > 5.0:
            logger.warning(f"Embedding generation exceeded SLA: {processing_time}s")
        
        logger.debug(f"Embedding generated in {processing_time:.3f}s")
        
        return embedding
    
    def generate_batch(self, image_list: List[Union[np.ndarray, str, bytes]], 
                       batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple images.
        
        TRD 6.2.4: Efficient batch processing
        """
        embeddings = []
        
        for i in range(0, len(image_list), batch_size):
            batch = image_list[i:i + batch_size]
            preprocessed_batch = np.vstack([self.preprocess_image(img) for img in batch])
            
            if hasattr(self, 'interpreter'):
                # TFLite - process one by one
                for img in preprocessed_batch:
                    img_expanded = np.expand_dims(img, axis=0)
                    self.interpreter.set_tensor(self.input_details[0]['index'], img_expanded)
                    self.interpreter.invoke()
                    emb = self.interpreter.get_tensor(self.output_details[0]['index'])
                    embeddings.append(emb.flatten())
            else:
                # Keras model - batch processing
                batch_embeddings = self.model.predict(preprocessed_batch, verbose=0)
                embeddings.extend(batch_embeddings)
        
        embeddings = np.array(embeddings)
        
        # L2 normalization
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return embeddings
    
    def decrypt_embedding(self, encrypted_embedding: str) -> np.ndarray:
        """
        Decrypt stored embedding.
        TRD 5.2.1: End-to-end encryption
        """
        if not self.cipher:
            raise ValueError("Encryption not configured")
        
        import base64
        encrypted_bytes = base64.b64decode(encrypted_embedding)
        decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
        embedding = np.frombuffer(decrypted_bytes, dtype=np.float32)
        
        return embedding
    
    def compare_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compare two embeddings using cosine similarity.
        
        TRD 6.2.1: Face matching accuracy > 98%
        TRD 6.2.2: False positive rate < 0.5%
        """
        # Ensure embeddings are normalized
        emb1 = embedding1 / np.linalg.norm(embedding1)
        emb2 = embedding2 / np.linalg.norm(embedding2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2)
        
        return float(similarity)
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return self.embedding_dimension
    
    def validate_embedding(self, embedding: np.ndarray) -> bool:
        """
        Validate embedding format and quality.
        TRD 3.1: Facial Recognition System
        """
        if embedding is None:
            return False
        
        if len(embedding) != self.embedding_dimension:
            return False
        
        # Check for NaN or Inf values
        if np.any(np.isnan(embedding)) or np.any(np.isinf(embedding)):
            return False
        
        return True