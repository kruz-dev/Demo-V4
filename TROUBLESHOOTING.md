# Demo V4 - Troubleshooting Guide

## ❌ Cheat Not Working? (Or getting an `WinDivert` Error)

Make sure that:
- All *VPNs* Turned off
- Your *Antivirus* is Disabled (Or add the `Demo V4` Folder to the exceptions)

## ⛔ Cheat Not Opening?

Common Causes:
- Python not installed
- PIP not installed
- Python/PIP not added to PATH

Solution:
1.  **Install Python 3.11+** from [www.python.org/downloads/release/python-3119/](https://www.python.org/downloads/release/python-3119/)
2.  **Select your platform** and download the installer
3.  **Run the installer**
4.  **Check the '`Add Python to PATH`' toggle**
5.  **Click "Install Now"**
6.  **In the `Demo V4` folder, run `Requirements Installer.bat`**
7.  **Ensure no VPNs or antivirus are interfering**
8.  **Run `start.bat` and start having fun :]**

## 🔧 How to Manually Add Python to PATH

**If Python is installed but not working, manually add it to PATH:**

### Windows 10/11:
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Click on the `Advanced` Section
3. Click **"Environment Variables"**
4. Under **"System Variables"**, find `Path` and click **"Edit"**
5. Click **"New"** and add these paths (adjust for your Python version & ***PC User Name***):
   ```
   C:\Users\[Type your PC Username here]\AppData\Local\Programs\Python\Python311
   C:\Users\[Type your PC Username here]\AppData\Local\Programs\Python\Python311\Scripts
   ```
6. Click **"OK"** to save all dialogs
