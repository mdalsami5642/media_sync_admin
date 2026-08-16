from flask import Flask, jsonify, request, render_template
from modules.sys_admin import (
    manage_service,
    get_service_status,
    get_service_logs,
    manage_package
)
from modules.config_manager import locate_config, add_samba_share

app = Flask(__name__)

@app.route("/")
def index():
    """Serves the main admin web interface."""
    return render_template("index.html")

# --- Service Status & Management Endpoints ---

@app.route("/api/status/<service_name>", methods=["GET"])
def api_service_status(service_name):
    """GET /api/status/smbd -> Returns running and boot state."""
    result = get_service_status(service_name)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/api/service/<service_name>/<action>", methods=["POST"])
def api_service_action(service_name, action):
    """POST /api/service/smbd/restart -> Executes lifecycle action."""
    result = manage_service(service_name, action)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


# --- Log Management Endpoints ---

@app.route("/api/logs/<service_name>", methods=["GET"])
def api_service_logs(service_name):
    """GET /api/logs/smbd?lines=20 -> Fetches journalctl log entries."""
    lines = request.args.get("lines", default=30, type=int)
    result = get_service_logs(service_name, lines=lines)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


# --- Configuration & Share Management Endpoints ---

@app.route("/api/config/<service_name>", methods=["GET"])
def api_locate_config(service_name):
    """GET /api/config/smbd -> Returns file path and raw configuration text."""
    result = locate_config(service_name)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


@app.route("/api/shares", methods=["POST"])
def api_create_share():
    """
    POST /api/shares
    JSON Payload: {"share_name": "Movies", "folder_path": "~/Media/Movies", "read_only": false, "guest_ok": true}
    """
    data = request.get_json() or {}
    share_name = data.get("share_name")
    folder_path = data.get("folder_path")
    read_only = data.get("read_only", False)
    guest_ok = data.get("guest_ok", True)

    if not share_name or not folder_path:
        return jsonify({"success": False, "message": "Missing required fields: share_name and folder_path"}), 400

    result = add_samba_share(
        share_name=share_name,
        folder_path=folder_path,
        read_only=read_only,
        guest_ok=guest_ok
    )
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


# --- Package Installation Endpoints ---

@app.route("/api/package/<package_name>/<action>", methods=["POST"])
def api_package_action(package_name, action):
    """POST /api/package/samba/install -> Installs or purges system packages."""
    result = manage_package(package_name, action)
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)