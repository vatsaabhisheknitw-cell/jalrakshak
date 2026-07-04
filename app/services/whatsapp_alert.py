"""WhatsApp / SMS compliance alerts via Twilio.

PRODUCTION CAVEAT (important):
  Compliance alerts are *business-initiated* messages. Outside the 24-hour
  customer-service window, WhatsApp only permits PRE-APPROVED Business
  template messages — you cannot send the free-form body below in production.
  To go live you must:
    1. Register a WhatsApp Business sender (via Twilio / Meta),
    2. Submit alert templates for approval with {{1}}, {{2}} ... placeholders,
    3. Send with `content_sid` + `content_variables` (see send_whatsapp_template).
  The sandbox sender `whatsapp:+14155238886` is DEV-ONLY.
  If template approval is a blocker at launch, use `send_sms_alert` instead —
  same trigger logic, no template gate.
"""
from __future__ import annotations

import os


def _client():
    from twilio.rest import Client
    return Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])


def _format_body(factory_name: str, alert: dict) -> str:
    critical = alert.get("severity") == "critical"
    header = "🔴 VIOLATION ALERT" if critical else "🟡 WARNING"
    detail = (
        f"Exceedance: {alert.get('exceedance_pct', '')}%" if critical
        else f"At {alert.get('usage_pct', '')}% of limit"
    )
    return (
        f"*{header} — {factory_name}*\n\n"
        f"Parameter: {alert['parameter'].upper()}\n"
        f"Value: {alert['value']} {alert.get('unit', '')}\n"
        f"Limit: {alert.get('limit', '')} {alert.get('unit', '')}\n"
        f"Date: {alert['date']}\n\n{detail}\n\n"
        "Action needed. Check ETP operations.\n\n— JalRakshak"
    )


def send_whatsapp_alert(to_number: str, factory_name: str, alert: dict,
                        from_number: str = "whatsapp:+14155238886") -> str:
    """DEV ONLY: free-form WhatsApp via the Twilio sandbox. See module caveat."""
    msg = _client().messages.create(
        body=_format_body(factory_name, alert),
        from_=from_number,
        to=f"whatsapp:+91{to_number}",
    )
    return msg.sid


def send_whatsapp_template(to_number: str, content_sid: str,
                           content_variables: dict, from_number: str) -> str:
    """PRODUCTION path: send an approved WhatsApp template message."""
    import json
    msg = _client().messages.create(
        from_=from_number,  # e.g. "whatsapp:+91XXXXXXXXXX" (approved sender)
        to=f"whatsapp:+91{to_number}",
        content_sid=content_sid,
        content_variables=json.dumps(content_variables),
    )
    return msg.sid


def send_sms_alert(to_number: str, factory_name: str, alert: dict,
                   from_number: str) -> str:
    """Fallback that avoids the WhatsApp template gate entirely."""
    msg = _client().messages.create(
        body=_format_body(factory_name, alert),
        from_=from_number,  # your Twilio SMS-capable number
        to=f"+91{to_number}",
    )
    return msg.sid
