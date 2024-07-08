from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import os
import json
import shutil
import uuid
from datetime import datetime
import subprocess
from threading import Thread

# from ROCAveGenerator import LaTeXROCAveGenerator
# from ROCReaderGenerator import LaTeXROCReaderGenerator 
# from ROCReaderAveGenerator import LaTeXROCReaderAveGenerator

# logging.basicConfig(filename=os.path.join(Config.APP_LOG_FOLDER, 'server.log'), level=logging.INFO,
#                     format='%(asctime)s %(levelname)s:%(message)s')

app = Flask(__name__)

DATA_DIR = 'Data/User'
os.makedirs(DATA_DIR, exist_ok=True)

# Load settings if they exist
SETTINGS_FILE = 'settings.json'
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, 'r') as f:
        settings = json.load(f)
        DATA_DIR = settings.get('data_dir', DATA_DIR)
        
OUTPUT_TEX_DIR = 'output_tex_files'

@app.route('/')
def upload():
    return render_template('upload.html')


@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    name = request.form.get('name', 'Unnamed')
    analysis_name = request.form.get('analysisName', 'Unnamed Analysis')
    analysis_type = request.form.get('analysisType')
    average_files = None
    readers_files = None
    boxplot_file = None
    
    if not analysis_type:
        return "Analysis Type is required", 400

    # Create a unique Job ID
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(DATA_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'input'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'output'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'temp'), exist_ok=True)  # Ensure the temp directory exists

    # Save uploaded files
    if analysis_type in ['average', 'both']:
        average_files = request.files.getlist('averageFile[]')
        for file in average_files:
            if file:
                file.save(os.path.join(job_dir, 'input', file.filename))
    
    if analysis_type in ['reader', 'both']:
        readers_files = request.files.getlist('readersFile[]')
        for file in readers_files:
            if file:
                file.save(os.path.join(job_dir, 'input', file.filename))
    
    boxplot_file = request.files.get('boxplotFile')
    if analysis_type == 'both' and boxplot_file:
        boxplot_file.save(os.path.join(job_dir, 'input', boxplot_file.filename))

    # Use a background thread to process the files and update the log
    thread = Thread(target=process_files_and_update_log, args=(job_id, name, analysis_name, analysis_type))
    thread.start()
    
    print(name, analysis_name, analysis_type, average_files, readers_files, boxplot_file)

    # update_user_log_status(job_id, 'RUNNING')
    # logging.info(f'Job {job_id} has been started!')

    # result = None
    
    # try:
    #     if analysis_type == 'Average Analysis':
    #         avef_files, avef_names, result = process_average_analysis(df, input_folder, output_folder, user_log, user_name)
    #     elif analysis_type == 'Reader Analysis':
    #         reader_files, type_names, group_names,result = process_reader_analysis(df, input_folder, output_folder, user_log, user_name)
    #     elif analysis_type == 'Average and Reader Analysis':
    #         result = process_average_and_reader_analysis(df, input_folder, output_folder, user_log, user_name)
    #     else:
    #         update_user_log_status(job_id, 'FAILED')
    #         logging.error(f'Unknown analysis type: {analysis_type}')
    #         return jsonify({'error': 'Unknown analysis type'}), 400
    # except Exception as e:
    #     update_user_log_status(job_id, 'FAILED')
    #     logging.error(f'Error processing analysis: {e}')
    #     return jsonify({'error': str(e)}), 400
    
    # update_user_log_status(job_id, 'COMPLETED')
    # logging.info(f'Job {job_id} has been completed!')
    
    
    return redirect(url_for('job_status'))


@app.route('/job_status')
def job_status():
    log_path = os.path.join(DATA_DIR, 'logfile.json')
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log_data = json.load(f)
    else:
        log_data = []

    return render_template('job_status.html', log_data=log_data)


@app.route('/job/<job_id>')
def job_details(job_id):
    job_dir = os.path.join(DATA_DIR, job_id)
    output_dir = os.path.join(job_dir, 'output')
    tex_files = [f for f in os.listdir(output_dir) if f.endswith('.tex')]
    return render_template('job_details.html', job_id=job_id, tex_files=tex_files)


