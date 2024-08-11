import csv
import xml.etree.ElementTree as ET
import uuid
import os
from datetime import datetime
import platform

class RocXml:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.ns = {
            '': 'http://www.uchicago.edu/cROC/roc',
            'i': 'http://www.uchicago.edu/cROC/roc/info',
            'g': 'http://www.uchicago.edu/cROC/roc/glossary',
            'd': 'http://www.uchicago.edu/cROC/roc/data'
        }
        self.__root = None
        self.__info = None
        self.__glossary = None
        self.__data = None
        self.__cases = None
        self.__experiments = None
        self.__readers = None
        
        self.__info_data = {
            'study_title_short': 'ROC Study',
            'study_title_full': 'ROC Study Full Title',
            'study_description': 'Study on ROC analysis',
        }
        
        self.__setup_namespaces()
        self.__create_xml_structure()
        self.__populate_info()
        self.__populate_glossary()
        self.__populate_cases()
        # self.__populate_experiments()
        # self.__populate_readers()

    def __setup_namespaces(self):
        """Register XML namespaces."""
        for prefix, uri in self.ns.items():
            ET.register_namespace(prefix, uri)

    def __create_xml_structure(self):
        """Create the basic XML structure."""
        self.__root = ET.Element("root")
        self.__info = self.__append_child(self.__root, "Info", attrib={'xmlns:i': self.ns['i']})
        self.__glossary = self.__append_child(self.__root, "Glossary", attrib={'xmlns:g': self.ns['g']})
        self.__data = self.__append_child(self.__root, "Data", attrib={'xmlns:d': self.ns['d']})
        self.__cases = self.__append_child(self.__data, "Cases")
        self.__experiments = self.__append_child(self.__data, "Experiments")
        self.__readers = self.__append_child(self.__data, "Readers")

    def __append_child(self, parent, tag, text=None, attrib=None):
        """Append a child element to the parent element."""
        child = ET.Element(tag, attrib if attrib else {})
        if text:
            child.text = text
        parent.append(child)
        return child

    def __populate_info(self):
        """Populate the Info section of the XML."""
        self.__append_child(self.__info, "i:ID", str(uuid.uuid1()), {'type': 'uuid1'})
        self.__append_child(self.__info, "i:study_title_short", self.__info_data['study_title_short'])
        self.__append_child(self.__info, "i:study_title_full", self.__info_data['study_title_full'])
        self.__append_child(self.__info, "i:study_description", self.__info_data['study_description'])
        self.__append_child(self.__info, "i:created", datetime.now().isoformat())
        self.__append_child(self.__info, "i:saved")
        try:
            self.__append_child(self.__info, "i:by", os.getlogin())
        except:
            self.__append_child(self.__info, "i:by", "unknown")

        src = self.__append_child(self.__info, "i:with_src")
        self.__append_child(src, "i:src_date", datetime.fromtimestamp(os.path.getmtime(__file__)).isoformat())
        self.__append_child(src, "i:src_dir", os.path.dirname(__file__))
        self.__append_child(self.__info, "i:work_dir", os.getcwd())

        host = self.__append_child(self.__info, "i:host")
        self.__append_child(host, "i:host_node", platform.node())
        self.__append_child(host, "i:host_system", platform.system())
        self.__append_child(host, "i:host_release", platform.release())
        self.__append_child(host, "i:host_version", platform.version())
        self.__append_child(host, "i:host_machine", platform.machine())
        self.__append_child(host, "i:host_processor", platform.processor())
        self.__append_child(host, "i:host_architecture", str(platform.architecture()))

        py = self.__append_child(self.__info, "i:python")
        self.__append_child(py, "i:python_version", platform.python_version())
        self.__append_child(py, "i:python_build", str(platform.python_build()))
        self.__append_child(py, "i:python_compiler", platform.python_compiler())
        self.__append_child(py, "i:python_branch", platform.python_branch())
        self.__append_child(py, "i:python_revision", platform.python_revision())
        self.__append_child(py, "i:python_implementation", platform.python_implementation())

    def __populate_glossary(self):
        """Populate the Glossary section of the XML."""
        glossary_entries = {
            "Info": "Information of date, time, user, executable source file, directories, host computer, and python environment",
            "Glossary": "Explanation of tags",
            "DataSummary": "Summary results of the simulation results",
            "DataForPlot": "Data for generating summary plots of the simulation results",
            "Data": "Simulation raw data",
            "d:Case": "A standalone case in the study",
            "d:Experiment": "A standalone simulation experiment",
            "d:Reader": "A reader participating in the study",
        }

        info_entries = {
            "i:ID": "Unique file ID, and also serves as the file name",
            "i:study_title_short": "Short study title for identification purpose",
            "i:study_title_full": "Full descriptive study title",
            "i:study_description": "Additional description of the study",
            "i:created": "Date and time data in this file began to be created",
            "i:saved": "Date and time data in this file were saved",
            "i:by": "The login user name who created this file",
            "i:with_src": "The executable source file that was used to create data in this file",
            "i:src_date": "Date and time of the executable source file that created data in this file",
            "i:src_dir": "Directory of the executable source file that created data in this file",
            "i:work_dir": "Directory in which the executable source file was run to create data in this file",
            "i:host": "Information of the host computer",
            "i:host_node": "The host computer network name",
            "i:host_system": "The host computer system/OS name",
            "i:host_release": "The host computer system release",
            "i:host_version": "The host computer system release version",
            "i:host_machine": "The host computer machine type",
            "i:host_processor": "The host computer (real) processor name",
            "i:host_architecture": "The host computer executable (Python interpreter binary) architecture information",
            "i:python": "Information of the Python interpreter",
            "i:python_version": "Python version",
            "i:python_build": "Python build number and date",
            "i:python_compiler": "Python compiler used to create data in this file",
            "i:python_branch": "Python implementation SCM branch",
            "i:python_revision": "Python implementation SCM revision",
            "i:python_implementation": "Python implementation",
        }

        for tag, text in glossary_entries.items():
            self.__append_child(self.__glossary, f"g:{tag}", attrib={'tag': tag}).text = text

        info_glossary = self.__append_child(self.__glossary, "g:Info", attrib={'tag': "Info"})
        for tag, text in info_entries.items():
            self.__append_child(info_glossary, f"g:i", attrib={'tag': tag}).text = text

        data_glossary = self.__append_child(self.__glossary, "g:Data", attrib={'tag': "Data"})
        case_glossary = self.__append_child(data_glossary, "g:d", attrib={'tag': "d:Case"})
        case_glossary.text = "A standalone case in the study"
        self.__append_child(case_glossary, "g:dc", attrib={'tag': "dc:StudyCase"}).text = "Unique identifier for the case"
        self.__append_child(case_glossary, "g:dc", attrib={'tag': "dc:truth"}).text = "Truth label for the case"
        self.__append_child(case_glossary, "g:dc", attrib={'tag': "dc:Modality1"}).text = "First modality used for the case"
        self.__append_child(case_glossary, "g:dc", attrib={'tag': "dc:Modality2"}).text = "Second modality used for the case"

        experiment_glossary = self.__append_child(data_glossary, "g:d", attrib={'tag': "d:Experiment"})
        experiment_glossary.text = "A standalone simulation experiment"
        self.__append_child(experiment_glossary, "g:de", attrib={'tag': "de:ExperimentID"}).text = "Unique identifier for the experiment"
        self.__append_child(experiment_glossary, "g:de", attrib={'tag': "de:StudyCase"}).text = "Identifier for the case being studied"
        self.__append_child(experiment_glossary, "g:de", attrib={'tag': "de:ReaderID"}).text = "Identifier for the reader conducting the experiment"
        self.__append_child(experiment_glossary, "g:de", attrib={'tag': "de:Modality"}).text = "Modality used in the experiment"
        self.__append_child(experiment_glossary, "g:de", attrib={'tag': "de:ConfidenceRating"}).text = "Confidence rating given by the reader"
        self.__append_child(experiment_glossary, "g:de", attrib={'tag': "de:BIRADS"}).text = "BI-RADS assessment given by the reader"
        self.__append_child(experiment_glossary, "g:de", attrib={'tag': "de:TimestampImageLoaded"}).text = "Timestamp when the image was loaded"
        self.__append_child(experiment_glossary, "g:de", attrib={'tag': "de:TimestampReportSubmitted"}).text = "Timestamp when the report was submitted"

        reader_glossary = self.__append_child(data_glossary, "g:d", attrib={'tag': "d:Reader"})
        reader_glossary.text = "A reader participating in the study"
        self.__append_child(reader_glossary, "g:dr", attrib={'tag': "dr:ReaderID"}).text = "Unique identifier for the reader"
        self.__append_child(reader_glossary, "g:dr", attrib={'tag': "dr:Name"}).text = "Name of the reader"
        self.__append_child(reader_glossary, "g:dr", attrib={'tag': "dr:Institution"}).text = "Institution of the reader"
        self.__append_child(reader_glossary, "g:dr", attrib={'tag': "dr:Experience"}).text = "Experience level of the reader"

    def __populate_cases(self):
        """Populate the Cases section of the XML."""
        with open(self.csv_file, newline='') as f:
            reader = csv.DictReader(f)
            cases_dict = {}
            for row in reader:
                study_case_id = row["StudyCase"]
                if study_case_id not in cases_dict:
                    case = self.__append_child(self.__cases, "d:Case", attrib={'id': f"dc{str(uuid.uuid4())}"})
                    cases_dict[study_case_id] = case
                    self.__append_child(case, "dc:StudyCase", study_case_id)
                    self.__append_child(case, "dc:truth", row["truth"])

                case = cases_dict[study_case_id]
                modalities = [col for col in row.keys() if col.startswith("Modality")]
                for modality in modalities:
                    modality_num = modality[-1]
                    modality_element = self.__append_child(case, f"dc:Modality{modality_num}")
                    self.__append_child(modality_element, "d:Name", row.get(f"Modality{modality_num}", ""))
                    self.__append_child(modality_element, "d:LOM", row.get(f"LOM{modality_num}", ""))
                    self.__append_child(modality_element, "d:BIRADS", row.get(f"BIRADS{modality_num}", ""))
                    self.__append_child(modality_element, "d:ForcedBIRADS", row.get(f"ForcedBIRADS{modality_num}", ""))
                    self.__append_child(modality_element, "d:DetectionAtLocation", row.get(f"DetectionAtLocation{modality_num}", ""))

    def __populate_experiments(self):
        """Populate the Experiments section of the XML."""
        with open(self.csv_file, newline='') as f:
            reader = csv.DictReader(f)
            experiments_dict = {}
            for row in reader:
                experiment_id = row["ExperimentID"]
                if experiment_id not in experiments_dict:
                    experiment = self.__append_child(self.__experiments, "d:Experiment", attrib={'id': f"de{str(uuid.uuid4())}"})
                    experiments_dict[experiment_id] = experiment
                    self.__append_child(experiment, "de:ExperimentID", experiment_id)
                    self.__append_child(experiment, "de:StudyCase", row["StudyCase"])
                    self.__append_child(experiment, "de:Modality", row.get("Modality1", ""))  # Assumed to be the first modality for experiment context
                    self.__append_child(experiment, "de:LOM", row.get("LOM1", ""))
                    self.__append_child(experiment, "de:BIRADS", row.get("BIRADS1", ""))

    def __populate_readers(self):
        """Populate the Readers section of the XML."""
        with open(self.csv_file, newline='') as f:
            reader = csv.DictReader(f)
            readers_dict = {}
            for row in reader:
                reader_id = row["ReaderID"]
                if reader_id not in readers_dict:
                    reader = self.__append_child(self.__readers, "d:Reader", attrib={'id': f"dr{str(uuid.uuid4())}"})
                    readers_dict[reader_id] = reader
                    self.__append_child(reader, "dr:ReaderID", reader_id)
                    self.__append_child(reader, "dr:Name", row.get("ReaderName", "Unknown"))
                    self.__append_child(reader, "dr:Institution", row.get("Institution", "Unknown"))
                    self.__append_child(reader, "dr:Experience", row.get("Experience", "5 years"))  

    def set_info_data(self, key, value):
        """Set the information data for the Info section."""
        if key in self.__info_data:
            self.__info_data[key] = value

    def read_xml(self, file_name):
        pass
    
    def write_xml(self, file_name):
        pass
    
    def save_xml(self, file_name):
        """Save the XML to a file."""
        tree = ET.ElementTree(self.__root)
        xml_str = ET.tostring(self.__root, encoding='unicode', method='xml')
        with open(file_name, 'w') as f:
            f.write(xml_str)
        print(f"XML file saved as {file_name}")

# Usage example
roc_xml = RocXml('/Users/summersane/Desktop/RA/Radiology/ROC_Analysis/Sample/xml/CRRS-4.SV01_day2.scored.csv')
roc_xml.set_info_data('study_title_full', 'Custom ROC Study Full Title')
roc_xml.set_info_data('study_description', 'Custom description of ROC analysis')
roc_xml.save_xml('roc_study.xml')
