#define MyAppName "Calculadora de Prestaciones"
#define MyAppVersion "1.4.1"
#define MyAppPublisher "Despacho Jurídico Laboral"
#define MyAppExeName "CalculadoraPrestaciones.exe"

[Setup]
AppId={{8CB87353-8D11-47C6-A497-A2B9F83664E2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Calculadora de Prestaciones
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Instalador
OutputBaseFilename=Instalador_CalculadoraPrestaciones_v{#MyAppVersion}
SetupIconFile=calculadora_despacho_(1).ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
Source: "dist\CalculadoraPrestaciones\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent
