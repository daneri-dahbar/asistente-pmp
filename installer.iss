[Setup]
; Información básica de la aplicación
AppId={{8C5D4A2B-1F3E-4B9A-8D2C-5E7F9A1B3C4D}
AppName=Asistente para Certificación PMP
AppVersion=2.0.0
AppVerName=Asistente para Certificación PMP 2.0.0
AppPublisher=Daneri Dahbar
AppPublisherURL=https://github.com/tu-usuario/asistente-pmp
AppSupportURL=https://github.com/tu-usuario/asistente-pmp/issues
AppUpdatesURL=https://github.com/tu-usuario/asistente-pmp/releases
DefaultDirName={autopf}\Asistente PMP
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=Asistente-PMP-Installer-v2.0.0
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Compatibilidad con Windows
MinVersion=10.0.17763
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Ejecutable principal
Source: "dist\ChatGPT-Assistant.exe"; DestDir: "{app}"; Flags: ignoreversion

; Archivos de configuración (se creará durante la instalación)

; Base de datos y configuración (si existen)
Source: "chat_history.db"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "db\*"; DestDir: "{app}\db"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; Assets
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentación
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "ICONO-README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{autoprograms}\Asistente PMP"; Filename: "{app}\ChatGPT-Assistant.exe"; IconFilename: "{app}\assets\icon.ico"
Name: "{autodesktop}\Asistente PMP"; Filename: "{app}\ChatGPT-Assistant.exe"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Asistente PMP"; Filename: "{app}\ChatGPT-Assistant.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\ChatGPT-Assistant.exe"; Description: "{cm:LaunchProgram,Asistente PMP}"; Flags: nowait postinstall skipifsilent

[Registry]
; Registrar la aplicación para desinstalación
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\AsistentePMP"; ValueType: string; ValueName: "DisplayName"; ValueData: "Asistente para Certificación PMP"
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\AsistentePMP"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "2.0.0"
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\AsistentePMP"; ValueType: string; ValueName: "Publisher"; ValueData: "Daneri Dahbar"

; Asociar archivos de configuración (opcional)
Root: HKCR; Subkey: ".pmpconfig"; ValueType: string; ValueName: ""; ValueData: "AsistentePMPConfig"
Root: HKCR; Subkey: "AsistentePMPConfig"; ValueType: string; ValueName: ""; ValueData: "Configuración Asistente PMP"
Root: HKCR; Subkey: "AsistentePMPConfig\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\assets\icon.ico"

[UninstallDelete]
Type: files; Name: "{app}\.env"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\.venv"

[Code]
procedure InitializeWizard;
begin
  WizardForm.Caption := 'Instalador - Asistente para Certificación PMP v2.0.0';
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  // Verificar en la página de directorio
  if CurPageID = wpSelectDir then
  begin
    // Verificar espacio en disco (mínimo 100 MB)
    if GetSpaceOnDisk(ExtractFileDrive(WizardForm.DirEdit.Text)) < 100 * 1024 * 1024 then
    begin
      MsgBox('No hay suficiente espacio en disco. Se requieren al menos 100 MB.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Crear archivo de configuración inicial si no existe
    if not FileExists(ExpandConstant('{app}\.env')) then
    begin
      SaveStringToFile(ExpandConstant('{app}\.env'), 
        '# Configuración de Asistente para Certificación PMP' + #13#10 +
        '# Reemplaza "tu_clave_api_aqui" con tu clave real de OpenAI' + #13#10 +
        'OPENAI_API_KEY=tu_clave_api_aqui' + #13#10 +
        '' + #13#10 +
        '# Configuración de base de datos (opcional)' + #13#10 +
        'DATABASE_URL=sqlite:///chat_history.db' + #13#10, False);
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Preguntar si eliminar datos de usuario
    if MsgBox('¿Deseas eliminar también los datos de usuario (historial de chat, configuración)?', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{app}'), True, True, True);
    end;
  end;
end; 