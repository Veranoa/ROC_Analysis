# TexGenerator.py
#
# Copyright (C) 2024-2030 Yun Liu
# University of Chicago
#
# LaTeX Generator
# 


import sys
import os
import re
import pandas as pd
import string
import subprocess
import itertools
from datetime import datetime
import json

class LaTeXGenerator:
    def __init__(self):
        self.default_colors = [
            '{0, 0, 1}',   # blue
            '{1, 0, 0}',   # red
            '{0, 0, 0}',   # black
            '{0, 1, 0}',   # green
            '{1, 0.65, 0}' # orange
        ]

        self.header_info = {
            "file_name": "ROC Analysis",
            "author": "Author",
            "date": datetime.now().strftime("%Y/%m/%d")  # Default header information
        }
        self.page_format = {
            "paper_size": "letterpaper",
            "orientation": "portrait",
            "margin": ".5in",
            "top_margin": ".7in",
            "headsep": ".1in",
            "headheight": ".1in",
            "bottom_margin": ".7in",
            "footskip": ".2in"  
        }
        self.plot_format = {
            "horizontal_size":"3",
            "vertical_size":"4",
            "horizontal_sep": "0pt",
            "vertical_sep": "0pt",
            "width": "2.8in",
            "height": "2.8in",
            "label_font_size_1": "12pt",
            "label_font_size_2": "14",
            "domain": "0:1",
            "restrict_y_domain": "0:1",
            "samples": "100",
            "minor_tick_num": "1",
            "xmin": "0",
            "xmax": "1",
            "ymin": "0",
            "ymax": "1",
            "x_ticklabels" : "{, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0}",
            "y_ticklabels" : "{, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0}",
            "tick_label_font_size_1": "10pt",
            "tick_label_font_size_2": "12pt",
            "tick_style": {
                "line width": "0.25pt",
                "color": "black",
                "line cap": "round"
            },
            "legend_style": {
                "at": "{(0.25,0.2)}",
                "anchor": "west",
                "fill": "none",
                "font": "\\fontsize{10pt}{12pt}\\selectfont"
            }  
        }
        
        self.make_figure_command = ""
        self.plot_fig_command = ""
        self.header_footer = self.generate_header_footer()

    def generate_document_header(self):
        """
        Generates the LaTeX document header based on the current page formatting options.
        """
        return """
\\documentclass[class=article, crop=false]{{standalone}}
\\usepackage[{paper_size}, {orientation}, margin={margin}, 
top={top_margin}, headsep={headsep}, headheight={headheight}, 
bottom={bottom_margin}, footskip={footskip}]{{geometry}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.17}}
\\usepgfplotslibrary{{groupplots}}
\\usepackage{{comment}}
\\usepackage{{fancyhdr}}
\\usepackage{{textcomp}}
\\usepackage{{pgfplotstable}}
\\usepackage{{tagging}}

""".format(**self.page_format)

    def generate_image_header(self):
        """
        Generates the LaTeX header for standalone image files.
        """
        return """
\\documentclass{{standalone}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.17}}
\\usepgfplotslibrary{{groupplots}}
\\usepackage{{comment}}
\\usepackage{{fancyhdr}}
\\usepackage{{textcomp}}
\\usepackage{{pgfplotstable}}
\\usepackage{{tagging}}

""".format(**self.page_format)

    def generate_make_figure_command(self):
        """
        Generates the LaTeX command for creating ROC figure plots.
        """
        tick_style = ", ".join([f"{k}={v}" for k, v in self.plot_format["tick_style"].items()])
        legend_style = ", ".join([f"{k}={v}" for k, v in self.plot_format["legend_style"].items()])
        plot_format_combined = self.plot_format.copy()
        plot_format_combined.update({"tick_style": tick_style, "legend_style": legend_style})
        return """
% Command for plotting a figure of a group of ROC curves:
\\newcommand{{\\MakeAfigure}}[1]{{
\\begin{{center}}
\\begin{{tikzpicture}}
\\begin{{groupplot}}[
  group style={{group size={horizontal_size} by {vertical_size},
  horizontal sep={horizontal_sep}, vertical sep={vertical_sep}}},
  width={width},
  height={height},
  label style={{font={{\\fontsize{{{label_font_size_1}}}{{{label_font_size_2}}}\\selectfont}}}},
  domain={domain},
  restrict y to domain={restrict_y_domain},
  samples={samples},
  minor tick num={minor_tick_num},
  xmin={xmin}, xmax={xmax},
  ymin={ymin}, ymax={ymax},
  xticklabels={x_ticklabels},
  yticklabels={y_ticklabels},
  tick label style={{font={{\\fontsize{{{tick_label_font_size_1}}}{{{tick_label_font_size_2}}}\\selectfont}}}},
  tick style={{{tick_style}}},
  legend style={{{legend_style}}},
  set layers=standard,
] #1
\\end{{groupplot}}
\\end{{tikzpicture}}
\\end{{center}}
}}

""".format(**plot_format_combined)

    def generate_plot_fig_command(self):
        pass

    def generate_header_footer(self):
        """
        Generates the LaTeX header and footer based on the current header information.
        """
        return f"""
% Document header and footer:
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[LE,LO]{{{self.header_info['file_name']}}}
\\fancyhead[RE,RO]{{{self.header_info['author']}, {self.header_info['date']}}}
\\fancyfoot[RE,RO]{{\\thepage}}
\\renewcommand{{\\headrulewidth}}{{.2pt}}
\\renewcommand{{\\footrulewidth}}{{.2pt}}

"""
    def generate_document_body_commands(self):
        """
        Placeholder for generating the document body commands.
        """
        pass

    def generate_document_body(self):
        """
        Generates the complete LaTeX document body.
        """
        body = r"\begin{document}"
        body += self.generate_document_body_commands()
        body += "\n"
        body += r"\end{document}"
        return body

    def set_header_info(self, name=None, author=None, date=None):
        """
        Sets the header information and regenerates the header/footer.
        """
        if name:
            self.header_info["file_name"] = name
        if author:
            self.header_info["author"] = author
        if date:
            self.header_info["date"] = date
        self.header_footer = self.generate_header_footer()

    def set_page_format(self, **kwargs):
        """
        Sets the page formatting options and regenerates the document header.
        """
        for key, value in kwargs.items():
            if key in self.page_format:
                self.page_format[key] = value
        self.document_header = self.generate_document_header()

    def set_plot_format(self, **kwargs):
        """
        Sets the plot formatting options and regenerates the make figure command.
        """
        for key, value in kwargs.items():
            if key in self.plot_format:
                if isinstance(self.plot_format[key], dict):
                    self.plot_format[key].update(value)
                else:
                    self.plot_format[key] = value
        self.make_figure_command = self.generate_make_figure_command() 
        
    def export_settings(self):
        """
        Exports the current settings of page_format, and plot_format to settings.
        """
        settings = {
            'page_format': self.page_format,
            'plot_format': self.plot_format
        }
        return settings
    
    def import_settings(self, settings):
        """
        Imports settings from a JSON file to page_format, and plot_format.
        """
        if isinstance(settings, str):
            with open(settings, 'r') as file:
                settings = json.load(file)
        self.page_format = settings['page_format']
        self.plot_format = settings['plot_format']

        self.document_header = self.generate_document_header()
        self.make_figure_command = self.generate_make_figure_command()    
            
    def generate_latex_document(self):
        pass
    
    def generate_latex_image(self):
        pass

    def generate_pdf(self, tex_file_path, output_dir):
        pass
