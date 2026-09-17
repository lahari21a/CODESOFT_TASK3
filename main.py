import sys
import argparse

def main():
    if len(sys.argv) > 1 and ("--cli" in sys.argv or "-i" in sys.argv or "-l" in sys.argv or "--help" in sys.argv or "-h" in sys.argv):
        from cli import main as cli_main
        cli_main()
    else:
        try:
            from gui import launch_gui
            launch_gui()
        except Exception as e:
            print(f"Unable to launch graphical interface ({e}). Falling back to CLI mode...\n")
            from cli import run_interactive
            run_interactive()

if __name__ == "__main__":
    main()
