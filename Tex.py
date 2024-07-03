import pandas as pd

df = pd.read_csv('Data/bar.csv')

latex_template = """
\\pgfplotsset{{compat=1.16}}
\\usepgfplotslibrary{{statistics}}
\\pgfplotstableread{{
Reader max avg median min n qfirst qthird deviation
{data}
}}\\datatable

\\begin{{tikzpicture}}
\\pgfplotstablegetrowsof{{\\datatable}}
\\pgfmathtruncatemacro{{\\rownumber}}{{\\pgfplotsretval-1}}
\\begin{{axis}}[boxplot/draw direction=y,
\\xticklabels={{1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,All}},
\\xtick={{1,...,\\the\\numexpr\\rownumber+1}},
\\xlabel = {{\\textbf{{Reader(s)}}}},
\\ylabel = {{\\textbf{{QT POM--FFDM POM}}}},
height=12cm]
\\typeout{{\\rownumber}}
\\pgfplotsinvokeforeach{{0,...,\\rownumber}}{{{
 \\pgfplotstablegetelem{{#1}}{{min}}\\of\\datatable
 \\edef\\mymin{{\\pgfplotsretval}}
 \\pgfplotstablegetelem{{#1}}{{avg}}\\of\\datatable
 \\edef\\myavg{{\\pgfplotsretval}}
 \\pgfplotstablegetelem{{#1}}{{max}}\\of\\datatable
 \\edef\\mymax{{\\pgfplotsretval}}
 \\pgfplotstablegetelem{{#1}}{{median}}\\of\\datatable
 \\edef\\mymedian{{\\pgfplotsretval}}
 \\pgfplotstablegetelem{{#1}}{{deviation}}\\of\\datatable
 \\edef\\mydeviation{{\\pgfplotsretval}}
 \\pgfplotstablegetelem{{#1}}{{qfirst}}\\of\\datatable
 \\edef\\myqfirst{{\\pgfplotsretval}}
 \\pgfplotstablegetelem{{#1}}{{qthird}}\\of\\datatable
 \\edef\\myqthird{{\\pgfplotsretval}}
 \\typeout{{\\mymin,\\mymax,\\myavg,\\mymedian,\\mydeviation,\\myqfirst,\\myqthird}}
 \\edef\\temp{{\\noexpand\\addplot[
    boxplot prepared={{
     lower whisker=\\mymin,
     upper whisker=\\mymax,
     lower quartile=\\myqfirst,
     upper quartile=\\myqthird,
     median=\\mymedian,
     average=\\myavg,
     every box/.style={{draw=black,fill=yellow}},
  }}
  ]coordinates {{}};}}
 \\temp
}}
\\end{{axis}}
\\end{{tikzpicture}}
"""

data = df.to_string(index=False, header=False)
print(data)

latex_content = latex_template.format(data=data)

with open('Output/boxplot.tex', 'w') as f:
    f.write(latex_content)

print("LaTeX code has been saved to boxplot.tex")
