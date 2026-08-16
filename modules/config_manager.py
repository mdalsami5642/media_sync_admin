import os
import subprocess

# Config file locations for OS audit requirements
CONFIG_PATHS = {
    "smbd": "/etc/samba/smb.conf",
    "ssh": "/etc/ssh/sshd_config"
}

def locate_config(service_name: str) -> dict:
    """
    Locates and returns the path and content of a service's configuration file.
    """
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
    """
    Appends a new public/private network share block to /etc/samba/smb.conf
    and reloads Samba configuration.
    """
    path = CONFIG_PATHS["smbd"]
    
    # 1. Expand user path (~/Media) and ensure folder exists
    expanded_path = os.path.expanduser(folder_path)
    os.makedirs(expanded_path, exist_ok=True)
    
    # Set folder permissions so Samba users can access it
    os.chmod(expanded_path, 0o777)

    # 2. Check if share section name already exists
    current_config = locate_config("smbd")
    if current_config["success"] and f"[{share_name}]" in current_config["content"]:
        return {"success": False, "message": f"Share [{share_name}] already exists in smb.conf."}

    # 3. Format Samba share configuration block
    share_block = (
        f"\n[{share_name}]\n"
        f"   path = {expanded_path}\n"
        f"   browseable = yes\n"
        f"   read only = {'yes' if read_only else 'no'}\n"
        f"   guest ok = {'yes' if guest_ok else 'no'}\n"
        f"   create mask = 0777\n"
        f"   directory mask = 0777\n"
    )

    try:
        # 4. Append to /etc/samba/smb.conf using sudo tee -a
        proc = subprocess.run(
            ["sudo", "tee", "-a", path],
            input=share_block,
            text=True,
            capture_output=True,
            timeout=5
        )
        
        if proc.returncode != 0:
            return {"success": False, "message": f"Failed to update config: {proc.stderr.strip()}"}

        # 5. Reload Samba service to apply changes dynamically
        subprocess.run(["sudo", "smbcontrol", "all", "reload-config"], capture_output=True, text=True)

        return {
            "success": True,
            "message": f"Share [{share_name}] added at '{expanded_path}' and Samba reloaded successfully."
        }
    except Exception as e:
        return {"success": False, "message": str(e)}