import sys
import os
import re
import json
import pandas as pd
import string
from openpyxl import load_workbook
from datetime import datetime

from ROCGenerator import LaTeXROCGenerator
from ROCBoxGenerator import LaTeXROCBoxGenerator
from ROCAveGenerator import LaTeXROCAveGenerator
from ROCReaderGenerator import LaTeXROCReaderGenerator
from ROCReaderAveGenerator import LaTeXROCReaderAveGenerator

class LaTeXROCReport(LaTeXROCGenerator):
    def __init__(self):
        super().__init__()
        
        self.__ave_files = []
        self.__reader_files = []
        self.__ave_names = []
        self.__type_names = []
        self.__group_names = []
        self.__box_file = None
        
        self.__document_header = self.generate_document_header()
        
        # Initialize the individual components
        self.__section_box = ""
        self.__section_ave = ""
        self.__section_reader = ""
        self.__section_reader_ave = ""
        
        self.__section_box_name = ""
        self.__section_ave_name = ""
        self.__section_reader_name = ""
        self.__section_reader_ave_name = ""

        self.__roc_box_generator = LaTeXROCBoxGenerator()
        self.__roc_ave_generator = LaTeXROCAveGenerator()
        self.__roc_reader_generator = LaTeXROCReaderGenerator()
        self.__roc_reader_ave_generator = LaTeXROCReaderAveGenerator()
        
    def setup(self, box_file = None, ave_files=None, reader_files=None,
              ave_names=None, type_names=None, group_names=None
              ):
        if box_file:
            self.__box_file = box_file
        if ave_files:
            self.__ave_files = ave_files
        if reader_files:
            self.__reader_files = reader_files
        if ave_names:
            self.__ave_names = ave_names
        if type_names:
            self.__type_names = type_names
        if group_names:
            self.__group_names = group_names    
        
        self.__generate_all()  
            
    def __generate_all(self):
        if self.__ave_files and self.__ave_names:
            self.__roc_ave_generator.parse_ave_files(self.__ave_files, self.__ave_names)
            self.__section_ave_name = "Average"
            self.__section_ave = self.__generate_average_section()
                        
        if self.__reader_files and self.__type_names and self.__group_names:
            self.__roc_reader_generator.parse_reader_files(self.__reader_files, self.__type_names, self.__group_names)
            self.__roc_reader_generator.set_plot_format(legend_style={"at": "{(0.4,0.3)}"})
            self.__roc_reader_generator.set_plot_format(x_ticklabels="{,,}", y_ticklabels="{,,}")
            self.__section_reader_name = "Reader"
            self.__section_reader = self.__generate_reader_section()

        if self.__ave_files and self.__reader_files and self.__ave_names and self.__type_names and self.__group_names:
            self.__roc_reader_ave_generator.parse_readerave_files(self.__ave_files, self.__reader_files, ave_names=self.__ave_names, type_names=self.__type_names, group_names=self.__group_names)
            self.__section_reader_ave_name = "Reader and Average"
            if self.__box_file:
                self.__roc_box_generator.parse_box_file(self.__box_file)
                
            self.__section_reader_ave = self.__generate_readerave_section()

    def __generate_average_section(self):
        if not self.__section_ave:
            self.__document_header += "\\usetag{average}\n"
            
        self.__section_ave = (
            f"\\section{{{self.__section_ave_name}}}\n" +
            "\\tagged{average}{\n" +
            self.__roc_ave_generator.ave_color_definitions +
            self.__roc_ave_generator.ave_plot_commands +
            self.__roc_ave_generator.ave_plot_frame_commands +
            self.__roc_ave_generator.make_figure_command +
            self.__roc_ave_generator.plot_fig_command +
            self.__roc_ave_generator.plot_ave_group_commands +
            self.__roc_ave_generator.generate_document_body_commands() +
            "\n}\n\n"
        )
        return self.__section_ave  # Ensure that this returns the string

    def __generate_reader_section(self):
        if not self.__section_reader:
            self.__document_header += "\\usetag{reader}\n"
            
        self.__section_reader = (
            f"\\section{{{self.__section_reader_name}}}\n" +
            "\\tagged{reader}{\n" +
            self.__roc_reader_generator.reader_color_definitions +
            self.__roc_reader_generator.reader_plot_commands +
            self.__roc_reader_generator.reader_plot_frame_commands +
            self.__roc_reader_generator.make_figure_command +
            self.__roc_reader_generator.plot_fig_command +
            self.__roc_reader_generator.plot_reader_group_commands +
            self.__roc_reader_generator.generate_document_body_commands() +
            "\n}\n\n"
        )
        return self.__section_reader  # Ensure that this returns the string

    def __generate_readerave_section(self):
        if not self.__section_reader_ave:
            self.__document_header += "\\usetag{readerave}\n"
            
        self.__section_reader_ave = (
            f"\\section{{{self.__section_reader_ave_name}}}\n" +
            "\\tagged{readerave}{\n" +

            self.__roc_reader_ave_generator.readerave_color_definitions +
            self.__roc_reader_ave_generator.ave_plot_commands +
            self.__roc_reader_ave_generator.reader_plot_commands +
            
            self.__roc_reader_ave_generator.readerave_plot_frame_commands +
            self.__roc_reader_ave_generator.plot_readerave_fig_commands +
            self.__roc_reader_ave_generator.plot_readerave_group_commands +
            self.__roc_reader_ave_generator.make_figure_command +
            self.__roc_reader_ave_generator.generate_document_body_commands() +
            "\n}\n\n"
        )
        
        if self.__box_file:
            self.__section_reader_ave += self.__roc_box_generator.generate_document_body_commands()
        return self.__section_reader_ave  # Ensure that this returns the string

        
    def generate_latex_document(self):
        # Make sure all parts are strings
        latex_document = (
            (self.__document_header or "") +
            "\n" +
            (self.__roc_reader_ave_generator.ave_data_commands or "") +
            (self.__roc_reader_ave_generator.reader_data_commands or "") +
            
            "\\begin{document}\n" +
            (self.__section_ave or "") +
            (self.__section_reader or "") +
            (self.__section_reader_ave or "") +
            (self.__header_footer or "") +
            "\\end{document}"
        )
        return latex_document
    
    def export_all_settings(self):
        all_settings = {
            'ave': self.__roc_ave_generator.export_ave_settings(),
            'reader': self.__roc_reader_generator.export_reader_settings(),
            'readerave': self.__roc_reader_ave_generator.export_readerave_settings(),
            'box': self.__roc_box_generator.export_settings()
        }
        return all_settings

    def import_all_settings(self, file_path):
        with open(file_path, 'r') as file:
            settings = json.load(file)
            self.__roc_ave_generator.import_ave_settings(settings['ave'])
            self.__roc_reader_generator.import_reader_settings(settings['reader'])
            self.__roc_reader_ave_generator.import_readerave_settings(settings['readerave'])
            self.__roc_box_generator.import_settings(settings['box'])       

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