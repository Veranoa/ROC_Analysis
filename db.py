import pandas as pd
import sqlite3

data = pd.read_csv("Abus_DATA_LABELS_2024-09-26_1143_corrected.csv")
data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")

if 'pd_row_inde' in data.columns:
    data.rename(columns={'pd_row_inde': 'record_id'}, inplace=True)

if 'final_diagnostic_birads_case' in data.columns:
    data.rename(columns={'final_diagnostic_birads_case': 'final_diagnostic_birads_for_case'}, inplace=True)

required_columns = ['record_id', 'age', 'mammographic_density']
optional_columns = ['final_diagnostic_birads_for_case']

missing_required = [col for col in required_columns if col not in data.columns]
if missing_required:
    raise KeyError(f"Missing required columns: {missing_required}")

# Add optional columns with default values if not present
for col in optional_columns:
    if col not in data.columns:
        data[col] = None

# Replace NaN with None for compatibility with SQLite
data = data.where(pd.notnull(data), None)

# Connect to SQLite database
conn = sqlite3.connect("medical_data.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    age INTEGER,
    complete TEXT,
    mammographic_density TEXT,
    abus_birads TEXT,
    lessions INTEGER,
    lesion_shape TEXT,
    lesion_orientation TEXT,
    lesion_margin TEXT,
    echo_pattern TEXT,
    posterior_features TEXT,
    biopsy_performed TEXT,
    biopsy_outcome TEXT,
    stage_of_cancer TEXT,
    which_breast TEXT,
    clock_position TEXT,
    distance_from_nipple REAL,
    size_of_cancer REAL,
    likelihood_of_malignancy INTEGER,
    diagnostic_birads TEXT,
    doctor_experience_years INTEGER,
    abus_interpretation_method TEXT
);
""")

# Record ID
# Age
# Complete?
# Mammographic Density
# ABUS BI-RADS
# Lesions
# Lesion Shape
# Lesion Orientation
# Lesion Margin
# Echo Pattern
# Posterior Features
# Architectural Distortion on Coronal
# Lesion Visibility
# If seen on 2 or more data sets with different levels of compression, is the cancer best seen on the data set with the most compression?
# If seen on only one data set, is cancer out of FOV on other data sets? 
# Lesion Shape
# Lesion Orientation
# Lesion Margin
# Echo Pattern
# Posterior Features
# Architectural Distortion on Coronal
# Lesion Visibility
# If seen on 2 or more data sets with different levels of compression, is the cancer best seen on the data set with the most compression?
# If seen on only one data set, is cancer out of FOV on other data sets? 
# Lesion Shape
# Lesion Orientation
# Lesion Margin
# Echo Pattern
# Posterior Features
# Architectural Distortion on Coronal
# Lesion Visibility
# If seen on 2 or more data sets with different levels of compression, is the cancer best seen on the data set with the most compression?
# If seen on only one data set, is cancer out of FOV on other data sets? 
# Biopsy Performed
# Biopsy Outcome
# Number of Cancers Present
# Histology of Benign Lesion
# Histology of Cancer (choice=IDC)
# Histology of Cancer (choice=ILC)
# Histology of Cancer (choice=DCIS)
# Histology of Cancer (choice=Mixed Ductal/Lobular)
# Stage of Cancer
# Which Breast?
# Which View? (choice=AP)
# Which View? (choice=LAT)
# Which View? (choice=MED)
# Which View? (choice=Other)
# Specify Other View
# AP Clock Position
# AP Distance from Nipple
# AP Size of Cancer
# LAT Clock Position
# LAT Distance from Nipple
# LAT Size of Cancer
# MED Clock Position
# MED Distance from Nipple
# MED Size of Cancer
# [other] Clock Position
# [other] Distance from Nipple
#  [other] Size of Cancer
# Histology of Cancer (choice=IDC)
# Histology of Cancer (choice=ILC)
# Histology of Cancer (choice=DCIS)
# Histology of Cancer (choice=Mixed Ductal/Lobular)
# Stage of Cancer
# Which Breast?
# Which View? (choice=AP)
# Which View? (choice=LAT)
# Which View? (choice=MED)
# Which View? (choice=Other)
# Specify Other View
# AP Clock Position
# AP Distance from Nipple
# AP Size of Cancer
# LAT Clock Position
# LAT Distance from Nipple
# LAT Size of Cancer
# MED Clock Position
# MED Distance from Nipple
# MED Size of Cancer
# [other2] Clock Position
#  [other2] Distance from Nipple
# [other2] Size of Cancer
# Which Breast?
# Which View? (choice=AP)
# Which View? (choice=LAT)
# Which View? (choice=MED)
# Which View? (choice=Other)
# Specify Other View
# AP Clock Position
# AP Distance from Nipple
# AP Size of Lesion
# LAT Clock Position
# LAT Distance from Nipple
# LAT Size of Lesion
# MED Clock Position
# MED Distance from Nipple
# MED Size of Lesion
# [other] Clock Position
# [other] Distance from Nipple
#  [other] Size of Lesion
# Complete?
# Practice Type
# Breast Fellowship Trained
# Years of breast imaging experience
# Percentage of time spent in breast imaging
# Number of screening mammograms read in year prior to study
# Total number of ABUS studies
# Average number of ABUS studies read per day
# Method of ABUS interpretation
# Other Method of Interpretation
# Complete?
# Coronal Interpretation Time
# Coronal Initial Screening BI-RADS
# Coronal No Lesions - True False 
# Lesion Location (choice=Left Breast)
# Lesion Location (choice=Right Breast)

cursor.execute("""
CREATE TABLE IF NOT EXISTS readers (
    reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    experience_years INTEGER,
    interpretation_method TEXT
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS reader_evaluations (
    evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    reader_id INTEGER,
    lesion_location TEXT,
    likelihood_of_malignancy INTEGER,
    final_birads TEXT,
    
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(reader_id) REFERENCES readers(reader_id)
);
""")

    
    # Number of left breast lesions
    # Coronal likelihood of malignancy - Lesion 1
    # Coronal Final Diagnostic BI-RADS - Lesion 1
    # Coronal True-False - Lesion 1
    # Coronal likelihood of malignancy - Lesion 2
    # Coronal Final Diagnostic BI-RADS - Lesion 2
    # Coronal True False - Lesion 2
    # Coronal likelihood of malignancy - Lesion 3
    # Number of right breast lesions
    # Coronal likelihood of malignancy - Lesion 1
    # Coronal Final Diagnostic BI-RADS - Lesion 3
    # Coronal True False  - Lesion 3
    # Coronal Final Diagnostic BI-RADS - Lesion 1
    # Coronal True False - Lesion 1
    # Coronal likelihood of malignancy - Lesion 2
    # Coronal Final Diagnostic BI-RADS - Lesion 2
    # Coronal True False - Lesion 2
    # Coronal likelihood of malignancy - Lesion 3
    # Coronal Final Diagnostic BI-RADS - Lesion 3
    # Coronal True False - Lesion 3
    # Final Coronal likelihood of malignancy for case
    # Final Diagnostic BI-RADS for case
    # Is case a FN?
    # Type of FN
    # Coronal/Transverse Interpretation Time
    # Same interpretation as coronal interpretation, or are there additional findings
    # Coronal/Transverse - Same Interpretation True False
    # Lesion Location (choice=Left Breast)
    # Lesion Location (choice=Right Breast)

# Insert data into database
for _, row in data.iterrows():
    # Insert patient data
    cursor.execute("""
    INSERT INTO patients (record_id, age, mammographic_density, diagnostic_birads)
    VALUES (?, ?, ?, ?)
    """, (
        row.at['record_id'],
        row.at['age'],
        row.at['mammographic_density'],
        row.get('final_diagnostic_birads_for_case', None)
    ))

    patient_id = cursor.lastrowid  # Get the inserted patient's ID

    # Insert reader evaluation data
    for col in data.columns:
        if "reader" in col and ("likelihood_of_malignancy" in col or "final_birads" in col):
            reader_name = col.split("_")[1]  # Extract reader name
            likelihood = row.at[col] if pd.notna(row[col]) else None
            final_birads = row.get(f"{col.replace('likelihood_of_malignancy', 'final_birads')}", None)

            # Insert reader information
            cursor.execute("""
            INSERT INTO readers (name) VALUES (?)
            """, (reader_name,))
            reader_id = cursor.lastrowid

            # Insert evaluation data
            cursor.execute("""
            INSERT INTO reader_evaluations (patient_id, reader_id, likelihood_of_malignancy, final_birads)
            VALUES (?, ?, ?, ?)
            """, (patient_id, reader_id, likelihood, final_birads))

# Commit changes and close connection
conn.commit()
conn.close()
