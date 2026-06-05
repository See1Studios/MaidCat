import sys
import time

sys.path.append("C:/Program Files/Epic Games/UE_5.5/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python")
import remote_execution

def execute_in_unreal(command_str):
    remote_exec = remote_execution.RemoteExecution()
    remote_exec.start()
    time.sleep(0.5) # Wait for discovery
    
    nodes = remote_exec.remote_nodes
    if not nodes:
        print("ERROR: No Unreal Editor instance found!")
        remote_exec.stop()
        return None
        
    node = nodes[0]
    node_id = node['node_id']
    remote_exec.open_command_connection(node_id)
    
    try:
        result = remote_exec.run_command(command_str)
        return result
    finally:
        remote_exec.close_command_connection()
        remote_exec.stop()

if __name__ == "__main__":
    test_cmd = "import unreal; print('Hello from Remote Python!')"
    print("Executing in Unreal:")
    res = execute_in_unreal(test_cmd)
    print("Result:", res)
