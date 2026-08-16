from modules.sys_admin import manage_service, get_service_status, get_service_logs

def test_sys_admin_engine():
    print("--- 1. Testing Initial Status ---")
    status = get_service_status("smbd")
    print(f"Samba status: Active={status['active']}, Enabled={status['enabled']}")

    print("\n--- 2. Testing Service Stop ---")
    stop_res = manage_service("smbd", "stop")
    print(f"Stop result: {stop_res['message']}")
    
    status_after_stop = get_service_status("smbd")
    print(f"Samba status after stop: Active={status_after_stop['active']}")

    print("\n--- 3. Testing Service Start ---")
    start_res = manage_service("smbd", "start")
    print(f"Start result: {start_res['message']}")

    status_after_start = get_service_status("smbd")
    print(f"Samba status after start: Active={status_after_start['active']}")

    print("\n--- 4. Testing Log Retrieval ---")
    logs_res = get_service_logs("smbd", lines=5)
    print(f"Retrieved {len(logs_res.get('logs', []))} log lines.")
    if logs_res.get('logs'):
        print(f"Latest log line: {logs_res['logs'][-1]}")

    if status_after_start['active'] and not status_after_stop['active']:
        print("\n✅ PHASE 2 TEST PASSED SUCCESSFULLY!")
    else:
        print("\n❌ PHASE 2 TEST FAILED.")

if __name__ == "__main__":
    test_sys_admin_engine()