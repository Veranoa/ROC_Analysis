# app.py
#
# Copyright (C) 2024-2030 Yun Liu
# University of Chicago
#
# Flask Application for ROC Analysis
#
# Description:
# This Flask application handles the uploading, processing, and analysis of ROC data.
# It supports various types of ROC analysis, including average, reader, and combined analyses.
# The application also allows users to download styling files and rerun analyses with updated styling.

from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash
from flask_wtf.csrf import CSRFProtect
import os
import json
import shutil
import uuid
from datetime import datetime
import subprocess
from threading import Thread
import logging
from werkzeug.datastructures import FileStorage

from collections import Counter
from rapidfuzz import fuzz

from config import Config
from tex.ROCAveGenerator import LaTeXROCAveGenerator
from tex.ROCReaderGenerator import LaTeXROCReaderGenerator 
from tex.ROCReaderAveGenerator import LaTeXROCReaderAveGenerator
from tex.ROCBoxGenerator import LaTeXROCBoxGenerator
from tex.ROCAllinOne import LaTeXROCReport

from tex.TexConfidenceGenerator import LaTeXConfidenceGenerator
from tex.sci_cr import CI, CG2

columns = []

# Ensure necessary directories exist
os.makedirs(Config.LOG_FOLDER, exist_ok=True)
DATA_DIR = Config.USER_FOLDER
os.makedirs(DATA_DIR, exist_ok=True)

# Load settings if they exist
SETTINGS_FILE = Config.SETTINGS_FILE
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, 'r') as f:
        settings = json.load(f)
        DATA_DIR = settings.get('data_dir', DATA_DIR)
        
DEFAULT_STYLING_FILES = {
    'average': 'average_settings.json',
    'reader': 'reader_settings.json',
    'both': 'all_settings.json',
    'confidence':'confidence_settings.json',
}

