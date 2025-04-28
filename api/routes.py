# api/routes.py
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import Patient, UploadedECG
from services.patient_service import build_patients_data

api = Blueprint('api', __name__)

@api.route('/patients')
@login_required
def api_list_patients():
    pts = Patient.query.filter_by(user_id=current_user.id).all()
    return jsonify(build_patients_data(pts))

@api.route('/ecgs')
@login_required
def api_list_ecgs():
    ecgs = UploadedECG.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': e.id,
        'filename': e.filename,
        'uploaded_at': e.upload_time.isoformat()
    } for e in ecgs])