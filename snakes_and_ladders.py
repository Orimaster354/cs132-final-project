"""
Snakes & Ladders — terminal edition
Two-player terminal game with randomized board, difficulty levels,
move history, and replay.

Requires: pip install rich
"""

import random
import time
import os
import json
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.align import Align
from rich.rule import Rule

console = Console()

C_TITLE     = "#C084FC"
C_P1        = "#60A5FA"
C_P2        = "#FBBF24"
C_BOTH      = "#F87171"
C_SNAKE_H   = "#F87171"
C_SNAKE_T   = "#FCA5A5"
C_LADDER_B  = "#86EFAC"
C_LADDER_T  = "#D9F99D"
C_WIN_SQ    = "#A3E635"
C_DIM       = "#6B7280"
C_GOLD      = "#FCD34D"
C_SNAKE_IC  = "#EF4444"
C_LADDER_IC = "#22C55E"
C_EASY      = "#86EFAC"
C_MED       = "#FCD34D"
C_HARD      = "#F87171"
C_CELL_A    = "#1e2030"
C_CELL_B    = "#161822"

DIFFICULTY_COLORS = {"Easy": C_EASY, "Medium": C_MED, "Hard": C_HARD}

DICE_ART = {
    1: ["┌─────┐", "│     │", "│  ●  │", "│     │", "└─────┘"],
    2: ["┌─────┐", "│ ●   │", "│     │", "│   ● │", "└─────┘"],
    3: ["┌─────┐", "│ ●   │", "│  ●  │", "│   ● │", "└─────┘"],
    4: ["┌─────┐", "│ ● ● │", "│     │", "│ ● ● │", "└─────┘"],
    5: ["┌─────┐", "│ ● ● │", "│  ●  │", "│ ● ● │", "└─────┘"],
    6: ["┌─────┐", "│ ● ● │", "│ ● ● │", "│ ● ● │", "└─────┘"],
}


def generate_board(difficulty):
    """
    Randomly place snakes and ladders on the board based on difficulty.

    Uses a set to track occupied squares and prevent overlaps.
    Snake count and ladder count are pulled from a config dictionary
    keyed by difficulty string.

    Returns two dictionaries:
        snakes  — {head_square: tail_square}
        ladders — {base_square: top_square}
    """
    config = {
        "Easy":   {"snakes": 5,  "ladders": 7},
        "Medium": {"snakes": 8,  "ladders": 5},
        "Hard":   {"snakes": 12, "ladders": 3},
    }
    n_snakes  = config[difficulty]["snakes"]
    n_ladders = config[difficulty]["ladders"]

    used    = {1, 100}
    snakes  = {}
    ladders = {}

    attempts = 0
    while len(snakes) < n_snakes and attempts < 500:
        attempts += 1
        head = random.randint(20, 99)
        tail = random.randint(2, head - 5)
        if head not in used and tail not in used and abs(head - tail) >= 5:
            snakes[head] = tail
            used.add(head)
            used.add(tail)

    attempts = 0
    while len(ladders) < n_ladders and attempts < 500:
        attempts += 1
        base = random.randint(2, 79)
        top  = random.randint(base + 5, min(base + 40, 99))
        if base not in used and top not in used:
            ladders[base] = top
            used.add(base)
            used.add(top)

    return snakes, ladders


def get_initials(name, length=2):
    """
    Derive a short board token from a player's name.

    Takes the first letter of the first and last word if the name has
    multiple words (e.g. 'John Smith' -> 'JS'). Falls back to the first
    `length` characters for single-word names (e.g. 'Raya' -> 'RA').
    Always returns uppercase.
    """
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name.strip()[:length].upper()


