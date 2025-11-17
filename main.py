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
    system_prompt = """
    You are a helpful AI coding agent. 
    When a user asks a question or makes a request, make a function call plan. You can perform the following operations: 
    - List files and directories
    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """
    if len(sys.argv) < 2:
        print("Error message: No prompt provided")
        sys.exit(1)

    user_prompt = sys.argv[1]
    verbose = "--verbose" in sys.argv

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-001", 
        contents=messages, 
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[available_functions],
        ),
    )

    function_calls = response.function_calls
    if function_calls:
        for fc in function_calls:
            function_call_result = call_function(fc, verbose)
            if not function_call_result.parts or not function_call_result.parts[0].function_response:
                raise Exception("Invalid function call result structure")
            if verbose:
               print("->", function_call_result.parts[0].function_response.response)
    else:
        print("Response:")
        print(response._get_text)

    if verbose:
        print("User prompt:")
        print(user_prompt)
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)
        
if __name__ == "__main__":
    main()
