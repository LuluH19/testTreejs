# Endpoint /status
from flask import Blueprint, jsonify, current_app
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from datetime import datetime, UTC
import time
from ..db import db

status_bp = Blueprint("status", __name__)

_start_time = time.time()
_version = "0.1.0"

@status_bp.route("/status", methods=["GET"])
def status():
		"""
		Health check et monitoring API
		---
		tags:
			- Monitoring
		responses:
			200:
				description: Statut de l'API
				examples:
					application/json:
						status: ok
						version: 0.1.0
						uptime_s: 12
						db_ok: true
						time: 2025-08-31T12:34:56.789Z
		"""
		uptime = int(time.time() - _start_time)
		db_ok = True
		try:
			db.session.execute(text("SELECT 1"))
		except OperationalError:
			db_ok = False
		return jsonify({
			"status": "ok",
			"version": _version,
			"uptime_s": uptime,
			"db_ok": db_ok,
			"time": datetime.now(UTC).isoformat().replace("+00:00", "Z")
		})
