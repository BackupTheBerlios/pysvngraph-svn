; Partie communes du script a tous les produits

;--------------------------------------------------------------------
!define PRODUCT_NAME "pysvngraph"
!define PRODUCT_PUBLISHER "pysvngraph Developpement team"
!define PRODUCT_WEB_SITE "http://pysvngraph.berlios.de/"
!define PRODUCT_PYTHON_NAME "pysvngraph"
!define PRODUCT_VERSION "0.0.3"
!define PRODUCT_ROOT_KEY "HKCU"
!define PRODUCT_PATH_KEY "Software\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "${PRODUCT_ROOT_KEY}"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_DEPLOIEMENT_PATH "."
!define PRODUCT_EXE "${PRODUCT_PYTHON_NAME}.exe"
!define PRODUCT_APPPATH_ROOTKEY "HKLM"
!define PRODUCT_APPPATH_KEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${PRODUCT_EXE}"
;--------------------------------------------------------------------
!define PRODUCT_NAME_VERSION "${PRODUCT_NAME} ${PRODUCT_VERSION}"
;--------------------------------------------------------------------
SetCompressor LZMA
;--------------------------------------------------------------------

;--------------------------------------------------------------------
!include "Sections.nsh"
;--------------------------------------------------------------------

;--------------------------------------------------------------------
; MUI 1.67 compatible ------
;--------------------------------------------------------------------
!include "MUI.nsh"
;--------------------------------------------------------------------

;--------------------------------------------------------------------
; MUI Settings
;--------------------------------------------------------------------
!define MUI_ABORTWARNING
!define MUI_ICON "..\res\pysvngraph.ico"
!define MUI_UNICON "..\res\pysvngraph.ico"
;--------------------------------------------------------------------

;====================================================================
; Pages
;--------------------------------------------------------------------
; Welcome page
!insertmacro MUI_PAGE_WELCOME
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!insertmacro MUI_PAGE_FINISH
;--------------------------------------------------------------------

;--------------------------------------------------------------------
; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES
;====================================================================

;====================================================================
; Language files
;!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "English"
;====================================================================

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------
;====================================================================


;====================================================================
; Variables
;--------------------------------------------------------------------
Name "${PRODUCT_NAME_VERSION}"

OutFile "${PRODUCT_DEPLOIEMENT_PATH}\${PRODUCT_NAME}-${PRODUCT_VERSION}.exe"

InstallDir "$PROGRAMFILES\${PRODUCT_NAME}"
ShowInstDetails show
ShowUnInstDetails show
!define UNINSTALL_EXE "$INSTDIR\Uninstall.exe"
!define UNINSTALL_NOM "Uninstall ${PRODUCT_NAME} ${PRODUCT_VERSION}.lnk"
;====================================================================

;====================================================================
; Sections
;--------------------------------------------------------------------
Section "Main" SecMain
    SetOutPath "$INSTDIR"

    File /r "..\src\dist\*"
    File "..\res\msvcr71.dll"

    WriteRegStr HKCR ".pysvngraph" "" "pysvngraph_File"
    WriteRegStr HKCR "pysvngraph_File\DefaultIcon" "" "$INSTDIR\${PRODUCT_EXE}"
    WriteRegStr HKCR "pysvngraph_File\shell\open\command" "" '$INSTDIR\${PRODUCT_EXE} "%1"'
    WriteRegStr HKCR "pysvngraph_File\shell\dumpconfig\command" "" '$INSTDIR\${PRODUCT_EXE} -dumpconfig "%1" "%1.ini"'

SectionEnd
;--------------------------------------------------------------------

Section -Post
    WriteUninstaller "${UNINSTALL_EXE}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "${PRODUCT_NAME_VERSION}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "${UNINSTALL_EXE}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
    WriteRegStr ${PRODUCT_APPPATH_ROOTKEY} "${PRODUCT_APPPATH_KEY}" "" "$INSTDIR\${PRODUCT_EXE}"
SectionEnd

Section -AdditionalIcons
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${UNINSTALL_NOM}" "${UNINSTALL_EXE}"
SectionEnd

;====================================================================

;====================================================================
; Fonctions
;--------------------------------------------------------------------
Function .onInit
FunctionEnd
;--------------------------------------------------------------------
; Desintallation
;--------------------------------------------------------------------
Function un.onUninstSuccess
    HideWindow
    MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) has been removed from your computer."
FunctionEnd
;--------------------------------------------------------------------
Function un.onInit
    MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to remove $(^Name) and all it's componants ?" IDYES +2
    Abort
FunctionEnd
;--------------------------------------------------------------------
Section Uninstall
    Delete "${UNINSTALL_EXE}"
    Delete "$SMPROGRAMS\${PRODUCT_NAME}\${UNINSTALL_NOM}"
    RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"

    RMDir /r "$INSTDIR"

    DeleteRegKey ${PRODUCT_ROOT_KEY} "${PRODUCT_PATH_KEY}"
    DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
    DeleteRegKey ${PRODUCT_APPPATH_ROOTKEY} "${PRODUCT_APPPATH_KEY}" ""
    DeleteRegKey HKCR ".pysvngraph"
    DeleteRegKey HKCR "pysvngraph_File"

    SetAutoClose true
SectionEnd
;====================================================================
