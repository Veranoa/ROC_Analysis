# ROCBoxGenerator.py
#
# Copyright (C) 2024-2030 Yun Liu
# University of Chicago
#
# LaTeX ROC Box Generator
#

import sys
import os
import re
import pandas as pd
import json
import string
import subprocess
from datetime import datetime
from ROCGenerator import LaTeXROCGenerator

class LaTeXROCBoxGenerator(LaTeXROCGenerator):
    def __init__(self):
        super().__init__()
        self.box_file = None
        self.box_data_commands = ""
        self.box_plot_commands = ""
        self.plot_format = {
            "xlabel": r"\textbf{Reader(s)}",
            "ylabel": r"\textbf{QT POM--FFDM POM}",
            "height": "12cm",
            "draw": "black",
            "fill": "yellow",
        }
        self.numeric_xticklabels = False

    def parse_box_file(self, box_file):
        """
        Parses the box plot CSV file and generates the necessary LaTeX commands.
        """
        self.box_file = box_file
        self.box_data_commands = self.generate_box_data_commands()
        self.box_plot_commands = self.generate_box_plot_commands()

    def generate_box_data_commands(self):
        """
        Generates LaTeX commands for box plot data from the parsed CSV file.
        """
        df = pd.read_csv(self.box_file)
        xticklabels = list(df.iloc[:, 0])
        self.plot_format["xticklabels"] = "{" + ", ".join(map(str, xticklabels)) + "}"
        self.plot_format["xticklabels_label"] = "{" + ", ".join(map(str, xticklabels)) + "}"
        self.plot_format["xticklabels_numeric"] = "{" + ", ".join([str(i) for i in range(1, len(xticklabels) + 1)]) + "}"

        box_data = r'''
\pgfplotsset{compat=1.16}
\usepgfplotslibrary{statistics}
\pgfplotstableread{
Reader max avg median min n qfirst qthird deviation
'''
        for index, row in df.iterrows():
            box_data += f"{row['Reader']} {row['max']} {row['avg']} {row['median']} {row['min']} {row['n']} {row['qfirst']} {row['qthird']} {row['deviation']}\n"

        box_data += r'''}
\datatable
'''
        return box_data
    
    def generate_box_plot_commands(self):
        """
        Generates LaTeX commands for creating box plots.
        """
        if self.numeric_xticklabels:
            self.plot_format["xticklabels"] = self.plot_format["xticklabels_numeric"]
        else:
            self.plot_format["xticklabels"] = self.plot_format["xticklabels_label"]

        box_plot_str = r'''
\begin{tikzpicture}
\pgfplotstablegetrowsof{\datatable}
\pgfmathtruncatemacro{\rownumber}{\pgfplotsretval-1}
\begin{axis}[boxplot/draw direction=y,
    xticklabels={xticklabels},
    xtick={1,...,\the\numexpr\rownumber+1},
    xlabel={xlabel},
    ylabel={ylabel},
    height={height}]
    
\pgfplotsinvokeforeach{0,...,\rownumber}{
    \pgfplotstablegetelem{#1}{min}\of\datatable
    \edef\mymin{\pgfplotsretval}
    \pgfplotstablegetelem{#1}{avg}\of\datatable
    \edef\myavg{\pgfplotsretval}
    \pgfplotstablegetelem{#1}{max}\of\datatable
    \edef\mymax{\pgfplotsretval}
    \pgfplotstablegetelem{#1}{median}\of\datatable
    \edef\mymedian{\pgfplotsretval}
    \pgfplotstablegetelem{#1}{deviation}\of\datatable
    \edef\mydeviation{\pgfplotsretval}
    \pgfplotstablegetelem{#1}{qfirst}\of\datatable
    \edef\myqfirst{\pgfplotsretval}
    \pgfplotstablegetelem{#1}{qthird}\of\datatable
    \edef\myqthird{\pgfplotsretval}
    \typeout{\mymin,\mymax,\myavg,\mymedian,\mydeviation,\myqfirst,\myqthird}
    \edef\temp{\noexpand\addplot[
        boxplot prepared={
         lower whisker=\mymin,
         upper whisker=\mymax,
         lower quartile=\myqfirst,
         upper quartile=\myqthird,
         median=\mymedian,
         average=\myavg,
         every  box/.style={draw={draw},fill={fill}},
      }
      ]coordinates {};}
    \temp
}
\end{axis}
\end{tikzpicture}
'''
        for key, value in self.plot_format.items():
            box_plot_str = box_plot_str.replace(f"{key}={{{key}}}", f"{key}={value}")
        return box_plot_str

    def generate_document_body_commands(self):
        """
        Generates LaTeX commands for the body of the document.
        """
        body_commands = ""
        body_commands += self.box_data_commands
        body_commands += self.box_plot_commands
        return body_commands
    
    def generate_document_body(self):
        """
        Generates the complete LaTeX document body.
        """
        body = "\\begin{document}\n"
        body += self.generate_document_body_commands()
        body += self.generate_header_footer()
        body += "\n"
        body += "\\end{document}"
        return body
    
    def generate_latex_document(self):
        """
        Generates the complete LaTeX document.
        """
        return (
            self.generate_document_header() +
            self.generate_document_body() 
        )

    def generate_latex_image(self):
        """
        Generates the LaTeX document for standalone images.
        """
        return (
            self.generate_image_header() +
            self.generate_document_body() 
        )
        
    def set_box_plot_format(self, **kwargs):
        """
        Sets the box plot format options.
        """
        for key, value in kwargs.items():
            if key in self.plot_format:
                self.plot_format[key] = value
    
    def set_numeric_xticklabels(self, numeric):
        """
        Sets whether the x-tick labels should be numeric.
        """
        self.numeric_xticklabels = numeric
  
# Usage example
if __name__ == "__main__":
    box_generator = LaTeXROCBoxGenerator()
    box_generator.parse_box_file("Data/bar.csv") 
    latex_document = box_generator.generate_latex_document()
    image_document = box_generator.generate_latex_image()

    output_dir = 'Output'
    os.makedirs(output_dir, exist_ok=True)
        
    export_file_path = os.path.join(output_dir, 'box_settings.json')
    box_generator.export_settings(export_file_path)
    # box_generator.import_settings(export_file_path)
        
    # new_export_file_path = os.path.join(output_dir, 'new_settings.json')
    # box_generator.export_settings(new_export_file_path)
        
    with open('Output/ROC_Box_analysis.tex', 'w') as file:
        file.write(latex_document)

    with open('Output/ROC_Box_image.tex', 'w') as file:
        file.write(image_document)