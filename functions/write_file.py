import os
from google.genai import types

def write_file(working_directory, file_path, content):
    abs_working_dir = os.path.abspath(working_directory)
    target_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_path.startswith(abs_working_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    dir_name = os.path.dirname(target_path)
    os.makedirs(dir_name, exist_ok=True)
    try:
        with open(target_path, "w") as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error: {e}'
    
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description=(
        "Creates or overwrites a file within the working directory with the "
        "provided content. Automatically creates parent directories if needed."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Relative path to the file to write."
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Full text content to write into the file."
            ),
        },
        required=["file_path", "content"],
    ),
)
