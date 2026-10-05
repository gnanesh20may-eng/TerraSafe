"""Mock-only notification adapters; no external delivery is attempted."""

from __future__ import annotations

from typing import Any

CHANNELS = ("web_push", "sms", "whatsapp", "email", "voice")

MESSAGE_TEMPLATES = {
    "en": (
        "Landslide risk {level} for {location}. This is a DEMO alert; follow "
        "official IMD, NDMA, and GSI guidance."
    ),
    "ta": (
        "{location} பகுதியில் மண்சரிவு அபாய நிலை {level}. இது DEMO எச்சரிக்கை; "
        "அதிகாரப்பூர்வ IMD/NDMA/GSI அறிவுறுத்தல்களைப் பின்பற்றவும்."
    ),
    "hi": (
        "{location} में भूस्खलन जोखिम स्तर {level} है। यह DEMO चेतावनी है; "
        "आधिकारिक IMD/NDMA/GSI निर्देशों का पालन करें।"
    ),
    "ml": (
        "{location} പ്രദേശത്തെ മണ്ണിടിച്ചിൽ അപകടനില {level} ആണ്. ഇത് DEMO "
        "അറിയിപ്പാണ്; ഔദ്യോഗിക IMD/NDMA/GSI നിർദേശങ്ങൾ പാലിക്കുക."
    ),
}


class MockNotificationAdapter:
    """Return an auditable demo result without sending a message."""

    def __init__(self, channel: str) -> None:
        if channel not in CHANNELS:
            raise ValueError(f"unsupported notification channel: {channel}")
        self.channel = channel

    def send(self, alert: Any) -> dict[str, str]:
        return {
            "channel": self.channel,
            "status": "DEMO",
            "message": f"Mock {self.channel} notification; no message was sent.",
            "alert_id": alert.id,
        }


def notification_adapters() -> dict[str, MockNotificationAdapter]:
    return {channel: MockNotificationAdapter(channel) for channel in CHANNELS}


def render_message(language: str, level: str, location: str) -> str:
    template = MESSAGE_TEMPLATES.get(language)
    if template is None:
        raise ValueError(f"unsupported message language: {language}")
    return template.format(level=level, location=location)
