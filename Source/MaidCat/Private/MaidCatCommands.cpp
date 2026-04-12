#include "MaidCatCommands.h"

#define LOCTEXT_NAMESPACE "FMaidCatModule"

void FMaidCatCommands::RegisterCommands()
{
	UI_COMMAND(OpenPluginWindow, "MaidCat", "Bring up MaidCat window", EUserInterfaceActionType::Button, FInputChord());
}

#undef LOCTEXT_NAMESPACE
