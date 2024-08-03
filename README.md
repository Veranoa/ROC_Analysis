
# ROC_Analysis

**[This analysis tool is still in development.]**

This software is designed to handle the uploading, processing, and analysis of ROC data. It supports various types of ROC analysis, including average, reader, and combined analyses. The application also allows users to download styling files and rerun analyses with updated styling.

## Features

- **Average Analysis**: Process and analyze average ROC data.
- **Reader Analysis**: Handle ROC data from multiple readers.
- **Combined Analysis**: Integrate both average and reader data for comprehensive analysis.
- **Styling Customization**: Download and upload styling settings to customize your analysis outputs.
- **Job Management**: Track and manage your analysis jobs, including rerunning jobs with updated settings.

## Requirements

- Python 3.6 or higher
- Flask
- pandas
- openpyxl
- json
- subprocess
- threading
- werkzeug

## Installation

The software is available as an install package for MacOS and Windows.

### MacOS and Windows

1. Clone the repository or download the package.
2. Navigate to the folder containing the project files:

   ```bash
   cd [path to this folder]
   ```
3. Install the required packages:

   ```bash
   pip install -r static/requirements.txt
   ```
4. Run the application:

   ```bash
   python app.py
   ```

## Usage

Once the application is running, open your web browser and navigate to `http://localhost:5000` to access the ROC Analysis tool.

### Home Page

- The home page provides an overview of the application and its features.

### Plotting Page

- The plotting page allows you to upload data files and generate ROC plots.

### Analysis Page

- The analysis page enables you to submit new analysis jobs and manage existing ones.

### Styling Page

- The styling page lets you download and upload styling files to customize your analysis outputs.

### Job Status Page

- The job status page displays the status of all your analysis jobs, including pending, running, and completed jobs.

## File Structure

- `app.py`: Main application file.
- `config.py`: Configuration settings for the application.
- `templates/`: HTML templates for rendering web pages.
- `static/`: Static files including CSS, JavaScript, and images.
- `logs/`: Directory for storing log files.
- `data/`: Directory for storing user data and job files.

## Troubleshooting

If you encounter any issues, please check the following:

- Ensure all required packages are installed.
- Verify that you are using Python 3.6 or higher.
- Check the `logs/` directory for error messages.

For further assistance, please contact the development team or submit an issue on the project's GitHub repository.

## Contributing

We welcome contributions to the ROC Analysis project. To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

Special thanks to the University of Chicago for supporting the development of this tool.

---

**Developed by Yun Liu**
University of Chicago
2024-2030
