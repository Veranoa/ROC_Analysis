# ROCReaderAveGenerator.py
#
# Copyright (C) 2024-2030 Yun Liu
# University of Chicago
#
# LaTeX ROC Reader and Average Generator
#

import sys
import os
import string
import pandas as pd
import json
from openpyxl import load_workbook
from tex.ROCReaderGenerator import LaTeXROCReaderGenerator 

class LaTeXROCReaderAveGenerator(LaTeXROCReaderGenerator):
    def __init__(self):
        super().__init__()
        self.reader_files = []
        self.readerave_colors = ['{0, 0, 1}', '{1, 0, 0}']
        
        self.readerave_color_definitions = ""
        self.readerave_plot_frame_commands = ""
        self.plot_readerave_fig_commands = ""
        self.plot_readerave_group_commands = ""
        self.plot_readerave_fig_commands = ""

    def parse_readerave_files(self, ave_files, reader_files, ave_names=None, type_names=None, group_names=None):
        """
        Parses both average and reader files and generates the necessary LaTeX commands.
        """
        self.parse_ave_files(ave_files, ave_names=ave_names)
        self.parse_reader_files(reader_files, type_names=type_names, group_names=group_names)
        
        self.readerave_color_definitions = self.generate_readerave_color_definitions()
        self.ave_plot_commands = self.generate_ave_plot_commands()
        self.reader_plot_commands = self.generate_reader_plot_commands()
        self.make_figure_command = self.generate_make_figure_command()
        self.readerave_plot_frame_commands = self.generate_readerave_plot_frame_commands()
        self.plot_readerave_group_commands = self.generate_readerave_group_commands()
        self.plot_readerave_fig_commands = self.generate_plot_readerave_fig_commands()
        self.header_footer = self.generate_header_footer()
               
    def parse_ave_files(self, group_files, ave_names=None, engine='openpyxl'):
        """
        Parses the average ROC Excel files and prepares the data for LaTeX commands.
        """
        groups = []
        ave_names = ave_names or list(string.ascii_uppercase[:len(group_files)])
        for group_file, group_name in zip(group_files, ave_names):
            if not os.path.exists(group_file) or not group_file.endswith('.xlsx'):
                raise ValueError(f"Error: File '{group_file}' does not exist or is not an XLSX file.")
            sheets = pd.ExcelFile(group_file, engine=engine).sheet_names
            group_name = self.clean_name(group_name)
            group_data = [(group_file, self.clean_name(sheet)) for sheet in sheets]
            groups.append((group_name, group_data))
            
        self.ave_groups = groups        
        self.ave_index_map = self.generate_ave_index_map()
        self.num_ave_colors = max(len(group_data) for _, group_data in self.ave_groups)
        self.ave_colors = self.default_colors[:self.num_ave_colors]
        
        self.ave_data_commands = self.generate_ave_data_commands()
        
    def parse_reader_files(self, reader_files, type_names=None, group_names=None, engine='openpyxl'):
        """
        Parses the reader ROC Excel files and prepares the data for LaTeX commands.
        """
        groups = []
        type_names = type_names or list(self.generate_names(len(reader_files)))
        
        if group_names is None:
            group_names = [list(self.generate_names(len(type_files))) for type_files in reader_files]
   
        for type_files, type_name, methods in zip(reader_files, type_names, group_names):
            if not all(os.path.exists(file) and file.endswith('.xlsx') for file in type_files):
                raise ValueError("One or more files do not exist or are not XLSX files.")
            
            method_sheets = []
            for file, method_name in zip(type_files, methods):
                sheets = pd.ExcelFile(file, engine=engine).sheet_names
                self.sheet_names.update(sheets)
                method_sheets.append((method_name, file, sheets))
            groups.append((type_name, method_sheets))
        
        self.reader_files = reader_files
        self.reader_groups = groups
        self.reader_index_map = self.generate_reader_index_map()

        max_files_per_type = max(len(methods) for _, methods in self.reader_groups)
        self.reader_colors = [self.default_colors[:max_files_per_type]] * len(type_names)
        self.reader_marks = [self.default_styles[:max_files_per_type]] * len(type_names)

        self.reader_data_commands = self.generate_reader_data_commands()

    def generate_readerave_color_definitions(self):
        """
        Generates LaTeX commands to define colors for average and reader ROC curves.
        """
        color_definitions = "% Define ROC curve colors:\n"
        color_definitions += f"""
\\definecolor{{COLORo0}}{{rgb}}{self.readerave_colors[0]}
\\definecolor{{COLORo1}}{{rgb}}{self.readerave_colors[1]}

"""
        return color_definitions
        
    def generate_ave_plot_commands(self):
        """
        Generates LaTeX commands for plotting average ROC curves.
        """
        plot_commands = "% Command for plotting average ROC curves:\n"
        for group_name, group_data in self.ave_groups:
            for file_index, (_, sheet_name) in enumerate(group_data):
                cmd_index = f"{group_name}_{sheet_name}"
                letter_index = self.ave_index_map[cmd_index]
                plot_commands += f"\\newcommand{{\\DrawLINEo{letter_index}oAve}}[1]{{\n"
                plot_commands += f"\\addplot[\n  color=COLORo{file_index % 2},\n  mark=dot,\n  line width=2pt,\n  on layer={{axis foreground}},\n] coordinates {{#1}};\n"
                plot_commands += f"}}\n\n"
        return plot_commands
       
    def generate_reader_plot_commands(self):
        """
        Generates LaTeX commands for plotting reader ROC curves.
        """
        plot_style = "% Command for plotting reader ROC curves:\n"
        for type_index, (type_name, methods) in enumerate(self.reader_groups):
            for method_index, (method_name, file, sheets) in enumerate(methods):
                plot_style += f"\\newcommand{{\\DrawLINEo{type_name}{method_name}oReader}}[1]{{\n"                     
                plot_style += f"\\addplot[\n  color=COLORo{(method_index+1) % 2},\n  mark=dot,\n  line width=0.5pt,\n  on layer={{axis foreground}},\n] coordinates {{#1}};\n"
                plot_style += f"}}\n\n"
        return plot_style
       
    def generate_readerave_plot_frame_commands(self):
        """
        Generates LaTeX commands for plotting combined average and reader ROC curves.
        """
        plot_frame_commands = "% Command for plotting ROC curves in one plot:\n"
        for ave_group_index, (ave_group_name, ave_group_data) in enumerate(self.ave_groups):
            for ave_file_index, (ave_file, ave_sheet_name) in enumerate(ave_group_data):
                ave_cmd_index = f"{ave_group_name}_{ave_sheet_name}"
                ave_letter_index = self.ave_index_map[ave_cmd_index]
                plot_frame_commands += f"\\newcommand{{\\PlotFRAMEoReadernAve{ave_letter_index}}}{{\n"

                for type_index, (type_name, methods) in enumerate(self.reader_groups):
                    for method_index, (method_name, file, sheets) in enumerate(methods):       
                        if (ave_group_index == type_index and ave_file_index == method_index):                                        
                            for sheet_index, sheet_name in enumerate(sheets):
                                reader_cmd_index = f"{type_name}_{method_name}_{sheet_name}"
                                reader_letter_index = self.reader_index_map[reader_cmd_index]
                                plot_frame_commands += f"  \\DrawLINEo{type_name}{method_name}oReader{{\\{reader_letter_index}Data}}\n"
                            
                plot_frame_commands += f"  \\DrawLINEo{ave_letter_index}oAve{{\\DATAoROCo{ave_letter_index}}}\n"
                plot_frame_commands += "}\n\n"
        return plot_frame_commands

    def generate_readerave_group_commands(self):
        """
        Generates LaTeX commands for plotting group ROC curves.
        """
        group_commands = r"""
% Command for making one plot:
\newcommand{\PlotFIG}[1]{
\nextgroupplot[
xlabel = {\textbf{{FPF}}},
ylabel = {{\textbf{{TPF}}}},
xticklabels={{, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0}},
yticklabels={{, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0}},
] #1
}	

"""
        return group_commands

    def generate_plot_readerave_fig_commands(self):
        """
        Generates LaTeX commands for plotting figures of combined average and reader ROC curves.
        """
        plot_fig_commands = "%Command for plotting group figures"
        for ave_group_index, (ave_group_name, ave_group_data) in enumerate(self.ave_groups):
            for ave_file_index, (ave_file, ave_sheet_name) in enumerate(ave_group_data):
                ave_cmd_index = f"{ave_group_name}_{ave_sheet_name}"
                ave_letter_index = self.ave_index_map[ave_cmd_index]
                plot_fig_commands += f"""
\\newcommand{{\\PlotFIGoReadernAve{ave_letter_index}}}[0]{{
  \\PlotFIG{{\\PlotFRAMEoReadernAve{ave_letter_index}}}
}}
"""
        return plot_fig_commands

    def generate_document_body_commands(self):
        """
        Generates LaTeX commands for the body of the document.
        """
        body_commands = r""
        for ave_group_index, (ave_group_name, ave_group_data) in enumerate(self.ave_groups):
            for ave_file_index, (ave_file, ave_sheet_name) in enumerate(ave_group_data):
                ave_cmd_index = f"{ave_group_name}_{ave_sheet_name}"
                ave_letter_index = self.ave_index_map[ave_cmd_index]
                body_commands += f"\\MakeAfigure{{\\PlotFIGoReadernAve{ave_letter_index}}}\n"
        return body_commands
    
    def generate_document_body(self):
        """
        Generates the complete LaTeX document body.
        """
        body = r"\begin{document}"
        body += self.generate_document_body_commands()
        body += "\n"
        body += r"\end{document}"
        return body
    
    def generate_latex_document(self):
        """
        Generates the complete LaTeX document.
        """
        latex_document = (
            self.generate_document_header() +
            self.ave_data_commands +
            self.reader_data_commands +

            self.readerave_color_definitions +
            self.ave_plot_commands +
            self.reader_plot_commands +
            
            self.readerave_plot_frame_commands +
            self.plot_readerave_fig_commands +
            self.plot_readerave_group_commands +
            self.make_figure_command +
            
            self.header_footer +
            self.generate_document_body()
        )
        return latex_document

    def generate_latex_image(self):
        """
        Generates the LaTeX document for standalone images.
        """
        latex_document = (
            self.generate_image_header() +
            self.ave_data_commands +
            self.reader_data_commands +

            self.readerave_color_definitions +
            self.ave_plot_commands +
            self.reader_plot_commands +
            
            self.readerave_plot_frame_commands +
            self.plot_readerave_fig_commands +
            self.plot_readerave_group_commands +

            self.make_figure_command +
            
            self.header_footer +
            self.generate_document_body()
        )
        return latex_document
    
    def export_readerave_settings(self):
        """
        Exports the current settings of page_format, plot_format, and readerave_colors.
        """
        settings = {
            'page_format': self.page_format,
            'plot_format': self.plot_format,
            'readerave_colors': self.readerave_colors
        }
        return settings

    def import_readerave_settings(self, settings):
        """
        Imports settings from a JSON file to page_format, plot_format, and readerave_colors.
        """
        if isinstance(settings, str):
            with open(settings, 'r') as file:
                settings = json.load(file)
        self.page_format = settings['page_format']
        self.plot_format = settings['plot_format']
        self.readerave_colors = settings['readerave_colors']
            
        self.document_header = self.generate_document_header()
        self.make_figure_command = self.generate_make_figure_command()    
        self.readerave_color_definitions = self.generate_readerave_color_definitions()
           
