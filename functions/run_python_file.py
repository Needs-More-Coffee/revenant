import os
import subprocess

def run_python_file(working_directory, file_path, args=[]):
    abs_working_dir = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_file.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        return f'Error: File "{file_path}" not found.'
    if not target_file.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    try:
        completed = subprocess.run(
            ["python", target_file, *args],
            cwd=abs_working_dir,
            capture_output=True,
            timeout=30,
            text=True,
       )
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()

        if not stdout and not stderr:
            return "No output produced."
       
        result = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"

        if completed.returncode != 0:
            result += f"\n\nProcess exited with code {completed.returncode}"
        
        return result
       
    except Exception as e:
        return f"Error: executing Python file: {e}"