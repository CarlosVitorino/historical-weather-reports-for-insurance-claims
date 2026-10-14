from fastapi.testclient import TestClient

from wxreport.web import app


def test_order_form_renders():
    r = TestClient(app).get("/")
    assert r.status_code == 200 and 'name="loss_date"' in r.text
