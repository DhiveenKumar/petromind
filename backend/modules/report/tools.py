import json
import os
from datetime import datetime
from langchain_core.tools import tool


TICKETS_LOG = "backend/evaluation/action_log.json"


def _log_action(action_type: str, details: dict):
    os.makedirs(os.path.dirname(TICKETS_LOG), exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "details": details
    }

    logs = []
    if os.path.exists(TICKETS_LOG):
        with open(TICKETS_LOG, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(log_entry)

    with open(TICKETS_LOG, 'w') as f:
        json.dump(logs, f, indent=2)

    return log_entry


@tool
def create_maintenance_ticket(
    equipment_name: str,
    priority: int,
    description: str
) -> str:
    """
    Creates a maintenance ticket in the CMMS (Computerized Maintenance
    Management System). Use this when priority_score is 7 or higher,
    indicating urgent maintenance action is required.

    Args:
        equipment_name: Name of the equipment requiring maintenance
        priority: Priority score from 1-10
        description: Description of the issue and required action
    """
    ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    _log_action("maintenance_ticket_created", {
        "ticket_id": ticket_id,
        "equipment_name": equipment_name,
        "priority": priority,
        "description": description,
        "status": "OPEN"
    })

    return (
        f"Maintenance ticket {ticket_id} created for {equipment_name} "
        f"with priority {priority}/10. Status: OPEN."
    )


@tool
def send_alert(
    message: str,
    equipment_name: str,
    severity: str
) -> str:
    """
    Sends an alert notification to the maintenance team channel.
    Use this when severity is HIGH or CRITICAL and immediate
    awareness is required.

    Args:
        message: Alert message content
        equipment_name: Equipment the alert relates to
        severity: HIGH or CRITICAL
    """
    _log_action("alert_sent", {
        "equipment_name": equipment_name,
        "severity": severity,
        "message": message,
        "channel": "#maintenance-alerts"
    })

    return (
        f"Alert sent to #maintenance-alerts channel for "
        f"{equipment_name}. Severity: {severity}."
    )


@tool
def check_spare_parts_inventory(part_name: str) -> str:
    """
    Checks spare parts inventory for a specific component.
    Use this when a maintenance recommendation involves
    replacing a specific part (seals, bearings, gaskets).

    Args:
        part_name: Name of the spare part to check
    """
    mock_inventory = {
        "seal": {"quantity": 12, "location": "Warehouse A, Bin 14"},
        "bearing": {"quantity": 3, "location": "Warehouse B, Bin 7"},
        "gasket": {"quantity": 25, "location": "Warehouse A, Bin 22"},
        "impeller": {"quantity": 1, "location": "Warehouse C, Bin 3"},
    }

    part_key = next(
        (k for k in mock_inventory if k in part_name.lower()),
        None
    )

    if part_key:
        info = mock_inventory[part_key]
        _log_action("inventory_checked", {
            "part_name": part_name,
            "quantity": info["quantity"],
            "location": info["location"]
        })
        return (
            f"{part_name}: {info['quantity']} units available "
            f"at {info['location']}"
        )
    else:
        _log_action("inventory_checked", {
            "part_name": part_name,
            "quantity": 0,
            "location": "Not found"
        })
        return f"{part_name}: Not found in inventory - order required"


def get_all_tools():
    return [create_maintenance_ticket, send_alert, check_spare_parts_inventory]


def get_action_log() -> list[dict]:
    if os.path.exists(TICKETS_LOG):
        with open(TICKETS_LOG, 'r') as f:
            return json.load(f)
    return []
