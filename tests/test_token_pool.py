import unittest

from freebuff2api.codebuff import CodebuffClient, TokenPool
from freebuff2api.config import Settings


class TokenPoolTests(unittest.IsolatedAsyncioTestCase):
    async def test_round_robin_distributes_across_tokens(self) -> None:
        pool = TokenPool(("token-a", "token-b", "token-c"), Settings())
        try:
            slot0 = await pool.acquire()
            slot1 = await pool.acquire()
            slot2 = await pool.acquire()
            slot3 = await pool.acquire()

            self.assertIs(slot0.client._token, "token-a")
            self.assertIs(slot1.client._token, "token-b")
            self.assertIs(slot2.client._token, "token-c")
            self.assertIs(slot3.client._token, "token-a")
        finally:
            await pool.aclose()

    async def test_single_token_always_returns_same_slot(self) -> None:
        pool = TokenPool(("only-token",), Settings())
        try:
            slot0 = await pool.acquire()
            slot1 = await pool.acquire()
            slot2 = await pool.acquire()

            self.assertIs(slot0.client._token, "only-token")
            self.assertIs(slot1.client._token, "only-token")
            self.assertIs(slot2.client._token, "only-token")
            self.assertIs(slot0, slot1)  # same slot object
            self.assertIs(slot1, slot2)
        finally:
            await pool.aclose()

    async def test_aclose_closes_all_clients(self) -> None:
        pool = TokenPool(("token-a", "token-b"), Settings())
        await pool.aclose()

        for slot in pool._slots:
            self.assertTrue(slot.client._client.is_closed)

    async def test_acquire_slots_are_independent(self) -> None:
        pool = TokenPool(("token-a", "token-b"), Settings())
        try:
            slot0 = await pool.acquire()
            slot1 = await pool.acquire()

            self.assertIsNot(slot0, slot1)
            self.assertIsNot(slot0.client, slot1.client)
            self.assertIsNot(slot0.sessions, slot1.sessions)
        finally:
            await pool.aclose()

    async def test_codebuff_client_per_instance_token(self) -> None:
        settings = Settings(codebuff_tokens=("default",))
        client_a = CodebuffClient(settings, token="override-a")
        client_b = CodebuffClient(settings, token="override-b")

        headers_a = client_a._headers(require_auth=True)
        headers_b = client_b._headers(require_auth=True)

        self.assertEqual(headers_a["Authorization"], "Bearer override-a")
        self.assertEqual(headers_b["Authorization"], "Bearer override-b")

    async def test_codebuff_client_falls_back_to_settings_token(self) -> None:
        settings = Settings(codebuff_tokens=("settings-token",))
        client = CodebuffClient(settings)

        headers = client._headers(require_auth=True)
        self.assertEqual(headers["Authorization"], "Bearer settings-token")


if __name__ == "__main__":
    unittest.main()