logging.basicConfig(filename=os.path.join(Config.LOG_FOLDER, 'server.log'), level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

app = Flask(__name__)
app.secret_key = 'e1221313479442f320168216451c78a2'
csrf = CSRFProtect(app)

@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')


@app.route('/plotting')
def plotting():
    """Render the plotting page."""
    return render_template('plotting.html')

@app.route('/analysis')
def analysis():
    """Render the analysis page."""
    return render_template('analysis.html')

def load_jobs(status_filter=None):
    """
    Load jobs from the log file, optionally filtering by status.

    Args:
        status_filter (str): Status to filter jobs by.

    Returns:
        list: List of job dictionaries.
    """
    log_path = os.path.join(DATA_DIR, 'logfile.json')
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            try:
                jobs = json.load(f)
                if status_filter:
                    jobs = [job for job in jobs if job.get('status') == status_filter]
                return jobs
            except json.JSONDecodeError:
                return []
    return []

@app.route('/styling')
def styling():
    """Render the styling page, displaying completed jobs."""
    jobs = load_jobs(status_filter='COMPLETED')
    return render_template('styling.html', jobs=jobs)

@app.route('/classify')
def classify():
    """Render the analysis page."""
    return render_template('classify.html')

@app.route('/auto_categorize_cases', methods=['POST'])
### ADD a func to correct the typos in column names and the group names
def auto_categorize_cases():
    data = request.json
    columns = data.get("columns", [])
    logging.info(f"Received columns: {columns}")

    if not columns:
        logging.error("No columns provided in request")
        return jsonify({"error": "No columns provided"}), 400

    similarity_threshold = 95
    repeat_threshold = 5

    column_counts = Counter(columns)

    valid_columns = [
        {"name": col, "index": i}
        for i, col in enumerate(columns)
        if column_counts[col] >= repeat_threshold
    ]

    groups = []
    used_indices = set()

    for i, base_column in enumerate(columns):
        if i in used_indices:
            continue

        group = [{"name": base_column, "index": i}]
        for j in range(i + 1, len(columns)):
            if (
                j not in used_indices
                and fuzz.partial_ratio(base_column, columns[j]) >= similarity_threshold
            ):
                group.append({"name": columns[j], "index": j})
                used_indices.add(j)

        used_indices.add(i)

        if len(group) >= repeat_threshold:
            groups.append(group)

    logging.info(f"Generated groups: {groups}")

    auto_recognized_groups = [
        {"groupName": group[0]["name"], "columns": group} for group in groups
    ]

    return jsonify({
        "autoRecognizedGroups": auto_recognized_groups,
    })

@app.route('/submit_categories', methods=['POST'])
def submit_categories():
    data = request.get_json()
    print(f"Received categories: {data}")
    return jsonify({"message": "Categories received successfully!"}), 200


@app.route('/download_styling/<job_id>')
def download_styling(job_id):
    """
    Download the styling file for a given job.

    Args:
        job_id (str): Job ID.

    Returns:
        file: The styling file to be downloaded.
    """
    job_dir = os.path.join(DATA_DIR, job_id)
    temp_folder = os.path.join(job_dir, 'temp')
    style_folder = os.path.join(job_dir, 'style')

    form_data_path = os.path.join(temp_folder, 'form_data.json')
    if os.path.exists(form_data_path):
        with open(form_data_path, 'r') as file:
            form_data = json.load(file)
        analysis_type = form_data.get('analysis_type')
        styling_filename = DEFAULT_STYLING_FILES.get(analysis_type)
    else:
        return "Form data file not found", 404
    
    styling_file_path = os.path.join(style_folder, styling_filename)
    if os.path.exists(styling_file_path):
        return send_file(styling_file_path, as_attachment=True)
    else:
        return "Styling file not found", 404

@app.route('/upload_styling', methods=['POST'])
def upload_styling():
    """
    Upload a new styling file for a job.

    Returns:
        json: Response message.
    """
    job_id = request.form['job_id']
    if 'stylingFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['stylingFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    job_dir = os.path.join(DATA_DIR, job_id)
    temp_dir = os.path.join(job_dir, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, 'new_styling.json')
    file.save(file_path)

    with open(os.path.join(temp_dir, 'uploaded_styling_file.json'), 'w') as f:
        json.dump({'filename': 'new_styling.json'}, f)

    return jsonify({'message': 'Styling file uploaded successfully!', 'filename': file.filename})

@app.route('/rerun_analysis/<job_id>', methods=['POST'])
def rerun_analysis(job_id):
    """
    Rerun an analysis with an updated styling file.

    Args:
        job_id (str): Job ID.

    Returns:
        response: Redirect to the styling page.
    """
    job_dir = os.path.join(DATA_DIR, job_id)
    temp_dir = os.path.join(job_dir, 'temp')

    styling_file_info_path = os.path.join(temp_dir, 'uploaded_styling_file.json')
    if not os.path.exists(styling_file_info_path):
        flash('No styling file uploaded.', 'danger')
        return redirect(url_for('styling'))

    with open(styling_file_info_path, 'r') as f:
        styling_file_info = json.load(f)

    styling_file_path = os.path.join(temp_dir, styling_file_info['filename'])
    if not os.path.exists(styling_file_path):
        flash('Styling file not found.', 'danger')
        return redirect(url_for('styling'))

    form_data_path = os.path.join(temp_dir, 'form_data.json')
    with open(form_data_path, 'r') as f:
        form_data = json.load(f)

    new_job_id = str(uuid.uuid4())
    new_job_dir = os.path.join(DATA_DIR, new_job_id)
    os.makedirs(new_job_dir, exist_ok=True)
    shutil.copytree(os.path.join(job_dir, 'input'), os.path.join(new_job_dir, 'input'), dirs_exist_ok=True)
    shutil.copytree(os.path.join(job_dir, 'temp'), os.path.join(new_job_dir, 'temp'), dirs_exist_ok=True)

    average_file_objects = []
    average_folder = os.path.join(new_job_dir, 'input', 'ave')
    if os.path.exists(average_folder):
        for filename in os.listdir(average_folder):
            file_path = os.path.join(average_folder, filename)
            average_file_objects.append(FileStorage(open(file_path, 'rb'), filename=filename))

    reader_file_objects = []
    reader_folder = os.path.join(new_job_dir, 'input', 'reader')
    if os.path.exists(reader_folder):
        for filename in os.listdir(reader_folder):
            file_path = os.path.join(reader_folder, filename)
            reader_file_objects.append(FileStorage(open(file_path, 'rb'), filename=filename))

    boxplot_file_object = None
    box_folder = os.path.join(new_job_dir, 'input', 'box')
    if form_data.get('boxplot_file'):
        boxplot_file_path = os.path.join(box_folder, form_data['boxplot_file'])
        if os.path.exists(boxplot_file_path):
            boxplot_file_object = FileStorage(open(boxplot_file_path, 'rb'), filename=form_data['boxplot_file'])

    thread = Thread(target=process_files_and_update_log, args=(
        new_job_id,
        form_data['name'],
        form_data['analysis_name'],
        form_data['analysis_type'],
        average_file_objects,
        reader_file_objects,
        boxplot_file_object,
        form_data['average_annotations'],
        form_data['readers_annotations'],
        form_data['readers_groups'],
        styling_file_path
    ))
    thread.start()

    flash(f"New analysis job {new_job_id} has been started successfully!", "success")
    return redirect(url_for('styling'))

@app.route('/upload_confidence_styling', methods=['POST'])
def upload_confidence_styling():
    """
    Upload a new styling file for a confidence interval job.
    """
    job_id = request.form['job_id']
    if 'stylingFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['stylingFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    job_dir = os.path.join(DATA_DIR, job_id)
    temp_dir = os.path.join(job_dir, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, 'new_confidence_styling.json')
    file.save(file_path)

    # Save metadata about the uploaded file
    with open(os.path.join(temp_dir, 'uploaded_confidence_styling_file.json'), 'w') as f:
        json.dump({'filename': 'new_confidence_styling.json'}, f)

    return jsonify({'message': 'Styling file uploaded successfully!', 'filename': file.filename})

@app.route('/rerun_confidence_analysis/<job_id>', methods=['POST'])
def rerun_confidence_analysis(job_id):
    """
    Rerun a confidence interval analysis with an updated styling file.
    """
    job_dir = os.path.join(DATA_DIR, job_id)
    temp_dir = os.path.join(job_dir, 'temp')

    styling_file_info_path = os.path.join(temp_dir, 'uploaded_confidence_styling_file.json')
    if not os.path.exists(styling_file_info_path):
        flash('No styling file uploaded.', 'danger')
        return redirect(url_for('styling'))

    with open(styling_file_info_path, 'r') as f:
        styling_file_info = json.load(f)

    styling_file_path = os.path.join(temp_dir, styling_file_info['filename'])
    if not os.path.exists(styling_file_path):
        flash('Styling file not found.', 'danger')
        return redirect(url_for('styling'))

    form_data_path = os.path.join(temp_dir, 'form_data.json')
    with open(form_data_path, 'r') as f:
        form_data = json.load(f)
        
    new_job_id = str(uuid.uuid4())
    new_job_dir = os.path.join(DATA_DIR, new_job_id)
    os.makedirs(new_job_dir, exist_ok=True)
    shutil.copytree(os.path.join(job_dir, 'temp'), os.path.join(new_job_dir, 'temp'), dirs_exist_ok=True)

    log_entry = {
        'job_id': new_job_id,
        'analysis_name': form_data['analysis_name'], 
        'analysis_type': 'confidence',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'PENDING'
    }
    
    log_path = os.path.join(DATA_DIR, 'logfile.json')
        
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                log_data = []
    else:
        log_data = []

    log_data.append(log_entry)
    with open(log_path, 'w') as f:
        json.dump(log_data, f, indent=4)
            
    thread = Thread(target=process_confidence_job, args=(new_job_id, form_data, styling_file_path))
    thread.start()

    flash(f"New confidence interval analysis job {new_job_id} has been started successfully!", "success")
    return redirect(url_for('styling'))

@app.route('/submit', methods=['POST'])
def submit():
    """
    Handle the submission of analysis job.

    Returns:
        response: Renders the job_started.html page.
    """
    name = request.form.get('name', 'Unnamed')
    analysis_name = request.form.get('analysisName', 'Unnamed Analysis')
    analysis_type = request.form.get('analysisType')
    average_files = request.files.getlist('averageFile[]')
    average_annotations = request.form.getlist('averageFileAnnotation[]')
    readers_files = request.files.getlist('readersFile[]')
    readers_annotations = request.form.getlist('readersFileAnnotation[]')
    readers_groups = request.form.getlist('readersGroup[]')
    boxplot_file = request.files.get('boxplotFile')
    
    # # Debug information
    # print(f"Name: {name}")
    # print(f"Analysis Name: {analysis_name}")
    # print(f"Analysis Type: {analysis_type}")
    # print(f"Average Files: {[file.filename for file in average_files]}")
    # print(average_files)
    # print(f"Average Annotation: {average_annotations}")
    # print(f"Readers Files: {[file.filename for file in readers_files]}")
    # print(readers_files)
    # print(f"Readers Annotation: {readers_annotations}")
    # print(f"Readers Groups: {readers_groups}")
    # print(f"Boxplot File: {boxplot_file.filename if boxplot_file else 'None'}")
    # print(boxplot_file)
    
    if not analysis_type:
        return "Analysis Type is required", 400

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(DATA_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'input'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'output'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'temp'), exist_ok=True)

    input_folder = os.path.join(job_dir, 'input')
    
    if analysis_type in ['average', 'both']:
        ave_folder = os.path.join(input_folder, 'ave')
        os.makedirs(ave_folder, exist_ok=True)
        for file in average_files:
            if file:
                file.save(os.path.join(ave_folder, file.filename))
    
    if analysis_type in ['reader', 'both']:
        reader_folder = os.path.join(input_folder, 'reader')
        os.makedirs(reader_folder, exist_ok=True)
        for file in readers_files:
            if file:
                file.save(os.path.join(reader_folder, file.filename))
    
    if boxplot_file:
        box_folder = os.path.join(input_folder, 'box')
        os.makedirs(box_folder, exist_ok=True)
        boxplot_file.save(os.path.join(box_folder, boxplot_file.filename))

    thread = Thread(target=process_files_and_update_log, args=(job_id, name, analysis_name, analysis_type, average_files, readers_files, boxplot_file, average_annotations, readers_annotations, readers_groups))
    thread.start()
    
    flash("Your job has been started successfully!", "success")
    
    return render_template('job_started.html')

