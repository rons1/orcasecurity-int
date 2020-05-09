import unittest

from models import setup_db, get_stats, get_attackers


class EmptyDataTest(unittest.TestCase):
    def setUp(self):
        setup_db(json_file_path="data\\test-input-0.json", clear_stats=True, reload_db=True)

    def test_get_stats(self):
        stats = get_stats()
        self.assertIn("average_request_time", stats)
        self.assertIn("request_count", stats)
        self.assertIn("vm_count", stats)
        self.assertGreaterEqual(stats["average_request_time"], 0)
        self.assertGreaterEqual(stats["request_count"], 0)
        self.assertGreaterEqual(stats["vm_count"], 0)

    def test_get_empty_vm_id(self):
        attackers = get_attackers("")
        self.assertEqual(attackers, [])

    def test_get_not_empty_vm_id(self):
        attackers = get_attackers("vm-123")
        self.assertEqual(attackers, [])


class ExistingDataTest(unittest.TestCase):
    def setUp(self):
        setup_db(json_file_path="data\\test-input-1.json", clear_stats=True, reload_db=True)

    def test_get_stats(self):
        stats = get_stats()
        self.assertIn("average_request_time", stats)
        self.assertIn("request_count", stats)
        self.assertIn("vm_count", stats)
        self.assertGreaterEqual(stats["average_request_time"], 0)
        self.assertGreaterEqual(stats["request_count"], 0)
        self.assertGreaterEqual(stats["vm_count"], 0)

    def test_get_empty_vm_id(self):
        attackers = get_attackers("")
        self.assertEqual(attackers, [])

    def test_get_not_empty_non_existing_vm_id(self):
        attackers = get_attackers("vm-123")
        self.assertEqual(attackers, [])

    def test_get_not_empty_vm_id_no_results(self):
        attackers = get_attackers("vm-111")
        self.assertEqual(attackers, [])

    def test_get_not_empty_vm_id_one_result(self):
        attackers = get_attackers("vm-222")
        self.assertEqual(attackers, ["vm-111"])

    def test_get_not_empty_vm_id_many_results(self):
        attackers = get_attackers("vm-333")
        self.assertIn("vm-444", attackers)
        self.assertIn("vm-555", attackers)
        self.assertEqual(2, len(attackers))

    def test_get_not_empty_vm_id_many_results_by_many_tags(self):
        attackers = get_attackers("vm-555")
        self.assertIn("vm-333", attackers)
        self.assertIn("vm-444", attackers)
        self.assertIn("vm-555", attackers)
        self.assertIn("vm-666", attackers)
        self.assertEqual(4, len(attackers))


if __name__ == '__main__':
    unittest.main()
