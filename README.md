# Snakes & Ladders — Terminal Edition

A two-player Snakes & Ladders game that runs entirely in the terminal, built with Python and the [Rich](https://github.com/Textualize/rich) library for a colorful, interactive UI.

---

## Features

- **2-player turn-based gameplay** — alternating turns with press-to-roll mechanics
- **Randomized board** — snakes and ladders are placed fresh every game
- **3 difficulty levels** — Easy (more ladders), Medium (balanced), Hard (more snakes)
- **Animated dice** — ASCII dice art with a rolling animation
- **Color-coded 10×10 board** — snake heads, ladder bases, and player tokens all highlighted
- **Overshoot rule** — player stays put if the roll would exceed square 100
- **Exact-100 win condition** — must land precisely on 100 to win
- **Replay last game** — step through every move of the previous game with board redraws
- **Move history table** — full per-turn log shown at game end
- **JSON game logs** — every completed game is saved to `game_logs/` automatically
- **Session scoreboard** — win counts persist across multiple games in one session

---

## Requirements

- Python 3.8+
- [`rich`](https://pypi.org/project/rich/) library

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/snakes-and-ladders.git
   cd snakes-and-ladders
   ```

2. **Install the dependency**
   ```bash
   pip install rich
   ```

---

## How to Run

```bash
python snakes_and_ladders.py
```

You'll be prompted to enter both player names, then the main menu appears.

---

## How to Play

| Menu Option | Action |
|-------------|--------|
| `1` New Game | Pick difficulty and start a fresh game |
| `2` Replay Last Game | Watch the previous game replay move-by-move |
| `3` View Move History | See the full move log table from the last game |
| `4` Quit | Exit the program |

**During a game:**
- Press **Enter** to roll the dice
- Type **`q`** and press Enter to quit back to the menu

**Rules:**
- Players move from square 1 to 100
- Landing on a **snake head** slides you down to its tail
- Landing on a **ladder base** climbs you up to its top
- Rolling past 100 does nothing — you need an exact roll to win
- Both players can occupy the same square simultaneously

---

## Project Structure

```
snakes-and-ladders/
├── snakes_and_ladders.py   # Main game file
├── game_logs/              # Auto-created; stores JSON logs of completed games
└── README.md
```

---

## Data Structures

| Structure | Type | Purpose |
|-----------|------|---------|
| `snakes` | `dict` | Maps snake head → tail square |
| `ladders` | `dict` | Maps ladder base → top square |
| `positions` | `list` | Current square for each player `[p1, p2]` |
| `wins` | `list` | Win count per player across the session |
| `history` | `list of dicts` | Full per-move log for replay and export |

---

## Example Board Output

```
 91  92  93  94  95  96  97  98  99  🏁
 90  89  88  87↓62  86  85  84  83  82
 71  72  73  74  75  76  77  78  79↑95  80
 ...
```

Cells show `head↓tail` for snakes and `base↑top` for ladders so you always know where they lead.

---

## Dependencies

- `random` — dice rolls and board generation (standard library)
- `time` — dice animation timing (standard library)
- `os` — terminal clearing via `console.clear()` (standard library)
- `json` — game log serialization (standard library)
- `datetime` — timestamp for log filenames (standard library)
- `rich` — all terminal UI rendering (**third-party**, install via pip)
