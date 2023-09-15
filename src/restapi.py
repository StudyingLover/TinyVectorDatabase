import random
from flask import Blueprint, request, jsonify, send_file
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_204_NO_CONTENT
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from PIL import Image
import io

from src.database import VectorDatabase
from src.encoder import image_to_features, text_to_features

api = Blueprint('api',
                  __name__, 
                  url_prefix='/api/v1/api')

@api.post('/all_keys')
def all_keys():
    db_name = request.json.get('db_name')
    if db_name is None:
        return jsonify({'error': 'db_name is required'}), HTTP_400_BAD_REQUEST
    db = VectorDatabase.load_database(db_name)
    print(db)
    keys = db.get_all_keys()
    return jsonify({'keys': keys}), HTTP_200_OK

@api.delete('/key')
def delete_key():
    db_name = request.json.get('db_name')
    key = request.json.get('key')
    if db_name is None:
        return jsonify({'error': 'db_name is required'}), HTTP_400_BAD_REQUEST
    if key is None:
        return jsonify({'error': 'key is required'}), HTTP_400_BAD_REQUEST
    db = VectorDatabase.load_database(db_name)
    db.delete(key)
    db.save_database(db_name)
    return jsonify({'success': f'delete key : {key}'}), HTTP_200_OK
    
@api.post('/key')
def insert():
    db_name = request.form.get('db_name')
    key = request.form.get('key')
    label = request.form.get('label') 
    if label == 'image':
        img = request.files.get('image')
        if img is None:
            return jsonify({'error': 'image is required'}), HTTP_400_BAD_REQUEST
        db = VectorDatabase.load_database(db_name)
        img_bytes = img.read()
        img = Image.open(io.BytesIO(img_bytes))
        img_vector = image_to_features(img)
        db.insert(key, img_vector)
        db.save_database(db_name)
    elif label == 'text':
        text = request.form.get('text')
        if text is None:
            return jsonify({'error': 'text is required'}), HTTP_400_BAD_REQUEST
        db = VectorDatabase.load_database(db_name)
        text_vector = text_to_features(text)
        db.insert(key, text_vector)
        db.save_database(db_name)
    else:
        return jsonify({'error': 'label is required'}), HTTP_400_BAD_REQUEST
    return jsonify({'success': f'insert {label} key : {key}'}), HTTP_200_OK
    