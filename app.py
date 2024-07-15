from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash
import os
import json
import shutil
import uuid
from datetime import datetime
import subprocess
from threading import Thread
import logging

from config import Config
from ROCAveGenerator import LaTeXROCAveGenerator
from ROCReaderGenerator import LaTeXROCReaderGenerator 
from ROCReaderAveGenerator import LaTeXROCReaderAveGenerator
from ROCBoxGenerator import LaTeXROCBoxGenerator
from ROCAllinOne import LaTeXROCReport
os.makedirs(Config.LOG_FOLDER, exist_ok=True)

DATA_DIR = Config.USER_FOLDER
os.makedirs(DATA_DIR, exist_ok=True)

# Load settings if they exist
SETTINGS_FILE = Config.SETTINGS_FILE
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, 'r') as f:
        settings = json.load(f)
        DATA_DIR = settings.get('data_dir', DATA_DIR)
        
OUTPUT_TEX_DIR = 'output_tex_files'

logging.basicConfig(filename=os.path.join(Config.LOG_FOLDER, 'server.log'), level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

app = Flask(__name__)
app.secret_key = 'e1221313479442f320168216451c78a2'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/plotting')
def plotting():
    return render_template('plotting.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
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

    # Create a unique Job ID
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(DATA_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'input'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'output'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'temp'), exist_ok=True)  # Ensure the temp directory exists

    input_folder = os.path.join(job_dir, 'input')
    
    # Save uploaded plotting files
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

    # Use a background thread to process the files and update the log
    thread = Thread(target=process_files_and_update_log, args=(job_id, name, analysis_name, analysis_type, average_files, readers_files, boxplot_file, average_annotations, readers_annotations, readers_groups))
    thread.start()
    
    flash("Your job has been started successfully!", "success")
    
    return render_template('job_started.html')

@app.route('/job_status')
def job_status():
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
    job_dir = os.path.join(DATA_DIR, job_id)
    output_dir = os.path.join(job_dir, 'output')
    tex_files = [f for f in os.listdir(output_dir) if f.endswith('.tex')]
    return render_template('job_details.html', job_id=job_id, tex_files=tex_files)

@app.route('/job_error/<job_id>')
def job_error(job_id):
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
    job_dir = os.path.join(DATA_DIR, job_id, 'output')
    tex_files = [f for f in os.listdir(job_dir) if f.endswith('.tex')]
    return render_template('preview.html', tex_files=tex_files, job_id=job_id)

@app.route('/static/tex_files/<job_id>/<filename>')
def serve_tex_file(job_id, filename):
    file_path = os.path.join(DATA_DIR, job_id, 'output', filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "File not found", 404

@app.route('/compile_tex', methods=['POST'])
def compile_tex():
    job_id = request.form.get('job_id')
    filename = request.form.get('filename')
    if not filename:
        return jsonify({'error': 'Filename not provided'}), 400

    tex_file_path = os.path.join(DATA_DIR, job_id, 'output', filename)
    if not os.path.exists(tex_file_path):
        return jsonify({'error': 'File not found'}), 404

    pdf_file_path = tex_file_path.replace('.tex', '.pdf')

    # Copy the static/laton file to the job_id/output directory
    laton_src_path = os.path.join(app.static_folder, 'laton')
    laton_dest_path = os.path.join(DATA_DIR, job_id, 'output', 'laton')
    try:
        shutil.copy(laton_src_path, laton_dest_path)
    except Exception as e:
        return jsonify({'error': 'Failed to copy laton file', 'details': str(e)}), 500

    try:
        # Change to the working directory
        working_dir = os.path.dirname(tex_file_path)
        os.chdir(working_dir)
        result = subprocess.run(['./laton', filename], capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({'error': 'Failed to compile TeX file', 'details': result.stderr}), 500
        return jsonify({'message': 'Compilation successful', 'pdf_url': url_for('serve_tex_file', job_id=job_id, filename=os.path.basename(pdf_file_path))})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Failed to compile TeX file', 'details': str(e)}), 500
    finally:
        # Change back to the original directory
        os.chdir(app.root_path)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        global DATA_DIR
        DATA_DIR = request.form.get('dataDir', DATA_DIR)
        os.makedirs(DATA_DIR, exist_ok=True)
        # Save settings
        settings = {'data_dir': DATA_DIR}
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
        return redirect(url_for('settings'))
    return render_template('settings.html', data_dir=DATA_DIR)

@app.route('/save_settings', methods=['POST'])
def save_settings():
    global DATA_DIR
    DATA_DIR = request.form.get('dataDir', DATA_DIR)
    os.makedirs(DATA_DIR, exist_ok=True)
    # Save settings
    settings = {'data_dir': DATA_DIR}
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)
    return redirect(url_for('settings'))

def process_files_and_update_log(job_id, name, analysis_name, analysis_type, 
                                 average_files, readers_files, boxplot_file,
                                 average_annotations, readers_annotations, readers_groups):
    job_dir = os.path.join(DATA_DIR, job_id)
  
    # Save form data as JSON
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
        'readers_groups': readers_groups
    }
    with open(os.path.join(job_dir, 'temp', 'form_data.json'), 'w') as f:
        json.dump(form_data, f)

    # Log job creation
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
        json.dump(log_data, f)
    
    logging.info(f"Job created: {log_entry}")
        
    # Start the analysis process
    try:
        update_user_log_status(job_id, 'RUNNING')
        logging.info(f'Job {job_id} has been started!')

        # Assuming you have these functions defined for your analysis
        if analysis_type == 'average':
            result = process_average_analysis(job_id, name, analysis_name, average_files, average_annotations)
        elif analysis_type == 'reader':
            result = process_reader_analysis(job_id, name, analysis_name, readers_files, readers_annotations, readers_groups)
        elif analysis_type == 'both':
            result = process_average_and_reader_analysis(job_id, name, analysis_name, average_files, readers_files, boxplot_file, average_annotations, readers_annotations, readers_groups)
        else:
            error_message = 'Unknown analysis type'
            update_user_log_status(job_id, 'FAILED', error_message=error_message)
            logging.error(f'Unknown analysis type: {analysis_type}')
            flash(error_message, 'danger')
            return
        
        update_user_log_status(job_id, 'COMPLETED')
        logging.info(f'Job {job_id} has been completed!')

        # Send email if needed (you can add email sending logic here)
    except Exception as e:
        error_message = str(e)
        update_user_log_status(job_id, 'FAILED', error_message=error_message)
        logging.error(f'Error processing analysis: {e}')
        flash(error_message, 'danger')


def update_user_log_status(job_id, status, error_message=None):
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
            break

    with open(log_path, 'w') as f:
        json.dump(log_data, f)
    
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

def process_average_analysis(job_id, author_name, analysis_name, average_files, average_annotations):
    job_dir = os.path.join(DATA_DIR, job_id)
    input_folder = os.path.join(job_dir, 'input')
    output_folder = os.path.join(job_dir, 'output')
    os.makedirs(output_folder, exist_ok=True)
    
    ave_folder = os.path.join(input_folder, 'ave')
    average_paths = [os.path.join(ave_folder, file.filename) for file in average_files]
        
    generator = LaTeXROCAveGenerator()
    logging.info(f"Parsing Excel files {[file.filename for file in average_files]} with LaTeXROCAveGenerator engine")
    
    generator.parse_ave_files(average_paths, average_annotations)
    
    if author_name:
        generator.set_header_info(author=author_name)
    if analysis_name:
         generator.set_header_info(name=analysis_name)
    
    latex_document = generator.generate_latex_document()
    doc_file_path = os.path.join(output_folder, 'ROC_average_analysis.tex')
    with open(doc_file_path, 'w') as f:
        f.write(latex_document)
        
    latex_image = generator.generate_latex_image()
    doc_file_path = os.path.join(output_folder, 'ROC_average_image.tex')
    with open(doc_file_path, 'w') as f:
        f.write(latex_image)
        
    return average_paths, average_annotations
        
        
def process_reader_analysis(job_id, author_name, analysis_name, readers_files, readers_annotations, readers_groups):
    job_dir = os.path.join(DATA_DIR, job_id)
    input_folder = os.path.join(job_dir, 'input')
    output_folder = os.path.join(job_dir, 'output')
    os.makedirs(output_folder, exist_ok=True)
    
    reader_folder = os.path.join(input_folder, 'reader')
    
    # Group the files and annotations by group
    grouped_files = {}
    grouped_annotations = {}
    
    for file, annotation, group in zip(readers_files, readers_annotations, readers_groups):
        if group not in grouped_files:
            grouped_files[group] = []
            grouped_annotations[group] = []
        grouped_files[group].append(file)
        grouped_annotations[group].append(annotation)
    
    # Prepare the inputs for the generator
    reader_paths = []
    group_names = []
    type_names = list(grouped_files.keys())
    
    for group in type_names:
        files = grouped_files[group]
        annotations = grouped_annotations[group]
        
        reader_file_paths = [os.path.join(reader_folder, file.filename) for file in files]
        reader_paths.append(reader_file_paths)
        group_names.append(annotations)
        
    # print(reader_paths)
    # print(group_names)
    # print(type_names)
    # Process the grouped files and annotations
    generator = LaTeXROCReaderGenerator()
    
    logging.info(f"Parsing Excel files {reader_paths} with LaTeXROCReaderGenerator engine")
    generator.parse_reader_files(reader_paths, type_names=type_names, group_names=group_names)
    
    if author_name:
        generator.set_header_info(author=author_name)
    if analysis_name:
         generator.set_header_info(name=analysis_name)
    
    generator.set_plot_format(legend_style={"at": "{(0.4,0.3)}"})
    generator.set_plot_format(x_ticklabels= "{,,}", y_ticklabels= "{,,}")
    
    latex_document = generator.generate_latex_document()
    doc_file_path = os.path.join(output_folder, 'ROC_reader_analysis.tex')
    with open(doc_file_path, 'w') as f:
        f.write(latex_document)
        
    latex_image = generator.generate_latex_image()
    image_file_path = os.path.join(output_folder, 'ROC_reader_image.tex')
    with open(image_file_path, 'w') as f:
        f.write(latex_image)
        
    return reader_paths, type_names, group_names


def process_average_and_reader_analysis(job_id, author_name, analysis_name, average_files, readers_files, boxplot_file, average_annotations, readers_annotations, readers_groups):
    job_dir = os.path.join(DATA_DIR, job_id)
    input_folder = os.path.join(job_dir, 'input')
    output_folder = os.path.join(job_dir, 'output')
    os.makedirs(output_folder, exist_ok=True)
    
    box_folder = os.path.join(input_folder, 'box')
    
    average_paths, average_annotations = process_average_analysis(job_id, author_name, analysis_name, average_files, average_annotations)
    reader_paths, type_names, group_names = process_reader_analysis(job_id, author_name, analysis_name, readers_files, readers_annotations, readers_groups)
    
    generator = LaTeXROCReaderAveGenerator()
    generator.parse_readerave_files(average_paths, reader_paths, ave_names=average_annotations, type_names=type_names, group_names=group_names)
    
    if author_name:
        generator.set_header_info(author=author_name)
    if analysis_name:
         generator.set_header_info(name=analysis_name)
         
    latex_document = generator.generate_latex_document()
    doc_file_path = os.path.join(output_folder, 'ROC_reader_ave_analysis.tex')
    with open(doc_file_path, 'w') as f:
        f.write(latex_document)

    latex_image = generator.generate_image_document()
    image_file_path = os.path.join(output_folder, 'ROC_reader_ave_image.tex')
    with open(image_file_path, 'w') as f:
        f.write(latex_image)
    
    if boxplot_file:
        box_path = os.path.join(box_folder, boxplot_file.filename)
        # print(box_path)
        
        box_generator = LaTeXROCBoxGenerator()
        box_generator.parse_box_file(box_path)  # Assuming your CSV data is in Data/bar.csv
        
        if author_name:
            box_generator.set_header_info(author=author_name)
        if analysis_name:
            box_generator.set_header_info(name=analysis_name)
         
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
        
        full_file_path = os.path.join(output_folder, 'ROC_full_analysis.tex')
        latex_document = generator.generate_latex_document()
        with open(full_file_path, 'w') as f:
            f.write(latex_document)

if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    app.run(debug=True)