def render_board(positions, names, snakes, ladders):
    """
    Build and return a Rich Table representing the 10x10 game board.

    Rows alternate between two subtle background shades and each cell
    also alternates shade by column to produce a checkerboard effect.
    Player tokens are shown as the player's initials wrapped in guillemets.
    Snake head cells show 'head-down-tail' and ladder base cells show
    'base-up-top' so connections are visible without checking the panel.

    Arguments:
        positions — list [p1_square, p2_square]
        names     — list [p1_name, p2_name]
        snakes    — dict {head: tail}
        ladders   — dict {base: top}
    """
    initials    = [get_initials(name) for name in names]
    snake_tails = set(snakes.values())
    ladder_tops = set(ladders.values())

    grid = Table(box=box.SIMPLE_HEAVY, show_header=False, padding=(0, 0))
    for col_num in range(10):
        grid.add_column(justify="center", min_width=6, no_wrap=True)

    for row in range(9, -1, -1):
        if row % 2 == 0:
            nums = list(range(row * 10 + 1, row * 10 + 11))
        else:
            nums = list(range(row * 10 + 10, row * 10, -1))

        row_shade = C_CELL_A if row % 2 == 0 else C_CELL_B
        cells     = []

        for col_idx, n in enumerate(nums):
            p1_here = positions[0] == n
            p2_here = positions[1] == n
            checker = C_CELL_A if (row + col_idx) % 2 == 0 else C_CELL_B

            if p1_here and p2_here:
                cell = Text(f"«{initials[0]}{initials[1]}»", style=f"bold {C_BOTH} on {checker}")
            elif p1_here:
                cell = Text(f" «{initials[0]}» ", style=f"bold {C_P1} on {checker}")
            elif p2_here:
                cell = Text(f" «{initials[1]}» ", style=f"bold {C_P2} on {checker}")
            elif n == 100:
                cell = Text("  🏁  ", style=f"bold {C_WIN_SQ} on {checker}")
            elif n in snakes:
                dest = snakes[n]
                cell = Text(f"{n}↓{dest}", style=f"bold {C_SNAKE_H} on {checker}")
            elif n in snake_tails:
                cell = Text(f"  {n:2} ", style=f"{C_SNAKE_T} on {checker}")
            elif n in ladders:
                dest = ladders[n]
                cell = Text(f"{n}↑{dest}", style=f"bold {C_LADDER_B} on {checker}")
            elif n in ladder_tops:
                cell = Text(f"  {n:2} ", style=f"{C_LADDER_T} on {checker}")
            else:
                cell = Text(f"  {n:2} ", style=f"{C_DIM} on {checker}")

            cells.append(cell)

        grid.add_row(*cells, style=f"on {row_shade}")

    return grid


def render_legend(snakes, ladders, names):
    """
    Return a one-line Rich Text legend showing player token symbols
    and the meaning of snake and ladder cell notation.
    """
    legend = Text()
    legend.append(f" «{get_initials(names[0])}»", style=f"bold {C_P1}")
    legend.append(f" {names[0]}   ")
    legend.append(f"«{get_initials(names[1])}»", style=f"bold {C_P2}")
    legend.append(f" {names[1]}   ")
    legend.append("##↓##", style=f"bold {C_SNAKE_H}")
    legend.append(" snake (head↓tail)   ")
    legend.append("##↑##", style=f"bold {C_LADDER_B}")
    legend.append(" ladder (base↑top)")
    return legend


def render_connections(snakes, ladders):
    """
    Return a Rich Panel showing all snakes and ladders as ASCII arrows.

    Snakes are listed in the left column sorted head-descending.
    Ladders are listed in the right column sorted base-ascending.
    Each entry is formatted as 'from ━━> to'.
    """
    snake_entries  = sorted(snakes.items(),  reverse=True)
    ladder_entries = sorted(ladders.items())
    row_count      = max(len(snake_entries), len(ladder_entries))

    table = Table(box=box.SIMPLE, show_header=True, padding=(0, 1),
                  header_style=f"bold {C_DIM}")
    table.add_column("🐍  snakes",  min_width=14, no_wrap=True)
    table.add_column("🪜  ladders", min_width=14, no_wrap=True)

    for row_idx in range(row_count):
        if row_idx < len(snake_entries):
            head, tail  = snake_entries[row_idx]
            snake_cell  = Text(f"{head:>2} ━━▶ {tail:<2}", style=C_SNAKE_IC)
        else:
            snake_cell  = Text("")

        if row_idx < len(ladder_entries):
            base, top   = ladder_entries[row_idx]
            ladder_cell = Text(f"{base:>2} ━━▶ {top:<2}", style=C_LADDER_IC)
        else:
            ladder_cell = Text("")

        table.add_row(snake_cell, ladder_cell)

    return Panel(table, border_style=C_DIM, padding=(0, 1))


def animate_dice(result):
    """
    Flash random dice faces five times then land on the real result.

    Clears the terminal on each frame to create an animation effect.
    Pauses briefly after landing so the player can read the final value.
    The result argument is the actual roll to display at the end.
    """
    for frame in range(5):
        fake = random.randint(1, 6)
        console.clear()
        console.print("\n  [bold #C084FC]Rolling...[/]")
        for line in DICE_ART[fake]:
            console.print(f"  [#60A5FA]{line}[/]")
        time.sleep(0.1)

    console.clear()
    console.print("\n  [bold #A3E635]You rolled:[/]")
    for line in DICE_ART[result]:
        console.print(f"  [bold #FBBF24]{line}[/]")
    time.sleep(0.4)


