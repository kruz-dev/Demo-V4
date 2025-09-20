#Persistent
#InstallKeybdHook
#InstallMouseHook

~LButton::
    While GetKeyState("LButton", "P")
    {
        Click
        Sleep, 50 ; 0.05 seconds
    }
Return
