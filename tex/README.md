# **ROC Analysis and Confidence Interval Analysis Guide**

This guide provides an overview and usage instructions for generating LaTeX documents and images for visualizing ROC (Receiver Operating Characteristic) curves, AUC (Area Under Curve) data, and confidence intervals (CI) and credible regions (CR).

## **Sections:**

1. **ROC Analysis**
   - [LaTeXROCAveGenerator](#11-usage-guide-for-latexrocavegenerator)
   - [LaTeXROCReaderGenerator](#12-usage-guide-for-latexrocreadergenerator)
   - [LaTeXROCReaderAveGenerator](#13-usage-guide-for-latexrocreaderavegenerator)
   - [LaTeXROCBoxGenerator](#14-usage-guide-for-latexrocboxgenerator)
   - [LaTeXROCReport](#15-usage-guide-for-latexrocreport)

2. **Confidence Interval Analysis**
   - [LaTeXConfidenceGenerator](#21-usage-guide-for-latexconfidencegenerator)

---

### **Detailed Usage Guide for Each Subclass**

This section provides a comprehensive guide for each subclass, detailing their functions, usage scenarios, and example workflows. The classes are divided into two main categories: ROC Analysis and Confidence Interval Analysis.

## **1. ROC Analysis**

### **1.1. Usage Guide for `LaTeXROCAveGenerator`**

The `LaTeXROCAveGenerator` class is designed to generate LaTeX documents and commands to visualize ROC curves and AUC data from multiple Excel files. This class extends the `LaTeXGenerator` class and adds specific functionalities for handling ROC curve visualizations.

#### **Initialization**

To use the `LaTeXROCAveGenerator`, you need to initialize an instance of the class:

```python
generator = LaTeXROCAveGenerator()
```

#### **Key Methods and Their Usage**

1. **`parse_ave_files(group_files, ave_names=None, engine='openpyxl')`**:

   - Parses multiple Excel files to extract ROC data and organizes it into groups.
   - **Parameters**:
     - `group_files`: List of Excel file paths containing ROC data.
     - `ave_names`: Optional list of group names corresponding to each file.
     - `engine`: The Excel engine to use, default is `'openpyxl'`.
   - **Usage**:
     ```python
     ave_files = ["Data/NP_average.xlsx"]
     ave_names = ['NP']
     generator.parse_ave_files(ave_files, ave_names)
     ```
2. **`generate_latex_document()`**:

   - Generates a complete LaTeX document that contains all commands for plotting ROC curves.
   - **Returns**: A string representing the LaTeX document.
   - **Usage**:
     ```python
     latex_document = generator.generate_latex_document()
     with open('Output/ROC_average_analysis.tex', 'w') as f:
         f.write(latex_document)
     ```
3. **`generate_latex_image()`**:

   - Generates a LaTeX document for standalone images.
   - **Returns**: A string representing the LaTeX document for images.
   - **Usage**:
     ```python
     image_document = generator.generate_latex_image()
     with open('Output/ROC_average_image.tex', 'w') as f:
         f.write(image_document)
     ```
4. **`set_ave_colors(*colors)`**:

   - Sets the colors for ROC curves. Accepts a list or tuples of colors.
   - **Parameters**:
     - `colors`: A list or tuple representing RGB color values.
   - **Usage**:
     ```python
     generator.set_ave_colors("#FF0000", "#00FF00", "#0000FF")  # Example colors
     ```
5. **`generate_pdf(tex_file_path, output_dir)`**:

   - Compiles the LaTeX file into a PDF document.
   - **Parameters**:
     - `tex_file_path`: Path to the LaTeX file.
     - `output_dir`: Directory where the PDF will be saved.
   - **Usage**:
     ```python
     generator.generate_pdf('Output/ROC_average_analysis.tex', 'Output')
     ```
6. **`export_ave_settings()`**:

   - Exports the current settings for page format, plot format, and colors.
   - **Returns**: A dictionary containing the current settings.
   - **Usage**:
     ```python
     settings = generator.export_ave_settings()
     with open('Output/average_settings.json', 'w') as file:
         json.dump(settings, file, indent=4)
     ```
7. **`import_ave_settings(settings)`**:

   - Imports settings from a JSON file and applies them.
   - **Parameters**:
     - `settings`: A dictionary or a path to a JSON file containing settings.
   - **Usage**:
     ```python
     generator.import_ave_settings('Output/average_settings.json')
     ```
8. **`update_group_names(new_group_names)`**:

   - Updates the names of the ROC groups.
   - **Parameters**:
     - `new_group_names`: A list of new names for the ROC groups.
   - **Usage**:
     ```python
     generator.update_group_names(['NewGroupName1', 'NewGroupName2'])
     ```

#### **Example Workflow**

Below is a simple example workflow to generate ROC curve plots:

```python
# Initialize generator
generator = LaTeXROCAveGenerator()

# Parse Excel files containing ROC data
ave_files = ["Data/NP_average.xlsx"]
ave_names = ['NP']
generator.parse_ave_files(ave_files, ave_names)

# Set custom colors (optional)
generator.set_ave_colors("#FF0000", "#00FF00", "#0000FF")

# Generate LaTeX document and save to file
latex_document = generator.generate_latex_document()
doc_file_path = 'Output/ROC_average_analysis.tex'
with open(doc_file_path, 'w') as f:
    f.write(latex_document)

# Generate standalone image LaTeX document and save to file
image_document = generator.generate_latex_image()
image_file_path = 'Output/ROC_average_image.tex'
with open(image_file_path, 'w') as f:
    f.write(image_document)

# Compile LaTeX document to PDF
generator.generate_pdf(doc_file_path, 'Output')

# Export settings to JSON
settings = generator.export_ave_settings()
with open('Output/average_settings.json', 'w') as file:
    json.dump(settings, file, indent=4)

# Import settings from JSON (optional)
generator.import_ave_settings('Output/average_settings.json')
```

#### **Error Handling**

- The script includes error handling for file not found or incorrect file types.
- Ensure that all necessary files exist and are accessible before running the script.
- Pay attention to LaTeX compilation errors which may arise due to incorrect or missing commands in the generated LaTeX document.

By following this guide, you can effectively use the `LaTeXROCAveGenerator` class to create detailed ROC curve visualizations in LaTeX.

### **1.2. Usage Guide for `LaTeXROCReaderGenerator`**

The `LaTeXROCReaderGenerator` class generates LaTeX documents and commands to visualize ROC curves for different readers or methods. It extends the `LaTeXROCAveGenerator` to handle multiple files and plot multiple ROC curves for comparison.

#### **Initialization**

To use the `LaTeXROCReaderGenerator`, initialize an instance:

```python
generator = LaTeXROCReaderGenerator()
```

#### **Key Methods and Their Usage**

1. **`parse_reader_files(reader_files, type_names=None, group_names=None, engine='openpyxl')`**:

   - Parses multiple Excel files for different readers/methods to extract ROC data.
   - **Parameters**:
     - `reader_files`: List of lists, each containing Excel file paths for a specific reader/method.
     - `type_names`: Optional list of names for each reader/method type.
     - `group_names`: Optional list of lists, each containing group names for the corresponding reader files.
     - `engine`: The Excel engine to use, default is `'openpyxl'`.
   - **Usage**:
     ```python
     reader_files = [
         ["Data/QR_t_Data.xlsx", "Data/MR_t_Data.xlsx"],
         ["Data/QR_p_Data.xlsx", "Data/MR_p_Data.xlsx"]
     ]
     type_names = ["t", "p"]
     group_names = [["QR", "MR"], ["QR", "MR"]]
     generator.parse_reader_files(reader_files, type_names, group_names)
     ```
2. **`generate_latex_document()`**:

   - Generates a complete LaTeX document for plotting ROC curves.
   - **Returns**: A string representing the LaTeX document.
   - **Usage**:
     ```python
     latex_document = generator.generate_latex_document()
     with open('Output/ROC_reader_analysis.tex', 'w') as f:
         f.write(latex_document)
     ```
3. **`generate_latex_image()`**:

   - Generates a LaTeX document for standalone ROC images.
   - **Returns**: A string representing the LaTeX document for images.
   - **Usage**:
     ```python
     image_document = generator.generate_latex_image()
     with open('Output/ROC_reader_image.tex', 'w') as f:
         f.write(image_document)
     ```
4. **`

set_plot_format(**kwargs)`**:

   - Sets the plot format options such as color, legend style, tick labels, etc.
   - **Parameters**:
     - `**kwargs`: Key-value pairs for different plot settings.
   - **Usage**:
     ```python
     generator.set_plot_format(legend_style={"at": "{(0.4,0.3)}"}, tick_style={"draw": "red"})
     ```
5. **`export_reader_settings()`**:

   - Exports the current settings for page format and plot format.
   - **Returns**: A dictionary containing the current settings.
   - **Usage**:
     ```python
     settings = generator.export_reader_settings()
     with open('Output/reader_settings.json', 'w') as file:
         json.dump(settings, file, indent=4)
     ```
6. **`import_reader_settings(settings)`**:

   - Imports settings from a JSON file and applies them.
   - **Parameters**:
     - `settings`: A dictionary or a path to a JSON file containing settings.
   - **Usage**:
     ```python
     generator.import_reader_settings('Output/reader_settings.json')
     ```

#### **Example Workflow**

```python
# Initialize generator
generator = LaTeXROCReaderGenerator()

# Parse Excel files for different readers/methods
reader_files = [
    ["Data/QR_t_Data.xlsx", "Data/MR_t_Data.xlsx"],
    ["Data/QR_p_Data.xlsx", "Data/MR_p_Data.xlsx"]
]
type_names = ["t", "p"]
group_names = [["QR", "MR"], ["QR", "MR"]]
generator.parse_reader_files(reader_files, type_names, group_names)

# Set custom plot format (optional)
generator.set_plot_format(legend_style={"at": "{(0.4,0.3)}"}, tick_style={"draw": "red"})

# Generate LaTeX document and save to file
latex_document = generator.generate_latex_document()
doc_file_path = 'Output/ROC_reader_analysis.tex'
with open(doc_file_path, 'w') as f:
    f.write(latex_document)

# Generate standalone image LaTeX document and save to file
image_document = generator.generate_latex_image()
image_file_path = 'Output/ROC_reader_image.tex'
with open(image_file_path, 'w') as f:
    f.write(image_document)

# Compile LaTeX document to PDF
generator.generate_pdf(doc_file_path, 'Output')

# Export settings to JSON
settings = generator.export_reader_settings()
with open('Output/reader_settings.json', 'w') as file:
    json.dump(settings, file, indent=4)

# Import settings from JSON (optional)
generator.import_reader_settings('Output/reader_settings.json')
```

#### **Error Handling**

- Ensure that all Excel files exist and are formatted correctly.
- Check the LaTeX document for any missing or incorrect commands that could cause compilation errors.

### **1.3. Usage Guide for `LaTeXROCReaderAveGenerator`**

The `LaTeXROCReaderAveGenerator` class combines functionalities of `LaTeXROCAveGenerator` and `LaTeXROCReaderGenerator` to generate ROC curves for both averages and different readers/methods.

#### **Initialization**

To use the `LaTeXROCReaderAveGenerator`, initialize an instance:

```python
generator = LaTeXROCReaderAveGenerator()
```

#### **Key Methods and Their Usage**

1. **`parse_readerave_files(ave_files, reader_files, ave_names=None, type_names=None, group_names=None)`**:

   - Parses both average and reader files to extract ROC data.
   - **Parameters**:
     - `ave_files`: List of Excel file paths for average ROC data.
     - `reader_files`: List of lists, each containing Excel file paths for reader ROC data.
     - `ave_names`: Optional list of group names for averages.
     - `type_names`: Optional list of names for each reader/method type.
     - `group_names`: Optional list of lists, each containing group names for the corresponding reader files.
   - **Usage**:
     ```python
     ave_files = ["Data/NP_average.xlsx", "Data/PBN_average.xlsx"]
     reader_files = [
         ["Data/QR_t_Data.xlsx", "Data/MR_t_Data.xlsx"],
         ["Data/QR_p_Data.xlsx", "Data/MR_p_Data.xlsx"]
     ]
     ave_names = ['NP', 'PBN']
     type_names = ["t", "p"]
     group_names = [["QR", "MR"], ["QR", "MR"]]
     generator.parse_readerave_files(ave_files, reader_files, ave_names, type_names, group_names)
     ```
2. **`generate_latex_document()`**:

   - Generates a complete LaTeX document that contains all commands for plotting ROC curves for averages and readers.
   - **Returns**: A string representing the LaTeX document.
   - **Usage**:
     ```python
     latex_document = generator.generate_latex_document()
     with open('Output/ROC_reader_ave_analysis.tex', 'w') as f:
         f.write(latex_document)
     ```
3. **`generate_latex_image()`**:

   - Generates a LaTeX document for standalone images of ROC curves.
   - **Returns**: A string representing the LaTeX document for images.
   - **Usage**:
     ```python
     image_document = generator.generate_latex_image()
     with open('Output/ROC_reader_ave_image.tex', 'w') as f:
         f.write(image_document)
     ```
4. **`export_readerave_settings()`**:

   - Exports the current settings for page format, plot format, and colors.
   - **Returns**: A dictionary containing the current settings.
   - **Usage**:
     ```python
     settings = generator.export_readerave_settings()
     with open('Output/readerave_settings.json', 'w') as file:
         json.dump(settings, file, indent=4)
     ```
5. **`import_readerave_settings(settings)`**:

   - Imports settings from a JSON file and applies them.
   - **Parameters**:
     - `settings`: A dictionary or a path to a JSON file containing settings.
   - **Usage**:
     ```python
     generator.import_readerave_settings('Output/readerave_settings.json')
     ```

#### **Example Workflow**

```python
# Initialize generator
generator = LaTeXROCReaderAveGenerator()

# Parse average and reader Excel files
ave_files = ["Data/NP_average.xlsx", "Data/PBN_average.xlsx"]
reader_files = [
    ["Data/QR_t_Data.xlsx", "Data/MR_t_Data.xlsx"],
    ["Data/QR_p_Data.xlsx", "Data/MR_p_Data.xlsx"]
]
ave_names = ['NP', 'PBN']
type_names = ["t", "p"]
group_names = [["QR", "MR"], ["QR", "MR"]]
generator.parse_readerave_files(ave_files, reader_files, ave_names, type_names, group_names)

# Generate LaTeX document and save to file
latex_document = generator.generate_latex_document()
doc_file_path = 'Output/ROC_reader_ave_analysis.tex'
with open(doc_file_path, 'w') as f:
    f.write(latex_document)

# Generate standalone image LaTeX document and save to file
image_document = generator.generate_latex_image()
image_file_path = 'Output/ROC_reader_ave_image.tex'
with open(image_file_path, 'w') as f:
    f.write(image_document)

# Compile LaTeX document to PDF
generator.generate_pdf(doc_file_path, 'Output')

# Export settings to JSON
settings = generator.export_readerave_settings()
with open('Output/readerave_settings.json', 'w') as file:
    json.dump(settings, file, indent=4)

# Import settings from JSON (optional)
generator.import_readerave_settings('Output/readerave_settings.json')
```

#### **Error Handling**

- Ensure that all necessary Excel files are provided and properly formatted.
- Handle potential errors when reading files or generating LaTeX documents.

### **1.4. Usage Guide for `LaTeXROCBoxGenerator`**

The `LaTeXROCBoxGenerator` class generates LaTeX documents and commands to create box plots from ROC analysis data. It provides a visual summary of the data distributions.

#### **Initialization**

To use the `LaTeXROCBoxGenerator`, initialize an instance:

```python
box_generator = LaTeXROCBoxGenerator()
```

#### **Key Methods and Their Usage**

1. **`parse_box_file(box_file)`**:

   - Parses a CSV file to extract data for box plots.
   - **Parameters**:
     - `box_file`: Path to the CSV file containing data for box plots.
   - **Usage**:
     ```python
     box_generator.parse_box_file("Data/bar.csv")
     ```
2. **`generate_latex_document()`**:

   - Generates a complete LaTeX document for creating box plots.
   - **Returns**: A string representing the LaTeX document.
   - **Usage**:
     ```python
     latex_document = box_generator.generate_latex_document()
     with open('Output/ROC_Box_analysis.tex', 'w') as f:
         f.write(latex_document)
     ```
3. **`generate_latex_image()`**:

   - Generates a LaTeX document for standalone box plot images.
   - **Returns**: A string representing the LaTeX document for images.
   - **Usage**:
     ```python
     image_document = box_generator.generate_latex_image()
     with open('Output/ROC_Box_image.tex', 'w') as f:
         f.write(image_document)
     ```
4. **`set_box_plot_format

(**kwargs)`**:

   - Sets formatting options for the box plot, such as axis labels and plot dimensions.
   - **Parameters**:
     - `**kwargs`: Key-value pairs for different plot settings.
   - **Usage**:
     ```python
     box_generator.set_box_plot_format(xlabel="Readers", ylabel="Values")
     ```
5. **`set_numeric_xticklabels(numeric)`**:

   - Determines if x-tick labels should be numeric.
   - **Parameters**:
     - `numeric`: Boolean to set numeric x-tick labels.
   - **Usage**:
     ```python
     box_generator.set_numeric_xticklabels(True)
     ```

#### **Example Workflow**

```python
# Initialize box plot generator
box_generator = LaTeXROCBoxGenerator()

# Parse CSV file for box plot data
box_generator.parse_box_file("Data/bar.csv")

# Set custom plot format (optional)
box_generator.set_box_plot_format(xlabel="Readers", ylabel="Values")

# Generate LaTeX document and save to file
latex_document = box_generator.generate_latex_document()
doc_file_path = 'Output/ROC_Box_analysis.tex'
with open(doc_file_path, 'w') as f:
    f.write(latex_document)

# Generate standalone image LaTeX document and save to file
image_document = box_generator.generate_latex_image()
image_file_path = 'Output/ROC_Box_image.tex'
with open(image_file_path, 'w') as f:
    f.write(image_document)

# Compile LaTeX document to PDF
box_generator.generate_pdf(doc_file_path, 'Output')

# Export settings to JSON
settings = box_generator.export_settings()
with open('Output/box_settings.json', 'w') as file:
    json.dump(settings, file, indent=4)
```

#### **Error Handling**

- Ensure that the CSV file exists and is formatted correctly.
- Handle potential errors during LaTeX document generation and compilation.

## **2. Confidence Interval Analysis**

### **2.1. Usage Guide for `LaTeXConfidenceGenerator`**

The `LaTeXConfidenceGenerator` class generates LaTeX documents and commands to visualize confidence intervals and credible regions for ROC curves.

#### **Initialization**

To use the `LaTeXConfidenceGenerator`, initialize an instance:

```python
confidence_generator = LaTeXConfidenceGenerator()
```

#### **Key Methods and Their Usage**

1. **`set_confidence_data(fp, n_n, tp, n_p, alpha, data)`**:

   - Sets the confidence data for the ROC plot.
   - **Parameters**:
     - `fp`: False positives.
     - `n_n`: Total number of negatives.
     - `tp`: True positives.
     - `n_p`: Total number of positives.
     - `alpha`: List of confidence levels.
     - `data`: The data string read from the calculated results file.
   - **Usage**:
     ```python
     confidence_generator.set_confidence_data(fp=10, n_n=50, tp=40, n_p=50, alpha=[0.1, 0.2], data=data)
     ```
2. **`generate_latex_document()`**:

   - Generates a complete LaTeX document that contains all commands for plotting confidence intervals.
   - **Returns**: A string representing the LaTeX document.
   - **Usage**:
     ```python
     latex_document = confidence_generator.generate_latex_document()
     with open('Output/ROC_confidence_analysis.tex', 'w') as f:
         f.write(latex_document)
     ```
3. **`generate_latex_image()`**:

   - Generates a LaTeX document for standalone images.
   - **Returns**: A string representing the LaTeX document for images.
   - **Usage**:
     ```python
     image_document = confidence_generator.generate_latex_image()
     with open('Output/ROC_confidence_image.tex', 'w') as f:
         f.write(image_document)
     ```
4. **`export_confidence_settings()`**:

   - Exports the current settings for page format, plot format, and colors.
   - **Returns**: A dictionary containing the current settings.
   - **Usage**:
     ```python
     settings = confidence_generator.export_confidence_settings()
     with open('Output/confidence_settings.json', 'w') as file:
         json.dump(settings, file, indent=4)
     ```
5. **`import_confidence_settings(settings)`**:

   - Imports settings from a JSON file and applies them.
   - **Parameters**:
     - `settings`: A dictionary or a path to a JSON file containing settings.
   - **Usage**:
     ```python
     confidence_generator.import_confidence_settings('Output/confidence_settings.json')
     ```

#### **Example Workflow**

```python
# Initialize generator
confidence_generator = LaTeXConfidenceGenerator()

# Set the confidence data
fp = 10  
n_n = 50  
tp = 40  
n_p = 50  
alpha = [0.1, 0.2] 

# Assume 'data' is read from a precomputed results file
confidence_generator.set_confidence_data(fp=fp, n_n=n_n, tp=tp, n_p=n_p, alpha=alpha, data=data)

# Generate LaTeX document and save to file
latex_document = confidence_generator.generate_latex_document()
doc_file_path = 'Output/ROC_confidence_analysis.tex'
with open(doc_file_path, 'w') as f:
    f.write(latex_document)

# Generate standalone image LaTeX document and save to file
image_document = confidence_generator.generate_latex_image()
image_file_path = 'Output/ROC_confidence_image.tex'
with open(image_file_path, 'w') as f:
    f.write(image_document)

# Compile LaTeX document to PDF
confidence_generator.generate_pdf(doc_file_path, 'Output')

# Export settings to JSON
settings = confidence_generator.export_confidence_settings()
with open('Output/confidence_settings.json', 'w') as file:
    json.dump(settings, file, indent=4)

# Import settings from JSON (optional)
confidence_generator.import_confidence_settings('Output/confidence_settings.json')
```

---
