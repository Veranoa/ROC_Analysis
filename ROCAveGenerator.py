# ROCAveGenerator.py
#
# Copyright (C) 2024-2030 Yun Liu
# University of Chicago
#
# LaTeX ROC Average Generator
#

import sys
import os
import re
import json
import pandas as pd
import string
import subprocess
import itertools
from datetime import datetime
from TexGenerator import LaTeXGenerator


class LaTeXROCAveGenerator(LaTeXGenerator):
    def __init__(self):
        super().__init__()
        self.ave_groups = []
        self.ave_index_map = {}
        self.ave_colors = []

        self.ave_data_commands = ""
        self.ave_color_definitions = ""
        self.ave_plot_commands = ""
        self.ave_plot_frame_commands = ""

        self.plot_ave_group_commands = ""

    def clean_name(self, name):
        """
        Cleans the group or sheet name by removing non-alphanumeric characters.
        """
        return re.sub(r'[^a-zA-Z0-9]', '', name)

    def parse_ave_files(self, group_files, ave_names=None, engine='openpyxl'):
        """
        Parses multiple Excel files to extract ROC data and organize it into groups.
        """
        groups = []
        ave_names = ave_names or list(
            string.ascii_uppercase[:len(group_files)])
        for group_file, group_name in zip(group_files, ave_names):
            if not os.path.exists(group_file) or not group_file.endswith('.xlsx'):
                raise ValueError(
                    f"Error: File '{group_file}' does not exist or is not an XLSX file.")
            sheets = pd.ExcelFile(group_file, engine=engine).sheet_names
            group_name = self.clean_name(group_name)
            group_data = [(group_file, self.clean_name(sheet))
                          for sheet in sheets]
            groups.append((group_name, group_data))

        self.ave_groups = groups
        self.ave_index_map = self.generate_ave_index_map()
        self.num_ave_colors = max(len(group_data)
                                  for _, group_data in self.ave_groups)
        if not self.ave_colors:
            self.ave_colors = self.default_colors[:self.num_ave_colors]

        self.ave_data_commands = self.generate_ave_data_commands()
        self.ave_color_definitions = self.generate_ave_color_definitions()
        self.ave_plot_commands = self.generate_ave_plot_commands()
        self.ave_plot_frame_commands = self.generate_ave_plot_frame_commands()
        self.make_figure_command = self.generate_make_figure_command()
        self.plot_fig_command = self.generate_plot_fig_command()
        self.plot_ave_group_commands = self.generate_ave_group_commands()
        self.header_footer = self.generate_header_footer()

    def generate_ave_index_map(self):
        """
        Generates an index map for the ROC groups and their respective data sheets.
        """
        index_map = {}
        for group_name, group_data in self.ave_groups:
            for file_index, (_, sheet_name) in enumerate(group_data):
                cmd_index = f"{group_name}_{sheet_name}"
                if sheet_name.lower().startswith("sheet"):
                    letter_index = f"{group_name}{string.ascii_lowercase[file_index]}"
                else:
                    letter_index = f"{group_name}o{sheet_name}"
                index_map[cmd_index] = letter_index
        return index_map

    def generate_ave_data_commands(self, engine='openpyxl'):
        """
        Generates LaTeX commands for ROC data from the parsed Excel files.
        """
        data_commands = "% ROC curve and AUC data:\n"
        for group_name, group_data in self.ave_groups:
            for _, (xlsx_file, sheet_name) in enumerate(group_data):
                df = pd.read_excel(
                    xlsx_file, sheet_name=sheet_name, engine=engine)
                auc_name = df.columns[0]
                auc_value = df.columns[1]
                roc_data = df.iloc[1:].values
                cmd_index = f"{group_name}_{sheet_name}"
                letter_index = self.ave_index_map[cmd_index]
                data_commands += f"\\newcommand{{\\DATAoAUCo{letter_index}}}[0]{{{auc_name}: {auc_value}}}\n"
                data_commands += f"\\newcommand{{\\DATAoROCo{letter_index}}}[0]{{\n  " + "\n  ".join(
                    [f"({row[0]}, {row[1]})" for row in roc_data]) + "\n}\n\n"
        return data_commands

    def generate_ave_color_definitions(self):
        """
        Generates LaTeX commands to define colors for ROC curves.
        """
        color_definitions = "% Define ROC curve colors:\n"
        for i, color in enumerate(self.ave_colors):
            color_definitions += f"\\definecolor{{COLORo{i}}}{{rgb}}{color}\n"
        color_definitions += "\n"
        return color_definitions

    def generate_ave_plot_commands(self):
        """
        Generates LaTeX commands for plotting individual ROC curves.
        """
        plot_commands = "% Command for plotting ROC curves in one plot:\n"
        for group_name, group_data in self.ave_groups:
            for file_index, (_, sheet_name) in enumerate(group_data):
                cmd_index = f"{group_name}_{sheet_name}"
                letter_index = self.ave_index_map[cmd_index]
                plot_commands += f"\\newcommand{{\\DrawLINEo{letter_index}}}[2]{{\n"
                plot_commands += f"\\addplot[\n  color=COLORo{file_index % len(self.ave_colors)},\n  mark=dot,\n  on layer={{axis foreground}},\n] coordinates {{#1}};\n"
                plot_commands += f"\\addlegendentry{{#2}}\n}}\n\n"
        return plot_commands

    def generate_ave_plot_frame_commands(self):
        """
        Generates LaTeX commands for plotting grouped ROC curves.
        """
        plot_frame_commands = "% Commands for plotting grouped ROC curves:\n"
        for group_name, group_data in self.ave_groups:
            plot_frame_commands += f"\\newcommand{{\\PlotFRAMEo{group_name}}}{{\n"
            for file_index, (_, sheet_name) in enumerate(group_data):
                cmd_index = f"{group_name}_{sheet_name}"
                letter_index = self.ave_index_map[cmd_index]
                plot_frame_commands += f"  \\DrawLINEo{letter_index}{{\\DATAoROCo{letter_index}}}{{\\DATAoAUCo{letter_index}}}\n"
            plot_frame_commands += "}\n\n"
        return plot_frame_commands

    def generate_plot_fig_command(self):
        """
        Generates LaTeX commands for plotting figures.
        """
        return r"""
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

    def generate_ave_group_commands(self):
        """
        Generates LaTeX commands for plotting ROC curves for each group.
        """
        group_commands = ""
        for group_name, _ in self.ave_groups:
            group_commands += f"""
