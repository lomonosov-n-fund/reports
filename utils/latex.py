# ensure uniform table formatting 
def pandas_to_latex(df, filename, caption, label):
    latex_table = df.to_latex(
        index=False,
        float_format="%.2f")
    latex_table = f""" 
\\begin{{table}}[h] 
\\centering 
{latex_table} 
\\caption{{{caption}}} 
\\label{{tab:{label}}} 
\\end{{table}} 
"""
    with open(filename, 'w') as f:
        f.write(latex_table)
