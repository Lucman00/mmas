import platform
import shutil
import subprocess
import sys

def _is_mpv_installed():
    """Check if mpv is available in PATH."""
    return shutil.which("mpv") is not None

def _install_mpv_windows():
    """Try Windows package managers in order of preference."""
    # Try winget first (built into Win10+)
    if shutil.which("winget"):
        try:
            subprocess.check_call([
                "winget", "install", "--id", "shinchiro.mpv", "-e"
            ])
            return True
        except subprocess.CalledProcessError:
            pass  # fall through to next option
    
    # Try scoop
    if shutil.which("scoop"):
        try:
            subprocess.check_call(["scoop", "install", "extras/mpv"])
            return True
        except subprocess.CalledProcessError:
            pass
    
    # Try chocolatey
    if shutil.which("choco"):
        try:
            subprocess.check_call(["choco", "install", "mpv", "-y"])
            return True
        except subprocess.CalledProcessError:
            pass
    
    return False

def _install_mpv_linux():
    """Detect distro and use appropriate package manager."""
    # Check which package manager exists
    if shutil.which("apt"):
        cmd = ["sudo", "apt", "install", "-y", "mpv"]
    elif shutil.which("dnf"):
        cmd = ["sudo", "dnf", "install", "-y", "mpv"]
    elif shutil.which("pacman"):
        cmd = ["sudo", "pacman", "-S", "--noconfirm", "mpv"]
    elif shutil.which("zypper"):
        cmd = ["sudo", "zypper", "install", "-y", "mpv"]
    else:
        return False
    
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:
        return False

def setup_mpv():
    """Main entry point for mpv setup."""
    if _is_mpv_installed():
        print(f"mpv already installed at: {shutil.which('mpv')}")
        return True
    
    system = platform.system().lower()
    
    if system == "windows":
        print("Attempting to install mpv via Windows package manager...")
        success = _install_mpv_windows()
    elif system == "linux":
        print("Attempting to install mpv via system package manager...")
        success = _install_mpv_linux()
    else:
        print(f"Automatic mpv installation not supported on {system}")
        return False
    
    if success:
        print("mpv installed successfully.")
    else:
        print("Could not install mpv automatically.")
        print("Please install manually: https://mpv.io/installation/")
    
    return success