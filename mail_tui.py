#!/usr/bin/env python3

import os
import sys
import glob
import shutil
import curses
import subprocess

# Configuration: Saves to the current working directory
BASE_DIR = os.getcwd()
PREFIX = "linux-mm"
LORE_URL = "https://lore.kernel.org/linux-mm/"


def get_mailbox_stats(path, is_maildir):
    """Lightweight parser to count emails, threads, and size without loading files into memory."""
    emails_count = 0
    threads = set()
    total_size = 0

    def process_msg_headers(headers_text):
        msg_id = None
        in_reply_to = None
        for line in headers_text.splitlines():
            lower_line = line.lower()
            if lower_line.startswith("message-id:"):
                msg_id = line.split(":", 1)[1].strip()
            elif lower_line.startswith("in-reply-to:"):
                in_reply_to = line.split(":", 1)[1].strip()
            elif line.strip() == "":
                break  # End of headers

        # If it has no in-reply-to, it's the root of a thread
        if not in_reply_to and msg_id:
            threads.add(msg_id)

    if is_maildir:
        for subdir in ["new", "cur"]:
            dpath = os.path.join(path, subdir)
            if os.path.isdir(dpath):
                for f in os.listdir(dpath):
                    fpath = os.path.join(dpath, f)
                    if os.path.isfile(fpath):
                        emails_count += 1
                        total_size += os.path.getsize(fpath)
                        try:
                            with open(
                                fpath, "r", encoding="utf-8", errors="ignore"
                            ) as fp:
                                # Read just the first 50 lines to catch headers quickly
                                head = "".join([fp.readline() for _ in range(50)])
                                process_msg_headers(head)
                        except Exception:
                            pass
    else:  # mbox
        if os.path.isfile(path):
            total_size = os.path.getsize(path)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    current_headers = []
                    in_headers = False
                    for line in fp:
                        if line.startswith("From "):
                            if current_headers:
                                process_msg_headers("".join(current_headers))
                            emails_count += 1
                            current_headers = []
                            in_headers = True
                        elif in_headers:
                            if line.strip() == "":
                                in_headers = False
                            else:
                                current_headers.append(line)
                    if current_headers:
                        process_msg_headers("".join(current_headers))
            except Exception:
                pass

    thread_count = len(threads)
    # Fallback if no explicit roots were found but emails exist
    if thread_count == 0 and emails_count > 0:
        thread_count = 1

    return emails_count, thread_count, total_size


def get_status_lines():
    """Generates the configuration and rich storage status strings."""
    lines = [
        "--- Current Configuration ---",
        f"Storage Dir : {BASE_DIR}",
        f"Prefix      : {PREFIX}",
        f"Lore URL    : {LORE_URL}",
        "",
        "--- Local Storage Status ---",
    ]

    targets = sorted(glob.glob(os.path.join(BASE_DIR, f"{PREFIX}*")))
    if not targets:
        lines.append("  No local mailboxes found.")
    else:
        # Limit to 10 entries to avoid overflowing small terminal windows
        for t in targets[:10]:
            name = os.path.basename(t)
            is_maildir = os.path.isdir(t)

            emails, threads, size_bytes = get_mailbox_stats(t, is_maildir)
            size_mb = size_bytes / (1024 * 1024)

            fmt_type = "[Maildir]" if is_maildir else "[mbox]   "
            lines.append(
                f"  {fmt_type} {name:<18} | {emails:>4} emails | {threads:>3} threads | {size_mb:>6.2f} MB"
            )

        if len(targets) > 10:
            lines.append(f"  ... and {len(targets) - 10} more.")

    lines.append("")
    lines.append("--- Starred Tips in mutt---")
    lines.append("1. To Copy (Recommended): Press C (Shift + c).")
    lines.append("      This leaves the original email untouched in your current")
    lines.append("      linux-mm folder and sends a duplicate to your starred folder.")
    lines.append("2. To Save/Move: Press s (lowercase s). This copies the email to")
    lines.append(
        "      your starred folder and marks the original with a D (Deletion) in your current folder."
    )

    return lines


