import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import requests

from linkedin_salesnav_pagination import fetch_salesnav_people, _request_with_retries


class ResponseStub:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)


class TestSalesNavPagination(unittest.TestCase):
    def test_request_with_retries_handles_retryable_status(self):
        session = MagicMock()
        session.post.side_effect = [
            ResponseStub(429, {"error": "rate limit"}),
            ResponseStub(200, {"items": [], "paging": {}}),
        ]
        with patch("linkedin_salesnav_pagination.time.sleep", return_value=None):
            status, data = _request_with_retries(
                session,
                "https://example.com",
                headers={},
                params={},
                payload={},
                timeout=5,
                max_retries=2,
            )
        self.assertEqual(status, 200)
        self.assertEqual(data.get("items"), [])
        self.assertEqual(session.post.call_count, 2)

    def test_fetch_salesnav_people_paginates_until_cursor_end(self):
        page1 = {
            "items": [{"id": "1"}, {"id": "2"}],
            "paging": {"total_count": 4},
            "cursor": "c1",
        }
        page2 = {
            "items": [{"id": "3"}, {"id": "4"}],
            "paging": {"total_count": 4},
            "cursor": None,
        }
        session = MagicMock()
        session.post.side_effect = [
            ResponseStub(200, page1),
            ResponseStub(200, page2),
        ]
        with patch("linkedin_salesnav_pagination.requests.Session", return_value=session):
            with patch("linkedin_salesnav_pagination.time.sleep", return_value=None):
                results = fetch_salesnav_people(
                    {"keywords": "RH"},
                    account_id="acc",
                    token="token",
                    base_url="https://api.test",
                    limit=100,
                    max_results=None,
                    min_delay=0.0,
                    max_delay=0.0,
                    checkpoint_path=None,
                    resume=False,
                )
        self.assertEqual(len(results), 4)
        ids = {item.get("id") for item in results}
        self.assertEqual(ids, {"1", "2", "3", "4"})
        self.assertEqual(session.post.call_count, 2)

    def test_fetch_salesnav_people_dedup_and_max_results(self):
        page = {
            "items": [{"id": "1"}, {"id": "1"}, {"id": "2"}],
            "paging": {"total_count": 3},
            "cursor": None,
        }
        session = MagicMock()
        session.post.return_value = ResponseStub(200, page)
        with patch("linkedin_salesnav_pagination.requests.Session", return_value=session):
            results = fetch_salesnav_people(
                {"keywords": "RH"},
                account_id="acc",
                token="token",
                base_url="https://api.test",
                limit=100,
                max_results=2,
                min_delay=0.0,
                max_delay=0.0,
                checkpoint_path=None,
                resume=False,
            )
        self.assertEqual(len(results), 2)
        ids = [item.get("id") for item in results]
        self.assertEqual(ids, ["1", "2"])

    def test_checkpoint_resume(self):
        page2 = {
            "items": [{"id": "2"}],
            "paging": {"total_count": 2},
            "cursor": None,
        }
        session = MagicMock()
        session.post.return_value = ResponseStub(200, page2)
        with tempfile.TemporaryDirectory() as tmpdir:
            checkpoint_path = os.path.join(tmpdir, "checkpoint.json")
            with open(checkpoint_path, "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "cursor": "c1",
                        "page": 1,
                        "count": 1,
                        "items": [{"id": "1"}],
                    },
                    handle,
                )
            with patch("linkedin_salesnav_pagination.requests.Session", return_value=session):
                with patch("linkedin_salesnav_pagination.time.sleep", return_value=None):
                    results = fetch_salesnav_people(
                        {"keywords": "RH"},
                        account_id="acc",
                        token="token",
                        base_url="https://api.test",
                        limit=100,
                        max_results=None,
                        min_delay=0.0,
                        max_delay=0.0,
                        checkpoint_path=checkpoint_path,
                        resume=True,
                    )
        self.assertEqual(len(results), 2)
        ids = {item.get("id") for item in results}
        self.assertEqual(ids, {"1", "2"})
        _, kwargs = session.post.call_args
        self.assertEqual(kwargs["params"].get("cursor"), "c1")


if __name__ == "__main__":
    unittest.main()
