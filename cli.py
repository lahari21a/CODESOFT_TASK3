import argparse
import sys
import subprocess
from generator import PasswordConfig, PasswordGenerator

def copy_to_clipboard(text: str) -> bool:
    """Copies text to system clipboard (Windows)."""
    try:
        process = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
        process.communicate(input=text.encode('utf-16'))
        return True
    except Exception:
        return False

def print_banner():
    print("=" * 60)
    print("      🔐 SECURE PYTHON PASSWORD GENERATOR 🔐")
    print("=" * 60)

def prompt_bool(prompt_text: str, default: bool = True) -> bool:
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt_text} ({default_str}): ").strip().lower()
    if not response:
        return default
    return response.startswith('y')

def run_interactive():
    print_banner()
    print("Specify your password preferences:\n")

    # Prompt Length
    while True:
        try:
            length_input = input("Enter desired password length (min 4, max 1024) [default: 16]: ").strip()
            if not length_input:
                length = 16
            else:
                length = int(length_input)
            if length < 4 or length > 1024:
                print("❌ Length must be between 4 and 1024.")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid integer.")

    use_uppercase = prompt_bool("Include Uppercase letters (A-Z)", True)
    use_lowercase = prompt_bool("Include Lowercase letters (a-z)", True)
    use_digits = prompt_bool("Include Digits (0-9)", True)
    use_symbols = prompt_bool("Include Special Symbols (!@#$...)", True)
    exclude_ambiguous = prompt_bool("Exclude Ambiguous characters (i, l, 1, I, o, 0, O)", False)
    
    custom_exclude = input("Enter any specific characters to exclude (or press Enter to skip): ").strip()

    # Prompt Count
    while True:
        try:
            count_input = input("How many passwords to generate? [default: 1]: ").strip()
            if not count_input:
                count = 1
            else:
                count = int(count_input)
            if count < 1 or count > 100:
                print("❌ Count must be between 1 and 100.")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid integer.")

    config = PasswordConfig(
        length=length,
        use_uppercase=use_uppercase,
        use_lowercase=use_lowercase,
        use_digits=use_digits,
        use_symbols=use_symbols,
        exclude_ambiguous=exclude_ambiguous,
        custom_exclude=custom_exclude
    )

    try:
        passwords = PasswordGenerator.generate_batch(config, count)
        print("\n" + "─" * 60)
        print("🔑 GENERATED PASSWORD(S):")
        print("─" * 60)
        for idx, pwd in enumerate(passwords, start=1):
            entropy = PasswordGenerator.calculate_entropy(pwd, config)
            strength, _, desc = PasswordGenerator.assess_strength(entropy)
            if count > 1:
                print(f"#{idx:02d}: {pwd}")
                print(f"     Strength: {strength} ({entropy:.1f} bits) — {desc}\n")
            else:
                print(f"Password:  {pwd}")
                print(f"Entropy:   {entropy:.1f} bits")
                print(f"Strength:  {strength}")
                print(f"Info:      {desc}\n")

                if copy_to_clipboard(pwd):
                    print("📋 Password copied to clipboard!")
        print("─" * 60)

    except ValueError as e:
        print(f"\n❌ Error generating password: {e}")

def main():
    parser = argparse.ArgumentParser(description="Cryptographically Secure Password Generator")
    parser.add_argument("-l", "--length", type=int, default=16, help="Length of password (default: 16)")
    parser.add_argument("--no-uppercase", action="store_true", help="Disable uppercase letters")
    parser.add_argument("--no-lowercase", action="store_true", help="Disable lowercase letters")
    parser.add_argument("--no-digits", action="store_true", help="Disable digits")
    parser.add_argument("--no-symbols", action="store_true", help="Disable symbols")
    parser.add_argument("--exclude-ambiguous", action="store_true", help="Exclude ambiguous characters")
    parser.add_argument("--exclude", type=str, default="", help="Custom characters to exclude")
    parser.add_argument("-c", "--count", type=int, default=1, help="Number of passwords to generate")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run interactive prompt mode")
    parser.add_argument("--copy", action="store_true", help="Copy generated password to clipboard")

    args = parser.parse_args()

    if args.interactive or len(sys.argv) == 1:
        run_interactive()
        return

    config = PasswordConfig(
        length=args.length,
        use_uppercase=not args.no_uppercase,
        use_lowercase=not args.no_lowercase,
        use_digits=not args.no_digits,
        use_symbols=not args.no_symbols,
        exclude_ambiguous=args.exclude_ambiguous,
        custom_exclude=args.exclude
    )

    try:
        passwords = PasswordGenerator.generate_batch(config, args.count)
        for idx, pwd in enumerate(passwords, start=1):
            entropy = PasswordGenerator.calculate_entropy(pwd, config)
            strength, _, desc = PasswordGenerator.assess_strength(entropy)
            if args.count > 1:
                print(f"#{idx:02d}: {pwd} [{strength}, {entropy:.1f} bits]")
            else:
                print(f"Generated Password: {pwd}")
                print(f"Strength: {strength} ({entropy:.1f} bits)")
                if args.copy and copy_to_clipboard(pwd):
                    print("Copied to clipboard.")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
