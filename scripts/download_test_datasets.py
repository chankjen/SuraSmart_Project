#!/usr/bin/env python3
# scripts/download_test_datasets.py
# Sura Smart - TRD Section 3.1.4: Diverse Datasets for Bias Testing
# TRD Section 6.2: AI Performance Validation

import os
import requests
import zipfile
import hashlib
from pathlib import Path
from typing import Dict


class DatasetDownloader:
    """
    Downloads test datasets for model validation.
    
    TRD 3.1.4: Bias mitigation algorithms trained on diverse datasets
    TRD 6.2: AI Performance Requirements
    """
    
    DATASETS = {
        'lfw': {
            'url': 'http://vis-www.cs.umass.edu/lfw/lfw-deepfunneled.tgz',
            'checksum': 'CHANGE_ME',
            'path': 'data/lfw',
            'description': 'Labeled Faces in the Wild - Baseline Testing'
        },
        'utkface': {
            'url': 'https://s3.amazonaws.com/alldataarchive/utkface/UTKFace.tar.gz',
            'checksum': 'CHANGE_ME',
            'path': 'data/utkface',
            'description': 'UTKFace - Bias Testing (Age, Gender, Ethnicity)'
        },
        'celeba': {
            'url': 'https://drive.google.com/uc?id=0B7EVK8r0v71pWEZsZE9oNnFzTm8',
            'checksum': 'CHANGE_ME',
            'path': 'data/celeba',
            'description': 'CelebA - Attribute Testing'
        },
        'wider_face': {
            'url': 'http://shuoyang1213.me/WIDERFACE/support/bbox_format.zip',
            'checksum': 'CHANGE_ME',
            'path': 'data/wider_face',
            'description': 'WIDER FACE - Occlusion & Crowd Testing'
        }
    }
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file integrity"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        actual_checksum = sha256_hash.hexdigest()
        return actual_checksum == expected_checksum
    
    def download_dataset(self, dataset_name: str) -> bool:
        """Download a single dataset"""
        dataset_info = self.DATASETS.get(dataset_name)
        
        if not dataset_info:
            print(f"❌ Dataset '{dataset_name}' not found")
            return False
        
        print(f"📥 Downloading {dataset_name}...")
        print(f"   Description: {dataset_info['description']}")
        
        dataset_path = self.data_dir / dataset_info['path']
        dataset_path.mkdir(parents=True, exist_ok=True)
        
        # Download file
        file_name = dataset_info['url'].split('/')[-1]
        file_path = dataset_path / file_name
        
        try:
            response = requests.get(dataset_info['url'], stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify checksum
            if dataset_info.get('checksum'):
                if not self.verify_checksum(file_path, dataset_info['checksum']):
                    print(f"❌ Checksum verification failed for {dataset_name}")
                    return False
            
            # Extract if compressed
            if file_name.endswith('.zip') or file_name.endswith('.tgz') or file_name.endswith('.tar.gz'):
                print(f"   Extracting {file_name}...")
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(dataset_path)
            
            print(f"✅ {dataset_name} downloaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {dataset_name}: {str(e)}")
            return False
    
    def download_all(self) -> Dict[str, bool]:
        """Download all test datasets"""
        results = {}
        
        print("=" * 60)
        print("SURA SMART - Test Dataset Download")
        print("TRD Section 3.1.4: Diverse Datasets for Bias Testing")
        print("=" * 60)
        
        for dataset_name in self.DATASETS.keys():
            results[dataset_name] = self.download_dataset(dataset_name)
        
        print("=" * 60)
        print(f"Download Summary: {sum(results.values())}/{len(results)} successful")
        print("=" * 60)
        
        return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Download Test Datasets')
    parser.add_argument('--dataset', type=str, default='all', 
                        help='Dataset to download (lfw, utkface, celeba, wider_face, or all)')
    parser.add_argument('--data-dir', type=str, default='data', 
                        help='Directory to store datasets')
    
    args = parser.parse_args()
    
    downloader = DatasetDownloader(data_dir=args.data_dir)
    
    if args.dataset == 'all':
        downloader.download_all()
    else:
        downloader.download_dataset(args.dataset)


if __name__ == '__main__':
    main()