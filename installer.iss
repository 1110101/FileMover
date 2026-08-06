; Inno Setup Script for FileMover
; Automatically creates installer with uninstaller for Windows

#define MyAppName "FileMover"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "FileMover"
#define MyAppURL "https://github.com/1110101/FileMover"
#define MyAppExeName "FileMover.exe"

[Setup]
; App information
AppId={{D8F9C7B3-4A2E-4F8D-9B7C-6E5A8F1D2C3B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
; Installation directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Output settings
OutputDir=installer_output
OutputBaseFilename=FileMover-{#MyAppVersion}-Setup
; Compression
Compression=lzma
SolidCompression=yes
; Windows version requirements
MinVersion=10.0
; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Uninstall settings
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
; Visual settings
WizardStyle=modern
SetupIconFile=

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Start {#MyAppName} automatically with Windows"; GroupDescription: "Startup Options:"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Autostart registry entry (only if user selected the task)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: autostart

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Kill any running instances before installation
    Exec('taskkill', '/F /IM FileMover.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
  RegKey: String;
begin
  if CurUninstallStep = usUninstall then
  begin
    // Kill any running instances
    Exec('taskkill', '/F /IM FileMover.exe /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Clean up registry configuration (ask user first)
    if MsgBox('Do you want to remove all FileMover configuration data (rules, settings)?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      RegDeleteKeyIncludingSubkeys(HKEY_CURRENT_USER, 'Software\FileMover');
    end;
  end;
end;

