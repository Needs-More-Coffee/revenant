import os
import sys
from google import genai
from dotenv import load_dotenv
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file
from functions.call_function import call_function

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info, 
            schema_write_file, 
            schema_run_python_file, 
            schema_get_file_content,
        ]
    )

    system_prompt = """You are a helpful AI coding agent.
        When the user asks a question, ALWAYS create a function-call plan. 
        You must answer questions by inspecting the files inside the working directory.

        You can perform the following operations:
        - List files and directories
        - Read file contents
        - Write file contents
        - Run Python files

        Rules:
        1. You MUST use function calls to gather information.
        2. NEVER ask the user to clarify file names. Instead, inspect the directory structure yourself.
        3. All paths must be relative to the working directory.
        4. The working directory is injected automatically; do not include it in function call args.
        5. If a question requires knowledge, first call get_files_info to explore folders.
        6. Then call get_file_content to inspect relevant files.

        Your goal is to gather enough info using the available tools to build the answer.
        """


    if len(sys.argv) < 2:
        print("Error message: No prompt provided")
        sys.exit(1)

    user_prompt = sys.argv[1]
    verbose = "--verbose" in sys.argv

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]

    while True:
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[available_functions],
            ),
        )
        
        if response.function_calls:
            for fc in response.function_calls:
                result_content = call_function(fc, verbose)
                messages.append(result_content)
            continue

        if response.text:
            messages.append(
                types.Content(
                    role="assistant",
                    parts=[types.Part(text=response.text)]
                )
            )

        print("\nResponse:\n")
        print(response.text)

        if verbose:
            print("\n--- Debug Info ---")
            print("User prompt:", user_prompt)
            print("Prompt tokens:", response.usage_metadata.prompt_token_count)
            print("Response tokens:", response.usage_metadata.candidates_token_count)

        break

if __name__ == "__main__":
    main()
