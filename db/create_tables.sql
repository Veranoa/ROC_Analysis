-- Create Patients Table
CREATE TABLE Patients (
    Record_ID INT PRIMARY KEY,
    Age INT,
    Mammographic_Density VARCHAR(50),
    ABUS_BI_RADS DECIMAL(3, 1),
    Complete VARCHAR(50)
);

-- Create Lesions Table
CREATE TABLE Lesions (
    Lesion_ID INT PRIMARY KEY AUTO_INCREMENT,
    Record_ID INT,
    Lesion_Shape VARCHAR(50),
    Lesion_Orientation VARCHAR(50),
    Lesion_Margin VARCHAR(50),
    Echo_Pattern VARCHAR(50),
    Posterior_Features VARCHAR(50),
    Architectural_Distortion_Coronal VARCHAR(50),
    Lesion_Visibility VARCHAR(50),
    Likelihood_of_Malignancy DECIMAL(5, 2),
    FOREIGN KEY (Record_ID) REFERENCES Patients (Record_ID)
);

-- Create Diagnostics Table
CREATE TABLE Diagnostics (
    Diagnosis_ID INT PRIMARY KEY AUTO_INCREMENT,
    Record_ID INT,
    Biopsy_Performed VARCHAR(50),
    Biopsy_Outcome VARCHAR(50),
    Number_of_Cancers_Present INT,
    Histology_Benign_Lesion VARCHAR(100),
    Histology_Cancer_IDC VARCHAR(50),
    Histology_Cancer_ILC VARCHAR(50),
    Histology_Cancer_DCIS VARCHAR(50),
    Histology_Cancer_Mixed VARCHAR(50),
    Stage_of_Cancer VARCHAR(10),
    Is_Case_FN VARCHAR(10),
    FN_Type VARCHAR(50),
    FOREIGN KEY (Record_ID) REFERENCES Patients (Record_ID)
);

-- Create Imaging Table
CREATE TABLE Imaging (
    Imaging_ID INT PRIMARY KEY AUTO_INCREMENT,
    Record_ID INT,
    Which_Breast VARCHAR(50),
    Clock_Position VARCHAR(20),
    Distance_From_Nipple DECIMAL(5, 2),
    Size_of_Cancer DECIMAL(5, 2),
    Which_View_AP BOOLEAN,
    Which_View_LAT BOOLEAN,
    Which_View_MED BOOLEAN,
    Which_View_Other BOOLEAN,
    FOREIGN KEY (Record_ID) REFERENCES Patients (Record_ID)
);

-- Create Interpretation Table (Additional Information on Interpretation)
CREATE TABLE Interpretation (
    Interpretation_ID INT PRIMARY KEY AUTO_INCREMENT,
    Record_ID INT,
    Coronal_Interpretation_Time VARCHAR(20),
    Coronal_Initial_Screening_BIRADS VARCHAR(50),
    Final_Coronal_Likelihood_of_Malignancy DECIMAL(5, 2),
    Final_Diagnostic_BIRADS VARCHAR(50),
    FOREIGN KEY (Record_ID) REFERENCES Patients (Record_ID)
);
