# sura_smart/facial_recognition/registry/mlflow_registry.py
"""
Sura Smart MLFlow Model Registry
TRD Section 7.2: CI/CD Pipeline
TRD Section 10.4: Quarterly Algorithm Retraining
TRD Section 7.4: Monitoring
"""

import mlflow
import mlflow.tensorflow
from typing import Dict, Optional, List
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    MLFlow-based Model Registry for Sura Smart.
    
    TRD 7.2: CI/CD Pipeline with model versioning
    TRD 10.4: Quarterly algorithm retraining
    TRD 7.4: Monitoring and metrics tracking
    """
    
    def __init__(self, tracking_uri: str = None):
        """
        Initialize model registry.
        
        Args:
            tracking_uri: MLFlow tracking server URI
        """
        self.tracking_uri = tracking_uri or os.environ.get(
            'MLFLOW_TRACKING_URI', 
            'http://localhost:5000'
        )
        mlflow.set_tracking_uri(self.tracking_uri)
        
        self.model_name = 'sura-smart-facial-recognition'
        
        logger.info(f"✅ Model Registry initialized: {self.tracking_uri}")
    
    def register_model(self, model_path: str, stage: str = 'staging',
                       metrics: Optional[Dict] = None) -> str:
        """
        Register model in MLFlow registry.
        
        TRD 7.2: CI/CD Pipeline with model versioning
        TRD 6.2: AI Performance metrics tracking
        """
        logger.info(f"📦 Registering model: {model_path}")
        
        with mlflow.start_run(
            run_name=f'model_registration_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        ):
            # Log model
            mlflow.tensorflow.log_model(
                tf_saved_model_dir=model_path,
                tf_meta_graph_tags=['serve'],
                tf_signature_def_key='serving_default',
                artifact_path='model'
            )
            
            # Log metrics
            if metrics:
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, (int, float)):
                        mlflow.log_metric(metric_name, metric_value)
            
            # Log parameters
            mlflow.log_param('model_type', 'facial_recognition')
            mlflow.log_param('trd_compliance', '3.1, 6.2')
            mlflow.log_param('accuracy_threshold', 0.98)
            mlflow.log_param('registered_at', datetime.now().isoformat())
            mlflow.log_param('next_retraining', 'quarterly')
            
            # Register model
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
            model_version = mlflow.register_model(model_uri, self.model_name)
            
            # Transition to stage
            client = mlflow.tracking.MlflowClient()
            client.transition_model_version_stage(
                name=self.model_name,
                version=model_version.version,
                stage=stage.upper()
            )
            
            logger.info(f"✅ Model registered: {self.model_name} v{model_version.version}")
            logger.info(f"   Stage: {stage}")
            
            return model_version.version
    
    def get_model_path(self, stage: str = 'production') -> str:
        """
        Get model path for specified stage.
        
        TRD 7.2: CI/CD Pipeline
        """
        client = mlflow.tracking.MlflowClient()
        
        try:
            versions = client.get_latest_versions(self.model_name, stages=[stage.upper()])
            
            if versions:
                model_uri = f"models:/{self.model_name}/{stage}"
                logger.info(f"✅ Loaded model: {self.model_name} ({stage})")
                return model_uri
            else:
                logger.warning(f"⚠️  No model found for stage: {stage}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get model: {str(e)}")
            raise
    
    def get_current_model_info(self) -> Dict:
        """
        Get current production model information.
        
        TRD 7.4: Monitoring
        TRD 10.4: Quarterly retracking schedule
        """
        client = mlflow.tracking.MlflowClient()
        
        try:
            versions = client.get_latest_versions(self.model_name, stages=['PRODUCTION'])
            
            if versions:
                version = versions[0]
                run = client.get_run(version.run_id)
                
                return {
                    'name': self.model_name,
                    'version': version.version,
                    'stage': 'production',
                    'created_at': version.creation_timestamp,
                    'metrics': run.data.metrics,
                    'params': run.data.params,
                    'next_retraining': 'quarterly'
                }
        except Exception as e:
            logger.error(f"❌ Failed to get model info: {str(e)}")
        
        return {
            'name': self.model_name,
            'version': 'unknown',
            'stage': 'unknown',
            'metrics': {}
        }
    
    def promote_model(self, version: str = None, stage: str = 'production'):
        """
        Promote model to production stage.
        
        TRD 7.3: Blue-green deployment
        TRD 7.5: Automated rollback
        """
        client = mlflow.tracking.MlflowClient()
        
        if version is None:
            # Get latest staging model
            versions = client.get_latest_versions(self.model_name, stages=['STAGING'])
            if versions:
                version = versions[0].version
        
        if version:
            client.transition_model_version_stage(
                name=self.model_name,
                version=version,
                stage=stage.upper()
            )
            logger.info(f"✅ Model v{version} promoted to {stage}")
    
    def list_models(self) -> List[Dict]:
        """
        List all registered models.
        
        TRD 7.2: CI/CD Pipeline
        """
        client = mlflow.tracking.MlflowClient()
        
        try:
            models = client.search_registered_models()
            
            model_list = []
            for model in models:
                versions = client.get_latest_versions(model.name)
                model_list.append({
                    'name': model.name,
                    'versions': [v.version for v in versions],
                    'stages': [v.current_stage for v in versions]
                })
            
            return model_list
        except Exception as e:
            logger.error(f"❌ Failed to list models: {str(e)}")
            return []
    
    def compare_models(self, version1: str, version2: str) -> Dict:
        """
        Compare two model versions.
        
        TRD 6.2: AI Performance comparison
        """
        client = mlflow.tracking.MlflowClient()
        
        try:
            v1 = client.get_model_version(self.model_name, version1)
            v2 = client.get_model_version(self.model_name, version2)
            
            run1 = client.get_run(v1.run_id)
            run2 = client.get_run(v2.run_id)
            
            return {
                'version1': {
                    'version': version1,
                    'metrics': run1.data.metrics,
                    'created_at': v1.creation_timestamp
                },
                'version2': {
                    'version': version2,
                    'metrics': run2.data.metrics,
                    'created_at': v2.creation_timestamp
                },
                'comparison': {
                    'accuracy_diff': run1.data.metrics.get('accuracy', 0) - run2.data.metrics.get('accuracy', 0),
                    'better_version': version1 if run1.data.metrics.get('accuracy', 0) > run2.data.metrics.get('accuracy', 0) else version2
                }
            }
        except Exception as e:
            logger.error(f"❌ Failed to compare models: {str(e)}")
            return {}
    
    def archive_model(self, version: str):
        """
        Archive old model version.
        
        TRD 7.2: Model lifecycle management
        """
        client = mlflow.tracking.MlflowClient()
        
        client.transition_model_version_stage(
            name=self.model_name,
            version=version,
            stage='ARCHIVED'
        )
        
        logger.info(f"✅ Model v{version} archived")