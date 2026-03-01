# scripts/data_loader.py
"""
VGGFace2 Data Loading Module
Aligns with TRD Section 3.1.4 - Bias mitigation algorithms
"""

import os
import pandas as pd
from pathlib import Path
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

class VGGFace2Loader:
    def __init__(self, data_path='data/vgg_face2'):
        self.data_path = Path(data_path)
        self.samples_path = self.data_path / 'samples'
        self.attributes_path = self.data_path / 'attributes'
        
    def load_metadata(self):
        """
        Load VGGFace2 identity and demographic metadata
        TRD Section 3.1.4: Diverse dataset training
        """
        # Load identity labels
        identities_file = self.attributes_path / 'identities.txt'
        if not identities_file.exists():
            print(f"Warning: {identities_file} not found.")
            return pd.DataFrame(columns=['filename', 'identity_id', 'gender'])
            
        identities = pd.read_csv(identities_file, sep=' ', header=None)
        identities.columns = ['filename', 'identity_id']
        
        # Load gender labels (for PRD Section 4.3.2 - Gender-Sensitive Recognition)
        gender_file = self.attributes_path / 'gender.txt'
        if gender_file.exists():
            gender = pd.read_csv(gender_file, sep=' ', header=None)
            gender.columns = ['filename', 'gender']  # 0=Male, 1=Female
            return identities.merge(gender, on='filename')
        
        return identities
    
    def load_image_batch(self, filenames, target_size=(224, 224)):
        """
        Load batch of images for training/validation
        TRD Section 6.2.4: Processing time < 5 seconds per image
        """
        images = []
        for filename in filenames:
            img_path = self.samples_path / filename
            if img_path.exists():
                img = load_img(img_path, target_size=target_size)
                img_array = img_to_array(img)
                images.append(img_array)
        return np.array(images)
    
    def get_demographic_split(self, metadata):
        """
        Split data by demographics for bias testing
        PRD Section 8: Facial recognition limitations in demographics
        """
        if 'gender' not in metadata.columns:
            return {'combined': metadata}
            
        male_data = metadata[metadata['gender'] == 0]
        female_data = metadata[metadata['gender'] == 1]
        
        return {
            'male': male_data,
            'female': female_data,
            'combined': metadata
        }
    
    def create_train_val_split(self, metadata, val_ratio=0.2):
        """
        Create stratified train/validation split
        TRD Section 6.2.1: Face matching accuracy > 98%
        """
        from sklearn.model_selection import train_test_split
        
        if 'identity_id' not in metadata.columns:
            return train_test_split(metadata, test_size=val_ratio, random_state=42)

        train_data, val_data = train_test_split(
            metadata,
            test_size=val_ratio,
            stratify=metadata['identity_id'] if len(metadata['identity_id'].unique()) > 1 else None,
            random_state=42
        )
        
        return train_data, val_data
