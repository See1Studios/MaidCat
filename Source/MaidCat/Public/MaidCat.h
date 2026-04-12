#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "Framework/Commands/UICommandList.h"
#include "Widgets/Docking/SDockTab.h"
#include "Widgets/Layout/SScrollBox.h"

class FMaidCatModule : public IModuleInterface, public TSharedFromThis<FMaidCatModule>
{
public:

	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

private:
	void RegisterMenus();
	void PluginButtonClicked();
	
	TSharedRef<SDockTab> OnSpawnPluginTab(const FSpawnTabArgs& SpawnTabArgs);
	FReply OnListPropertiesClicked();
	void AddObjectPropertiesToList(UObject* Object);

private:
	TSharedPtr<class FUICommandList> PluginCommands;
	TSharedPtr<SScrollBox> PropertiesScrollBox;
};
