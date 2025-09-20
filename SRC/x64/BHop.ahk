#Persistent
#InstallKeybdHook
#UseHook
SetKeyDelay, 10, 10
SetBatchLines, -1

; =============== CONFIG =================
pressDuration := 10      ; Space pressed down for 10 ms (0.01s)
interval := 45           ; Repeat every 45 ms
; ========================================

; Detect when W is held, but also send it through to the game
$w::
    Send, {w down}                ; keep W working
    While GetKeyState("w", "P")   ; while W is physically held
    {
        ; Check if ANY movement key is being held
        if (GetKeyState("w", "P") or GetKeyState("a", "P") or GetKeyState("s", "P") or GetKeyState("d", "P"))
        {
            Send, {Space down}
            Sleep, %pressDuration%
            Send, {Space up}
            Sleep, % (interval - pressDuration)
        }
        else
        {
            break
        }
    }
    Send, {w up}   ; release W when you let go
return
