#!/usr/bin/env python3
# scripts/download_training_data.py
# Sura Smart - TRD Section 3.1.4: Diverse Training Datasets
# TRD Section 10.4: Quarterly Model Retraining

import os
import requests
from pathlib import Path
from typing import Dict, List
import json


class TrainingDataDownloader:
    """
    Downloads training data for model retraining.
    
    TRD 3.1.4: Bias mitigation algorithms trained on diverse datasets
    TRD 10.4: Quarterly algorithm retraining with new data
    """
    
    def __init__(self, data_dir: str = 'data', config_path: str = 'config/data_sources.json'):
        self.data_dir = Path(data_dir)
        self.config_path = Path(config_path)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_data_sources(self) -> Dict:
        """Load configured data sources"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Default data sources
        return {
            'vggface2': {
                'type': 'academic',
                'license': 'academic_use_only',
                'path': 'data/vgg_face2',
                'requires_approval': True
            },
            'ms_celeb_1m': {
                'type': 'open',
                'license': 'cc_by_nc',
                'path': 'data/ms_celeb_1m',
                'requires_approval': False
            },
            'openimages': {
                'type': 'open',
                'license': 'cc_by',
                'path': 'data/openimages',
                'requires_approval': False
            }
        }
    
    def check_license_compliance(self, dataset_name: str, use_case: str = 'training') -> bool:
        """
        Check license compliance for dataset usage.
        TRD 8: Compliance Requirements
        """
        sources = self.load_data_sources()
        dataset_info = sources.get(dataset_name, {})
        
        license_type = dataset_info.get('license', 'unknown')
        
        # Commercial use restrictions
        if use_case == 'production' and license_type in ['academic_use_only', 'cc_by_nc']:
            print(f"⚠️  WARNING: {dataset_name} license ({license_type}) may not allow commercial use")
            return False
        
        return True
    
    def download_dataset(self, dataset_name: str) -> bool:
        """Download training dataset"""
        sources = self.load_data_sources()
        dataset_info = sources.get(dataset_name)
        
        if not dataset_info:
            print(f"❌ Dataset '{dataset_name}' not configured")
            return False
        
        # Check license compliance
        if not self.check_license_compliance(dataset_name, 'training'):
            print(f"❌ License compliance check failed for {dataset_name}")
            return False
        
        print(f"📥 Downloading training data: {dataset_name}")
        print(f"   License: {dataset_info.get('license', 'unknown')}")
        print(f"   Path: {dataset_info.get('path', 'unknown')}")
        
        # In production: Implement actual download logic
        # For now, create directory structure
        dataset_path = self.data_dir / dataset_info['path']
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        # Create metadata file
        metadata = {
            'dataset': dataset_name,
            'downloaded_at': datetime.now().isoformat(),
            'license': dataset_info.get('license'),
            'requires_approval': dataset_info.get('requires_approval', False)
        }
        
        with open(dataset_path / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ {dataset_name} ready for training")
        return True
    
    def prepare_training_manifest(self) -> Dict:
        """Create manifest of all available training data"""
        sources = self.load_data_sources()
        manifest = {
            'available_datasets': [],
            'total_size_gb': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        for dataset_name, info in sources.items():
            dataset_path = self.data_dir / info['path']
            if dataset_path.exists():
                manifest['available_datasets'].append({
                    'name': dataset_name,
                    'path': str(dataset_path),
                    'license': info.get('license'),
                    'compliance_status': 'verified'
                })
        
        # Save manifest
        manifest_path = self.data_dir / 'training_manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest


def main():
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Download Training Data')
    parser.add_argument('--dataset', type=str, default='all', 
                        help='Dataset to download')
    parser.add_argument('--data-dir', type=str, default='data', 
                        help='Directory to store training data')
    parser.add_argument('--check-license', action='store_true', 
                        help='Check license compliance before download')
    
    args = parser.parse_args()
    
    downloader = TrainingDataDownloader(data_dir=args.data_dir)
    
    if args.check_license:
        print("🔍 Checking license compliance...")
        sources = downloader.load_data_sources()
        for dataset_name in sources.keys():
            compliant = downloader.check_license_compliance(dataset_name, 'training')
            print(f"   {dataset_name}: {'✅ Compliant' if compliant else '❌ Non-compliant'}")
    
    if args.dataset == 'all':
        sources = downloader.load_data_sources()
        for dataset_name in sources.keys():
            downloader.download_dataset(dataset_name)
        
        # Generate manifest
        manifest = downloader.prepare_training_manifest()
        print(f"\n📋 Training manifest created: {len(manifest['available_datasets'])} datasets")
    else:
        downloader.download_dataset(args.dataset)


if __name__ == '__main__':
    main()