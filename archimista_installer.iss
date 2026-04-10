; ============================================================================
; archimista_installer.iss — Inno Setup script for Archimista Windows installer
; ============================================================================
;
; This creates a professional Windows installer (.exe) that:
;   - Bundles the PyInstaller output (dist\archimista\)
;   - Guides the user through installation with a wizard
;   - Creates Start Menu shortcuts
;   - Optionally launches Archimista after installation
;
; Requirements:
;   - Inno Setup 6.x installed (https://jrsoftware.org/isdl.php)
;   - PyInstaller bundle already built (run build_installer.bat first)
;
; Build:
;   Right-click this file → Compile in Inno Setup Compiler
;   Or: iscc.exe archimista_installer.iss
; ============================================================================

#define MyAppName "Archimista"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Archimista"
#define MyAppURL "https://github.com/srbntt/archimista"
#define MyAppExeName "Archimista.exe"
#define MyAppDescription "Sistema informativo per la descrizione archivistica"

[Setup]
; App identity
AppId={{A3B7C9D1-4E5F-6A7B-8C9D-0E1F2A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation paths
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Output
OutputDir=output
OutputBaseFilename=Archimista-Setup-{#MyAppVersion}
SetupIconFile=
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; UI
WizardStyle=modern
WizardSizePercent=100,100
DisableWelcomePage=no
ShowLanguageDialog=no

; Privileges — we need write access to the install dir for db/media
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Misc
UsePreviousAppDir=yes
DisableProgramGroupPage=no
DisableReadyPage=no

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Core application files (from PyInstaller build)
; The source path assumes you ran build_installer.bat first.
Source: "dist\archimista\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; NOTE: If dist\archimista\ doesn't exist, the build will fail.
; Make sure to run build_installer.bat before compiling this installer.

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Run]
; Launch after installation (optional)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent shellexec; WorkingDir: "{app}"

[Code]
// ============================================================================
// Custom Pascal code for installer behavior
// ============================================================================

var
  InstallWithoutData: Boolean;

// ---------------------------------------------------------------------------
// Check if the PyInstaller output exists before proceeding
// ---------------------------------------------------------------------------
function InitializeSetup(): Boolean;
var
  CheckFile: String;
begin
  Result := True;
  CheckFile := ExpandConstant('{src}\dist\archimista\{#MyAppExeName}');
  if not FileExists(CheckFile) then
  begin
    // Try the default source path
    CheckFile := ExpandConstant('{srcexe}');
    // We allow the setup to proceed — the Files section will fail if missing
  end;
end;

// ---------------------------------------------------------------------------
// Create media directory at install time so it's writable
// ---------------------------------------------------------------------------
procedure CurStepChanged(CurStep: TSetupStep);
var
  MediaDir: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Ensure media directory exists for user uploads
    MediaDir := ExpandConstant('{app}\media');
    if not DirExists(MediaDir) then
      CreateDir(MediaDir);

    // Ensure staticfiles directory exists
    MediaDir := ExpandConstant('{app}\staticfiles');
    if not DirExists(MediaDir) then
      CreateDir(MediaDir);
  end;
end;

// ---------------------------------------------------------------------------
// Custom page: Ask about demo data (informational — handled by launcher)
// ---------------------------------------------------------------------------
procedure InitializeWizard();
begin
  // The launcher handles the demo data question at first run,
  // so we just show a note in the wizard.
end;
