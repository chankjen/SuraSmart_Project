# scripts/license_checker.py
"""
License Compliance Checker
TRD Section 8: Compliance Requirements
"""

DATASET_LICENSES = {
    'vgg_face2': {
        'type': 'Academic Use Only',
        'commercial_allowed': False,
        'action': 'Purchase commercial license OR use synthetic data',
        'contact': 'vgg@robots.ox.ac.uk'
    },
    'lfw': {
        'type': 'Open Access',
        'commercial_allowed': True,
        'action': 'Safe for production use'
    },
    'utkface': {
        'type': 'Open Access',
        'commercial_allowed': True,
        'action': 'Safe for production use'
    }
}

def check_license_compliance(dataset_name, use_case='production'):
    license_info = DATASET_LICENSES.get(dataset_name)
    
    if not license_info:
        return {'status': 'UNKNOWN', 'message': 'Dataset not in license registry'}
    
    if use_case == 'production' and not license_info['commercial_allowed']:
        return {
            'status': 'VIOLATION',
            'message': f"{dataset_name} cannot be used for commercial production",
            'recommendation': license_info['action']
        }
    
    return {'status': 'COMPLIANT', 'message': f"{dataset_name} is safe for {use_case}"}
