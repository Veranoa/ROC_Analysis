# ROCConfidenceGenerator.py
#
# Copyright (C) 2024-2030 Yun Liu
# University of Chicago
#
# LaTeX ROC Confidence Generator
#

from TexGenerator import LaTeXGenerator
import sys
import os
import json

class LaTeXConfidenceGenerator(LaTeXGenerator):
    def __init__(self):
        super().__init__()
        self.confidence_data = {}
        self.make_figure_command = self.generate_make_figure_command()

        # Default settings for customization
        self.ellipse_color = "blue"
        self.point_color = "red"
        self.box_color = "black"
        self.point_size = 1.0
        self.ellipse_line_width = 1.0
        self.box_line_width = 1.0

    def set_confidence_data(self, fpf, tpf, fpf_lower, fpf_upper, tpf_lower, tpf_upper):
        """
        Set the confidence data for the ROC plot.
        """
        self.confidence_data = {
            "fpf": fpf,
            "tpf": tpf,
            "fpf_lower": fpf_lower,
            "fpf_upper": fpf_upper,
            "tpf_lower": tpf_lower,
            "tpf_upper": tpf_upper
        }

    def set_customization(self, ellipse_color=None, point_color=None, box_color=None,
                          point_size=None, ellipse_line_width=None, box_line_width=None):
        """
        Customize colors, point size, and line widths.
        """
        if ellipse_color:
            self.ellipse_color = ellipse_color
        if point_color:
            self.point_color = point_color
        if box_color:
            self.box_color = box_color
        if point_size:
            self.point_size = point_size
        if ellipse_line_width:
            self.ellipse_line_width = ellipse_line_width
        if box_line_width:
            self.box_line_width = box_line_width

    def generate_confidence_commands(self):
        """
        Generate LaTeX commands for plotting the confidence intervals and the ellipse with customization.
        """
        commands = f"""
% Command for plotting the confidence interval box, ellipse, and point:
\\newcommand{{\\DrawConfidence}}[0]{{%
  \\addplot[color={self.point_color}, mark=*, mark size={self.point_size}, only marks] coordinates {{({self.confidence_data['fpf']}, {self.confidence_data['tpf']})}};
  \\draw[dashed, color={self.box_color}, line width={self.box_line_width}pt] (axis cs:{self.confidence_data['fpf_lower']}, {self.confidence_data['tpf_lower']}) rectangle (axis cs:{self.confidence_data['fpf_upper']}, {self.confidence_data['tpf_upper']});
  \\draw[draw, color={self.ellipse_color}, line width={self.ellipse_line_width}pt] (axis cs:{(self.confidence_data['fpf_upper'] + self.confidence_data['fpf_lower'])/2}, {(self.confidence_data['tpf_upper'] + self.confidence_data['tpf_lower'])/2}) ellipse [x radius={(self.confidence_data['fpf_upper'] - self.confidence_data['fpf_lower'])/2}, y radius={(self.confidence_data['tpf_upper'] - self.confidence_data['tpf_lower'])/2}];
}}
"""
        return commands

    def generate_plot_fig_command(self):
        """
        Generates LaTeX commands for plotting figures with confidence intervals.
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

% Command for plotting confidence interval figure:
\newcommand{\PlotConfidenceFIG}[0]{
  \PlotFIG{\DrawConfidence}
}
"""

    def generate_latex_document(self):
        """
        Generate the complete LaTeX document for the confidence result.
        """
        confidence_commands = self.generate_confidence_commands()
        plot_fig_command = self.generate_plot_fig_command()

        latex_document = (
            self.generate_document_header() +
            confidence_commands +
            plot_fig_command +
            self.make_figure_command +
            self.generate_header_footer() +
            self.generate_document_body()
        )

        return latex_document

    def generate_latex_image(self):
        """
        Generate the LaTeX document for a standalone image.
        """
        confidence_commands = self.generate_confidence_commands()
        plot_fig_command = self.generate_plot_fig_command()

        image_document = (
            self.generate_image_header() +
            confidence_commands +
            plot_fig_command +
            self.make_figure_command +
            self.generate_document_body()
        )
        return image_document

    def generate_document_body_commands(self):
        """
        Generate the body commands specific to the confidence interval plot.
        """
        body_commands = "\n\\MakeAfigure{\\PlotConfidenceFIG}"
        return body_commands

    def export_confidence_settings(self):
        """
        Export current settings to a dictionary.
        """
        # Check if the parent class has export_settings method
        settings = {}
        if hasattr(super(), 'export_settings'):
            settings = super().export_settings()
        else:
            # If the parent class does not have export_settings, proceed without it
            print("Parent class does not have export_settings method")

        # Add current class-specific settings
        settings.update({
            'ellipse_color': self.ellipse_color,
            'point_color': self.point_color,
            'box_color': self.box_color,
            'point_size': self.point_size,
            'ellipse_line_width': self.ellipse_line_width,
            'box_line_width': self.box_line_width
        })
        return settings

    def import_confidence_settings(self, settings):
        """
        Import settings from a dictionary.
        """
        # Check if the parent class has import_settings method
        if hasattr(super(), 'import_settings'):
            super().import_settings(settings)
        else:
            # If the parent class does not have import_settings, proceed without it
            print("Parent class does not have import_settings method")

        # Set current class-specific settings
        self.ellipse_color = settings.get('ellipse_color', self.ellipse_color)
        self.point_color = settings.get('point_color', self.point_color)
        self.box_color = settings.get('box_color', self.box_color)
        self.point_size = settings.get('point_size', self.point_size)
        self.ellipse_line_width = settings.get('ellipse_line_width', self.ellipse_line_width)
        self.box_line_width = settings.get('box_line_width', self.box_line_width)


if __name__ == "__main__":
    try:
        generator = LaTeXConfidenceGenerator()

        # Set the confidence interval data (example values)
        generator.set_confidence_data(
            fpf=0.3, tpf=0.7, fpf_lower=0.25, fpf_upper=0.35, tpf_lower=0.65, tpf_upper=0.75
        )

        # Customize the appearance
        generator.set_customization(
            ellipse_color="blue",
            point_color="red",
            box_color="black",
            point_size=2.0,
            ellipse_line_width=1.5,
            box_line_width=1.5
        )

        output_dir = 'Output'
        os.makedirs(output_dir, exist_ok=True)
        
        generator.set_header_info(
            name='New', 
            author='AAA'
        )

        # Export settings
        settings_path = os.path.join(output_dir, 'settings.json')
        with open(settings_path, 'w') as f:
            json.dump(generator.export_confidence_settings(), f, indent=4)

        # Import settings (just as a test, you can comment this out)
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        generator.import_confidence_settings(settings)

        # Generate full document
        latex_document = generator.generate_latex_document()
        doc_file_path = os.path.join(output_dir, 'ROC_confidence_analysis.tex')
        with open(doc_file_path, 'w') as f:
            f.write(latex_document)

        image = generator.generate_latex_image()
        image_file_path = os.path.join(output_dir, 'ROC_confidence_image.tex')
        with open(image_file_path, 'w') as f:
            f.write(image)

    except ValueError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