def press_to_roll(pname, color):
    """
    Display a styled prompt for the current player and wait for input.

    Returns the raw input string lowercased and stripped.
    The caller should treat a return value of 'q' as a quit signal.
    """
    console.print(f"\n  [bold {color}]▶  {pname}[/]  — press [bold]ENTER[/] to roll  [dim](or 'q' to quit)[/dim]")
    val = input("  ❯ ").strip().lower()
    return val


def move_player(position, roll, snakes, ladders):
    """
    Calculate a player's new position after rolling the dice.

    Applies the overshoot rule (stay put if new position exceeds 100),
    then checks the snakes dictionary and ladders dictionary for
    teleport destinations.

    Returns a tuple:
        (new_position, event_message_or_None, event_type_or_None)
    Event type is one of 'snake', 'ladder', 'overshoot', or None.
    """
    new_pos = position + roll
    event = None
    event_type = None

    if new_pos > 100:
        return position, f"[{C_MED}]Overshoot! Needs exact roll — stays at {position}.[/]", "overshoot"

    if new_pos in snakes:
        tail  = snakes[new_pos]
        event = f"[bold {C_SNAKE_IC}]🐍  Snake at {new_pos}! Slides down to {tail}.[/]"
        event_type = "snake"
        new_pos = tail
    elif new_pos in ladders:
        top  = ladders[new_pos]
        event  = f"[bold {C_LADDER_IC}]🪜  Ladder at {new_pos}! Climbs up to {top}.[/]"
        event_type = "ladder"
        new_pos = top

    return new_pos, event, event_type


def render_scoreboard(names, wins):
    """
    Return a Rich Panel showing each player's name and total win count.

    The wins argument is a list [p1_wins, p2_wins] that persists
    across multiple games within the same session.
    """
    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
    table.add_column()
    table.add_column(justify="right")
    table.add_row(
        Text(f"🏆  {names[0]}", style=f"bold {C_P1}"),
        Text(str(wins[0]),      style=f"bold {C_P1}")
    )
    table.add_row(
        Text(f"🏆  {names[1]}", style=f"bold {C_P2}"),
        Text(str(wins[1]),      style=f"bold {C_P2}")
    )
    return Panel(table, title="[bold]Scoreboard[/]", border_style=C_DIM, padding=(0, 1))


