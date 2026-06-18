; Script de Inno Setup para crear el instalador de BacilosApp
; Requiere Inno Setup 6+: https://jrsoftware.org/isdl.php

#define MyAppName "Sistema de Analisis de Bacilos"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Laboratorio"
#define MyAppExeName "BacilosApp.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".bac"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
AppId={{BacilosApp-2026-PROD}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\BacilosApp
DisableProgramGroupPage=yes
LicenseFile=readme.md
OutputDir=.
OutputBaseFilename=BacilosApp_Setup
SetupIconFile=assets\bacilos.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; NOTA: Cambia "dist\BacilosApp" por la ruta real de tu build
Source: "dist\BacilosApp\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\BacilosApp\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; No borrar datos del usuario durante desinstalación
Type: filesandordirs; Name: "{app}\_internal"
Type: files; Name: "{app}\{#MyAppExeName}"
