#!/usr/bin/env python3
"""
Glyph-Noetic CLI

An interactive command-line interface for the Glyph-Noetic Engine.
Allows users to compose and send noetic sentences to the daemon.
"""

import json
import socket
import readline
import sys

SOCKET_PATH = "/tmp/glyph_noetic_daemon.sock"

def send_command(sentence: list) -> dict:
    """Send a command to the daemon and return the response."""
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(SOCKET_PATH)
            request = {"jsonrpc": "2.0", "id": 1, "sentence": sentence}
            s.sendall(json.dumps(request).encode('utf-8'))
            response_data = s.recv(8192)
            return json.loads(response_data.decode('utf-8'))
    except FileNotFoundError:
        print(f"Error: Daemon socket not found at {SOCKET_PATH}. Is the daemon running?")
        return {"error": "Daemon not running"}
    except ConnectionRefusedError:
        print("Error: Connection refused. The daemon might be starting up or has crashed.")
        return {"error": "Connection refused"}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": str(e)}

def print_help():
    """Prints the help message with available glyphs."""
    print("\n-- Glyph-Noetic CLI Help --")
    print("Compose noetic sentences using glyphs and operators.")
    print("Example: [C:PLN]?")
    print("Example: compose [T~g] -> [C:PLN]")

    print("\nAvailable Glyphs (Examples):")
    print("  Temporal (Blue):   [T-HIERARCHY], [T~g], [T~d] ...")
    print("  Cognitive (Purple):[C:PLN], [C:PATTERN], [C:MOSES] ...")
    print("  Structural (Green):[S:ATOMSPACE], [S:atom] ...")
    print("  Noetic (Orange):   [N:DECISION], [N:TV], [N:AV] ...")

    print("\nOperators:")
    print("  ? : Query a glyph's state.")
    print("  ! : Execute a glyph's default action.")
    print("  ->: Define a relationship or flow.")
    print("  | : Pipe output to a filter (e.g., | filter(av.sti > 100))")

    print("\nCommands:")
    print("  help: Show this message.")
    print("  status: Get the overall daemon status.")
    print("  exit: Exit the CLI.")
    print("")

def main():
    """Main CLI loop."""
    print("Welcome to the Glyph-Noetic CLI. Type 'help' for commands.")

    while True:
        try:
            raw_input = input("> ").strip()
            if not raw_input:
                continue

            if raw_input.lower() == 'exit':
                break
            if raw_input.lower() == 'help':
                print_help()
                continue
            if raw_input.lower() == 'status':
                # This is a shortcut for a common glyph command
                raw_input = '[S:ATOMSPACE]?'

            # Simple parsing: split by space, but keep bracketed glyphs whole
            # This is a naive parser for demonstration purposes.
            import re
            # Parse: keep bracketed glyphs whole, including trailing ? or !
            tokens = re.findall(r'\[[^\]]+\][?!]?|\S+', raw_input)
            # Remove brackets but preserve operators
            sentence = [s.replace('[', '').replace(']', '') for s in tokens]
            # Filter out pure operators that are separate tokens (like ->)
            # but keep them in the sentence for the daemon to interpret

            response = send_command(sentence)

            # Pretty print the JSON response
            print(json.dumps(response, indent=2))

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred in the CLI: {e}")

if __name__ == "__main__":
    main()
