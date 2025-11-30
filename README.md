# Python Poker Bot Template

This repository contains a Python framework and example implementations for building poker bots compatible with the Turing Games platform. It provides a structured way to connect to the game server via WebSockets, handle game state updates, and implement custom strategies.

## Installation

1.  Clone the repository.
2.  Install the required dependencies:

```bash
pip install -r requirements.txt
```

The project relies on `websockets` for communication and `treys` for poker hand evaluation.

## Usage

There are two example bots included in the project. You can run them directly from the command line.

### Running the Max Eric Bot

The `main.py` file runs the `max_eric_bot`, a sophisticated bot that uses hand range analysis and Expected Value (EV) calculations.

```bash
python main.py --room my-room --key my-secret-key
```

### Running the Kelly Criterion Bot

The `kellycriterion.py` file implements a strategy using Monte Carlo simulations and the Kelly Criterion for bet sizing.

```bash
python kellycriterion.py --room my-room --key my-secret-key --simulations 1000
```

### Command Line Arguments

Both bots accept the following arguments to configure the connection:

- `--host`: The server host (default: `localhost`)
- `--port`: The server port (optional)
- `--room`: The game room ID to connect to (default: `my-new-room`)
- `--party`: The party identifier (default: `poker`)
- `--key`: Authentication key for the bot
- `--simulations`: Number of Monte Carlo simulations to run per move (default: `1000` or `900`)

### Testing with Multiple Bots

The `join-bots.sh` script allows you to launch multiple bot instances simultaneously for testing purposes.

Usage:

```bash
./join-bots.sh <count> <host> <port> <bot_command> <room>
```

## Architecture & Implementation

### The Framework (`tg/bot.py`)

The core logic is in `tg/bot.py`. This handles the plumbing so you don't have to write networking code for every new bot.

- **Connection**: It connects to the poker server using a WebSocket.
- **Listening**: It continuously listens for messages (JSON) from the server.
- **State Tracking**: It parses these messages into a `state` object that tracks the board cards, player stacks, whose turn it is, etc.
- **Triggers**:
  - When the game starts, it calls `start_game()`.
  - When an opponent moves, it calls `opponent_action()`.
  - **Crucially**, when the server says it is your turn (`state.game_state.whose_turn == state.client_id`), it calls your `act()` method.

To create a new bot, you subclass `Bot` and implement the abstract methods (`act`, `opponent_action`, `game_over`, `start_game`).

### Bot Strategies

#### 1. Max Eric Bot (`tg/max_eric_bot.py`)

This is the primary bot currently active in `main.py`. It implements a hybrid strategy combining Monte Carlo simulations with hand range analysis and EV (Expected Value) maximization.

**Strategy Breakdown:**

1.  **Pre-flop (Simulations)**:

    - Similar to the Kelly bot, it uses Monte Carlo simulations (default 900) to estimate the raw win probability of the hole cards against random hands.
    - It uses this probability to calculate the EV of calling vs. folding.

2.  **Post-flop (Hand Range Analysis)**:

    - **Villain Modeling**: It maintains a "villain tolerance" metric (starting at 50th percentile) to estimate the range of hands the opponent is likely holding. This tolerance adapts based on the opponent's observed fold frequency.
    - **Range Pruning**: If an opponent raises, the bot assumes they have a stronger hand and "prunes" the weaker hands from the estimated range.
    - **Exact Evaluation**: It iterates through every specific hand combination in the opponent's estimated range and compares it to the bot's hand + board to calculate precise Win/Loss/Tie probabilities.

3.  **Decision Making (EV Maximization)**:
    - The bot calculates the Expected Value (EV) for three main actions:
      - **Fold**: EV = 0.
      - **Call**: EV = `P(Win) * (Pot + Bet) - Cost * P(Loss)`.
      - **Raise**: It iterates through multiple bet sizes (e.g., 10, 20, Pot, 2x Pot) to find the raise amount that yields the highest EV.
    - It selects the action with the highest EV, with safeguards to prevent infinite raising wars (caps raises at 2 per round).

#### 2. KellyCriterion Bot (`kellycriterion.py`)

This bot plays based on bankroll management principles.

**A. Monte Carlo Simulation (Win Probability)**
When asked to `act()`, the bot calculates its chance of winning (`p`) by running thousands of random simulations of the remaining cards.

**B. The Kelly Criterion (Bet Sizing)**
It uses the Kelly formula to determine the optimal bet size to maximize long-term growth while minimizing risk of ruin.

$$ \text{Bet Fraction} = P - \frac{1-P}{b} $$

- **$P$**: Probability of winning.
- **$b$**: Payout odds (approximated by number of players).

**The Decision Logic:**

- If the optimal bet is higher than the target, it **Raises**.
- If the optimal bet covers the call cost, it **Calls**.
- Otherwise, it **Folds**.

#### 3. TemplateBot (Class in `main.py`)

A simple reference implementation that always calls/checks. It is included in the `main.py` file but not currently active by default.
