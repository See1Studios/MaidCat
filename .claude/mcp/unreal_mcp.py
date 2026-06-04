import sys
import os
import json
import time
from pathlib import Path

# Load dev.local.json to find engine path dynamically
project_root = Path(__file__).resolve().parent.parent
dev_local_path = project_root / "dev.local.json"

engine_version = "5.5" # Fallback
if dev_local_path.exists():
    try:
        with open(dev_local_path, "r", encoding="utf-8") as f:
            dev_data = json.load(f)
            engine_version = dev_data.get("engine_version", "5.5")
    except Exception:
        pass

# Setup paths for remote_execution.py
# Assuming default Unreal Engine installation path on Windows
ue_path = Path(f"C:/Program Files/Epic Games/UE_{engine_version}")
remote_exec_dir = ue_path / "Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python"

if not remote_exec_dir.exists():
    # Attempt fallback to other versions if not found
    for fallback_ver in ["5.5", "5.4", "5.3"]:
        alt_path = Path(f"C:/Program Files/Epic Games/UE_{fallback_ver}/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python")
        if alt_path.exists():
            remote_exec_dir = alt_path
            break

if str(remote_exec_dir) not in sys.path:
    sys.path.append(str(remote_exec_dir))

try:
    import remote_execution
except ImportError as e:
    print(f"Error: Could not import remote_execution.py from {remote_exec_dir}. {e}", file=sys.stderr)
    sys.exit(1)

# Import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: 'mcp' package is not installed. Please run 'pip install mcp'", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP("unreal-remote")

@mcp.tool()
def execute_unreal_python(code: str) -> str:
    """
    Executes a block of Python code inside the running Unreal Engine editor instance.
    Requires 'Enable Remote Execution' to be checked in Unreal Project Settings under Python.
    """
    remote_exec = remote_execution.RemoteExecution()
    remote_exec.start()
    
    # Wait for node discovery (UDP discovery takes a brief moment)
    time.sleep(1.0)
    
    nodes = remote_exec.remote_nodes
    if not nodes:
        remote_exec.stop()
        return "Error: No active Unreal Editor instance found. Ensure the editor is running and 'Enable Remote Execution' is enabled in Project Settings."
    
    target_node = nodes[0]
    node_id = target_node.get("node_id")
    
    try:
        remote_exec.open_command_connection(node_id)
        result_dict = remote_exec.run_command(code, exec_mode=remote_execution.MODE_EXEC_FILE)
        
        output = []
        if result_dict.get("success"):
            output.append("=== Execution Successful ===")
        else:
            output.append("=== Execution Failed ===")
            
        result_logs = result_dict.get("output", [])
        if result_logs:
            output.append("\nLogs:")
            for log in result_logs:
                output.append(f"[{log.get('type')}] {log.get('output').strip()}")
                
        ret_val = result_dict.get("result")
        if ret_val:
            output.append(f"\nReturn Value:\n{ret_val}")
            
        return "\n".join(output)
        
    except Exception as e:
        return f"Exception occurred during remote execution: {str(e)}"
    finally:
        remote_exec.stop()

if __name__ == "__main__":
    mcp.run()
