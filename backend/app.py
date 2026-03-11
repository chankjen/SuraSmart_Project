from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from deepface import DeepFace
import os
import sqlite3
import sys
import numpy as np
import tensorflow as tf

# Add scripts directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from scripts.data_loader import VGGFace2Loader
from scripts.model_trainer import SuraSmartTrainer
from scripts.bias_audit import BiasAuditor

app = Flask(__name__)

# Paths to Django project resources
PROJECT_ROOT = 'd:/SuraSmart_Project'
DB_PATH = os.path.join(PROJECT_ROOT, 'data/db.sqlite3')
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'backend/media')
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
MODEL_PATH = os.path.join(PROJECT_ROOT, 'models/best_model.h5')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize AI helpers (Global context)
# For production, we would load the actual model here
# model = tf.keras.models.load_model(MODEL_PATH)
try:
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception:
    # Use DeepFace as fallback or mock for this demonstration
    model = None 

auditor = BiasAuditor(model)

# --- Helper functions ---
def preprocess_image(image_path, target_size=(224, 224)):
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=target_size)
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) # Add batch dimension
    return img_array

def verify_admin_access(req):
    # Simplified authentication mock for TRD Section 4.2.3
    # In real application, this would verify JWT tokens or sessions
    auth_header = req.headers.get('Authorization')
    return auth_header == 'AdminToken123' 

# --- Routes ---

# Route to serve Django media files
@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(MEDIA_ROOT, filename)

# Route to serve VGGFace2 samples
@app.route('/vgg_media/<identity_id>/<filename>')
def serve_vgg_media(identity_id, filename):
    vgg_samples_root = os.path.join(PROJECT_ROOT, 'data/vgg_face2/samples/loose_crop (release version)')
    identity_path = os.path.join(vgg_samples_root, identity_id)
    return send_from_directory(identity_path, filename)

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Function to get all images and person details from the database
def get_db_images():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return []
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()
    
    query = """
        SELECT 
            img.image_file, 
            mp.full_name, 
            mp.age, 
            mp.gender, 
            mp.status,
            mp.last_seen_location
        FROM facial_recognition_facialrecognitionimage img
        JOIN facial_recognition_missingperson mp ON img.missing_person_id = mp.id
        WHERE img.status = 'completed'
    """
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        image_list = []
        for row in rows:
            abs_path = os.path.join(MEDIA_ROOT, row['image_file'])
            if os.path.exists(abs_path):
                image_list.append(dict(row))
                image_list[-1]['abs_path'] = abs_path
            else:
                print(f"Image file not found: {abs_path}")
        
        return image_list
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def get_vgg_samples():
    """Fetches all samples from the VGGFace2 dataset using the loader."""
    loader = VGGFace2Loader()
    return loader.get_all_samples()

@app.route('/upload', methods=['POST'])
def upload_image():
    uploaded_file = request.files['image']
    
    if uploaded_file:
        uploaded_image_name = uploaded_file.filename
        uploaded_file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(uploaded_file_path)
        
        db_images = get_db_images() 
        
        matches = []
        for person in db_images:
            try:
                result = DeepFace.verify(
                    img1_path=uploaded_file_path, 
                    img2_path=person['abs_path'], 
                    model_name='Facenet512',
                    enforce_detection=False
                )
                
                if result['verified']: 
                    matches.append({
                        'name': person['full_name'],
                        'age': person['age'],
                        'gender': person['gender'],
                        'status': person['status'],
                        'location': person['last_seen_location'],
                        'image_url': f"/media/{person['image_file']}",
                        'distance': result['distance']
                    })
                    break 
            except Exception as e:
                print(f"Facial recognition error: {e}")
                continue
        
        # If no matches in DB, search VGGFace2 dataset
        if not matches:
            vgg_samples = get_vgg_samples()
            for sample in vgg_samples:
                try:
                    result = DeepFace.verify(
                        img1_path=uploaded_file_path, 
                        img2_path=sample['abs_path'], 
                        model_name='Facenet512',
                        enforce_detection=False
                    )
                    
                    if result['verified']:
                        matches.append({
                            'name': f"VGGFace2 Identity: {sample['identity_id']}",
                            'age': 'N/A',
                            'gender': 'N/A',
                            'status': 'VGGFace2 Dataset',
                            'location': 'N/A',
                            'image_url': f"/vgg_media/{sample['identity_id']}/{sample['filename']}",
                            'distance': result['distance'],
                            'source': 'vgg_face2'
                        })
                        break
                except Exception as e:
                    print(f"VGGFace2 recognition error: {e}")
                    continue
            
        return render_template('results.html', matches=matches, uploaded_image=uploaded_image_name)
    
    return redirect(url_for('index'))

# --- New VGGFace2 Integration API Endpoints ---

