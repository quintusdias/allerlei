# Shortcut style to use at the prompt.  'vi' or 'emacs'
c.TerminalInteractiveShell.editing_mode = 'vi'

# Set the editor used by IPython
c.TerminalInteractiveShell.editor = 'vim'

# Lines of code to run at IPython startup
c.InteractiveShellApp.exec_lines = [
    'import matplotlib.pyplot as plt',
    'import numpy as np',
    'import pandas as pd',
    'import seaborn as sns',
]

