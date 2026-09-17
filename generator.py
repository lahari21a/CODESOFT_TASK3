import math
import secrets
import string
from dataclasses import dataclass
from typing import List, Tuple

AMBIGUOUS_CHARS = set("il1Io0O")

@dataclass
class PasswordConfig:
    length: int = 16
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_digits: bool = True
    use_symbols: bool = True
    exclude_ambiguous: bool = False
    custom_exclude: str = ""

    def validate(self) -> None:
        if not isinstance(self.length, int) or self.length < 4:
            raise ValueError("Password length must be an integer of at least 4.")
        if self.length > 1024:
            raise ValueError("Password length cannot exceed 1024 characters.")
        if not (self.use_uppercase or self.use_lowercase or self.use_digits or self.use_symbols):
            raise ValueError("At least one character set must be enabled.")

class PasswordGenerator:
    """Cryptographically secure password generator."""

    SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    @classmethod
    def get_character_pools(cls, config: PasswordConfig) -> List[Tuple[str, str]]:
        """Returns a list of (pool_name, characters) tuples based on configuration."""
        pools = []
        exclude_set = set(config.custom_exclude or "")
        if config.exclude_ambiguous:
            exclude_set.update(AMBIGUOUS_CHARS)

        def clean_pool(pool: str) -> str:
            return "".join(c for c in pool if c not in exclude_set)

        if config.use_uppercase:
            pool = clean_pool(string.ascii_uppercase)
            if not pool:
                raise ValueError("Uppercase pool is empty after exclusions.")
            pools.append(("uppercase", pool))

        if config.use_lowercase:
            pool = clean_pool(string.ascii_lowercase)
            if not pool:
                raise ValueError("Lowercase pool is empty after exclusions.")
            pools.append(("lowercase", pool))

        if config.use_digits:
            pool = clean_pool(string.digits)
            if not pool:
                raise ValueError("Digits pool is empty after exclusions.")
            pools.append(("digits", pool))

        if config.use_symbols:
            pool = clean_pool(cls.SYMBOLS)
            if not pool:
                raise ValueError("Symbols pool is empty after exclusions.")
            pools.append(("symbols", pool))

        return pools

    @classmethod
    def generate(cls, config: PasswordConfig) -> str:
        """Generates a secure password guaranteed to include at least one char from each selected pool."""
        config.validate()
        pools = cls.get_character_pools(config)

        if config.length < len(pools):
            raise ValueError(f"Password length ({config.length}) must be at least the number of selected character sets ({len(pools)}).")

        password_chars = []

        # Guarantee at least one character from each active pool
        for _, pool_chars in pools:
            password_chars.append(secrets.choice(pool_chars))

        # Fill the remaining slots from combined character pool
        combined_pool = "".join(pool for _, pool in pools)
        remaining_length = config.length - len(password_chars)
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(combined_pool))

        # Securely shuffle using SystemRandom
        secrets.SystemRandom().shuffle(password_chars)
        return "".join(password_chars)

    @classmethod
    def generate_batch(cls, config: PasswordConfig, count: int = 5) -> List[str]:
        """Generates a list of secure passwords."""
        if count < 1 or count > 100:
            raise ValueError("Batch count must be between 1 and 100.")
        return [cls.generate(config) for _ in range(count)]

    @classmethod
    def calculate_pool_size(cls, config: PasswordConfig) -> int:
        """Calculates the total size of the active character pool."""
        pools = cls.get_character_pools(config)
        return sum(len(pool) for _, pool in pools)

    @classmethod
    def calculate_entropy(cls, password: str, config: PasswordConfig) -> float:
        """Calculates Shannon Entropy E = L * log2(R)."""
        if not password:
            return 0.0
        try:
            pool_size = cls.calculate_pool_size(config)
        except ValueError:
            pool_size = len(set(password))
        
        if pool_size <= 1:
            return 0.0
        return len(password) * math.log2(pool_size)

    @classmethod
    def assess_strength(cls, entropy: float) -> Tuple[str, str, str]:
        """
        Assesses password strength based on entropy in bits.
        Returns: (Strength Label, Color Code, Recommendation/Description)
        """
        if entropy < 36:
            return ("Very Weak", "#e74c3c", "Extremely vulnerable to brute-force attacks.")
        elif entropy < 60:
            return ("Weak", "#e67e22", "Can be cracked relatively quickly.")
        elif entropy < 80:
            return ("Moderate", "#f1c40f", "Good security for standard online accounts.")
        elif entropy < 120:
            return ("Strong", "#2ecc71", "High resistance to advanced brute-force attacks.")
        else:
            return ("Very Strong", "#1abc9c", "Maximum security. Suitable for high-value keys.")
