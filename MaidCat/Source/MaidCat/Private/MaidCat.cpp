#include "MaidCat.h"
#include "MaidCatStyle.h"
#include "MaidCatCommands.h"
#include "LevelEditor.h"
#include "Widgets/Docking/SDockTab.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Text/STextBlock.h"
#include "ToolMenus.h"
#include "Engine/Selection.h"
#include "Editor.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SScrollBox.h"
#include "UObject/UnrealType.h"

static const FName MaidCatTabName("MaidCat");

#define LOCTEXT_NAMESPACE "FMaidCatModule"

void FMaidCatModule::StartupModule()
{
	// This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file

	FMaidCatStyle::Initialize();
	FMaidCatStyle::ReloadTextures();

	FMaidCatCommands::Register();
	
	PluginCommands = MakeShareable(new FUICommandList);

	PluginCommands->MapAction(
		FMaidCatCommands::Get().OpenPluginWindow,
		FExecuteAction::CreateRaw(this, &FMaidCatModule::PluginButtonClicked),
		FCanExecuteAction());

	UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FMaidCatModule::RegisterMenus));
	
	FGlobalTabmanager::Get()->RegisterNomadTabSpawner(MaidCatTabName, FOnSpawnTab::CreateRaw(this, &FMaidCatModule::OnSpawnPluginTab))
		.SetDisplayName(LOCTEXT("FMaidCatTabTitle", "MaidCat"))
		.SetMenuType(ETabSpawnerMenuType::Hidden);
}

void FMaidCatModule::ShutdownModule()
{
	// This function may be called during shutdown to clean up your module.  For modules that support dynamic reloading,
	// we call this function before unloading the module.

	UToolMenus::UnRegisterStartupCallback(this);

	UToolMenus::UnregisterOwner(this);

	FMaidCatStyle::Shutdown();

	FMaidCatCommands::Unregister();

	FGlobalTabmanager::Get()->UnregisterNomadTabSpawner(MaidCatTabName);
}

TSharedRef<SDockTab> FMaidCatModule::OnSpawnPluginTab(const FSpawnTabArgs& SpawnTabArgs)
{
	return SNew(SDockTab)
		.TabRole(ETabRole::NomadTab)
		[
			SNew(SVerticalBox)
			+ SVerticalBox::Slot()
			.AutoHeight()
			.Padding(10)
			[
				SNew(SButton)
				.Text(LOCTEXT("ListPropertiesButton", "List Selected Object Properties"))
				.OnClicked(this, &FMaidCatModule::OnListPropertiesClicked)
			]
			+ SVerticalBox::Slot()
			.FillHeight(1.0f)
			.Padding(10)
			[
				SAssignNew(PropertiesScrollBox, SScrollBox)
			]
		];
}

void FMaidCatModule::RegisterMenus()
{
	// Owner will be used for cleanup in call to UToolMenus::UnregisterOwner
	FToolMenuOwnerScoped OwnerScoped(this);

	{
		UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Window");
		{
			FToolMenuSection& Section = Menu->FindOrAddSection("WindowLayout");
			Section.AddMenuEntryWithCommandList(FMaidCatCommands::Get().OpenPluginWindow, PluginCommands);
		}
	}

	{
		UToolMenu* ToolbarMenu = UToolMenus::Get()->ExtendMenu("LevelEditor.LevelEditorToolBar");
		{
			FToolMenuSection& Section = ToolbarMenu->FindOrAddSection("Settings");
			{
				FToolMenuEntry& Entry = Section.AddEntry(FToolMenuEntry::InitToolBarButton(FMaidCatCommands::Get().OpenPluginWindow));
				Entry.SetCommandList(PluginCommands);
			}
		}
	}
}

void FMaidCatModule::PluginButtonClicked()
{
	FGlobalTabmanager::Get()->TryInvokeTab(MaidCatTabName);
}

FReply FMaidCatModule::OnListPropertiesClicked()
{
	if (PropertiesScrollBox.IsValid())
	{
		PropertiesScrollBox->ClearChildren();
		
		// Get selected objects
		USelection* Selection = GEditor->GetSelectedActors();
		if (Selection && Selection->Num() > 0)
		{
			for (FSelectionIterator It(*Selection); It; ++It)
			{
				if (UObject* SelectedObject = Cast<UObject>(*It))
				{
					AddObjectPropertiesToList(SelectedObject);
				}
			}
		}
		else
		{
			PropertiesScrollBox->AddSlot()
			[
				SNew(STextBlock)
				.Text(LOCTEXT("NoSelection", "No objects selected. Please select an object to list its properties."))
			];
		}
	}
	
	return FReply::Handled();
}

void FMaidCatModule::AddObjectPropertiesToList(UObject* Object)
{
	if (!Object || !PropertiesScrollBox.IsValid())
		return;

	// Add object name header
	PropertiesScrollBox->AddSlot()
	[
		SNew(STextBlock)
		.Text(FText::FromString(FString::Printf(TEXT("=== %s ==="), *Object->GetName())))
		.Font(FCoreStyle::GetDefaultFontStyle("Bold", 12))
		.ColorAndOpacity(FLinearColor::Yellow)
	];

	// Iterate through all properties
	for (TFieldIterator<FProperty> PropertyIt(Object->GetClass()); PropertyIt; ++PropertyIt)
	{
		FProperty* Property = *PropertyIt;
		if (!Property)
			continue;

		// Get property name and type
		FString PropertyName = Property->GetName();
		FString PropertyType = Property->GetClass()->GetName();
		
		// Get property value as string
		FString PropertyValue = TEXT("(Unable to get value)");
		
		// Try to get the property value
		if (Property->HasAnyPropertyFlags(CPF_Edit | CPF_BlueprintVisible))
		{
			// Export the property value to string
			const void* PropertyPtr = Property->ContainerPtrToValuePtr<void>(Object);
			if (PropertyPtr)
			{
				Property->ExportText_Direct(PropertyValue, PropertyPtr, nullptr, Object, PPF_None);
			}
		}

		// Add property info to the list
		PropertiesScrollBox->AddSlot()
		[
			SNew(SHorizontalBox)
			+ SHorizontalBox::Slot()
			.AutoWidth()
			.Padding(5, 2)
			[
				SNew(STextBlock)
				.Text(FText::FromString(PropertyName))
				.ColorAndOpacity(FLinearColor::White)
			]
			+ SHorizontalBox::Slot()
			.AutoWidth()
			.Padding(5, 2)
			[
				SNew(STextBlock)
				.Text(FText::FromString(FString::Printf(TEXT("(%s)"), *PropertyType)))
				.ColorAndOpacity(FLinearColor::Gray)
			]
			+ SHorizontalBox::Slot()
			.FillWidth(1.0f)
			.Padding(5, 2)
			[
				SNew(STextBlock)
				.Text(FText::FromString(PropertyValue))
				.ColorAndOpacity(FLinearColor::Green)
				.AutoWrapText(true)
			]
		];
	}

	// Add separator
	PropertiesScrollBox->AddSlot()
	[
		SNew(STextBlock)
		.Text(FText::FromString(TEXT("")))
	];
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FMaidCatModule, MaidCat)