@app.route('/static/tex_files/<filename>')
def serve_tex_file(filename):
    return send_file(os.path.join(OUTPUT_TEX_DIR, filename))


@app.route('/preview')
def preview():
    tex_files = [f for f in os.listdir(OUTPUT_TEX_DIR) if f.endswith('.tex')]
    return render_template('preview.html', tex_files=tex_files)

@app.route('/compile_tex', methods=['POST'])
def compile_tex():
    filename = request.form.get('filename')
    if not filename:
        return jsonify({'error': 'Filename not provided'}), 400

    tex_file_path = os.path.join(OUTPUT_TEX_DIR, filename)
    if not os.path.exists(tex_file_path):
        return jsonify({'error': 'File not found'}), 404

    pdf_file_path = tex_file_path.replace('.tex', '.pdf')

    try:
        # Change to the working directory
        working_dir = os.path.dirname(tex_file_path)
        os.chdir(working_dir)
        result = subprocess.run(['/Users/summersane/Desktop/RA/Radiology/Example_plots_tex/ROC/ROC_Analysis/static/laton', filename], capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({'error': 'Failed to compile TeX file', 'details': result.stderr}), 500
        return jsonify({'message': 'Compilation successful', 'pdf_url': url_for('serve_tex_file', filename=os.path.basename(pdf_file_path))})
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


def process_files_and_update_log(job_id, name, analysis_name, analysis_type):
    job_dir = os.path.join(DATA_DIR, job_id)
  
    # Save form data as JSON
    form_data = {
        'name': name,
        'analysis_name': analysis_name,
        'analysis_type': analysis_type,
        'job_id': job_id,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'PENDING'
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
            log_data = json.load(f)
    else:
        log_data = []

    log_data.append(log_entry)
    with open(log_path, 'w') as f:
        json.dump(log_data, f)


# def process_average_analysis(df, input_folder, output_folder, user_log, user_name):
#     ave_folder = os.path.join(input_folder, 'ave')
#     os.makedirs(ave_folder, exist_ok=True)
#     ave_np_url = df['Nonparametric'].iloc[0]
#     ave_pbn_url = df['Proper-binormal'].iloc[0]
#     ave_np_path = os.path.join(ave_folder, os.path.basename(ave_np_url))
#     ave_pbn_path = os.path.join(ave_folder, os.path.basename(ave_pbn_url))
#     download_file(ave_np_url, ave_np_path)
#     download_file(ave_pbn_url, ave_pbn_path)
#     user_log['ave'] = {'NP': ave_np_path, 'PBN': ave_pbn_path}
    
#     update_user_log_file(user_log)
    
#     group_files = [ave_np_path, ave_pbn_path]
#     group_names=["NP", "PBN"]
#     generator = LaTeXROCAveGenerator()
    
#     logging.info(f"Parsing Excel files {group_files} with openpyxl engine")

#     generator.parse_ave_files(group_files, avef_names=group_names)
#     generator.set_header_info(author=user_name)

#     latex_document = generator.generate_latex_document()
#     doc_file_path = os.path.join(output_folder, 'ROC_ave_analysis.tex')
#     with open(doc_file_path, 'w') as f:
#         f.write(latex_document)

#     image_document = generator.generate_latex_image()
#     image_file_path = os.path.join(output_folder, 'ROC_ave_image.tex')
#     with open(image_file_path, 'w') as f:
#         f.write(image_document)
    
#     update_user_log_file(user_log)
    
#     result = {
#         'status': 'COMPLETED',
#         'latex_file': doc_file_path,
#         'image_file': image_file_path
#     }
#     return group_files, group_names, result

# def process_reader_analysis(df, input_folder, output_folder, user_log, user_name):
#     reader_folder = os.path.join(input_folder, 'reader')
#     os.makedirs(reader_folder, exist_ok=True)
    
#     try:
#         reader_np_urls = df['Nonparametric.1'].dropna().astype(str).str.split('<br/>\r\n').tolist()[0]
#         reader_pbn_urls = df['Proper-binormal.1'].dropna().astype(str).str.split('<br/>\r\n').tolist()[0]
#     except IndexError as e:
#         logging.error(f"Error accessing DataFrame rows: {e}")
#         return {"error": "Error accessing DataFrame rows"}

#     user_log['reader'] = {'NP': [], 'PBN': []}
    
#     np_paths = []
#     pbn_paths = []

#     for np_url in reader_np_urls:
#         np_path = os.path.join(reader_folder, os.path.basename(np_url))
#         try:
#             download_file(np_url, np_path)
#             user_log['reader']['NP'].append(np_path)
#             np_paths.append(np_path)
#         except Exception as e:
#             logging.error(f"Error downloading NP file from {np_url}: {e}")

#     for pbn_url in reader_pbn_urls:
#         pbn_path = os.path.join(reader_folder, os.path.basename(pbn_url))
#         try:
#             download_file(pbn_url, pbn_path)
#             user_log['reader']['PBN'].append(pbn_path)
#             pbn_paths.append(pbn_path)
#         except Exception as e:
#             logging.error(f"Error downloading PBN file from {pbn_url}: {e}")

#     update_user_log_file(user_log)
    
#     # Use LaTeXROCReaderGenerator to process the files
#     generator = LaTeXROCReaderGenerator()
#     reader_files = [np_paths, pbn_paths]
#     type_names = ["t", "p"]
#     group_names = [["QR", "MR"], ["QR", "MR"]]    

#     logging.info(f"Parsing Excel files {reader_files} with openpyxl engine")
#     generator.parse_reader_files(reader_files, type_names=type_names, group_names=group_names)
#     generator.set_header_info(author=user_name)
    
#     generator.set_plot_format(legend_style={"at": "{(0.4,0.3)}"})
#     generator.set_plot_format(x_ticklabels= "{,,}", y_ticklabels= "{,,}")
#     generator.set_header_info(name="ROC Reader Analysis")

#     latex_document = generator.generate_latex_document()
#     doc_file_path = os.path.join(output_folder, 'ROC_reader_analysis.tex')
#     with open(doc_file_path, 'w') as f:
#         f.write(latex_document)

#     image = generator.generate_image_document()
#     image_file_path = os.path.join(output_folder, 'ROC_reader_image.tex')
#     with open(image_file_path, 'w') as f:
#         f.write(image)
        
#     result = {
#         'status': 'COMPLETED',
#         'reader_files': user_log['reader']
#     }
    
#     return reader_files, type_names, group_names, result

# def process_average_and_reader_analysis(df, input_folder, output_folder, user_log, user_name):
#     avef_files, avef_names, result_average = process_average_analysis(df, input_folder, output_folder, user_log, user_name)
#     reader_files, type_names, group_names, result_reader = process_reader_analysis(df, input_folder, output_folder, user_log, user_name)
        
#     generator = LaTeXROCReaderAveGenerator()
#     generator.parse_readerave_files(avef_files, reader_files, ave_names=avef_names, type_names=type_names, group_names=group_names)

#     latex_document = generator.generate_latex_document()
#     doc_file_path = os.path.join(output_folder, 'ROC_reader_ave_analysis.tex')
#     with open(doc_file_path, 'w') as f:
#         f.write(latex_document)

#     image = generator.generate_image_document()
#     image_file_path = os.path.join(output_folder, 'ROC_reader_ave_image.tex')
#     with open(image_file_path, 'w') as f:
#         f.write(image)
        
#     return {
#         'average_result': result_average,
#         'reader_result': result_reader
#     }

def update_user_log_status(job_id, status):
    log_file_path = os.path.join(app.config['LOG_FOLDER'], 'user_log.txt')
    with open(log_file_path, 'r') as log_file:
        logs = log_file.readlines()
    with open(log_file_path, 'w') as log_file:
        for log in logs:
            if log.strip():
                log_data = json.loads(log)
                if log_data['job_id'] == job_id:
                    log_data['status'] = status
                log_file.write(json.dumps(log_data) + "\n")
                
def update_user_log_file(user_log):
    log_file_path = os.path.join(app.config['LOG_FOLDER'], 'user_log.txt')
    
    # Read the existing log entries
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            logs = log_file.readlines()
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
    with open(log_file_path, 'w') as log_file:
        log_file.write("\n".join(updated_logs) + "\n")


if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    app.run(debug=True)
