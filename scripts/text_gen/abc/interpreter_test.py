import unittest

from scripts.text_gen.abc.abcnet_to_python_interpreter import print_interpreter


class TestInterpreter(unittest.TestCase):
    def test_print_norm(self):
        self.assertEqual(print_interpreter(0, "print(a, b);"), "print(a, b, end=' ')")
        self.assertEqual(print_interpreter(0, "println(a);"), "print(a + '\n', end=' ')")
        self.assertEqual(print_interpreter(0, "println($'{a}###{b}');"), "print(f'{a}###{b}' + '\n', end=' ')")

