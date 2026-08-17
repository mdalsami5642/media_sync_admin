import os
import subprocess

CONFIG_PATHS = {
    "smbd": "/etc/samba/smb.conf",
    "ssh": "/etc/ssh/sshd_config"
}

def locate_config(service_name: str) -> dict:
    path = CONFIG_PATHS.get(service_name)
    if not path or not os.path.exists(path):
        return {"success": False, "message": f"Config file for '{service_name}' not found."}

    try:
        with open(path, "r") as f:
            content = f.read()
        return {
            "success": True,
            "service": service_name,
            "path": path,
            "content": content
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


def add_samba_share(share_name: str, folder_path: str, read_only: bool = False, guest_ok: bool = True) -> dict:
    path = CONFIG_PATHS["smbd"]
    
    # 1. Expand user path (~/Videos)
    expanded_path = os.path.expanduser(folder_path)
    os.makedirs(expanded_path, exist_ok=True)
    
    # 2. Fix parent home directory permissions (allows Samba guest/user traversal)
    parent_dir = os.path.dirname(expanded_path)
    if parent_dir.startswith("/home/"):
        os.chmod(parent_dir, 0o755)

    # 3. Grant full read/write/execute permissions to folder & recursively to files
    try:
        subprocess.run(["chmod", "-R", "777", expanded_path], check=True)
    except Exception:
        os.chmod(expanded_path, 0o777)

    # 4. Check duplicate shares
    current_config = locate_config("smbd")
    if current_config["success"] and f"[{share_name}]" in current_config["content"]:
        return {"success": False, "message": f"Share [{share_name}] already exists in smb.conf."}

    # 5. Format robust Samba block supporting all media/file types on Android & PC
    share_block = (
        f"\n[{share_name}]\n"
        f"   path = {expanded_path}\n"
        f"   browseable = yes\n"
        f"   read only = {'yes' if read_only else 'no'}\n"
        f"   guest ok = {'yes' if guest_ok else 'no'}\n"
        f"   public = {'yes' if guest_ok else 'no'}\n"
        f"   force user = {os.getlogin()}\n"
        f"   create mask = 0777\n"
        f"   directory mask = 0777\n"
    )

    try:
        proc = subprocess.run(
            ["sudo", "tee", "-a", path],
            input=share_block,
            text=True,
            capture_output=True,
            timeout=5
        )
        
        if proc.returncode != 0:
            return {"success": False, "message": f"Failed to update config: {proc.stderr.strip()}"}

        # Reload Samba settings
        subprocess.run(["sudo", "smbcontrol", "all", "reload-config"], capture_output=True, text=True)

        return {
            "success": True,
            "message": f"Share [{share_name}] ready! Access seamlessly on Android & Desktop PC."
        }
    except Exception as e:
        return {"success": False, "message": str(e)}