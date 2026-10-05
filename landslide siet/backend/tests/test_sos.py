from backend.app.api.sos import _sos_events


def test_sos_post_stores_event_and_get_lists_it(api_request):
    _sos_events.clear()
    payload = {
        "lat": 11.35,
        "lon": 76.8,
        "name": "Asha",
        "timestamp": "2026-10-05T12:00:00Z",
    }

    created = api_request("POST", "/sos", json=payload)
    listed = api_request("GET", "/sos")

    assert created.status_code == 201
    assert created.json()["id"]
    assert {key: created.json()[key] for key in payload} == payload
    assert listed.status_code == 200
    assert listed.json()["items"] == [created.json()]