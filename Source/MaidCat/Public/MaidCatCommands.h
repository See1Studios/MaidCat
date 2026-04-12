#pragma once

#include "CoreMinimal.h"
#include "Framework/Commands/Commands.h"
#include "MaidCatStyle.h"

class FMaidCatCommands : public TCommands<FMaidCatCommands>
{
public:

	FMaidCatCommands()
		: TCommands<FMaidCatCommands>(TEXT("MaidCat"), NSLOCTEXT("Contexts", "MaidCat", "MaidCat Plugin"), NAME_None, FMaidCatStyle::GetStyleSetName())
	{
	}

	// TCommands<> interface
	virtual void RegisterCommands() override;

public:
	TSharedPtr< FUICommandInfo > OpenPluginWindow;
};
