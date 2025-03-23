import unittest

from util.calculator import calc_time_diff

class TestCalculator(unittest.TestCase):
    def test_calc_time_diff(self):
        start_date_str = '2025-04-10T21:00:00.000+09:00'
        end_date_str = '2025-04-10T20:00:00.000+09:00'
        actual = calc_time_diff(start_date_str, end_date_str)
        expected = -1
        self.assertEqual(actual, expected)

    def test_calc_time_diff_when_arg_is_not_str(self):
        start_date_str = 2025
        end_date_str = 2025
        with self.assertRaises(ValueError):
            calc_time_diff(start_date_str, end_date_str)
            
if __name__ == '__main__':
    unittest.main()