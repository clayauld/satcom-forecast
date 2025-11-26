
import unittest

class TestCoordinatorLogic(unittest.TestCase):
    """Test coordinator logic."""

    def test_days_logic(self):
        """Test days determination logic."""
        config = {"default_days": 3}
        
        # Helper function to simulate the logic in coordinator.py
        def get_days(msg, config):
            days = msg.get("days")
            if days is None:
                days = config.get("default_days", 3)
            return days

        # Test cases
        self.assertEqual(get_days({"days": 0}, config), 0)
        self.assertEqual(get_days({"days": 5}, config), 5)
        self.assertEqual(get_days({}, config), 3)
        self.assertEqual(get_days({"days": None}, config), 3)

if __name__ == "__main__":
    unittest.main()
