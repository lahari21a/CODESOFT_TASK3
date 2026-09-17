import unittest
import string
from generator import PasswordConfig, PasswordGenerator, AMBIGUOUS_CHARS

class TestPasswordGenerator(unittest.TestCase):

    def test_default_generation(self):
        config = PasswordConfig(length=16)
        password = PasswordGenerator.generate(config)
        self.assertEqual(len(password), 16)
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(c in PasswordGenerator.SYMBOLS for c in password))

    def test_custom_length(self):
        for length in [4, 8, 32, 64, 128]:
            config = PasswordConfig(length=length)
            pwd = PasswordGenerator.generate(config)
            self.assertEqual(len(pwd), length)

    def test_invalid_length(self):
        with self.assertRaises(ValueError):
            PasswordConfig(length=3).validate()
        with self.assertRaises(ValueError):
            PasswordConfig(length=2000).validate()

    def test_no_pools_selected(self):
        config = PasswordConfig(
            use_uppercase=False,
            use_lowercase=False,
            use_digits=False,
            use_symbols=False
        )
        with self.assertRaises(ValueError):
            PasswordGenerator.generate(config)

    def test_exclude_ambiguous(self):
        config = PasswordConfig(length=50, exclude_ambiguous=True)
        for _ in range(10):
            pwd = PasswordGenerator.generate(config)
            for amb in AMBIGUOUS_CHARS:
                self.assertNotIn(amb, pwd)

    def test_custom_exclude(self):
        exclude_chars = "ABCDEF123!@"
        config = PasswordConfig(length=40, custom_exclude=exclude_chars)
        for _ in range(5):
            pwd = PasswordGenerator.generate(config)
            for c in exclude_chars:
                self.assertNotIn(c, pwd)

    def test_guaranteed_character_inclusion(self):
        config = PasswordConfig(
            length=8,
            use_uppercase=True,
            use_lowercase=True,
            use_digits=True,
            use_symbols=True
        )
        for _ in range(20):
            pwd = PasswordGenerator.generate(config)
            self.assertTrue(any(c in string.ascii_uppercase for c in pwd))
            self.assertTrue(any(c in string.ascii_lowercase for c in pwd))
            self.assertTrue(any(c in string.digits for c in pwd))
            self.assertTrue(any(c in PasswordGenerator.SYMBOLS for c in pwd))

    def test_batch_generation(self):
        config = PasswordConfig(length=12)
        batch = PasswordGenerator.generate_batch(config, count=10)
        self.assertEqual(len(batch), 10)
        for pwd in batch:
            self.assertEqual(len(pwd), 12)

    def test_entropy_and_strength(self):
        config_weak = PasswordConfig(length=4, use_uppercase=False, use_digits=False, use_symbols=False)
        pwd_weak = PasswordGenerator.generate(config_weak)
        entropy_weak = PasswordGenerator.calculate_entropy(pwd_weak, config_weak)
        strength_weak, _, _ = PasswordGenerator.assess_strength(entropy_weak)
        self.assertLess(entropy_weak, 36)
        self.assertEqual(strength_weak, "Very Weak")

        config_strong = PasswordConfig(length=24)
        pwd_strong = PasswordGenerator.generate(config_strong)
        entropy_strong = PasswordGenerator.calculate_entropy(pwd_strong, config_strong)
        strength_strong, _, _ = PasswordGenerator.assess_strength(entropy_strong)
        self.assertGreater(entropy_strong, 80)
        self.assertIn(strength_strong, ["Strong", "Very Strong"])

if __name__ == "__main__":
    unittest.main()
