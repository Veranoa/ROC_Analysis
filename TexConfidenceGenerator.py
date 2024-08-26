from TexGenerator import LaTeXGenerator
import sys
import os
import json
from sci_cr import CI, CG2

class LaTeXConfidenceGenerator(LaTeXGenerator):
    def __init__(self):
        super().__init__()
        self.confidence_data = {}
        self.make_figure_command = self.generate_make_figure_command()

        self.MLE_color = '{1.0, 0.25, 0.0}'
        self.confidence_colors={
            'COLORoNinetynine': '{1.0, 0.25, 0.0}',
            'COLORoNinetyfive': '{.0, .0, 1.0}',
            'COLORoNinety': '{.0, 1.0, 0.0}',
            'COLORoEighty': '{1.0, .65, 0.}',
        }
        
        self.figure_number_position = (0.92, 0.92)
        self.legend_position = (0.65, 0.45)
        
        self.confidence_data_commands = ""
        self.confidence_color_definitions = ""
        self.confidence_plot_commands = ""
        self.confidence_plot_frame_commands = ""
        self.confidence_group_commands = ""
        
    def set_confidence_data(self, fp, n_n, tp, n_p, alpha, data):
        """
        Set the confidence data for the ROC plot.
        """
        self.confidence_data = {
            'fp': fp,
            'n_n': n_n,
            'tp': tp,
            'n_p': n_p,
            'alpha': alpha,
        }
        self.alpha = alpha  

        self.confidence_data_commands = data
        self.confidence_color_definitions = self.generate_confidence_color_definitions()
        self.confidence_plot_commands = self.generate_confidence_plot_commands()
        self.confidence_plot_frame_commands = self.generate_confidence_plot_frame_commands()
        self.confidence_plot_fig_commands = self.generate_plot_fig_command()
        self.confidence_group_commands = self.generate_confidence_group_commands()

    def generate_confidence_color_definitions(self):
        """
        Generates LaTeX commands to define colors.
        """
        alpha_commands = {
            0.01: f"\\definecolor{{COLORoNinetynine}}{{rgb}}{self.confidence_colors['COLORoNinetynine']}",
            0.05: f"\\definecolor{{COLORoNinetyfive}}{{rgb}}{self.confidence_colors['COLORoNinetyfive']}",
            0.10: f"\\definecolor{{COLORoNinety}}{{rgb}}{self.confidence_colors['COLORoNinety']}",
            0.20: f"\\definecolor{{COLORoEighty}}{{rgb}}{self.confidence_colors['COLORoEighty']}",
        }

        alpha_colors = {
            0.01: 'COLORoNinetynine',
            0.05: 'COLORoNinetyfive',
            0.10: 'COLORoNinety',
            0.20: 'COLORoEighty',
        }

        new_confidence_colors = {}
        color_definitions = f"""
% Define colors:
\\definecolor{{COLORoMLE}}{{rgb}}{self.MLE_color}
"""

        for a in self.alpha:  
            if a in alpha_commands:
                color_definitions += alpha_commands[a] + "\n"
                new_confidence_colors[alpha_colors[a]] = self.confidence_colors[alpha_colors[a]]

        self.confidence_colors = new_confidence_colors

        return color_definitions

    def generate_confidence_plot_commands(self):
        """
        Generate LaTeX commands for plotting the confidence intervals and the ellipse with customization.
        """
        commands = r"""
\newcommand{\DrawOperatingPOINT}[3]{
\addplot[
  color=#2,
  mark=*,
  mark size=1.pt,
  only marks,
  on layer={axis foreground},
] coordinates {#1};
\if\relax\detokenize{#3}\relax\else\addlegendentry{#3}\fi
}

\newcommand{\DrawPOINTSoCR}[3]{
\addplot[
  color=#2,
  mark=*,
  mark size=.1pt,
  line width=1pt,
  on layer={axis foreground},
] coordinates {#1};
\if\relax\detokenize{#3}\relax\else\addlegendentry{#3}\fi
}

\newcommand{\DrawPOINTSoCI}[3]{
\addplot[
  color=#2,
  mark=*,
  mark size=.1pt,
  dashed,
  dash pattern=on 3pt off 3pt,  % Adjust the dash pattern here
  line width=1pt,
  on layer={axis foreground},
] coordinates {#1};
\if\relax\detokenize{#3}\relax\else\addlegendentry{#3}\fi
}      
"""
        return commands

    def generate_confidence_plot_frame_commands(self):
        """
        Generates LaTeX commands for plotting the confidence intervals and CRs, based on the specified alpha values.
        """
        alpha_commands = {
            0.01: "\\DrawPOINTSoCR{\\CRninetynine}{COLORoNinetynine}{CR Ninetynine}\n  \\DrawPOINTSoCI{\\CIninetynine}{COLORoNinetynine}{CI Ninetynine}",
            0.05: "\\DrawPOINTSoCR{\\CRninetyfive}{COLORoNinetyfive}{CR Ninetyfive}\n  \\DrawPOINTSoCI{\\CIninetyfive}{COLORoNinetyfive}{CI Ninetyfive}",
            0.10: "\\DrawPOINTSoCR{\\CRninety}{COLORoNinety}{CR Ninety}\n  \\DrawPOINTSoCI{\\CIninety}{COLORoNinety}{CI Ninety}",
            0.20: "\\DrawPOINTSoCR{\\CReighty}{COLORoEighty}{CR Eighty}\n  \\DrawPOINTSoCI{\\CIeighty}{COLORoEighty}{CI Eighty}",
        }
        
        alpha_CI_commands = {
            0.01: "\\DrawPOINTSoCI{\\CIninetynine}{COLORoNinetynine}{CI Ninetynine}",
            0.05: "\\DrawPOINTSoCI{\\CIninetyfive}{COLORoNinetyfive}{CI Ninetyfive}",
            0.10: "\\DrawPOINTSoCI{\\CIninety}{COLORoNinety}{CI Ninety}",
            0.20: "\\DrawPOINTSoCI{\\CIeighty}{COLORoEighty}{CI Eighty}",
        }

        alpha_CR_commands = {
            0.01: "\\DrawPOINTSoCR{\\CRninetynine}{COLORoNinetynine}{CR Ninetynine}",
            0.05: "\\DrawPOINTSoCR{\\CRninetyfive}{COLORoNinetyfive}{CR Ninetyfive}",
            0.10: "\\DrawPOINTSoCR{\\CRninety}{COLORoNinety}{CR Ninety}",
            0.20: "\\DrawPOINTSoCR{\\CReighty}{COLORoEighty}{CR Eighty}",
        }
        
        commands = r"""
\newcommand{\PlotFRAMEoCIoCR}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Operating Point}
"""

        for a in self.alpha:
            if a in alpha_commands:
                commands += "  " + alpha_commands[a] + "\n"

        commands += r"""}
"""

        commands += r"""
\newcommand{\PlotFRAMEoCI}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{}
"""

        for a in self.alpha:
            if a in alpha_CI_commands:
                commands += "  " + alpha_CI_commands[a] + "\n"

        commands += r"""}
"""

        commands += r"""
\newcommand{\PlotFRAMEoCR}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{}
"""

        for a in self.alpha:
            if a in alpha_CR_commands:
                commands += "  " + alpha_CR_commands[a] + "\n"

        commands += r"""}
"""

        if len(self.alpha) > 1:
            for a in self.alpha:
                if a == 0.01:
                    commands += r"""
\newcommand{\PlotFRAMEoNinetynineoCIoCR}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Ninetynine}
  \DrawPOINTSoCR{\CRninetynine}{COLORoNinetynine}{CR Ninetynine}
  \DrawPOINTSoCI{\CIninetynine}{COLORoNinetynine}{CI Ninetynine}
}

\newcommand{\PlotFRAMEoNinetynineoCI}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Ninetynine}
  \DrawPOINTSoCI{\CIninetynine}{COLORoNinetynine}{CI Ninetynine}
}

\newcommand{\PlotFRAMEoNinetynineoCR}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Ninetynine}
  \DrawPOINTSoCR{\CRninetynine}{COLORoNinetynine}{CR Ninetynine}
}
"""
                elif a == 0.05:
                    commands += r"""
\newcommand{\PlotFRAMEoNinetyfiveoCIoCR}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Ninetyfive}
  \DrawPOINTSoCR{\CRninetyfive}{COLORoNinetyfive}{CR Ninetyfive}
  \DrawPOINTSoCI{\CIninetyfive}{COLORoNinetyfive}{CI Ninetyfive}
}

\newcommand{\PlotFRAMEoNinetyfiveoCI}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Ninetyfive}
  \DrawPOINTSoCI{\CIninetyfive}{COLORoNinetyfive}{CI Ninetyfive}
}

\newcommand{\PlotFRAMEoNinetyfiveoCR}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Ninetyfive}
  \DrawPOINTSoCR{\CRninetyfive}{COLORoNinetyfive}{CR Ninetyfive}
}
"""
                elif a == 0.10:
                    commands += r"""
\newcommand{\PlotFRAMEoNinetyoCIoCR}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Ninety}
  \DrawPOINTSoCR{\CRninety}{COLORoNinety}{CR Ninety}
  \DrawPOINTSoCI{\CIninety}{COLORoNinety}{CI Ninety}
}

\newcommand{\PlotFRAMEoNinetyoCI}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Ninety}
  \DrawPOINTSoCI{\CIninety}{COLORoNinety}{CI Ninety}
}

\newcommand{\PlotFRAMEoNinetyoCR}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Ninety}
  \DrawPOINTSoCR{\CRninety}{COLORoNinety}{CR Ninety}
}
"""
                elif a == 0.20:
                    commands += r"""
\newcommand{\PlotFRAMEoEightyoCIoCR}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Eighty}
  \DrawPOINTSoCR{\CReighty}{COLORoEighty}{CR Eighty}
  \DrawPOINTSoCI{\CIeighty}{COLORoEighty}{CI Eighty}
}

\newcommand{\PlotFRAMEoEightyoCI}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Eighty}
  \DrawPOINTSoCI{\CIeighty}{COLORoEighty}{CI Eighty}
}

\newcommand{\PlotFRAMEoEightyoCR}{
  \DrawOperatingPOINT{\MLE}{COLORoMLE}{Eighty}
  \DrawPOINTSoCR{\CReighty}{COLORoEighty}{CR Eighty}
}
"""

        return commands


    def generate_plot_fig_command(self):
        """
        Generates LaTeX commands for plotting figures with confidence intervals.
        """
        return rf"""
% Command for making one plot:
\newcommand{{\PlotFIG}}[2]{{
\nextgroupplot[
  xlabel = {{\textbf{{FPF}}}},
  ylabel = {{\textbf{{TPF}}}},
  xticklabels={{, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0}},
  yticklabels={{, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0}},
  legend style={{at={{({self.legend_position[0]},{self.legend_position[1]})}}, anchor=north, font=\small}}, 
  legend cell align={{left}},
] #1

% Add figure number in the top right corner
\node[anchor=north east] at (rel axis cs:{self.figure_number_position[0]},{self.figure_number_position[1]}) {{\textbf{{#2}}}};
}}
"""


    def generate_confidence_group_commands(self):
        fig_num = 0 
        fig_labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)', '(h)','(i)', '(j)', '(k)', '(l)', '(m)', '(n)', '(o)', '(p)']
        
        commands = rf"""
\newcommand{{\PlotFIGoCIoCR}}[0]{{
  \PlotFIG{{\PlotFRAMEoCIoCR}}{{{fig_labels[fig_num]}}}
}}
\newcommand{{\PlotFIGoCI}}[0]{{
  \PlotFIG{{\PlotFRAMEoCI}}{{{fig_labels[fig_num + 1]}}}
}}
\newcommand{{\PlotFIGoCR}}[0]{{
  \PlotFIG{{\PlotFRAMEoCR}}{{{fig_labels[fig_num + 2]}}}
}}
"""
        fig_num += 3 

        if len(self.alpha) > 1:
            for a in self.alpha:
                if a == 0.01:
                    commands += rf"""
\newcommand{{\PlotFIGoNinetynineoCIoCR}}[0]{{
  \PlotFIG{{\PlotFRAMEoNinetynineoCIoCR}}{{{fig_labels[fig_num]}}}
}}
\newcommand{{\PlotFIGoNinetynineoCI}}[0]{{
  \PlotFIG{{\PlotFRAMEoNinetynineoCI}}{{{fig_labels[fig_num + 1]}}}
}}
\newcommand{{\PlotFIGoNinetynineoCR}}[0]{{
  \PlotFIG{{\PlotFRAMEoNinetynineoCR}}{{{fig_labels[fig_num + 2]}}}
}}
"""
                    fig_num += 3  
                elif a == 0.05:
                    commands += rf"""
\newcommand{{\PlotFIGoNinetyfiveoCIoCR}}[0]{{
  \PlotFIG{{\PlotFRAMEoNinetyfiveoCIoCR}}{{{fig_labels[fig_num]}}}
}}
\newcommand{{\PlotFIGoNinetyfiveoCI}}[0]{{
  \PlotFIG{{\PlotFRAMEoNinetyfiveoCI}}{{{fig_labels[fig_num + 1]}}}
}}
\newcommand{{\PlotFIGoNinetyfiveoCR}}[0]{{
  \PlotFIG{{\PlotFRAMEoNinetyfiveoCR}}{{{fig_labels[fig_num + 2]}}}
}}
"""
                    fig_num += 3 
                elif a == 0.10:
                    commands += rf"""
\newcommand{{\PlotFIGoNinetyoCIoCR}}[0]{{
  \PlotFIG{{\PlotFRAMEoNinetyoCIoCR}}{{{fig_labels[fig_num]}}}
}}
\newcommand{{\PlotFIGoNinetyoCI}}[0]{{
  \PlotFIG{{\PlotFRAMEoNinetyoCI}}{{{fig_labels[fig_num + 1]}}}
}}
\newcommand{{\PlotFIGoNinetyoCR}}[0]{{
  \PlotFIG{{\PlotFRAMEoNinetyoCR}}{{{fig_labels[fig_num + 2]}}}
}}
"""
                    fig_num += 3  
                elif a == 0.20:
                    commands += rf"""
\newcommand{{\PlotFIGoEightyoCIoCR}}[0]{{
  \PlotFIG{{\PlotFRAMEoEightyoCIoCR}}{{{fig_labels[fig_num]}}}
}}
\newcommand{{\PlotFIGoEightyoCI}}[0]{{
  \PlotFIG{{\PlotFRAMEoEightyoCI}}{{{fig_labels[fig_num + 1]}}}
}}
\newcommand{{\PlotFIGoEightyoCR}}[0]{{
  \PlotFIG{{\PlotFRAMEoEightyoCR}}{{{fig_labels[fig_num + 2]}}}
}}
"""
                    fig_num += 3  

        return commands

        
    def generate_latex_document(self):
        """
        Generate the complete LaTeX document for the confidence result.
        """

        latex_document = (
            self.generate_document_header() +
            self.confidence_data_commands +
            self.confidence_color_definitions +
            self.confidence_plot_commands +
            self.confidence_plot_frame_commands +
            self.confidence_plot_fig_commands +
            self.confidence_group_commands +
            self.make_figure_command +
            self.generate_header_footer() +
            self.generate_document_body_with_caption()
        )

        return latex_document

    def generate_latex_image(self):
        """
        Generate the LaTeX document for a standalone image.
        """
        image_document = (
            self.generate_image_header() +
            self.confidence_data_commands +
            self.confidence_color_definitions +
            self.confidence_plot_commands +
            self.confidence_plot_frame_commands +
            self.confidence_plot_fig_commands +
            self.confidence_group_commands +
            self.make_figure_command +
            self.generate_document_body()
        )
        return image_document

    def generate_document_body_commands(self):
        """
        Generate the body commands specific to the confidence interval plot.
        """
        body_commands = ""
        
        if len(self.alpha) == 1:
            body_commands = r"""
  \textbf{}
  \MakeAfigure{\PlotFIGoCIoCR}
  \MakeAfigure{\PlotFIGoCI}
  \MakeAfigure{\PlotFIGoCR}
"""
        else:
            body_commands = r"""
  \textbf{}
  \MakeAfigure{\PlotFIGoCIoCR}
  \MakeAfigure{\PlotFIGoCI}
  \MakeAfigure{\PlotFIGoCR}
"""
            for a in self.alpha:
                if a == 0.01:
                    body_commands += r"""
  \newpage
  \textbf{}
  \MakeAfigure{\PlotFIGoNinetynineoCIoCR}
  \MakeAfigure{\PlotFIGoNinetynineoCI}
  \MakeAfigure{\PlotFIGoNinetynineoCR}
"""         
                elif a == 0.05:
                    body_commands += r"""
  \newpage
  \textbf{}
  \MakeAfigure{\PlotFIGoNinetyfiveoCIoCR}
  \MakeAfigure{\PlotFIGoNinetyfiveoCI}
  \MakeAfigure{\PlotFIGoNinetyfiveoCR}
"""
                elif a == 0.10:
                    body_commands += r"""
  \newpage
  \textbf{}
  \MakeAfigure{\PlotFIGoNinetyoCIoCR}
  \MakeAfigure{\PlotFIGoNinetyoCI}
  \MakeAfigure{\PlotFIGoNinetyoCR}
"""
                elif a == 0.20:
                    body_commands += r"""
  \newpage
  \textbf{}
  \MakeAfigure{\PlotFIGoEightyoCIoCR}
  \MakeAfigure{\PlotFIGoEightyoCI}
  \MakeAfigure{\PlotFIGoEightyoCR}
"""
        
        return body_commands

    def generate_document_body_with_caption(self):
        """
        Generates the complete LaTeX document body.
        """
        body = r"\begin{document}"
        body += self.generate_document_body_commands_with_caption()
        body += "\n"
        body += r"\end{document}"
        return body
    
    def generate_document_body_commands_with_caption(self):
        """
        Generate the body commands specific to the confidence interval plot.
        """
        body_commands = ""
        fig_num = 0  
        fig_labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)', '(g)', '(h)','(i)', '(j)', '(k)', '(l)', '(m)', '(n)', '(o)', '(p)']
        captions = []

        if len(self.alpha) == 1:
            body_commands = rf"""
  \textbf{{}}
  \MakeAfigure{{\PlotFIGoCIoCR}}
  \MakeAfigure{{\PlotFIGoCI}}
  \MakeAfigure{{\PlotFIGoCR}}
"""
            body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} shows the ROC plot with both Confidence Intervals (CI) and Credible Regions (CR).}}"
            fig_num += 1
            body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} displays the ROC plot with Confidence Intervals (CI) only.}}"
            fig_num += 1
            body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} presents the ROC plot with Credible Regions (CR) only.}}"
            fig_num += 1
        else:
            body_commands = rf"""
  \textbf{{}}
  \MakeAfigure{{\PlotFIGoCIoCR}}
  \MakeAfigure{{\PlotFIGoCI}}
  \MakeAfigure{{\PlotFIGoCR}}
"""
            body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} shows the ROC plot with both Confidence Intervals (CI) and Credible Regions (CR).}}"
            fig_num += 1
            body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} displays the ROC plot with Confidence Intervals (CI) only.}}"
            fig_num += 1
            body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} presents the ROC plot with Credible Regions (CR) only.}}"
            fig_num += 1

            for a in self.alpha:
                if a == 0.01:
                    body_commands += rf"""
                    
  \newpage
  \textbf{{}}
  \MakeAfigure{{\PlotFIGoNinetynineoCIoCR}}
  \MakeAfigure{{\PlotFIGoNinetynineoCI}}
  \MakeAfigure{{\PlotFIGoNinetynineoCR}}
"""
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} shows the ROC plot for 99\% CI and CR.}}"
                    fig_num += 1
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} displays the ROC plot for 99\% CI only.}}"
                    fig_num += 1
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} presents the ROC plot for 99\% CR only.}}"
                    fig_num += 1
                elif a == 0.05:
                    body_commands += rf"""
                    
  \newpage
  \textbf{{}}
  \MakeAfigure{{\PlotFIGoNinetyfiveoCIoCR}}
  \MakeAfigure{{\PlotFIGoNinetyfiveoCI}}
  \MakeAfigure{{\PlotFIGoNinetyfiveoCR}}
"""
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} shows the ROC plot for 95\% CI and CR.}}"
                    fig_num += 1
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} displays the ROC plot for 95\% CI only.}}"
                    fig_num += 1
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} presents the ROC plot for 95\% CR only.}}"
                    fig_num += 1
                elif a == 0.10:
                    body_commands += rf"""
                    
  \newpage
  \textbf{{}}
  \MakeAfigure{{\PlotFIGoNinetyoCIoCR}}
  \MakeAfigure{{\PlotFIGoNinetyoCI}}
  \MakeAfigure{{\PlotFIGoNinetyoCR}}
"""
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} shows the ROC plot for 90\% CI and CR.}}"
                    fig_num += 1
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} displays the ROC plot for 90\% CI only.}}"
                    fig_num += 1
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} presents the ROC plot for 90\% CR only.}}"
                    fig_num += 1
                elif a == 0.20:
                    body_commands += rf"""
                    
  \newpage
  \textbf{{}}
  \MakeAfigure{{\PlotFIGoEightyoCIoCR}}
  \MakeAfigure{{\PlotFIGoEightyoCI}}
  \MakeAfigure{{\PlotFIGoEightyoCR}}
"""
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} shows the ROC plot for 80\% CI and CR.}}"
                    fig_num += 1
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} displays the ROC plot for 80\% CI only.}}"
                    fig_num += 1
                    body_commands +=rf"  \textnormal{{Figure {fig_labels[fig_num]} presents the ROC plot for 80\% CR only.}}"
                    fig_num += 1

        # Combine captions into one paragraph per page
        body_commands += "\n".join(captions)

        # Add a new page for the analysis results
        body_commands += r"""
        
  \newpage
  This section summarizes the analysis results based on the ROC plots generated. 

  - Discuss the confidence intervals and credible regions for each alpha value.
  
  - Interpret the significance of the operating points in each plot.
  
  - Highlight key observations, such as any trends or patterns seen in the data.
  
  - Provide a conclusion based on the analysis outcomes.
  
"""
    
        return body_commands
    
    def export_confidence_settings(self):
        """
        Export current settings to a dictionary.
        """
        settings = {
            'page_format': self.page_format,
            'plot_format': self.plot_format,
            'MLE_color':self.MLE_color,
            'confidence_colors': self.confidence_colors,
            'figure_number_position': self.figure_number_position,
            'legend_position': self.legend_position
        }
        return settings

    def import_confidence_settings(self, settings):
        """
        Import settings from a dictionary.
        """
        if isinstance(settings, str):
            with open(settings, 'r') as file:
                settings = json.load(file)
        
        self.page_format = settings.get('page_format', self.page_format)
        self.plot_format = settings.get('plot_format', self.plot_format)
        self.MLE_color = settings.get('MLE_color', self.MLE_color)
        self.confidence_colors = settings.get('confidence_colors', {})
        self.figure_number_position = settings.get('figure_number_position', self.figure_number_position)
        self.legend_position = settings.get('legend_position', self.legend_position)

        default_colors = {
            'COLORoNinetynine': '{1.0, 0.25, 0.0}',
            'COLORoNinetyfive': '{.0, .0, 1.0}',
            'COLORoNinety': '{.0, 1.0, 0.0}',
            'COLORoEighty': '{1.0, .65, 0.}',
        }
        
        for key, value in default_colors.items():
            if key not in self.confidence_colors:
                self.confidence_colors[key] = value
        
        self.confidence_color_definitions = self.generate_confidence_color_definitions()
        self.document_header = self.generate_document_header()
        self.make_figure_command = self.generate_make_figure_command()


if __name__ == "__main__":
    try:
        generator = LaTeXConfidenceGenerator()
        
        cg2 = CG2()
        ci = CI()

        fp = 10  
        n_n = 50  
        tp = 40  
        n_p = 50  
        alpha = [0.1, 0.2] 
        dx = 0.001
        dy = 0.001
        
        tex = {'dir': './Output', 'CR_data': 'cg2_CR_results'}
    
        esmt = cg2.cal(fp=fp, n_n=n_n, tp=tp, n_p=n_p, alpha=alpha, dx=dx, dy=dy, FPF=None, TPF=None, tex=tex, verbose=True, CI=ci)

        data_file_path = os.path.join(tex['dir'], f"{tex['CR_data']}.{fp}_{n_n}.{tp}_{n_p}")
        with open(data_file_path, 'r') as file:
            data = file.read()

        generator.set_confidence_data(
            fp=fp, n_n=n_n, tp=tp, n_p=n_p, alpha=alpha, data=data
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

        # Generate standalone image document
        image = generator.generate_latex_image()
        image_file_path = os.path.join(output_dir, 'ROC_confidence_image.tex')
        with open(image_file_path, 'w') as f:
            f.write(image)

    except ValueError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
