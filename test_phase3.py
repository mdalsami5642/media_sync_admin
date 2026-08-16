import os
from modules.config_manager import locate_config, add_samba_share

def test_config_manager():
    print("--- 1. Testing Config File Locating ---")
    smb_info = locate_config("smbd")
    print(f"Samba Config Located: {smb_info['success']} | Path: {smb_info.get('path')}")
    
    ssh_info = locate_config("ssh")
    print(f"SSH Config Located: {ssh_info['success']} | Path: {ssh_info.get('path')}")

    print("\n--- 2. Testing Samba Share Creation ---")
    test_folder = os.path.expanduser("~/SmartMediaSync_Test")
    share_name = "SmartTestShare"
    
    result = add_samba_share(share_name=share_name, folder_path=test_folder, read_only=False, guest_ok=True)
    print(f"Add Share Result: {result['message']}")

    print("\n--- 3. Verifying Share in Config ---")
    updated_info = locate_config("smbd")
    if result["success"] and f"[{share_name}]" in updated_info["content"]:
        print(f"✅ SUCCESS: [{share_name}] section verified inside /etc/samba/smb.conf!")
        print(f"✅ Directory created at: {test_folder}")
        print("\n✅ PHASE 3 TEST PASSED SUCCESSFULLY!")
    else:
        print("\n❌ PHASE 3 TEST FAILED.")

if __name__ == "__main__":
    test_config_manager()