% Command for plotting group {group_name} figures:
\\newcommand{{\\PlotFIGo{group_name}}}[0]{{
  \\PlotFIG{{\\PlotFRAMEo{group_name}}}
}}
"""
        return group_commands

    def generate_document_body_commands(self):
        """
        Generates LaTeX commands for the body of the document.
        """
        body_commands = r""
        for group_name, _ in self.ave_groups:
            body_commands += f"\n\\MakeAfigure{{\\PlotFIGo{group_name}}}"
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

    def set_ave_colors(self, *colors):
        """
        Sets the colors for the ROC curves. Colors can be provided as a list or tuples.
        """
        if isinstance(colors[0], tuple) and len(colors) == 2 and isinstance(colors[1], tuple):
            self.ave_colors = [self.default_colors] * len(self.ave_groups)
            for color in colors:
                if isinstance(color, tuple) and len(color) == 3:
                    for group_index, group_color in enumerate(color):
                        if group_index < len(self.ave_groups):
                            self.ave_colors[group_index] = group_color
        else:
            self.ave_colors = colors
        self.ave_color_definitions = self.generate_ave_color_definitions()

    def generate_latex_document(self):
        """
        Generates the complete LaTeX document.
        """
        latex_document = (
            self.generate_document_header() +
            self.ave_data_commands +
            self.ave_color_definitions +
            self.ave_plot_commands +
            self.ave_plot_frame_commands +
            self.make_figure_command +
            self.plot_fig_command +
            self.plot_ave_group_commands +
            self.header_footer +
            self.generate_document_body()
        )

        return latex_document

    def generate_latex_image(self):
        """
        Generates the LaTeX document for standalone images.
        """
        image_document = (
            self.generate_image_header() +
            self.ave_data_commands +
            self.ave_color_definitions +
            self.ave_plot_commands +
            self.ave_plot_frame_commands +
            self.make_figure_command +
            self.plot_fig_command +
            self.plot_ave_group_commands +
            self.generate_document_body()
        )
        return image_document

    def generate_pdf(self, tex_file_path, output_dir):
        """
        Generates a PDF from the LaTeX file.
        """
        try:
            subprocess.run(['pdflatex', '-output-directory',
                           output_dir, tex_file_path], check=True)
            print(
                f"PDF generated successfully: {os.path.join(output_dir, os.path.basename(tex_file_path).replace('.tex', '.pdf'))}")
        except subprocess.CalledProcessError as e:
            print(f"Error during PDF generation: {e}")

    def update_group_names(self, new_group_names):
        """
        Updates the names of the ROC groups.
        """
        if len(new_group_names) != len(self.ave_groups):
            raise ValueError(
                "Number of new group names must match the number of groups.")
        self.ave_groups = [(new_name, group_data) for new_name, (_, group_data) in zip(
            new_group_names, self.ave_groups)]
        self.ave_index_map = self.generate_ave_index_map()

        self.ave_data_commands = self.generate_ave_data_commands()
        self.ave_color_definitions = self.generate_ave_color_definitions()
        self.ave_plot_commands = self.generate_ave_plot_commands()
        self.ave_plot_frame_commands = self.generate_ave_plot_frame_commands()
        self.make_figure_command = self.generate_make_figure_command()
        self.plot_fig_command = self.generate_plot_fig_command()
        self.plot_ave_group_commands = self.generate_ave_group_commands()
        self.header_footer = self.generate_header_footer()

    def export_ave_settings(self):
        """
        Exports the current settings of page_format, plot_format, and ave_colors.
        """
        settings = {
            'page_format': self.page_format,
            'plot_format': self.plot_format,
            'ave_colors': self.ave_colors
        }
        return settings

    def import_ave_settings(self, settings):
        """
        Imports settings from a JSON file to page_format, plot_format, and ave_colors.
        """
        if isinstance(settings, str):
            with open(settings, 'r') as file:
                settings = json.load(file)

        self.page_format = settings['page_format']
        self.plot_format = settings['plot_format']
        self.ave_colors = settings['ave_colors']

        # Update the dependent variables
        self.document_header = self.generate_document_header()
        self.make_figure_command = self.generate_make_figure_command()
        self.ave_color_definitions = self.generate_ave_color_definitions()


if __name__ == "__main__":
    try:
        ave_files = ["Data/NP_average.xlsx"]
        ave_names = ['NP']

        # group_files = ["Data/NP_average.xlsx", "Data/PBN_average.xlsx", "Data/PBN_average.xlsx"]
        # group_names = ['NP', 'PBN', 'PB']
        generator = LaTeXROCAveGenerator()

        generator.parse_ave_files(ave_files, ave_names)

        # Modify colors or header information as needed
        generator.set_header_info(author="Author", name="ROC Average Analysis")

        output_dir = 'Output'
        os.makedirs(output_dir, exist_ok=True)

        # Generate full document
        export_file_path = os.path.join(output_dir, 'average_settings.json')
        with open(export_file_path, 'w') as file:
            json.dump(generator.export_ave_settings(), file, indent=4)

        # generator.import_ave_settings(export_file_path)
        # new_export_file_path = os.path.join(
        #     output_dir, 'new_average_settings.json')
        # with open(new_export_file_path, 'w') as file:
        #     json.dump(generator.export_ave_settings(), file, indent=4)

        latex_document = generator.generate_latex_document()
        doc_file_path = os.path.join(output_dir, 'ROC_average_analysis.tex')
        with open(doc_file_path, 'w') as f:
            f.write(latex_document)

        image = generator.generate_latex_image()
        image_file_path = os.path.join(output_dir, 'ROC_average_image.tex')
        with open(image_file_path, 'w') as f:
            f.write(image)

    except ValueError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")