def save_history(names, difficulty, history, winner):
    """
    Save the completed game's move history to a JSON file in game_logs/.

    Creates the game_logs directory if it does not exist. The file is
    named with a timestamp so each game produces a unique file. The
    history list of dicts is written under the 'moves' key alongside
    player names, difficulty, winner name, and timestamp string.

    Returns the filename path as a string.
    """
    os.makedirs("game_logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"game_logs/game_{timestamp}.json"
    data = {
        "players":    names,
        "difficulty": difficulty,
        "winner":     winner,
        "moves":      history,
        "timestamp":  timestamp,
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    return filename


def render_history_table(history, names):
    """
    Return a Rich Table showing every move from a completed game.

    Columns: move number, player name, dice roll, starting square,
    ending square, and event type (snake / ladder / overshoot / win).

    The history argument is a list of move dictionaries, each containing
    keys: player (int index), roll, from, to, event_type.
    """
    table = Table(title="Move History", box=box.MINIMAL_DOUBLE_HEAD,
                  show_lines=False, padding=(0, 1))
    table.add_column("#",      style=C_DIM, width=4)
    table.add_column("Player", width=16)
    table.add_column("Roll",   justify="center", width=5)
    table.add_column("From",   justify="center", width=5)
    table.add_column("To",     justify="center", width=5)
    table.add_column("Event",  width=30)

    for move_num, move in enumerate(history, 1):
        color      = C_P1 if move["player"] == 0 else C_P2
        event_type = move.get("event_type", "")

        if event_type == "snake":
            event_cell = Text("🐍 Snake",    style=C_SNAKE_IC)
        elif event_type == "ladder":
            event_cell = Text("🪜 Ladder",   style=C_LADDER_IC)
        elif event_type == "overshoot":
            event_cell = Text("↩ Overshoot", style=C_MED)
        elif event_type == "win":
            event_cell = Text("🏆 WIN!",     style=C_GOLD)
        else:
            event_cell = Text("—",           style=C_DIM)

        table.add_row(
            str(move_num),
            Text(names[move["player"]], style=f"bold {color}"),
            Text(str(move["roll"]),     style="bold"),
            str(move["from"]),
            str(move["to"]),
            event_cell,
        )

    return table


def replay_game(names, history, snakes, ladders):
    """
    Step through every move of the last completed game with board redraws.

    Reconstructs player positions move by move from the history list,
    printing the board state after each move with a short pause so the
    replay is readable. Waits for Enter at the end before returning.
    """
    console.clear()
    console.print(Rule("[bold #C084FC]Replay — Last Game[/]"))
    positions = [1, 1]

    for move_idx, move in enumerate(history):
        player_idx            = move["player"]
        positions[player_idx] = move["to"]
        color                 = C_P1 if player_idx == 0 else C_P2

        console.print(
            f"\n  [bold]Move {move_idx + 1}[/]  [{color}]{names[player_idx]}[/] "
            f"rolled [bold]{move['roll']}[/]  ->  square [bold]{move['to']}[/]"
        )

        if move.get("event_type") == "snake":
            console.print(f"  [bold {C_SNAKE_IC}]🐍 Hit a snake![/]")
        elif move.get("event_type") == "ladder":
            console.print(f"  [bold {C_LADDER_IC}]🪜 Climbed a ladder![/]")
        elif move.get("event_type") == "win":
            console.print(f"  [bold {C_GOLD}]🏆 {names[player_idx]} won![/]")

        console.print(render_board(positions, names, snakes, ladders))
        time.sleep(0.9)

    input("\n  Press Enter to return to menu... ")


def pick_difficulty():
    """
    Display a difficulty selection menu and return the chosen string.

    Presents three options: Easy (more ladders), Medium (balanced),
    Hard (more snakes). Returns one of 'Easy', 'Medium', 'Hard'.
    Defaults to 'Medium' if the player presses Enter without typing.
    """
    console.print(Panel(
        "[bold]Choose difficulty:[/]\n\n"
        f"  [bold {C_EASY}]1[/]  Easy   — more ladders, few snakes\n"
        f"  [bold {C_MED}]2[/]  Medium — balanced\n"
        f"  [bold {C_HARD}]3[/]  Hard   — many snakes, few ladders\n",
        title="[bold #C084FC]Difficulty[/]", border_style=C_DIM, padding=(1, 2)
    ))
    choice = Prompt.ask("  Enter", choices=["1", "2", "3"], default="2")
    return {"1": "Easy", "2": "Medium", "3": "Hard"}[choice]


def play_game(names, difficulty, wins, last_game):
    """
    Run a single complete game between two players.

    Generates a fresh randomized board each game, then loops turn by
    turn until one player lands on exactly square 100. Tracks every
    move in a history list of dicts and saves it to disk on completion.
    Updates the wins list and last_game dict in place.

    Data structures in use:
        positions — list [p1_square, p2_square]
        history   — list of dicts, each with keys:
                    player, roll, from, to, event_type
        snakes    — dict {head_square: tail_square}
        ladders   — dict {base_square: top_square}
        wins      — list [p1_win_count, p2_win_count]
    """
    snakes, ladders = generate_board(difficulty)
    positions       = [1, 1]
    history         = []
    current         = 0
    diff_color      = DIFFICULTY_COLORS[difficulty]

    while True:
        console.clear()
        pcolor = C_P1 if current == 0 else C_P2
        pname  = names[current]

        console.print(Panel(
            Align.center(Text("🐍  Snakes & Ladders  🪜", style=f"bold {C_TITLE}")),
            subtitle=f"[{diff_color}]{difficulty}[/]",
            border_style=C_DIM,
        ))

        board = render_board(positions, names, snakes, ladders)
        score = render_scoreboard(names, wins)
        console.print(Columns([
            Panel(board, border_style=C_DIM, padding=(0, 0)),
            score,
        ], equal=False, expand=False))

        console.print(render_legend(snakes, ladders, names))
        console.print()
        console.print(render_connections(snakes, ladders))
        console.print()

        val = press_to_roll(pname, pcolor)
        if val == "q":
            console.print("\n  [dim]Quitting game...[/dim]")
            break

        roll                           = random.randint(1, 6)
        animate_dice(roll)

        prev                           = positions[current]
        new_pos, event_msg, event_type = move_player(prev, roll, snakes, ladders)
        positions[current]             = new_pos

        history.append({
            "player":     current,
            "roll":       roll,
            "from":       prev,
            "to":         new_pos,
            "event_type": event_type or "",
        })

        console.clear()
        console.print(Panel(
            Align.center(Text("🐍  Snakes & Ladders  🪜", style=f"bold {C_TITLE}")),
            subtitle=f"[{diff_color}]{difficulty}[/]",
            border_style=C_DIM,
        ))
        console.print(render_board(positions, names, snakes, ladders))
        console.print()
        console.print(f"  [{pcolor}]{pname}[/] rolled [bold]{roll}[/] -> square [bold]{new_pos}[/]")
        if event_msg:
            console.print(f"  {event_msg}")

        if new_pos == 100:
            history[-1]["event_type"] = "win"
            wins[current] += 1
            console.print()
            console.print(Panel(
                Align.center(Text(f"🏆  {pname} wins!  🏆", style=f"bold {C_GOLD}")),
                border_style=C_GOLD,
                padding=(1, 4),
            ))
            console.print(render_scoreboard(names, wins))
            console.print()
            console.print(render_history_table(history, names))

            fname = save_history(names, difficulty, history, pname)
            console.print(f"\n  [dim]History saved -> {fname}[/dim]\n")

            last_game.update({
                "names":   names,
                "history": history,
                "snakes":  snakes,
                "ladders": ladders,
            })
            input("  Press Enter to continue... ")
            return

        console.print()
        input("  Press Enter to continue... ")
        current = 1 - current


def main_menu():
    """
    Clear the screen, display the main menu panel, and return the choice.

    Returns one of: '1' (new game), '2' (replay last game),
    '3' (view move history), '4' (quit).
    """
    console.clear()
    console.print(Panel(
        Align.center(
            Text("🐍  SNAKES & LADDERS  🪜\n", style=f"bold {C_TITLE}") +
            Text("terminal edition", style=C_DIM)
        ),
        border_style=C_TITLE, padding=(1, 4)
    ))
    console.print(
        f"  [bold {C_EASY}]1[/]  New Game\n"
        f"  [bold {C_MED}]2[/]  Replay Last Game\n"
        f"  [bold {C_HARD}]3[/]  View Move History\n"
        f"  [bold {C_DIM}]4[/]  Quit\n"
    )
    return Prompt.ask("  Choose", choices=["1", "2", "3", "4"], default="1")


def main():
    """
    Entry point. Collects player names then runs the main menu loop.

    The wins list and last_game dict persist across multiple games
    within the session so the scoreboard and replay feature stay intact.
    """
    wins      = [0, 0]
    names     = [None, None]
    last_game = {}

    console.clear()
    console.print(Panel(
        "[bold #C084FC]Welcome to Snakes & Ladders![/]\n\nEnter your names:",
        border_style=C_DIM, padding=(1, 2)
    ))
    names[0] = Prompt.ask(f"  [bold {C_P1}]Player 1 name[/]") or "Player 1"
    names[1] = Prompt.ask(f"  [bold {C_P2}]Player 2 name[/]") or "Player 2"

    initials = [get_initials(name) for name in names]
    console.print(
        f"\n  [{C_P1}]{names[0]}[/] -> [{C_P1}][{initials[0]}][/]   "
        f"[{C_P2}]{names[1]}[/] -> [{C_P2}][{initials[1]}][/]"
    )
    time.sleep(1.2)

    while True:
        choice = main_menu()

        if choice == "1":
            difficulty = pick_difficulty()
            play_game(names, difficulty, wins, last_game)

        elif choice == "2":
            if not last_game:
                console.print("\n  [dim]No game played yet![/dim]\n")
                time.sleep(1.2)
            else:
                replay_game(
                    last_game["names"],  last_game["history"],
                    last_game["snakes"], last_game["ladders"]
                )

        elif choice == "3":
            if not last_game:
                console.print("\n  [dim]No history yet — play a game first![/dim]\n")
                time.sleep(1.2)
            else:
                console.clear()
                console.print(render_history_table(last_game["history"], last_game["names"]))
                input("\n  Press Enter to go back... ")

        elif choice == "4":
            console.print(f"\n  [{C_TITLE}]Thanks for playing! 🐍🪜[/]\n")
            break


if __name__ == "__main__":
    main()