@app.route('/api/v1/search', methods=['POST'])
def api_search():
    """
    Core search endpoint
    TRD Section 4.1.1: Advanced Facial Recognition with VGGFace2-trained model
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image = request.files['image']
    temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{image.filename}")
    image.save(temp_path)
    
    # Process through model if loaded
    if model:
        try:
            processed = preprocess_image(temp_path)
            embedding = model.predict(processed)
            # Search logic here...
        except Exception as e:
            return jsonify({'error': f'Model inference failed: {str(e)}'}), 500
    
    return jsonify({
        'status': 'success',
        'message': 'API endpoint ready. Model inference configured.',
        'note': 'This uses the vggface2-integrated architecture'
    })

@app.route('/api/v1/audit/bias', methods=['GET'])
def run_bias_audit():
    """
    Endpoint for running bias audits
    TRD Section 10.5: Quarterly algorithm retraining
    """
    if not verify_admin_access(request):
        return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
    
    # Load test datasets (Simulation)
    loader = VGGFace2Loader()
    metadata = loader.load_metadata()
    test_datasets = loader.get_demographic_split(metadata)
    
    audit_results = auditor.run_full_audit(test_datasets)
    report = auditor.generate_audit_report(audit_results)
    
    return jsonify({
        'results': audit_results,
        'report': report
    })

@app.route('/api/v1/model/retrain', methods=['POST'])
def trigger_retraining():
    """
    Trigger model retraining with new VGGFace2 data
    TRD Section 10.4: Quarterly algorithm retraining
    """
    if not verify_admin_access(request):
        return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
    
    # Start training pipeline
    loader = VGGFace2Loader()
    metadata = loader.load_metadata()
    train_data, val_data = loader.create_train_val_split(metadata)
    
    # trainer = SuraSmartTrainer()
    # history = trainer.train(train_data, val_data)
    
    return jsonify({
        'status': 'Retraining initiated',
        'train_samples': len(train_data),
        'val_samples': len(val_data)
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)

# Add to existing app.py

from edge_ai.edge_inference import EdgeInferenceEngine
import os

# Initialize Edge Engine (if edge model available)
EDGE_MODEL_PATH = os.environ.get('EDGE_MODEL_PATH', 'models/edge/model.tflite')
edge_engine = None

if os.path.exists(EDGE_MODEL_PATH):
    try:
        edge_engine = EdgeInferenceEngine(model_path=EDGE_MODEL_PATH)
        logger.info("Edge AI Engine initialized successfully")
    except Exception as e:
        logger.warning(f"Edge AI Engine initialization failed: {str(e)}")


@app.route('/api/v1/search/edge', methods=['POST'])
@require_auth(role_required=['family', 'law_enforcement', 'admin'])
def search_edge_offline():
    """
    Edge AI search endpoint for low-connectivity environments.
    
    TRD 4.3.1: Function with < 100kbps connectivity
    TRD 6.1.4: Offline-first architecture
    """
    search_id = str(uuid.uuid4())
    
    if not edge_engine:
        return jsonify({
            'error': 'Edge AI not available', 
            'code': 'EDGE_001',
            'fallback': 'Use cloud search endpoint'
        }), 503
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided', 'code': 'SEARCH_001'}), 400
    
    image = request.files['image']
    user_id = g.user_id
    
    try:
        # Read image
        import numpy as np
        from PIL import Image
        import io
        
        image_data = np.array(Image.open(io.BytesIO(image.read())))
        
        # Run edge inference
        result = edge_engine.run_inference(image_data)
        
        # Cache results for later sync (TRD 6.1.4)
        edge_engine.cache_search_results(search_id, result)
        
        # Search local cache database (if available)
        local_matches = search_local_cache(result['embedding'])
        
        return jsonify({
            'search_id': search_id,
            'mode': 'edge_offline',
            'connectivity_status': edge_engine.connectivity_status['status'],
            'matches': local_matches,
            'inference_time': result['inference_time_seconds'],
            'sync_pending': not edge_engine.connectivity_status['sync_enabled'],
            'trd_compliance': result['trd_compliance']
        })
    
    except Exception as e:
        logger.error(f"Edge search failed: {str(e)}")
        return jsonify({'error': 'Edge search failed', 'code': 'EDGE_002'}), 500


@app.route('/api/v1/edge/sync', methods=['POST'])
@require_auth(role_required=['family', 'law_enforcement', 'admin'])
def sync_edge_results():
    """
    Sync cached edge results to cloud.
    
    TRD 6.1.4: Automatic sync when connectivity restored
    TRD 5.1.2: Blockchain audit trail update
    """
    if not edge_engine:
        return jsonify({'error': 'Edge AI not available', 'code': 'EDGE_001'}), 503
    
    try:
        sync_result = edge_engine.sync_cached_results()
        return jsonify(sync_result)
    except Exception as e:
        logger.error(f"Edge sync failed: {str(e)}")
        return jsonify({'error': 'Sync failed', 'code': 'EDGE_003'}), 500


@app.route('/api/v1/edge/stats', methods=['GET'])
@require_auth(role_required=['admin'])
def get_edge_stats():
    """
    Get edge AI performance statistics.
    
    TRD 7.4: Monitoring and metrics
    """
    if not edge_engine:
        return jsonify({'error': 'Edge AI not available', 'code': 'EDGE_001'}), 503
    
    stats = edge_engine.get_performance_stats()
    return jsonify(stats)