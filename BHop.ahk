#Persistent
#InstallKeybdHook
#UseHook
SetKeyDelay, 10, 10
SetBatchLines, -1

; =============== CONFIG =================
pressDuration := 10      ; Space pressed down for 10 ms (0.01s)
interval := 45           ; Repeat every 45 ms
delayBeforeBhop := 600   ; Wait 600 ms (0.6s) before jumping for more momentum
; ========================================

$w::
    Send, {w down}   ; keep W working

    startTime := A_TickCount  ; record the time when W is pressed

    While GetKeyState("w", "P")  ; while W is physically held
    {
        elapsed := A_TickCount - startTime
        if (elapsed < delayBeforeBhop)
        {
            Sleep, 10  ; small sleep to avoid CPU overuse
            continue
        }

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

    Send, {w up}  ; release W when you let go
return