@app.route('/job_status')
def job_status():
    """
    Display the status of all jobs.

    Returns:
        response: Renders the job_status.html page.
    """
    log_path = os.path.join(DATA_DIR, 'logfile.json')
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                log_data = []
    else:
        log_data = []

    return render_template('job_status.html', log_data=log_data)

@app.route('/job/<job_id>')
def job_details(job_id):
    """
    Display details of a specific job.

    Args:
        job_id (str): Job ID.

    Returns:
        response: Renders the job_details.html page.
    """
    job_dir = os.path.join(DATA_DIR, job_id)
    output_dir = os.path.join(job_dir, 'output')
    tex_files = [f for f in os.listdir(output_dir) if f.endswith('.tex')]
    return render_template('job_details.html', job_id=job_id, tex_files=tex_files)

@app.route('/job_error/<job_id>')
def job_error(job_id):
    """
    Display error message for a specific job.

    Args:
        job_id (str): Job ID.

    Returns:
        response: Renders the job_error.html page.
    """
    log_path = os.path.join(DATA_DIR, 'logfile.json')
    error_message = "No error message available."
    
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            try:
                log_data = json.load(f)
                for job in log_data:
                    if job['job_id'] == job_id and job.get('status') == 'FAILED':
                        error_message = job.get('error_message', error_message)
                        break
            except json.JSONDecodeError:
                pass

    flash(error_message, 'danger')
    return render_template('job_error.html', job_id=job_id)

