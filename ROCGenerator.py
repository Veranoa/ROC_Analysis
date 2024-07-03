import sys
import os
import re
import pandas as pd
import string
import subprocess
import itertools
from datetime import datetime

class LaTeXROCGenerator:
    def __init__(self):
        self.avef_groups = []
        self.avef_index_map = {}
        self.default_colors = ['black', 'red', 'blue', 'green', 'orange']
        self.ave_colors = self.default_colors
        self.header_info = {
            "file_name": "QT BR15 Analysis (CONFIDENTIAL)",
            "author": "Author",
            "date": datetime.now().strftime("%Y/%m/%d")
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
            "label_font_size": "12pt",
            "domain": "0:1",
            "restrict_y_domain": "0:1",
            "samples": "100",
            "minor_tick_num": "1",
            "xmin": "0",
            "xmax": "1",
            "ymin": "0",
            "ymax": "1",
            "tick_label_font_size": "10pt",
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
        self.ave_data_commands = ""
        self.ave_color_definitions = ""
        self.ave_plot_commands = ""
        self.ave_plot_frame_commands = ""
        self.make_ave_figure_command = ""
        self.plot_fig_command = ""
        self.plot_avef_group_commands = ""
        self.header_footer = ""

    def clean_name(self, name):
        return re.sub(r'[^a-zA-Z0-9]', '', name)
    
    def generate_names(self, n):
        """Generate names like A, B, ..., Z, AA, AB, ..., AZ, BA, ..., ZZ, etc."""
        for size in itertools.count(1):
            for s in itertools.product(string.ascii_uppercase, repeat=size):
                yield "".join(s)
                if len(list(itertools.islice(itertools.product(string.ascii_uppercase, repeat=size), 0, None))) >= n:
                    return
                
    def parse_ave_group_files(self, group_files, group_names=None):
        groups = []
        group_names = group_names or list(self.generate_names(len(group_files)))
        for group_file, group_name in zip(group_files, group_names):
            if not os.path.exists(group_file) or not group_file.endswith('.xlsx'):
                raise ValueError(f"Error: File '{group_file}' does not exist or is not an XLSX file.")
            sheets = pd.ExcelFile(group_file).sheet_names
            group_name = self.clean_name(group_name)
            group_data = [(group_file, self.clean_name(sheet)) for sheet in sheets]
            groups.append((group_name, group_data))
            
        self.avef_groups = groups
        self.avef_index_map = self.generate_ave_index_map()
        self.num_ave_colors = max(len(group_data) for _, group_data in self.avef_groups)
        
        self.ave_data_commands = self.generate_ave_data_commands()
        self.ave_color_definitions = self.generate_ave_color_definitions()
        self.ave_plot_commands = self.generate_ave_plot_commands()
        self.ave_plot_frame_commands = self.generate_ave_plot_frame_commands()
        self.make_ave_figure_command = self.generate_make_ave_figure_command()
        self.plot_fig_command = self.generate_plot_fig_command()
        self.plot_avef_group_commands = self.generate_avef_group_commands()
        self.header_footer = self.generate_header_footer()
        
    def generate_ave_index_map(self):
        index_map = {}
        for group_name, group_data in self.avef_groups:
            for file_index, (_, sheet_name) in enumerate(group_data):
                cmd_index = f"{group_name}_{sheet_name}"
                if sheet_name.lower().startswith("sheet"):
                    letter_index = f"{group_name}{string.ascii_lowercase[file_index]}"
                else:
                    letter_index = f"{group_name}o{sheet_name}"
                index_map[cmd_index] = letter_index
        return index_map

    def generate_document_header(self):
        return """
\\documentclass[class=article, crop=false]{{standalone}}
\\usepackage[{paper_size}, {orientation}, margin={margin}, 
top={top_margin}, headsep={headsep}, headheight={headheight}, 
bottom={bottom_margin}, footskip={footskip}]{{geometry}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}
\\usepgfplotslibrary{{groupplots}}
\\usepackage{{comment}}
\\usepackage{{fancyhdr}}
\\usepackage{{textcomp}}

""".format(**self.page_format)

    def generate_image_header(self):
        return """
\documentclass{{standalone}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.18}}
\\usepgfplotslibrary{{groupplots}}
\\usepackage{{comment}}
\\usepackage{{fancyhdr}}
\\usepackage{{textcomp}}

""".format(**self.page_format)

    def generate_ave_data_commands(self):
        data_commands = "% ROC curve and AUC data:\n"
        for group_name, group_data in self.avef_groups:
            for _, (xlsx_file, sheet_name) in enumerate(group_data):
                df = pd.read_excel(xlsx_file, sheet_name=sheet_name)
                auc_name = df.columns[0]
                auc_value = df.columns[1]
                roc_data = df.iloc[1:].values
                cmd_index = f"{group_name}_{sheet_name}"
                letter_index = self.avef_index_map[cmd_index]
                data_commands += f"\\newcommand{{\\DATAoAUCo{letter_index}}}[0]{{{auc_name}: {auc_value}}}\n"
                data_commands += f"\\newcommand{{\\DATAoROCo{letter_index}}}[0]{{\n  " + "\n  ".join([f"({row[0]}, {row[1]})" for row in roc_data]) + "\n}\n\n"
        return data_commands

    def generate_ave_color_definitions(self):
        color_definitions = "% Define ROC curve colors:\n"
        for i, color in enumerate(self.ave_colors):
            color_definitions += f"\\definecolor{{COLORo{i}}}{{named}}{{{color}}}\n"
        color_definitions += "\n"
        return color_definitions

    def generate_ave_plot_commands(self):
        plot_commands = "% Command for plotting ROC curves in one plot:\n"
        for group_name, group_data in self.avef_groups:
            for file_index, (_, sheet_name) in enumerate(group_data):
                cmd_index = f"{group_name}_{sheet_name}"
                letter_index = self.avef_index_map[cmd_index]
                plot_commands += f"\\newcommand{{\\DrawLINEo{letter_index}}}[2]{{\n"
                plot_commands += f"\\addplot[\n  color=COLORo{file_index % len(self.ave_colors)},\n  mark=dot,\n  on layer={{axis foreground}},\n] coordinates {{#1}};\n"
                plot_commands += f"\\addlegendentry{{#2}}\n}}\n\n"
        return plot_commands

    def generate_ave_plot_frame_commands(self):
        plot_frame_commands = "% Commands for plotting grouped ROC curves:\n"
        for group_name, group_data in self.avef_groups:
            plot_frame_commands += f"\\newcommand{{\\PlotFRAMEo{group_name}}}{{\n"
            for file_index, (_, sheet_name) in enumerate(group_data):
                cmd_index = f"{group_name}_{sheet_name}"
                letter_index = self.avef_index_map[cmd_index]
                plot_frame_commands += f"  \\DrawLINEo{letter_index}{{\\DATAoROCo{letter_index}}}{{\\DATAoAUCo{letter_index}}}\n"
            plot_frame_commands += "}\n\n"
        return plot_frame_commands

    def generate_make_ave_figure_command(self):
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
  label style={{font={{\\fontsize{{{label_font_size}}}{{{label_font_size}}}\\selectfont}}}},
  domain={domain},
  restrict y to domain={restrict_y_domain},
  samples={samples},
  minor tick num={minor_tick_num},
  xmin={xmin}, xmax={xmax},
  ymin={ymin}, ymax={ymax},
  xticklabels={{, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0}},
  yticklabels={{, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0}},
  tick label style={{font={{\\fontsize{{{tick_label_font_size}}}{{{tick_label_font_size}}}\\selectfont}}}},
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

    def generate_avef_group_commands(self):
        group_commands = ""
        for group_name, _ in self.avef_groups:
            group_commands += f"""
% Command for plotting group {group_name} figures:
\\newcommand{{\\PlotFIGo{group_name}}}[0]{{
  \\PlotFIG{{\\PlotFRAMEo{group_name}}}
}}
"""
        return group_commands

    def generate_header_footer(self):
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

    def generate_document_body(self):
        body = r"\begin{document}"
        for group_name, _ in self.avef_groups:
            body += f"\n\\MakeAfigure{{\\PlotFIGo{group_name}}}"
        body += "\n"
        body += r"\end{document}"
        return body

    def set_ave_colors(self, *colors):
        if isinstance(colors[0], tuple) and len(colors) == 2 and isinstance(colors[1], tuple):
            self.ave_colors = [self.default_colors] * len(self.avef_groups)
            for color in colors:
                if isinstance(color, tuple) and len(color) == 3:
                    for group_index, group_color in enumerate(color):
                        if group_index < len(self.avef_groups):
                            self.ave_colors[group_index] = group_color
        else:
            self.ave_colors = colors
        self.ave_color_definitions = self.generate_ave_color_definitions()

    def set_header_info(self, name=None, author=None, date=None):
        if name:
            self.header_info["file_name"] = name
        if author:
            self.header_info["author"] = author
        if date:
            self.header_info["date"] = date
        self.header_footer = self.generate_header_footer()

    def set_page_format(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.page_format:
                self.page_format[key] = value
        self.document_header = self.generate_document_header()

    def set_plot_format(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.plot_format:
                if isinstance(self.plot_format[key], dict):
                    self.plot_format[key].update(value)
                else:
                    self.plot_format[key] = value
        self.make_ave_figure_command = self.generate_make_ave_figure_command()             

    def generate_latex_document(self):
        latex_document = (
            self.generate_document_header() +
            self.ave_data_commands +
            self.ave_color_definitions +
            self.ave_plot_commands +
            self.ave_plot_frame_commands +
            self.make_ave_figure_command +
            self.plot_fig_command +
            self.plot_avef_group_commands +
            self.header_footer +
            self.generate_document_body()
        )
        
        return latex_document
    
    def generate_latex_image(self):
        image_document = (
            self.generate_image_header() +
            self.ave_data_commands +
            self.ave_color_definitions +
            self.ave_plot_commands +
            self.ave_plot_frame_commands +
            self.make_ave_figure_command +
            self.plot_fig_command +
            self.plot_avef_group_commands +
            self.generate_document_body()
        )
        return image_document

    def generate_pdf(self, tex_file_path, output_dir):
        try:
            subprocess.run(['pdflatex', '-output-directory', output_dir, tex_file_path], check=True)
            print(f"PDF generated successfully: {os.path.join(output_dir, os.path.basename(tex_file_path).replace('.tex', '.pdf'))}")
        except subprocess.CalledProcessError as e:
            print(f"Error during PDF generation: {e}")

    def update_group_names(self, new_group_names):
        if len(new_group_names) != len(self.avef_groups):
            raise ValueError("Number of new group names must match the number of groups.")
        self.avef_groups = [(new_name, group_data) for new_name, (_, group_data) in zip(new_group_names, self.avef_groups)]
        self.avef_index_map = self.generate_ave_index_map()
        
        self.ave_data_commands = self.generate_ave_data_commands()
        self.ave_color_definitions = self.generate_ave_color_definitions()
        self.ave_plot_commands = self.generate_ave_plot_commands()
        self.ave_plot_frame_commands = self.generate_ave_plot_frame_commands()
        self.make_ave_figure_command = self.generate_make_ave_figure_command()
        self.plot_fig_command = self.generate_plot_fig_command()
        self.plot_avef_group_commands = self.generate_avef_group_commands()
        self.header_footer = self.generate_header_footer()
        

if __name__ == "__main__":
    try:
        group_files = ["Data/NP.xlsx", "Data/PBN.xlsx"]
        generator = LaTeXROCGenerator()
        
        generator.parse_ave_group_files(group_files)

        # Modify colors or header information as needed
        generator.set_header_info(author="New Author")

        # Modify colors or header information as needed
        generator.set_ave_colors("red", "blue")  # Red and blue
        generator.set_header_info(author="New Author")

        # Modify page format or plot format as needed
        generator.set_page_format(margin=".75in", top_margin=".8in")
        generator.set_plot_format(width="3in", height="3in", tick_style={"draw": "red"}, legend_style={"anchor": "west"})

        # Generate full document
        latex_document = generator.generate_latex_document()
        output_dir = 'Output'
        os.makedirs(output_dir, exist_ok=True)
        
        doc_file_path = os.path.join(output_dir, 'output.tex')
        with open(doc_file_path, 'w') as f:
            f.write(latex_document)
        
        image = generator.generate_latex_image()
        image_file_path = os.path.join(output_dir, 'image.tex')
        with open(image_file_path, 'w') as f:
            f.write(image)

        # Update group names if needed
        new_group_names = ["NewNP", "NewPBN"]
        generator.update_group_names(new_group_names)
        latex_document = generator.generate_latex_document()
        doc_file_path = os.path.join(output_dir, 'updated_output.tex')
        with open(doc_file_path, 'w') as f:
            f.write(latex_document)
                        
    except ValueError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
       