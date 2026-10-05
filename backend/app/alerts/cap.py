"""CAP 1.2 XML export for demo alerts."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from backend.app.models import Alert

CAP_NAMESPACE = "urn:oasis:names:tc:emergency:cap:1.2"
ET.register_namespace("", CAP_NAMESPACE)


def export_cap(alert: Alert) -> str:
    namespace = f"{{{CAP_NAMESPACE}}}"
    root = ET.Element(namespace + "alert")
    values = {
        "identifier": alert.id,
        "sender": "terrasafe-demo",
        "sent": alert.created_at.isoformat(),
        "status": "Test",
        "msgType": "Alert",
        "scope": "Public",
    }
    for name, value in values.items():
        ET.SubElement(root, namespace + name).text = value
    info = ET.SubElement(root, namespace + "info")
    for name, value in (
        ("category", "Geo"),
        ("event", "Landslide risk"),
        ("urgency", "Unknown"),
        ("severity", "Unknown"),
        ("certainty", "Unknown"),
        ("headline", f"DEMO landslide risk {alert.risk_level}"),
        ("description", alert.message),
        ("instruction", "Follow official IMD, NDMA, and GSI warnings."),
        ("language", alert.language),
    ):
        ET.SubElement(info, namespace + name).text = value
    area = ET.SubElement(info, namespace + "area")
    ET.SubElement(area, namespace + "areaDesc").text = (
        f"SIMULATED area; unverified supplied location: {alert.location}"
    )
    if alert.latitude is not None and alert.longitude is not None:
        ET.SubElement(area, namespace + "circle").text = (
            f"{alert.latitude},{alert.longitude},1"
        )
    return ET.tostring(root, encoding="unicode", xml_declaration=True)