if __name__ == "__main__":
    try:
        ave_files = ["Data/NP_average.xlsx", "Data/PBN_average.xlsx"]
        ave_names = ['NP', 'PBN']
        
        reader_files = [
            ["Data/QR_t_Data.xlsx", "Data/MR_t_Data.xlsx"],
            ["Data/QR_p_Data.xlsx", "Data/MR_p_Data.xlsx"]
        ]
        type_names = ["t", "p"]
        group_names = [["QR", "MR"], ["QR", "MR"]]    
        
        # ave_files = ["Data/NP_average.xlsx", "Data/PBN_average.xlsx", "Data/PBN_average.xlsx"]
        # ave_names = ['NP', 'PBN', 'PB']
        
        # reader_files = [
        #     ["Data/QR_t_Data.xlsx", "Data/MR_t_Data.xlsx"],
        #     ["Data/QR_p_Data.xlsx", "Data/MR_p_Data.xlsx"],
        #     ["Data/QR_p_Data.xlsx", "Data/MR_p_Data.xlsx"]
        # ]

        # type_names = ["t", "p", "x"]
        # group_names = [["QR", "MR"], ["QR", "MR"], ["QR", "MR"]]
        
        generator = LaTeXROCReaderAveGenerator()
        
        generator.parse_readerave_files(ave_files, reader_files, ave_names=ave_names, type_names=type_names, group_names=group_names)

        generator.set_header_info(name="ROC Reader and Average Analysis")

        # generator.set_ave_colors((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)) 
        # generator.set_header_info(author="New Author")

        # generator.set_page_format(margin=".75in", top_margin=".8in")
        output_dir = 'Output'
        os.makedirs(output_dir, exist_ok=True)
        
        export_file_path = os.path.join(output_dir, 'readerave_settings.json')
        with open(export_file_path, 'w') as file:
            json.dump(generator.export_readerave_settings(), file, indent=4)
        # generator.import_readerave_settings(export_file_path)
        
        # new_export_file_path = os.path.join(output_dir, 'new_readerave_settings.json')
        # generator.export_readerave_settings(new_export_file_path)
        
        latex_document = generator.generate_latex_document()
        with open('Output/ROC_reader_ave_analysis.tex', 'w') as f:
            f.write(latex_document)
            
        image = generator.generate_latex_image()
        with open('Output/ROC_reader_ave_image.tex', 'w') as f:
            f.write(image)
            
    except ValueError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)