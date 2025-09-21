#Persistent
#InstallKeybdHook
#InstallMouseHook

~LButton::
    SetTimer, AutoClick, 50 ; start the auto-clicking every 50ms
Return

~LButton Up::
    SetTimer, AutoClick, Off ; stop the auto-clicking when button is released
Return

AutoClick:
    Click
Return
