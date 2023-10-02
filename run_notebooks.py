import papermill as pm
import os

def execute_notebooks(notebooks_directory):
    # Delete existing -out.ipynb files
    for filename in os.listdir(notebooks_directory):
        if filename.endswith("-out.ipynb"):
            os.remove(os.path.join(notebooks_directory, filename))
    
    # Execute notebooks and save with -out.ipynb suffix
    for filename in os.listdir(notebooks_directory):
        if filename.endswith(".ipynb") and not filename.endswith("-out.ipynb"):
            input_path = os.path.join(notebooks_directory, filename)
            output_path = os.path.join(notebooks_directory, filename.replace(".ipynb", "-out.ipynb"))
            pm.execute_notebook(
                input_path,
                output_path,
                log_output=True,
            )

if __name__ == "__main__":
    notebooks_directory = 'notebooks'
    execute_notebooks(notebooks_directory)
