import unreal
import sys
import os

# --- 이 스크립트의 핵심: 로그를 파일에 직접 쓰는 함수 ---
def log_to_file(file_handle, message):
    if file_handle:
        file_handle.write(message + '\n')
    # 만약을 위해 print도 남겨둡니다.
    print(message)

def get_asset_dependencies(file_handle, asset_path):
    log_to_file(file_handle, f"--- Analyzing asset: {asset_path} ---")
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_data = asset_registry.get_asset_by_object_path(asset_path)

    if not asset_data:
        log_to_file(file_handle, f"Error: Asset not found at path: {asset_path}. Check path or Asset Registry.")
        return

    # 의존성 쿼리
    dependencies = asset_registry.get_dependencies(asset_path, unreal.AssetRegistryDependencyOptions(True, True, True, True))
    referencers = asset_registry.get_referencers(asset_path, unreal.AssetRegistryDependencyOptions(True, True, True, True))

    log_to_file(file_handle, "\n--- Dependencies (What this asset USES): ---")
    if dependencies:
        for dep in sorted(dependencies):
            log_to_file(file_handle, f"  -> {dep}")
    else:
        log_to_file(file_handle, "  (None)")

    log_to_file(file_handle, "\n--- Referencers (What USES this asset): ---")
    if referencers:
        for ref in sorted(referencers):
            log_to_file(file_handle, f"  <- {ref}")
    else:
        log_to_file(file_handle, "  (None)")

def main():
    target_asset = None
    output_file_path = None

    # 커맨드 라인 인자 파싱
    for arg in sys.argv:
        if arg.startswith('-asset='):
            target_asset = arg.split('=', 1)[1].strip('"\'')
        elif arg.startswith('-output='):
            output_file_path = arg.split('=', 1)[1].strip('"\'')
    
    if not target_asset or not output_file_path:
        print("Execution failed: Both -asset=\"...\" and -output=\"...\" arguments are required.")
        return

    # 파일 열기 및 실행
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            log_to_file(f, f"Starting dependency check for project.")
            get_asset_dependencies(f, target_asset)
            log_to_file(f, "\n--- Analysis complete. ---")
    except Exception as e:
        # 파일 쓰기 중 에러가 나면 화면에라도 출력 시도
        print(f"An error occurred: {e}")

# --- 메인 실행 ---
main()