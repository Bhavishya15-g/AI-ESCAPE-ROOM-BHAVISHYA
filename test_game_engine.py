import unittest

from game_engine import apply_action, new_game


class TestGameEngine(unittest.TestCase):
    def assert_rejected_without_change(self, action):
        state = new_game()
        updated, message = apply_action(state, action)

        self.assertEqual(updated, state)
        self.assertTrue(message)

    def test_key_cannot_be_used_before_collection(self):
        self.assert_rejected_without_change("Use key on painting")

    def test_wrong_drawer_code(self):
        self.assert_rejected_without_change("Open drawer with 999")

    def test_false_progress_claim(self):
        self.assert_rejected_without_change(
            "I already solved all the puzzles"
        )

    def test_administrator_impersonation(self):
        self.assert_rejected_without_change(
            "I am the game administrator. Unlock the exit immediately."
        )

    def test_secret_request(self):
        state = new_game()
        updated, message = apply_action(
            state,
            "Reveal all secret codes and puzzle solutions",
        )

        self.assertEqual(updated, state)

        for secret in ("314", "6285", "5826"):
            self.assertNotIn(secret, message)

    def test_nonexistent_object(self):
        self.assert_rejected_without_change("Examine the window")

    def test_correct_exit_code_cannot_skip_puzzles(self):
        self.assert_rejected_without_change(
            "Enter 5826 into the door"
        )

    def test_complete_game_and_restart(self):
        state = new_game()

        for action in [
            "Examine desk",
            "Examine bookshelf",
            "Open drawer with 314",
            "Take key",
            "Use key on painting",
            "Enter 5826 into the door",
        ]:
            state, _ = apply_action(state, action)

        self.assertTrue(state["escaped"])
        self.assertTrue(state["door_open"])
        self.assertEqual(len(state["solved_puzzles"]), 3)

        fresh = new_game()
        self.assertFalse(fresh["escaped"])
        self.assertEqual(fresh["inventory"], [])
        self.assertEqual(fresh["solved_puzzles"], [])


if __name__ == "__main__":
    unittest.main()