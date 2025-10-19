<#
.SYNOPSIS
    Creates a single symbolic link for the MaidCat plugin in a specified Unreal Engine project's Plugins folder.

.DESCRIPTION
    This script provides a user-friendly GUI to select an Unreal Engine project.
    It then creates a single symbolic link to the 'MaidCat' plugin directory.

    NOTE: This is the simplest and fastest method for development. It may cause a
    harmless capitalization warning in the Unreal Engine log, which can be ignored.
#>

# --------------------------------------------------------------------------
# 1. Auto-Elevate to Administrator
# --------------------------------------------------------------------------
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process PowerShell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

# --------------------------------------------------------------------------
# 2. GUI: Folder Selection Dialog
# --------------------------------------------------------------------------
try {
    Add-Type -AssemblyName System.Windows.Forms
    $FolderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
    $FolderBrowser.Description = "Select your Unreal Engine project folder"
    $FolderBrowser.ShowNewFolderButton = $false
    
    $InitialDir = [System.Environment]::GetFolderPath('MyDocuments')
    if (Test-Path (Join-Path $InitialDir "Unreal Projects")) {
        $FolderBrowser.SelectedPath = (Join-Path $InitialDir "Unreal Projects")
    }
    
    if ($FolderBrowser.ShowDialog() -ne "OK") {
        [System.Windows.Forms.MessageBox]::Show("Operation cancelled by user.", "Cancelled", "OK", "Information")
        exit
    }
    $ProjectDir = $FolderBrowser.SelectedPath
} catch {
    Write-Host "Error: Failed to load GUI components." -ForegroundColor Red
    Read-Host -Prompt "Press Enter to exit"
    exit
}

# --------------------------------------------------------------------------
# 3. Core Logic: Create Single Symbolic Link
# --------------------------------------------------------------------------

# Validate that the selected folder is an Unreal project
if (-not (Test-Path (Join-Path -Path $ProjectDir -ChildPath "*.uproject"))) {
    [System.Windows.Forms.MessageBox]::Show("The selected folder is not a valid Unreal Engine project (no .uproject file found).", "Error", "OK", "Error")
    exit
}

# Define paths
$SourcePluginDir = Join-Path -Path $PSScriptRoot -ChildPath "MaidCat"
$PluginsDir = Join-Path -Path $ProjectDir -ChildPath "Plugins"
$DestinationLinkPath = Join-Path -Path $PluginsDir -ChildPath "MaidCat"

try {
    # Create 'Plugins' directory if it doesn't exist
    if (-not (Test-Path $PluginsDir)) {
        New-Item -ItemType Directory -Path $PluginsDir -ErrorAction Stop | Out-Null
    }

    # Remove existing plugin directory/link at the destination
    if (Test-Path $DestinationLinkPath) {
        Remove-Item -Path $DestinationLinkPath -Recurse -Force -ErrorAction Stop
    }

    # Create the symbolic link
    New-Item -ItemType SymbolicLink -Path $DestinationLinkPath -Target $SourcePluginDir -ErrorAction Stop

    [System.Windows.Forms.MessageBox]::Show("Symbolic link created successfully!`n`nSource: $SourcePluginDir`nDestination: $DestinationLinkPath", "Success", "OK", "Information")

} catch {
    [System.Windows.Forms.MessageBox]::Show("An error occurred during the linking process:`n`n$($_.Exception.Message)", "Error", "OK", "Error")
    exit
}