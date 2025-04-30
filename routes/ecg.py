# ecg/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from extensions import db
from models import UploadedECG, Patient
from uuid import uuid4
from werkzeug.utils import secure_filename
import os

ecg_bp = Blueprint('ecg', __name__, url_prefix='/ecg')

@ecg_bp.route('/', methods=['GET'])
@login_required
def list_ecgs():
    page     = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ECGS_PER_PAGE', 20)
    pag      = UploadedECG.query.filter_by(user_id=current_user.id)\
                                .order_by(UploadedECG.upload_time.desc())\
                                .paginate(page=page, per_page=per_page, error_out=False)
    return render_template('ecg/list.html', ecgs=pag.items, pagination=pag)

@ecg_bp.route('/upload', methods=['POST'])
@login_required
def upload_ecg():
    pid  = request.form.get('patient_id')
    file = request.files.get('file')
    if not pid or not file:
        flash('Selecione paciente e arquivo válido.', 'warning')
        return redirect(url_for('ecg.list_ecgs'))
    patient = Patient.query.get(pid)
    if not patient or patient.user_id != current_user.id:
        flash('Paciente inválido.', 'danger')
        return redirect(url_for('ecg.list_ecgs'))
    fn = f"{uuid4().hex}_{secure_filename(file.filename)}"
    fp = os.path.join(current_app.config['UPLOAD_FOLDER'], fn)
    file.save(fp)
    ecg = UploadedECG(filename=fn, user_id=current_user.id, patient_id=pid)
    db.session.add(ecg)
    db.session.commit()
    flash('ECG enviado!', 'success')
    return redirect(url_for('ecg.list_ecgs'))