import sys
import os
import re
import json
import pandas as pd
import string
from openpyxl import load_workbook
from datetime import datetime

from TexGenerator import LaTeXGenerator
from ROCBoxGenerator import LaTeXROCBoxGenerator
from ROCAveGenerator import LaTeXROCAveGenerator
from ROCReaderGenerator import LaTeXROCReaderGenerator
from ROCReaderAveGenerator import LaTeXROCReaderAveGenerator

class LaTeXROCReport(LaTeXGenerator):
    def __init__(self):
        super().__init__()
        
        self.ave_files = []
        self.reader_files = []
        self.ave_names = []
        self.type_names = []
        self.group_names = []
        self.box_file = None
        
        self.document_header = self.generate_document_header()
        
        # Initialize the individual components
        self.section_box = ""
        self.section_ave = ""
        self.section_reader = ""
        self.section_reader_ave = ""
        
        self.section_box_name = ""
        self.section_ave_name = ""
        self.section_reader_name = ""
        self.section_reader_ave_name = ""

        self.roc_box_generator = LaTeXROCBoxGenerator()
        self.roc_ave_generator = LaTeXROCAveGenerator()
        self.roc_reader_generator = LaTeXROCReaderGenerator()
        self.roc_reader_ave_generator = LaTeXROCReaderAveGenerator()
        
        # Load data or set up configurations here

    def setup(self, box_file = None, ave_files=None, reader_files=None,
              ave_names=None, type_names=None, group_names=None
              ):
        if box_file:
            self.box_file = box_file
        if ave_files:
            self.ave_files = ave_files
        if reader_files:
            self.reader_files = reader_files
        if ave_names:
            self.ave_names = ave_names
        if type_names:
            self.type_names = type_names
        if group_names:
            self.group_names = group_names    
        
        self.generate_all()  
            
    def generate_all(self):
        if self.ave_files and self.ave_names:
            self.roc_ave_generator.parse_ave_files(self.ave_files, self.ave_names)
            self.section_ave_name = "Average"
            self.section_ave = self.generate_average_section()
                        
        if self.reader_files and self.type_names and self.group_names:
            self.roc_reader_generator.parse_reader_files(self.reader_files, self.type_names, self.group_names)
            self.roc_reader_generator.set_plot_format(legend_style={"at": "{(0.4,0.3)}"})
            self.roc_reader_generator.set_plot_format(x_ticklabels= "{,,}", y_ticklabels= "{,,}")
            self.section_reader_name = "Reader"
            self.section_reader = self.generate_reader_section()

        if self.ave_files and self.reader_files and self.ave_names and self.type_names and self.group_names:
            self.roc_reader_ave_generator.parse_readerave_files(self.ave_files, self.reader_files, ave_names=self.ave_names, type_names=self.type_names, group_names=self.group_names)
            self.section_reader_ave_name = "Reader and Average"
            if self.box_file:
                self.roc_box_generator.parse_box_file(self.box_file)
                
            self.section_reader_ave = self.generate_readerave_section()

    def generate_average_section(self):
        if not self.section_ave:
            self.document_header += "\\usetag{average}\n"
            
        self.section_ave = (
            f"\\section{{{self.section_ave_name}}}\n" +
            "\\tagged{average}{\n" +
            self.roc_ave_generator.ave_color_definitions +
            self.roc_ave_generator.ave_plot_commands +
            self.roc_ave_generator.ave_plot_frame_commands +
            self.roc_ave_generator.make_figure_command +
            self.roc_ave_generator.plot_fig_command +
            self.roc_ave_generator.plot_ave_group_commands +
            self.roc_ave_generator.generate_document_body_commands() +
            "\n}\n\n"
        )
        return self.section_ave  # Ensure that this returns the string

    def generate_reader_section(self):
        if not self.section_reader:
            self.document_header += "\\usetag{reader}\n"
            
        self.section_reader = (
            f"\\section{{{self.section_reader_name}}}\n" +
            "\\tagged{reader}{\n" +
            self.roc_reader_generator.reader_color_definitions +
            self.roc_reader_generator.reader_plot_commands +
            self.roc_reader_generator.reader_plot_frame_commands +
            self.roc_reader_generator.make_figure_command +
            self.roc_reader_generator.plot_fig_command +
            self.roc_reader_generator.plot_reader_group_commands +
            self.roc_reader_generator.generate_document_body_commands() +
            "\n}\n\n"
        )
        return self.section_reader  # Ensure that this returns the string

    def generate_readerave_section(self):
        if not self.section_reader_ave:
            self.document_header += "\\usetag{readerave}\n"
            
        self.section_reader_ave = (
            f"\\section{{{self.section_reader_ave_name}}}\n" +
            "\\tagged{readerave}{\n" +

            self.roc_reader_ave_generator.readerave_color_definitions +
            self.roc_reader_ave_generator.ave_plot_commands +
            self.roc_reader_ave_generator.reader_plot_commands +
            
            self.roc_reader_ave_generator.readerave_plot_frame_commands +
            self.roc_reader_ave_generator.plot_readerave_fig_commands +
            self.roc_reader_ave_generator.plot_readerave_group_commands +
            self.roc_reader_ave_generator.make_figure_command +
            self.roc_reader_ave_generator.generate_document_body_commands() +
            "\n}\n\n"
        )
        
        if self.box_file:
            self.section_reader_ave += self.roc_box_generator.generate_document_body_commands()
        return self.section_reader_ave  # Ensure that this returns the string

        
    def generate_latex_document(self):
        # Make sure all parts are strings
        latex_document = (
            (self.document_header or "") +
            "\n" +
            (self.roc_reader_ave_generator.ave_data_commands or "") +
            (self.roc_reader_ave_generator.reader_data_commands or "") +
            
            "\\begin{document}\n" +
            (self.section_ave or "") +
            (self.section_reader or "") +
            (self.section_reader_ave or "") +
            (self.header_footer or "") +
            "\\end{document}"
        )
        return latex_document
    
    def export_all_settings(self):
        all_settings = {
            'ave': self.roc_ave_generator.export_ave_settings(),
            'reader': self.roc_reader_generator.export_reader_settings(),
            'readerave': self.roc_reader_ave_generator.export_readerave_settings(),
            'box': self.roc_box_generator.export_settings()
        }
        return all_settings

    def import_all_settings(self, file_path):
        with open(file_path, 'r') as file:
            settings = json.load(file)
            self.roc_ave_generator.import_ave_settings(settings['ave'])
            self.roc_reader_generator.import_reader_settings(settings['reader'])
            self.roc_reader_ave_generator.import_readerave_settings(settings['readerave'])
            self.roc_box_generator.import_settings(settings['box'])       

if __name__ == "__main__":

        ave_files = ["Data/NP_average.xlsx", "Data/PBN_average.xlsx"]
        ave_names = ['NP', 'PBN']
        
        reader_files = [
            ["Data/QR_t_Data.xlsx", "Data/MR_t_Data.xlsx"],
            ["Data/QR_p_Data.xlsx", "Data/MR_p_Data.xlsx"]
        ]
        type_names = ["t", "p"]
        group_names = [["QR", "MR"], ["QR", "MR"]] 
        
        box_file = "Data/bar.csv"  
        
        generator = LaTeXROCReport()
        generator.setup(box_file=box_file, ave_files=ave_files, reader_files=reader_files, ave_names=ave_names, type_names=type_names, group_names=group_names)
        
        settings = generator.export_all_settings()
        
        output_dir = 'Output'
        os.makedirs(output_dir, exist_ok=True)
        
        export_file_path = os.path.join(output_dir, 'all_settings.json')
        with open(export_file_path, 'w') as file:
            json.dump(settings, file, indent=4)
        
        latex_document = generator.generate_latex_document()
        with open('Output/ROC_analysis.tex', 'w') as f:
            f.write(latex_document)