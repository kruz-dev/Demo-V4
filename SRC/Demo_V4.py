# Demo V4.py - OP Aim + Recoil Control + GodMode + External Full Auto + Auto BHop (with config)
import os
import sys
import time
import threading
import ctypes
import subprocess
import win32gui
import win32con
import win32process
import psutil

# ---------------------------
# Clear screen function
# ---------------------------
def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

# ---------------------------
# Admin check
# ---------------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

# Clear screen after admin check
clear_screen()

# ---------------------------
# Install modules if missing
# ---------------------------
modules = ["pyautogui", "pynput", "pydivert", "pywin32", "psutil"]
for module in modules:
    try:
        __import__(module)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

import pyautogui
pyautogui.FAILSAFE = False
from pynput import mouse, keyboard as kb
import pydivert

# ---------------------------
# Set WinDivert DLL path
# ---------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
windivert_dll = os.path.join(current_dir, "x64", "WinDivert.dll")
if not os.path.exists(windivert_dll):
    print(f"WinDivert.dll not found in {windivert_dll}")
    sys.exit(1)

pydivert.WinDivert.lib_path = windivert_dll

# ---------------------------
# Config system
# ---------------------------
CONFIG_FILE = os.path.join(current_dir, "config.txt")

default_config = {
    "recoil_speed": 3,
    "recoil_interval": 0.04,
    "spread_delay": 0.10,
    "freeze_duration": 0.25,
    "freeze_interval": 0.25,
    "god_freeze_duration": 0.2,
    "god_freeze_interval": 0.4
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            for k, v in default_config.items():
                f.write(f"{k}={v}\n")
        return default_config.copy()

    config = default_config.copy()
    with open(CONFIG_FILE, "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                try:
                    config[k] = float(v)
                except ValueError:
                    pass
    return config

# ---------------------------
# Window Selection System
# ---------------------------
def get_all_windows():
    """Get all visible windows with their titles and process IDs"""
    windows = []
    
    def enum_windows_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = psutil.Process(pid)
                    exe_name = process.name()
                except:
                    exe_name = "Unknown"
                
                windows.append((hwnd, window_text, pid, exe_name))
        return True
    
    win32gui.EnumWindows(enum_windows_callback, None)
    return windows

def select_target_window():
    """Let user select which window to target"""
    print("Demo V4 — Select a process to inject into.")
    windows = get_all_windows()
    
    if not windows:
        print("No windows found!")
        return None
    
    print("\nAvailable Processes:")
    print("-" * 80)
    print(f"{'Index':<6} {'Window Title':<40} {'Process':<20} {'PID':<8}")
    print("-" * 80)
    
    for i, (hwnd, title, pid, exe_name) in enumerate(windows):
        display_title = title[:37] + "..." if len(title) > 40 else title
        print(f"{i:<6} {display_title:<40} {exe_name:<20} {pid:<8}")
    
    print("-" * 80)
    
    while True:
        try:
            choice = input("\nSelect process by index: ").strip()
            if choice == "":
                print("Please enter a valid index number.")
                continue
                
            index = int(choice)
            if 0 <= index < len(windows):
                hwnd, title, pid, exe_name = windows[index]
                print(f"Selected: {title} ({exe_name})")
                return hwnd, pid, exe_name
            else:
                print("Invalid index. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def is_target_window_active(target_hwnd):
    """Check if the target window is currently active"""
    foreground_hwnd = win32gui.GetForegroundWindow()
    return foreground_hwnd == target_hwnd

# ---------------------------
# DemoV4 Class
# ---------------------------
class DemoV4:
    def __init__(self):
        cfg = load_config()

        # Recoil settings
        self.recoil_speed = cfg["recoil_speed"]
        self.recoil_interval = cfg["recoil_interval"]
        self.spread_delay = cfg["spread_delay"]

        # State flags
        self.is_lmb_pressed = False
        self.is_rmb_pressed = False
        self.god_mode = False
        self.full_auto_mode = False
        self.bhop_mode = False
        self.should_exit = False
        self.alt_pressed = False
        self.target_window = None
        self.target_pid = None
        self.target_process_name = None

        # Lag switch timing
        self.freeze_duration = cfg["freeze_duration"]
        self.freeze_interval = cfg["freeze_interval"]

        # GodMode timing
        self.god_freeze_duration = cfg["god_freeze_duration"]
        self.god_freeze_interval = cfg["god_freeze_interval"]
        
        # Process handles
        self.full_auto_process = None
        self.bhop_process = None
        
        # Track actual active states (for dynamic control)
        self.god_mode_active = False
        self.full_auto_active = False
        self.bhop_active = False

    def is_our_window_active(self):
        """Check if our console window is active"""
        # Get our process ID
        our_pid = os.getpid()
        
        # Get foreground window and its process ID
        foreground_hwnd = win32gui.GetForegroundWindow()
        _, foreground_pid = win32process.GetWindowThreadProcessId(foreground_hwnd)
        
        # Check if foreground window belongs to our process
        return foreground_pid == our_pid

    def is_game_focused(self):
        """Check if either game window or our console is focused"""
        target_active = self.target_window and is_target_window_active(self.target_window)
        our_window_active = self.is_our_window_active()
        return target_active or our_window_active

    # ---------------------------
    # Window Selection
    # ---------------------------
    def select_window(self):
        """Let user select target window"""
        result = select_target_window()
        if result:
            self.target_window, self.target_pid, self.target_process_name = result
            print(f"Target process set: {self.target_process_name}")
            return True
        else:
            print("Failed to select window. Exiting.")
            return False

    # ---------------------------
    # Recoil control
    # ---------------------------
    def recoil_control(self):
        while self.is_lmb_pressed and not self.should_exit:
            if self.target_window and is_target_window_active(self.target_window):
                pyautogui.moveRel(0, self.recoil_speed)
            time.sleep(self.recoil_interval)
            time.sleep(self.spread_delay)

    # ---------------------------
    # Start/Stop Full Auto EXE
    # ---------------------------
    def toggle_full_auto(self):
        if self.full_auto_mode:
            exe_path = os.path.join(current_dir, "x64", "FL.exe")
            if os.path.exists(exe_path):
                try:
                    self.full_auto_process = subprocess.Popen([exe_path])
                    self.full_auto_active = True
                    print("External Full Auto ENABLED")
                except Exception as e:
                    print(f"Failed to start Full Auto: {e}")
                    self.full_auto_mode = False
            else:
                print("FL.exe not found in x64 folder!")
                print("Please compile FL.ahk to FL.exe and place it in the x64 folder")
                self.full_auto_mode = False
        else:
            if self.full_auto_process:
                try:
                    self.full_auto_process.terminate()
                    try:
                        self.full_auto_process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        self.full_auto_process.kill()
                    self.full_auto_active = False
                    print("External Full Auto DISABLED")
                except Exception as e:
                    print(f"Error stopping Full Auto: {e}")
                    try:
                        subprocess.run(["taskkill", "/f", "/im", "FL.exe"], 
                                      capture_output=True, creationflags=0x08000000)
                    except:
                        pass
                finally:
                    self.full_auto_process = None

    # ---------------------------
    # Start/Stop BHop EXE
    # ---------------------------
    def toggle_bhop(self):
        if self.bhop_mode:
            exe_path = os.path.join(current_dir, "x64", "BHop.exe")
            if os.path.exists(exe_path):
                try:
                    self.bhop_process = subprocess.Popen([exe_path])
                    self.bhop_active = True
                    print("Auto BHop ENABLED")
                except Exception as e:
                    print(f"Failed to start BHop: {e}")
                    self.bhop_mode = False
            else:
                print("BHop.exe not found in x64 folder!")
                print("Please compile BHop.ahk to BHop.exe and place it in the x64 folder")
                self.bhop_mode = False
        else:
            if self.bhop_process:
                try:
                    self.bhop_process.terminate()
                    try:
                        self.bhop_process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        self.bhop_process.kill()
                    self.bhop_active = False
                    print("Auto BHop DISABLED")
                except Exception as e:
                    print(f"Error stopping BHop: {e}")
                    try:
                        subprocess.run(["taskkill", "/f", "/im", "BHop.exe"], 
                                      capture_output=True, creationflags=0x08000000)
                    except:
                        pass
                finally:
                    self.bhop_process = None

    # ---------------------------
    # Dynamic feature control
    # ---------------------------
    def manage_external_features(self):
        """Dynamically manage external features based on focus by killing/restarting processes"""
        last_focus_state = True  # Assume initially focused
        
        while not self.should_exit:
            game_focused = self.is_game_focused()
            
            # Only take action if focus state changed
            if game_focused != last_focus_state:
                last_focus_state = game_focused
                
                # Manage Full Auto
                if self.full_auto_mode and self.full_auto_active:
                    if not game_focused:
                        # Kill Full Auto when game not focused
                        try:
                            if self.full_auto_process:
                                self.full_auto_process.terminate()
                                try:
                                    self.full_auto_process.wait(timeout=1)
                                except subprocess.TimeoutExpired:
                                    self.full_auto_process.kill()
                                self.full_auto_process = None
                        except Exception as e:
                            print(f"Error stopping Full Auto: {e}")
                            try:
                                subprocess.run(["taskkill", "/f", "/im", "FL.exe"], 
                                              capture_output=True, creationflags=0x08000000)
                            except:
                                pass
                    else:
                        # Restart Full Auto when game focused
                        try:
                            exe_path = os.path.join(current_dir, "x64", "FL.exe")
                            if os.path.exists(exe_path):
                                self.full_auto_process = subprocess.Popen([exe_path])
                            else:
                                print("FL.exe not found, cannot restart Full Auto")
                        except Exception as e:
                            print(f"Failed to restart Full Auto: {e}")
                
                # Manage BHop
                if self.bhop_mode and self.bhop_active:
                    if not game_focused:
                        # Kill BHop when game not focused
                        try:
                            if self.bhop_process:
                                self.bhop_process.terminate()
                                try:
                                    self.bhop_process.wait(timeout=1)
                                except subprocess.TimeoutExpired:
                                    self.bhop_process.kill()
                                self.bhop_process = None
                        except Exception as e:
                            print(f"Error stopping BHop: {e}")
                            try:
                                subprocess.run(["taskkill", "/f", "/im", "BHop.exe"], 
                                              capture_output=True, creationflags=0x08000000)
                            except:
                                pass
                    else:
                        # Restart BHop when game focused
                        try:
                            exe_path = os.path.join(current_dir, "x64", "BHop.exe")
                            if os.path.exists(exe_path):
                                self.bhop_process = subprocess.Popen([exe_path])
                            else:
                                print("BHop.exe not found, cannot restart BHop")
                        except Exception as e:
                            print(f"Failed to restart BHop: {e}")
            
            time.sleep(0.1)  # Check every 100ms

    # ---------------------------
    # Mouse events
    # ---------------------------
    def on_click(self, x, y, button, pressed):
        # Only process mouse events if target window is active
        if self.target_window and not is_target_window_active(self.target_window):
            return
            
        if button == mouse.Button.left:
            self.is_lmb_pressed = pressed
            if pressed and not self.full_auto_mode:
                threading.Thread(target=self.recoil_control, daemon=True).start()
        elif button == mouse.Button.right:
            self.is_rmb_pressed = pressed

    # ---------------------------
    # Keyboard events
    # ---------------------------
    def on_key_press(self, key):
        # Allow hotkeys to work in both the target window AND our console window
        target_active = self.target_window and is_target_window_active(self.target_window)
        our_window_active = self.is_our_window_active()
        
        # Only process hotkeys if either window is active (except F2 which works globally)
        if (key != kb.Key.f2 and not target_active and not our_window_active):
            return
            
        try:
            if key == kb.Key.f2:
                print("F2 pressed - exiting...")
                self.should_exit = True
                if self.full_auto_mode and self.full_auto_process:
                    self.full_auto_mode = False
                    self.toggle_full_auto()
                if self.bhop_mode and self.bhop_process:
                    self.bhop_mode = False
                    self.toggle_bhop()
                return False
            elif key == kb.Key.alt or key == kb.Key.alt_l or key == kb.Key.alt_r:
                self.alt_pressed = True
            elif key == kb.KeyCode.from_char('j') or key == kb.KeyCode.from_char('J'):
                if self.alt_pressed:
                    self.god_mode = not self.god_mode
                    self.god_mode_active = self.god_mode
                    status = "ENABLED" if self.god_mode else "DISABLED"
                    print(f"GodMode {status} - Less damage taken! (Not full invincibility)")
            elif key == kb.KeyCode.from_char('k') or key == kb.KeyCode.from_char('K'):
                if self.alt_pressed:
                    self.full_auto_mode = not self.full_auto_mode
                    self.toggle_full_auto()
            elif key == kb.KeyCode.from_char('l') or key == kb.KeyCode.from_char('L'):
                if self.alt_pressed:
                    self.bhop_mode = not self.bhop_mode
                    self.toggle_bhop()
            elif key == kb.KeyCode.from_char('c') or key == kb.KeyCode.from_char('C'):
                if self.alt_pressed:
                    clear_screen()
                    self.show_status()
        except AttributeError:
            pass

    def on_key_release(self, key):
        try:
            if key == kb.Key.alt or key == kb.Key.alt_l or key == kb.Key.alt_r:
                self.alt_pressed = False
        except AttributeError:
            pass

    # ---------------------------
    # Status display
    # ---------------------------
    def show_status(self):
        """Show current status in a clean format"""
        print("""
██████╗ ███████╗ ███╗   ███╗  ██████╗     ██╗   ██╗ ██╗██╗
██╔══██╗██╔════╝ ████╗ ████║ ██╔═══██╗    ██║   ██║ ██╔╝██║
██║  ██║█████╗   ██╔████╔██║ ██║   ██║    ██║   ██║ ██║ ██║
██║  ██║██╔══╝   ██║╚██╔╝██║ ██║   ██║    ╚██╗ ██╔╝ ███████║
██████╔╝███████╗ ██║ ╚═╝ ██║ ╚██████╔╝     ╚████╔╝  ╚════██║
╚═════╝ ╚══════╝ ╚═╝     ╚═╝ ╚═════╝       ╚═══╝        ╚═╝
        """)
        print("Demo V4 - OP Aim + Recoil Control + GodMode + External Full Auto + Auto BHop")
        print("=" * 75)
        print(f"Injected Process: {self.target_process_name}")
        print("=" * 75)
        print("CONTROLS:")
        print("LMB: Recoil control")
        print("RMB: Freezes Enemies for Easier Aiming (HOLD TO FREEZE)")
        print("Alt+J: Toggle GodMode (Harder for others to hit you)")
        print("Alt+K: Toggle Full Auto (Controls External Feature)")
        print("Alt+L: Toggle Auto BHop (NEW!)")
        print("Alt+C: Clear Logs")
        print("F2: Exit")
        print("=" * 75)

    # ---------------------------
    # Lag switch (inbound)
    # ---------------------------
    def process_inbound(self):
        try:
            with pydivert.WinDivert("inbound and (tcp or udp)") as w:
                last_freeze = time.time()
                while not self.should_exit:
                    try:
                        packet = w.recv()
                        if self.is_rmb_pressed and self.target_window and is_target_window_active(self.target_window):
                            now = time.time()
                            if now - last_freeze >= self.freeze_interval:
                                time.sleep(self.freeze_duration)
                                last_freeze = now
                        w.send(packet)
                    except pydivert.WinDivertError:
                        continue
        except Exception as e:
            print(f"Inbound WinDivert error: {e}")

    # ---------------------------
    # GodMode (outbound)
    # ---------------------------
    def process_outbound(self):
        try:
            with pydivert.WinDivert("outbound and (tcp or udp)") as w:
                last_god_freeze = time.time()
                while not self.should_exit:
                    try:
                        packet = w.recv()
                        # GodMode only works when game is focused
                        if self.god_mode and self.god_mode_active and self.is_game_focused():
                            now = time.time()
                            if now - last_god_freeze >= self.god_freeze_interval:
                                time.sleep(self.god_freeze_duration)
                                last_god_freeze = now
                        w.send(packet)
                    except pydivert.WinDivertError:
                        continue
        except Exception as e:
            print(f"Outbound WinDivert error: {e}")

    # ---------------------------
    # Start everything
    # ---------------------------
    def start(self):
        # Clear screen and show initial status
        clear_screen()
        
        # Window selection
        if not self.select_window():
            return
        
        # Clear screen again and show main interface
        clear_screen()
        self.show_status()

        # Start packet processing threads
        threading.Thread(target=self.process_inbound, daemon=True).start()
        threading.Thread(target=self.process_outbound, daemon=True).start()
        
        # Start external feature manager thread
        threading.Thread(target=self.manage_external_features, daemon=True).start()

        # Start mouse listener
        mouse_listener = mouse.Listener(on_click=self.on_click)
        mouse_listener.start()

        # Start keyboard listener
        with kb.Listener(on_press=self.on_key_press, on_release=self.on_key_release) as keyboard_listener:
            keyboard_listener.join()

        # Cleanup
        self.should_exit = True
        try:
            subprocess.run(["taskkill", "/f", "/im", "FL.exe"], 
                          capture_output=True, creationflags=0x08000000)
        except:
            pass
        try:
            subprocess.run(["taskkill", "/f", "/im", "BHop.exe"],
                          capture_output=True, creationflags=0x08000000)
        except:
            pass
        time.sleep(0.5)
        print("Exiting...")

# ---------------------------
# Run script
# ---------------------------
if __name__ == "__main__":
    app = DemoV4()
    app.start()
