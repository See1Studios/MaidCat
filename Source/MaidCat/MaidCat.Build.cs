using UnrealBuildTool;

public class MaidCat : ModuleRules
{
	public MaidCat(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicIncludePaths.AddRange(
			new string[] {
			}
		);

		PrivateIncludePaths.AddRange(
			new string[] {
			}
		);

		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				"CoreUObject", 
				"Engine",
				"UnrealEd",
				"EditorStyle",
				"EditorWidgets",
				"ToolMenus",
				"Projects"  // 이 줄을 추가해주세요
			}
		);

		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"Slate",
				"SlateCore",
				"EditorStyle",
				"EditorWidgets",
				"UnrealEd",
				"ToolMenus",
				"PropertyEditor"
			}
		);

		DynamicallyLoadedModuleNames.AddRange(
			new string[]
			{
			}
		);
	}
}
