import os
from pathlib import Path

def generate_latex_table(df, filename, path=None, insert_line_before="Observations"):
    """
    將指定的 DataFrame 轉換成 LaTeX 表格，
    並在特定行之前插入一條水平線，最後將 LaTeX code 保存到 .tex 中。

    Parameters
    ----------
        df : DataFrame
            要轉換成 LaTeX 表格的 pandas DataFrame。
        filename : str
            保存生成的 LaTeX 表格的文件名稱。
        path : WindowsPath or Path
            .tex 儲存路徑，預設在 latex_table folder
        insert_line_before : str
            在此列名之前插入一條水平線（\midrule）。預設為 "Observations"。

    Returns
    -------
        None
            將生成的 LaTeX 代碼保存到指定 folder。
    """
    # project 相對路徑
    if path is None:
        current_working_directory = Path(os.getcwd())
        project_root = current_working_directory.parents[1]
        path = project_root / 'latex_table'

    # 確保目標目錄存在
    path.mkdir(parents=True, exist_ok=True)

    # 生成 LaTeX 表格
    # 'l' for index, 'c' for columns
    column_format = "l" + "c" * len(df.columns)
    latex_table = df.to_latex(index=True, escape=False, column_format=column_format)
    latex_table = latex_table.replace("_", "\_")

    # 插入 \midrule
    lines = latex_table.split('\n')
    for i, line in enumerate(lines):
        if insert_line_before in line:
            lines.insert(i, '\midrule')  # 在指定行插入 \midrule
            break

    modified_latex_table = '\n'.join(lines)
    
    # 包裝 LaTeX 文檔
    latex_code = f"""
    \\documentclass{{article}}
    \\usepackage{{booktabs}}
    \\usepackage{{geometry}}
    \\geometry{{left=1cm, top=1cm, right=1cm, bottom=2cm}}
    \\usepackage{{makecell}}
    \\usepackage{{fontspec}}
    \\usepackage{{xeCJK}}
    \\setCJKmainfont{{NotoSerifCJKtc-Regular}}

    \\begin{{document}}
    \\fontsize{{12pt}}{{14pt}}\\selectfont
    
    {modified_latex_table}
    
    \\fontsize{{11pt}}{{14pt}}\\selectfont
    註：*: p<0.05; **: p<0.01; ***: p<0.001，括弧內的數字為標準誤。
    \\end{{document}}
    """

    # 將 LaTeX 代碼寫入文件
    output_path = path / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_code)
