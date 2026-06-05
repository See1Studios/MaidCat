import sys
import time

# Engine's remote execution path
sys.path.append("C:/Program Files/Epic Games/UE_5.5/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python")

def execute_code(code_string):
    """
    Execute python code string inside the running Unreal Editor via Remote Execution.
    
    Args:
        code_string (str): The Python code to run in Unreal.
        
    Returns:
        dict: The execution result dictionary from Remote Execution, containing 'success', 'result', and 'output'.
    """
    try:
        import remote_execution
    except ImportError:
        return {
            "success": False,
            "result": "Unreal remote_execution module not found. Is PythonScriptPlugin active?",
            "output": []
        }
        
    remote_exec = remote_execution.RemoteExecution()
    remote_exec.start()
    time.sleep(0.5)
    
    nodes = remote_exec.remote_nodes
    if not nodes:
        remote_exec.stop()
        return {
            "success": False,
            "result": "No running Unreal Editor instance found with Remote Execution enabled.",
            "output": []
        }
        
    node = nodes[0]
    remote_exec.open_command_connection(node['node_id'])
    
    try:
        result = remote_exec.run_command(code_string)
        return result
    finally:
        remote_exec.close_command_connection()
        remote_exec.stop()

def execute_file(file_path):
    """
    Execute a python file inside the running Unreal Editor.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        return execute_code(code)
    except Exception as e:
        return {
            "success": False,
            "result": f"Failed to read file: {e}",
            "output": []
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m agentcat.remote <script_path.py> or 'python code string'")
        sys.exit(1)
        
    arg = sys.argv[1]
    if arg.endswith('.py'):
        res = execute_file(arg)
    else:
        res = execute_code(arg)
        
    if res:
        if res.get('success'):
            for log in res.get('output', []):
                print(log.get('output'), end='')
        else:
            print(f"Execution failed: {res.get('result')}", file=sys.stderr)
            sys.exit(1)
