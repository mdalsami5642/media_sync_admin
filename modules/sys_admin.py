import subprocess
import shutil

# Canonical list of allowed services to prevent arbitrary command injection
ALLOWED_SERVICES = {"smbd": "Samba", "ssh": "SSH Server"}

def manage_service(service_name: str, action: str) -> dict:
    """
    Manages service lifecycle: start, stop, restart, enable, disable.
    """
    if service_name not in ALLOWED_SERVICES:
        return {"success": False, "message": f"Unauthorized service: {service_name}"}

    allowed_actions = {"start", "stop", "restart", "enable", "disable"}
    if action not in allowed_actions:
        return {"success": False, "message": f"Unauthorized action: {action}"}

    cmd = ["sudo", "systemctl", action, service_name]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return {"success": True, "message": f"Successfully executed '{action}' on {service_name}."}
        else:
            return {"success": False, "message": result.stderr.strip() or "Command failed."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def get_service_status(service_name: str) -> dict:
    """
    Returns running state (active/inactive) and boot persistence (enabled/disabled).
    """
    if service_name not in ALLOWED_SERVICES:
        return {"success": False, "message": f"Unauthorized service: {service_name}"}

    # Check active state
    active_cmd = ["sudo", "systemctl", "is-active", service_name]
    active_res = subprocess.run(active_cmd, capture_output=True, text=True)
    is_active = active_res.stdout.strip() == "active"

    # Check boot-enable state
    enabled_cmd = ["sudo", "systemctl", "is-enabled", service_name]
    enabled_res = subprocess.run(enabled_cmd, capture_output=True, text=True)
    is_enabled = enabled_res.stdout.strip() == "enabled"

    return {
        "success": True,
        "service": service_name,
        "active": is_active,
        "enabled": is_enabled,
        "raw_state": active_res.stdout.strip()
    }


def get_service_logs(service_name: str, lines: int = 30) -> dict:
    """
    Fetches recent system log entries using journalctl.
    """
    if service_name not in ALLOWED_SERVICES:
        return {"success": False, "message": f"Unauthorized service: {service_name}"}

    cmd = ["sudo", "journalctl", "-u", service_name, "-n", str(lines), "--no-pager"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        log_lines = result.stdout.strip().splitlines() if result.stdout else []
        return {"success": True, "logs": log_lines}
    except Exception as e:
        return {"success": False, "message": str(e)}


def manage_package(package_name: str, action: str) -> dict:
    """
    Installs or purges packages using apt.
    """
    allowed_packages = {"samba", "openssh-server"}
    if package_name not in allowed_packages:
        return {"success": False, "message": f"Unauthorized package: {package_name}"}

    if action == "install":
        cmd = ["sudo", "apt", "install", "-y", package_name]
    elif action == "uninstall":
        cmd = ["sudo", "apt", "purge", "-y", package_name]
    else:
        return {"success": False, "message": "Invalid action. Use 'install' or 'uninstall'."}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return {"success": True, "message": f"Package '{package_name}' {action}ed successfully."}
        else:
            return {"success": False, "message": result.stderr.strip()}
    except Exception as e:
        return {"success": False, "message": str(e)}