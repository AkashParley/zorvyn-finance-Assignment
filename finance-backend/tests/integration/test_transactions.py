import pytest


SAMPLE_TX = {
    "amount": "1500.00",
    "type": "income",
    "category": "Salary",
    "date": "2024-06-15",
    "description": "Monthly salary",
}


class TestCreateTransaction:
    def test_admin_can_create(self, client, admin_headers):
        resp = client.post("/api/v1/transactions", json=SAMPLE_TX, headers=admin_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["category"] == "Salary"
        assert data["type"] == "income"

    def test_viewer_cannot_create(self, client, viewer_headers):
        resp = client.post("/api/v1/transactions", json=SAMPLE_TX, headers=viewer_headers)
        assert resp.status_code == 403

    def test_negative_amount_rejected(self, client, admin_headers):
        payload = {**SAMPLE_TX, "amount": "-100.00"}
        resp = client.post("/api/v1/transactions", json=payload, headers=admin_headers)
        assert resp.status_code == 422

    def test_zero_amount_rejected(self, client, admin_headers):
        payload = {**SAMPLE_TX, "amount": "0"}
        resp = client.post("/api/v1/transactions", json=payload, headers=admin_headers)
        assert resp.status_code == 422


class TestReadTransactions:
    def test_viewer_can_list(self, client, viewer_headers):
        resp = client.get("/api/v1/transactions", headers=viewer_headers)
        assert resp.status_code == 200
        assert "transactions" in resp.json()

    def test_unauthenticated_denied(self, client):
        resp = client.get("/api/v1/transactions")
        assert resp.status_code == 403

    def test_filter_by_type(self, client, admin_headers):
        client.post("/api/v1/transactions", json=SAMPLE_TX, headers=admin_headers)
        resp = client.get("/api/v1/transactions?type=income", headers=admin_headers)
        assert resp.status_code == 200
        for tx in resp.json()["transactions"]:
            assert tx["type"] == "income"

    def test_search_by_keyword(self, client, admin_headers):
        client.post("/api/v1/transactions", json={**SAMPLE_TX, "description": "Bonus payment"}, headers=admin_headers)
        resp = client.get("/api/v1/transactions?search=Bonus", headers=admin_headers)
        assert resp.status_code == 200
        results = resp.json()["transactions"]
        assert any("Bonus" in (tx.get("description") or "") for tx in results)

    def test_pagination(self, client, admin_headers):
        resp = client.get("/api/v1/transactions?page=1&page_size=5", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["transactions"]) <= 5
        assert data["page"] == 1


class TestUpdateTransaction:
    def test_admin_can_update(self, client, admin_headers):
        create = client.post("/api/v1/transactions", json=SAMPLE_TX, headers=admin_headers)
        tx_id = create.json()["id"]
        resp = client.patch(f"/api/v1/transactions/{tx_id}",
                            json={"amount": "2000.00"}, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["amount"] == "2000.00"

    def test_viewer_cannot_update(self, client, admin_headers, viewer_headers):
        create = client.post("/api/v1/transactions", json=SAMPLE_TX, headers=admin_headers)
        tx_id = create.json()["id"]
        resp = client.patch(f"/api/v1/transactions/{tx_id}",
                            json={"amount": "500.00"}, headers=viewer_headers)
        assert resp.status_code == 403


class TestDeleteTransaction:
    def test_admin_soft_delete(self, client, admin_headers):
        create = client.post("/api/v1/transactions", json=SAMPLE_TX, headers=admin_headers)
        tx_id = create.json()["id"]
        resp = client.delete(f"/api/v1/transactions/{tx_id}", headers=admin_headers)
        assert resp.status_code == 204
        # Soft deleted — should now 404
        get = client.get(f"/api/v1/transactions/{tx_id}", headers=admin_headers)
        assert get.status_code == 404

    def test_viewer_cannot_delete(self, client, admin_headers, viewer_headers):
        create = client.post("/api/v1/transactions", json=SAMPLE_TX, headers=admin_headers)
        tx_id = create.json()["id"]
        resp = client.delete(f"/api/v1/transactions/{tx_id}", headers=viewer_headers)
        assert resp.status_code == 403
