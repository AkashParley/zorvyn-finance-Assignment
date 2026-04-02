import pytest


class TestDashboard:

    def _seed_transactions(self, client, headers):
        records = [
            {"amount": "5000.00", "type": "income",  "category": "Salary",   "date": "2024-06-01"},
            {"amount": "1200.00", "type": "expense", "category": "Rent",     "date": "2024-06-02"},
            {"amount": "300.00",  "type": "expense", "category": "Food",     "date": "2024-06-03"},
            {"amount": "800.00",  "type": "income",  "category": "Freelance","date": "2024-05-15"},
        ]
        for r in records:
            client.post("/api/v1/transactions", json=r, headers=headers)

    def test_summary_accessible_by_viewer(self, client, viewer_headers):
        resp = client.get("/api/v1/dashboard/summary", headers=viewer_headers)
        assert resp.status_code == 200

    def test_summary_structure(self, client, admin_headers):
        self._seed_transactions(client, admin_headers)
        resp = client.get("/api/v1/dashboard/summary", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_income" in data
        assert "total_expenses" in data
        assert "net_balance" in data
        assert "income_by_category" in data
        assert "expense_by_category" in data
        assert "monthly_trends" in data
        assert "recent_transactions" in data

    def test_net_balance_is_correct(self, client, admin_headers):
        self._seed_transactions(client, admin_headers)
        resp = client.get("/api/v1/dashboard/summary", headers=admin_headers)
        data = resp.json()
        expected_net = float(data["total_income"]) - float(data["total_expenses"])
        assert abs(float(data["net_balance"]) - expected_net) < 0.01

    def test_unauthenticated_denied(self, client):
        resp = client.get("/api/v1/dashboard/summary")
        assert resp.status_code == 403
