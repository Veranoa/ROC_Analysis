import xml.etree.ElementTree as ET
import pandas as pd

def parse_xml_to_dict(xml_root):
    data_dict = {}
    
    def recurse_tree(element, parent_path):
        for child in element:
            child_path = f"{parent_path}/{child.tag}"
            if len(child):
                recurse_tree(child, child_path)
            else:
                data_dict[child_path] = child.text
    
    recurse_tree(xml_root, "")
    return data_dict

def xml_to_dataframe(xml_root):
    data_dict = parse_xml_to_dict(xml_root)
    df = pd.DataFrame(data_dict.items(), columns=['Path', 'Value'])
    return df

def xml_to_xlsx(xml_file, xlsx_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    df = xml_to_dataframe(root)
    df.to_excel(xlsx_file, index=False)
    print(f"XML data has been successfully written to {xlsx_file}")
    
def xml_to_average_xlsx(xml_file, xlsx_file):
    pass

def xml_to_reader_xlsx(xml_file, output_folder):
    pass

def xml_to_bar_csv(xml_file, output_folder):
    pass

xml_file = 'example.xml'
xlsx_file = 'output.xlsx'
xml_to_xlsx(xml_file, xlsx_file)


import openpyxl
from openpyxl import Workbook

class sim_xml():
    # Existing methods...

    def xml_to_xlsx(self, xml_file, xlsx_file):
        """
        Convert XML data to XLSX format.

        Parameters
        ----------
        xml_file : str
            XML file name to read.
        xlsx_file : str
            XLSX file name to write.
        """
        # Load the XML data
        self.__load_xml(xml_file)
        
        # Create a new workbook and select the active worksheet
        wb = Workbook()
        ws = wb.active

        # Extracting data from the XML tree
        root = self.__xml['root']
        data = []

        # This is a simple example assuming a fixed structure
        # Adjust this according to your actual XML structure
        for experiment in root.findall('d:experiment', self.__xml['ns']):
            exp_id = experiment.find('d:ID', self.__xml['ns']).text
            for trial in experiment.findall('dt:trial', self.__xml['ns']):
                seq = trial.find('dt:seq', self.__xml['ns']).text
                emp_FP = trial.find('dt:emp_FP', self.__xml['ns']).text
                emp_TP = trial.find('dt:emp_TP', self.__xml['ns']).text
                mle_FPF = trial.find('dt:mle_FPF', self.__xml['ns']).text
                mle_TPF = trial.find('dt:mle_TPF', self.__xml['ns']).text
                data.append([exp_id, seq, emp_FP, emp_TP, mle_FPF, mle_TPF])

        # Writing data to the worksheet
        headers = ["Experiment ID", "Sequence", "Empirical FP", "Empirical TP", "MLE FPF", "MLE TPF"]
        ws.append(headers)
        for row in data:
            ws.append(row)

        # Save the workbook
        wb.save(xlsx_file)

        if self.__verbose:
            print(f"  .. Converted XML to XLSX: {xlsx_file}")

# Usage
sim = sim_xml()  # Assuming you have a CI instance
sim.xml_to_xlsx('path/to/your.xml', 'path/to/output.xlsx')
