import sys
import time

sys.path.append("C:/Program Files/Epic Games/UE_5.5/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python")
import remote_execution

def execute_file_in_unreal(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        command_str = f.read()
        
    remote_exec = remote_execution.RemoteExecution()
    remote_exec.start()
    time.sleep(0.5)
    
    nodes = remote_exec.remote_nodes
    if not nodes:
        print("ERROR: No Unreal Editor instance found!")
        remote_exec.stop()
        return None
        
    node = nodes[0]
    remote_exec.open_command_connection(node['node_id'])
    
    try:
        result = remote_exec.run_command(command_str)
        return result
    finally:
        remote_exec.close_command_connection()
        remote_exec.stop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_file_in_unreal.py <script_to_run.py>")
        sys.exit(1)
    res = execute_file_in_unreal(sys.argv[1])
    if res:
        if res.get('success'):
            print("SUCCESS")
            for log in res.get('output', []):
                print(log.get('output'), end='')
        else:
            print("FAILED")
            print(res.get('result'))
