import subprocess

def test_sudo_access():
    # Check for 'ssh' (Debian/Ubuntu) or 'sshd' (RHEL/Arch)
    services_to_check = ["ssh", "sshd", "cron"]
    
    for service in services_to_check:
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "status", service],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Exit codes: 0 = active, 1-3 = inactive/failed (command ran successfully)
            if result.returncode in [0, 1, 2, 3]:
                print(f"✅ SUCCESS: Passwordless sudo worked for '{service}'!")
                print(f"   Status line: {result.stdout.splitlines()[0] if result.stdout else 'No output'}")
                return True
            elif result.returncode == 4:
                print(f"⚠️  Unit '{service}' not installed on this system.")
        except subprocess.TimeoutExpired:
            print(f"❌ FAILURE: Command timed out on '{service}'. Sudo is still prompting for a password!")
            return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

    print("❌ FAILURE: None of the target services could be queried.")
    return False

if __name__ == "__main__":
    test_sudo_access()