@app.route('/preview/<job_id>')
def preview(job_id):
    """
    Preview the TeX files generated for a specific job.

    Args:
        job_id (str): Job ID.

    Returns:
        response: Renders the preview.html page.
    """
    job_dir = os.path.join(DATA_DIR, job_id, 'output')
    tex_files = [f for f in os.listdir(job_dir) if f.endswith('.tex')]
    return render_template('preview.html', tex_files=tex_files, job_id=job_id)

@app.route('/static/tex_files/<job_id>/<filename>')
def serve_tex_file(job_id, filename):
    """
    Serve the TeX file for download.

    Args:
        job_id (str): Job ID.
        filename (str): Filename.

    Returns:
        file: The TeX file to be downloaded.
    """
    file_path = os.path.join(DATA_DIR, job_id, 'output', filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "File not found", 404

@app.route('/compile_tex', methods=['POST'])
def compile_tex():
    """
    Compile a TeX file into a PDF.

    Returns:
        json: Response message with the PDF URL or error message.
    """
    job_id = request.form.get('job_id')
    filename = request.form.get('filename')
    if not filename:
        return jsonify({'error': 'Filename not provided'}), 400

    tex_file_path = os.path.join(DATA_DIR, job_id, 'output', filename)
    if not os.path.exists(tex_file_path):
        return jsonify({'error': 'File not found'}), 404
    
    if filename in ['ROC_reader_image.tex', 'ROC_average_image.tex']:
        return jsonify({'error': 'Form is not supported, please use other methods to generate this file.'}), 400
    
    with open(tex_file_path, 'r') as file:
        lines = file.readlines()
        if len(lines) > 8000:
            return jsonify({'error': 'File too large, Please use other methods to generate PDF file.'}), 400
    pdf_file_path = tex_file_path.replace('.tex', '.pdf')

    laton_src_path = os.path.join(app.static_folder, 'laton')
    laton_dest_path = os.path.join(DATA_DIR, job_id, 'output', 'laton')
    try:
        shutil.copy(laton_src_path, laton_dest_path)
    except Exception as e:
        return jsonify({'error': 'Failed to copy laton file', 'details': str(e)}), 500

    try:
        working_dir = os.path.dirname(tex_file_path)
        os.chdir(working_dir)
        result = subprocess.run(['./laton', filename], capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({'error': 'Failed to compile TeX file', 'details': result.stderr}), 500
        return jsonify({'message': 'Compilation successful', 'pdf_url': url_for('serve_tex_file', job_id=job_id, filename=os.path.basename(pdf_file_path))})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Failed to compile TeX file', 'details': str(e)}), 500
    finally:
        os.chdir(app.root_path)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    Display and update application settings.

    Returns:
        response: Renders the settings.html page.
    """
    if request.method == 'POST':
        global DATA_DIR
        DATA_DIR = request.form.get('dataDir', DATA_DIR)
        os.makedirs(DATA_DIR, exist_ok=True)
        settings = {'data_dir': DATA_DIR}
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return redirect(url_for('settings'))
    return render_template('settings.html', data_dir=DATA_DIR)

@app.route('/save_settings', methods=['POST'])
def save_settings():
    """
    Save application settings.

    Returns:
        response: Redirects to the settings page.
    """
    global DATA_DIR
    DATA_DIR = request.form.get('dataDir', DATA_DIR)
    os.makedirs(DATA_DIR, exist_ok=True)
    settings = {'data_dir': DATA_DIR}
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)
    return redirect(url_for('settings'))

@app.route('/calculate_confidence', methods=['GET', 'POST'])
def calculate_confidence():
    if request.method == 'POST':
        # Handle form submission and calculations
        job_id = str(uuid.uuid4())
        job_dir = os.path.join(DATA_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)
        os.makedirs(os.path.join(job_dir, 'output'), exist_ok=True)
        os.makedirs(os.path.join(job_dir, 'temp'), exist_ok=True)
        
        # Extract form data
        fp = int(request.form['fp'])
        n_n = int(request.form['n_n'])
        tp = int(request.form['tp'])
        n_p = int(request.form['n_p'])
        alpha = [float(a) for a in request.form.getlist('alpha')]
        name = request.form['name']
        file_name = request.form['file_name']

        # Save the form data to a JSON file for later reference
        form_data = {
            'name': name,
            'analysis_name': file_name, 
            'analysis_type': 'confidence',
            'job_id': job_id,
            'fp': fp,
            'n_n': n_n,
            'tp': tp,
            'n_p': n_p,
            'alpha': alpha,
        }
        form_data_path = os.path.join(job_dir, 'temp', 'form_data.json')
        with open(form_data_path, 'w') as f:
            json.dump(form_data, f, indent=4)

        # Update the log file with the job entry
        log_entry = {
            'job_id': job_id,
            'analysis_name': file_name, 
            'analysis_type': 'confidence',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'PENDING'
        }
        log_path = os.path.join(DATA_DIR, 'logfile.json')
        
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except json.JSONDecodeError:
                    log_data = []
        else:
            log_data = []

        log_data.append(log_entry)
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=4)
        
        # Start the calculation as a background thread
        thread = Thread(target=process_confidence_job, args=(job_id, form_data))
        thread.start()
        
        flash("Your confidence interval calculation job has been started successfully!", "success")
        return redirect(url_for('job_status'))
    
    # If GET request, render the form
    return render_template('confidence_form.html')

@app.route('/confidence_result/<job_id>')
def confidence_result(job_id):
    """
    Display the confidence interval result for a specific job.

    Args:
        job_id (str): Job ID.

    Returns:
        response: Renders the confidence_result.html page.
    """
    job_dir = os.path.join(DATA_DIR, job_id)
    result_path = os.path.join(job_dir, 'output', 'result.json')

    if os.path.exists(result_path):
        with open(result_path, 'r') as f:
            result = json.load(f)
        
        # List generated TeX files in the output directory
        tex_files = [f for f in os.listdir(os.path.join(job_dir, 'output')) if f.endswith('.tex')]
        
        return render_template('confidence_result.html', result=result, tex_files=tex_files, job_id=job_id)
    else:
        flash('Result not found', 'danger')
        return redirect(url_for('job_status'))

def process_files_and_update_log(job_id, name, analysis_name, analysis_type, 
                                 average_files, readers_files, boxplot_file,
                                 average_annotations, readers_annotations, readers_groups,
                                 style_path=None):
    """
    Process uploaded files and update the log file.

    Args:
        job_id (str): Job ID.
        name (str): User's name.
        analysis_name (str): Analysis name.
        analysis_type (str): Type of analysis.
        average_files (list): List of average files.
        readers_files (list): List of readers files.
        boxplot_file (file): Boxplot file.
        average_annotations (list): List of average annotations.
        readers_annotations (list): List of readers annotations.
        readers_groups (list): List of readers groups.
        style_path (str): Path to styling file.

    Returns:
        None
    """
    job_dir = os.path.join(DATA_DIR, job_id)
  
    form_data = {
        'name': name,
        'analysis_name': analysis_name,
        'analysis_type': analysis_type,
        'job_id': job_id,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'average_files': [file.filename for file in average_files],
        'readers_files': [file.filename for file in readers_files],
        'boxplot_file': boxplot_file.filename if boxplot_file else None,
        'average_annotations': average_annotations,
        'readers_annotations': readers_annotations,
        'readers_groups': readers_groups,
        'style_path': style_path
    }
    with open(os.path.join(job_dir, 'temp', 'form_data.json'), 'w') as f:
        json.dump(form_data, f, indent=4)

    log_entry = {
        'job_id': job_id,
        'analysis_name': analysis_name,
        'analysis_type': analysis_type,
        'created_at': form_data['created_at'],
        'status': 'PENDING'
    }
    log_path = os.path.join(DATA_DIR, 'logfile.json')
    
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                log_data = []
    else:
        log_data = []

    log_data.append(log_entry)
    with open(log_path, 'w') as f:
        json.dump(log_data, f, indent=4)
    
    logging.info(f"Job created: {log_entry}")
    
    try:
        update_user_log_status(job_id, 'RUNNING')
        logging.info(f'Job {job_id} has been started!')

        if analysis_type == 'average':
            result = process_average_analysis(job_id, name, analysis_name, average_files, average_annotations, style_path)
        elif analysis_type == 'reader':
            result = process_reader_analysis(job_id, name, analysis_name, readers_files, readers_annotations, readers_groups, style_path)
        elif analysis_type == 'both':
            result = process_average_and_reader_analysis(job_id, name, analysis_name, average_files, readers_files, boxplot_file, average_annotations, readers_annotations, readers_groups, style_path)
        else:
            error_message = 'Unknown analysis type'
            update_user_log_status(job_id, 'FAILED', error_message=error_message)
            logging.error(f'Unknown analysis type: {analysis_type}')
            flash(error_message, 'danger')
            return
        
        update_user_log_status(job_id, 'COMPLETED')
        logging.info(f'Job {job_id} has been completed!')
    except Exception as e:
        error_message = str(e)
        update_user_log_status(job_id, 'FAILED', error_message=error_message)
        logging.error(f'Error processing analysis: {e}')
        flash(error_message, 'danger')

def update_user_log_status(job_id, status, error_message=None, analysis_name=None, analysis_type=None):
    """
    Update the status of a job in the log file.

    Args:
        job_id (str): Job ID.
        status (str): New status of the job.
        error_message (str, optional): Error message if the job failed.

    Returns:
        None
    """
    log_path = os.path.join(DATA_DIR, 'logfile.json')
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                log_data = []
    else:
        log_data = []

    for entry in log_data:
        if entry['job_id'] == job_id:
            entry['status'] = status
            if error_message:
                entry['error_message'] = error_message
            if analysis_name:
                entry['analysis_name'] = analysis_name
            if analysis_type:
                entry['analysis_type'] = analysis_type
            break

    with open(log_path, 'w') as f:
        json.dump(log_data, f, indent=4)
    
    logging.info(f'Updated job status: job_id={job_id}, status={status}, error_message={error_message}')

def update_user_log_file(user_log):
    log_path = os.path.join(DATA_DIR, 'logfile.json')
    
    # Read the existing log entries
    if os.path.exists(log_path):
        with open(log_path, 'r') as log_file:
            try:
                logs = json.load(log_file)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []
    
    # Check if the entry with the given job_id exists and update it if it does
    job_id = user_log['job_id']
    entry_exists = False
    updated_logs = []
    for log in logs:
        if log.strip():
            log_data = json.loads(log)
            if log_data['job_id'] == job_id:
                log_data.update(user_log)
                entry_exists = True
            updated_logs.append(json.dumps(log_data))
    
    # Add the new entry if it doesn't exist
    if not entry_exists:
        updated_logs.append(json.dumps(user_log))
    
    # Write the updated log entries back to the file
    with open(log_path, 'w') as log_file:
        log_file.write("\n".join(updated_logs) + "\n")

def process_average_analysis(job_id, author_name, analysis_name, average_files, average_annotations, style=None):
    """
    Process average analysis.

    Args:
        job_id (str): Job ID.
        author_name (str): Author name.
        analysis_name (str): Analysis name.
        average_files (list): List of average files.
        average_annotations (list): List of average annotations.
        style (str, optional): Path to styling file.

    Returns:
        tuple: Paths and annotations of average files.
    """
    job_dir = os.path.join(DATA_DIR, job_id)
    input_folder = os.path.join(job_dir, 'input')
    output_folder = os.path.join(job_dir, 'output')
    style_folder = os.path.join(job_dir, 'style')
    
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(style_folder, exist_ok=True)
    
    ave_folder = os.path.join(input_folder, 'ave')
    average_paths = [os.path.join(ave_folder, file.filename) for file in average_files]

    generator = LaTeXROCAveGenerator()
    logging.info(f"Parsing Excel files {[file.filename for file in average_files]} with LaTeXROCAveGenerator engine")
    
    generator.parse_ave_files(average_paths, average_annotations)
    
    if author_name:
        generator.set_header_info(author=author_name)
    if analysis_name:
         generator.set_header_info(name=analysis_name)
    
    if style:
        generator.import_ave_settings(style)

    export_file_path = os.path.join(style_folder, 'average_settings.json')
    with open(export_file_path, 'w') as file:
        json.dump(generator.export_ave_settings(), file, indent=4)
    
    latex_document = generator.generate_latex_document()
    doc_file_path = os.path.join(output_folder, 'ROC_average_analysis.tex')
    with open(doc_file_path, 'w') as f:
        f.write(latex_document)
        
    latex_image = generator.generate_latex_image()
    doc_file_path = os.path.join(output_folder, 'ROC_average_image.tex')
    with open(doc_file_path, 'w') as f:
        f.write(latex_image)
        
    return average_paths, average_annotations

def process_reader_analysis(job_id, author_name, analysis_name, readers_files, readers_annotations, readers_groups, style=None):
    """
    Process reader analysis.

    Args:
        job_id (str): Job ID.
        author_name (str): Author name.
        analysis_name (str): Analysis name.
        readers_files (list): List of readers files.
        readers_annotations (list): List of readers annotations.
        readers_groups (list): List of readers groups.
        style (str, optional): Path to styling file.

    Returns:
        tuple: Paths, type names, and group names of reader files.
    """
    job_dir = os.path.join(DATA_DIR, job_id)
    input_folder = os.path.join(job_dir, 'input')
    output_folder = os.path.join(job_dir, 'output')
    style_folder = os.path.join(job_dir, 'style')
    
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(style_folder, exist_ok=True)
    
    reader_folder = os.path.join(input_folder, 'reader')
    
    grouped_files = {}
    grouped_annotations = {}
    
    for file, annotation, group in zip(readers_files, readers_annotations, readers_groups):
        if group not in grouped_files:
            grouped_files[group] = []
            grouped_annotations[group] = []
        grouped_files[group].append(file)
        grouped_annotations[group].append(annotation)
    
    reader_paths = []
    group_names = []
    type_names = list(grouped_files.keys())
    
    for group in type_names:
        files = grouped_files[group]
        annotations = grouped_annotations[group]
        
        reader_file_paths = [os.path.join(reader_folder, file.filename) for file in files]
        reader_paths.append(reader_file_paths)
        group_names.append(annotations)
        
    if not reader_paths:
        logging.error("No reader paths provided for analysis.")
        return [], [], []
        
    generator = LaTeXROCReaderGenerator()
    
    logging.info(f"Parsing Excel files {reader_paths} with LaTeXROCReaderGenerator engine")
    generator.parse_reader_files(reader_paths, type_names=type_names, group_names=group_names)
    
    if author_name:
        generator.set_header_info(author=author_name)
    if analysis_name:
        generator.set_header_info(name=analysis_name)
    
    generator.set_plot_format(legend_style={"at": "{(0.4,0.3)}"})
    generator.set_plot_format(x_ticklabels= "{,,}", y_ticklabels= "{,,}")
    
    if style:
        generator.import_reader_settings(style)

    export_file_path = os.path.join(style_folder, 'reader_settings.json')
    with open(export_file_path, 'w') as file:
        json.dump(generator.export_reader_settings(), file, indent=4)
    
    latex_document = generator.generate_latex_document()
    doc_file_path = os.path.join(output_folder, 'ROC_reader_analysis.tex')
    with open(doc_file_path, 'w') as f:
        f.write(latex_document)
        
    latex_image = generator.generate_latex_image()
    image_file_path = os.path.join(output_folder, 'ROC_reader_image.tex')
    with open(image_file_path, 'w') as f:
        f.write(latex_image)
        
    return reader_paths, type_names, group_names

def process_average_and_reader_analysis(job_id, author_name, analysis_name, average_files, readers_files, boxplot_file, average_annotations, readers_annotations, readers_groups, style=None):
    """
    Process both average and reader analysis.

    Args:
        job_id (str): Job ID.
        author_name (str): Author name.
        analysis_name (str): Analysis name.
        average_files (list): List of average files.
        readers_files (list): List of readers files.
        boxplot_file (file): Boxplot file.
        average_annotations (list): List of average annotations.
        readers_annotations (list): List of readers annotations.
        readers_groups (list): List of readers groups.
        style (str, optional): Path to styling file.

    Returns:
        None
    """
    job_dir = os.path.join(DATA_DIR, job_id)
    input_folder = os.path.join(job_dir, 'input')
    output_folder = os.path.join(job_dir, 'output')
    style_folder = os.path.join(job_dir, 'style')
    temp_folder = os.path.join(job_dir, 'temp')
    
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(style_folder, exist_ok=True)
    
    box_folder = os.path.join(input_folder, 'box')
    
    settings = {
        "ave": {},
        "reader": {},
        "readerave": {},
        "box": {},
    }
    
    if style:
        with open(style, 'r') as file:
            settings = json.load(file)
    
    average_paths, average_annotations = process_average_analysis(job_id, author_name, analysis_name, average_files, average_annotations, style=settings['ave'])
    reader_paths, type_names, group_names = process_reader_analysis(job_id, author_name, analysis_name, readers_files, readers_annotations, readers_groups, style=settings['reader'])
    
    os.remove(os.path.join(style_folder, 'average_settings.json'))
    os.remove(os.path.join(style_folder, 'reader_settings.json'))
    
    readerave_generator = LaTeXROCReaderAveGenerator()
    readerave_generator.parse_readerave_files(average_paths, reader_paths, ave_names=average_annotations, type_names=type_names, group_names=group_names)
    
    if author_name:
        readerave_generator.set_header_info(author=author_name)
    if analysis_name:
        readerave_generator.set_header_info(name=analysis_name)
        
    if style:
        readerave_generator.import_readerave_settings(settings['readerave'])
    
    latex_document = readerave_generator.generate_latex_document()
    doc_file_path = os.path.join(output_folder, 'ROC_reader_ave_analysis.tex')
    with open(doc_file_path, 'w') as f:
        f.write(latex_document)

    latex_image = readerave_generator.generate_latex_image()
    image_file_path = os.path.join(output_folder, 'ROC_reader_ave_image.tex')
    with open(image_file_path, 'w') as f:
        f.write(latex_image)
    
    box_path = None
    if boxplot_file:
        box_path = os.path.join(box_folder, boxplot_file.filename)
        
        box_generator = LaTeXROCBoxGenerator()
        box_generator.parse_box_file(box_path)
        
        if author_name:
            box_generator.set_header_info(author=author_name)
        if analysis_name:
            box_generator.set_header_info(name=analysis_name)
        
        if style:
            box_generator.import_confidence_settings(style['box'])
         
        box_latex_document = box_generator.generate_latex_document()
        box_doc_file_path = os.path.join(output_folder, 'ROC_box_analysis.tex')
        with open(box_doc_file_path, 'w') as file:
            file.write(box_latex_document)
            
        box_image_file_path = os.path.join(output_folder, 'ROC_reader_ave_image.tex')
        box_image_document = box_generator.generate_latex_image()
        with open(box_image_file_path, 'w') as file:
            file.write(box_image_document)
        
    full_generator = LaTeXROCReport()
    full_generator.setup(box_file=box_path, ave_files=average_paths, reader_files=reader_paths, ave_names=average_annotations, type_names=type_names, group_names=group_names)
        
    if style:
        full_generator.import_all_settings(style)
    
    settings = full_generator.export_all_settings()
        
    all_settings_path = os.path.join(style_folder, 'all_settings.json')
    with open(all_settings_path, 'w') as file:
        json.dump(settings, file, indent=4)
        
    full_file_path = os.path.join(output_folder, 'ROC_full_analysis.tex')
    latex_document = full_generator.generate_latex_document()
    with open(full_file_path, 'w') as f:
        f.write(latex_document)

def process_confidence_job(job_id, form_data, style=None):
    job_dir = os.path.join(DATA_DIR, job_id)
    output_folder = os.path.join(job_dir, 'output')
    style_folder = os.path.join(job_dir, 'style')
    
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(style_folder, exist_ok=True)

    try:
        update_user_log_status(job_id, 'RUNNING')
        logging.info(f'Confidence interval job {job_id} has been started!')

        ci_calculator = CI()
        alphas = form_data['alpha']  
        fpf_ci = ci_calculator.cal(x=form_data['fp'], n=form_data['n_n'], alpha=alphas)
        tpf_ci = ci_calculator.cal(x=form_data['tp'], n=form_data['n_p'], alpha=alphas)

        result = {
            'fpf_mle': fpf_ci['mle'],
            'tpf_mle': tpf_ci['mle'],
            'confidence_intervals': {}
        }
        
        for alpha in alphas:
            result['confidence_intervals'][str(alpha)] = {
                'fpf_lower': fpf_ci['CI'][alpha]['L'],
                'fpf_upper': fpf_ci['CI'][alpha]['R'],
                'tpf_lower': tpf_ci['CI'][alpha]['L'],
                'tpf_upper': tpf_ci['CI'][alpha]['R'],
                'confidence_level': (1 - alpha) * 100
            }

        result_path = os.path.join(output_folder, 'result.json')
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=4)

        generator = LaTeXConfidenceGenerator()
        cg2 = CG2()
        
        fp = form_data['fp']
        tp = form_data['tp']
        n_n = form_data['n_n']
        n_p = form_data['n_p']
        dx = 0.001
        dy = 0.001
        
        tex = {'dir': output_folder, 'CR_data': 'cg2_CR_results'}
    
        esmt = cg2.cal(fp=fp, n_n=n_n, tp=tp, n_p=n_p, alpha=alphas, dx=dx, dy=dy, FPF=None, TPF=None, tex=tex, verbose=True, CI=ci_calculator)

        data_file_path = os.path.join(tex['dir'], f"{tex['CR_data']}.{fp}_{n_n}.{tp}_{n_p}")
        with open(data_file_path, 'r') as file:
            data = file.read()

        print(alphas)
        generator.set_confidence_data(
            fp=fp, n_n=n_n, tp=tp, n_p=n_p, alpha=alphas, data=data
        )
        
        generator.set_header_info(
            name=form_data['analysis_name'], 
            author=form_data['name']
        )

        if style and isinstance(style, str):
            with open(style, 'r') as file:
                style = json.load(file)

        if style:
            generator.import_confidence_settings(style)
        
        export_file_path = os.path.join(style_folder, 'confidence_settings.json')
        with open(export_file_path, 'w') as file:
            json.dump(generator.export_confidence_settings(), file, indent=4)
            
        latex_document = generator.generate_latex_document()
        latex_file_path = os.path.join(output_folder, 'ROC_confidence_analysis.tex')
        with open(latex_file_path, 'w') as f:
            f.write(latex_document)

        image_document = generator.generate_latex_document()
        image_file_path = os.path.join(output_folder, 'ROC_confidence_image.tex')
        with open(image_file_path, 'w') as f:
            f.write(image_document)
            
        update_user_log_status(job_id, 'COMPLETED')
        logging.info(f'Confidence interval job {job_id} has been completed successfully!')

    except Exception as e:
        error_message = str(e)
        update_user_log_status(job_id, 'FAILED', error_message=error_message, analysis_name='Confidence Interval Calculation', analysis_type='confidence')
        logging.error(f'Error processing confidence interval job: {e}')

if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    app.run(debug=True)