def curses_menu(stdscr, title, options, status_lines):
    """Generates a scrollable menu using curses, including status."""
    curses.curs_set(0)  # Hide the cursor
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Highlight color
    current_row = 0

    while True:
        stdscr.clear()

        try:
            # Draw Title
            stdscr.addstr(0, 0, title, curses.A_BOLD)

            # Draw Status and Config (Calculated once outside the loop to prevent UI lag)
            row = 2
            for line in status_lines:
                stdscr.addstr(row, 0, line)
                row += 1

            row += 1
            stdscr.addstr(row, 0, "--- Menu Options ---", curses.A_BOLD)
            row += 1
            menu_start_row = row

            # Draw Menu Options
            for idx, option in enumerate(options):
                x = 2
                y = menu_start_row + idx
                if idx == current_row:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, f"> {option}")
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, f"  {option}")
        except curses.error:
            # Terminal might be too small to draw everything, safely ignore
            pass

        stdscr.refresh()
        key = stdscr.getch()

        # Handle arrow keys and Enter
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            return current_row


def handle_lei():
    print("\n--- Fetching recent linux-mm (lei) ---")

    # Add to a single common directory. lei will automatically merge/update it.
    target_path = os.path.join(BASE_DIR, PREFIX)

    print(f"Fetching into common directory: {target_path} ...\n")
    # rt:24.hours.ago.. safely fetches recent emails without UTC timezone bugs
    cmd = [
        "lei",
        "q",
        "-I",
        LORE_URL,
        "rt:24.hours.ago..",
        "-o",
        target_path,
        "--threads",
    ]
    subprocess.run(cmd)


def handle_b4():
    print("\n--- Fetching specific patch thread (b4) ---")
    msg_id = input("Enter the specific Message-ID to fetch: ").strip()

    if not msg_id:
        print("Message-ID cannot be empty.")
        return

    target_mbox = os.path.join(BASE_DIR, f"{PREFIX}-b4-{msg_id.split('@')[0]}.mbx")
    print(f"Fetching into: {target_mbox} ...\n")

    cmd = ["b4", "mbox", msg_id, "-o", target_mbox]
    subprocess.run(cmd)


def handle_flush():
    print("\n--- Flushing Local Storage & Cache ---")
    print(f"WARNING: This will delete all '{PREFIX}*' files/folders in {BASE_DIR}")
    confirm = input("Are you sure? (y/n): ").strip().lower()

    if confirm == "y":
        print("Cleaning up files...")
        targets = glob.glob(os.path.join(BASE_DIR, f"{PREFIX}*"))
        for target in targets:
            try:
                if os.path.isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)
                print(f"Removed: {target}")
            except Exception as e:
                print(f"Failed to remove {target}: {e}")

        print("\nKilling lei daemon to flush cache...")
        subprocess.run(["lei", "daemon-kill"], stderr=subprocess.DEVNULL)
        print("Flush complete.")
    else:
        print("Aborted.")


def handle_mutt():
    targets = sorted(glob.glob(os.path.join(BASE_DIR, f"{PREFIX}*")))

    if not targets:
        print("\nNo local mailboxes found to open.")
        return
    elif len(targets) == 1:
        subprocess.run(["mutt", "-f", targets[0]])
    else:

        def simple_menu(stdscr, title, options):
            curses.curs_set(0)
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curr = 0
            while True:
                stdscr.clear()
                stdscr.addstr(0, 0, title, curses.A_BOLD)
                for i, opt in enumerate(options):
                    if i == curr:
                        stdscr.attron(curses.color_pair(1))
                        stdscr.addstr(2 + i, 2, f"> {opt}")
                        stdscr.attroff(curses.color_pair(1))
                    else:
                        stdscr.addstr(2 + i, 2, f"  {opt}")
                stdscr.refresh()
                k = stdscr.getch()
                if k == curses.KEY_UP and curr > 0:
                    curr -= 1
                elif k == curses.KEY_DOWN and curr < len(options) - 1:
                    curr += 1
                elif k in [curses.KEY_ENTER, 10, 13]:
                    return curr

        choice = curses.wrapper(
            simple_menu,
            "Select a mailbox to open with mutt:",
            [os.path.basename(t) for t in targets],
        )

        target_mail = targets[choice]
        subprocess.run(["mutt", "-f", target_mail])


def main():
    menu_options = [
        "Fetch recent linux-mm emails (via lei)",
        "Download a specific patch thread (via b4)",
        "Flush local storage and cache",
        "Open local storage (via mutt)",
        "Exit",
    ]

    while True:
        # Pre-calculate status lines before entering the menu to prevent UI lag
        status_lines = get_status_lines()
        choice = curses.wrapper(
            curses_menu, "=== linux-mm Workflow Manager ===", menu_options, status_lines
        )

        if choice == 0:
            handle_lei()
        elif choice == 1:
            handle_b4()
        elif choice == 2:
            handle_flush()
        elif choice == 3:
            handle_mutt()
        elif choice == 4:
            print("\nExiting...")
            sys.exit(0)

        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
