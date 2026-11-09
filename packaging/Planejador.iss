#ifndef AppVersion
#define AppVersion "0.2.10"
#endif
[Setup]
AppId={{A1E67E80-1B29-4D13-B744-523F1CA0C0B7}
AppName=Planejador de Experimentos
AppVersion={#AppVersion}
AppPublisher=Lucas Montalvão
DefaultDirName={localappdata}\Programs\Planejador de Experimentos
DefaultGroupName=Planejador de Experimentos
PrivilegesRequired=lowest
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist\installer
OutputBaseFilename=Planejador-Windows-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\Planejador de Experimentos.exe
[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"
[Files]
Source: "..\dist\release\Planejador de Experimentos\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{autoprograms}\Planejador de Experimentos"; Filename: "{app}\Planejador de Experimentos.exe"
Name: "{autodesktop}\Planejador de Experimentos"; Filename: "{app}\Planejador de Experimentos.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\Planejador de Experimentos.exe"; Description: "Abrir Planejador de Experimentos"; Flags: nowait postinstall skipifsilent
