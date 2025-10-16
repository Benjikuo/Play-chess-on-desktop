# Play-chess-on-desktop
A program which lets people play chess on the desktop.

---

## 🧩 Features
- 🎮 **Interactive Chessboard** – Drag, click, and play directly on screen  
- 🤖 **AI Opponent** – Simple minimax engine with positional evaluation  
- 💾 **Save & Load** – Game automatically stored in `chess_save.json`  
- ⏪ **Undo / Redo / Replay** – Step through previous game states  
- 🔁 **Board Flip** – Instantly switch perspective  
- 🧠 **AI Move Highlights** – Shows AI’s thinking process  
- ♕ **Pawn Promotion UI** – Pick your new piece visually  
- 🎥 **Animated Launcher** – Start the game via `chess_button.py` with pawn animation

---

## 📂 Project Structure
```
Desktop chess/
├── image/               # Chessboard and piece graphics
├── video/               # PawnPromotion.mp4 animation
├── chess_board.py       # Main GUI and game control
├── chess_button.py      # Animation launcher and game toggle
├── chess_engine.py      # AI logic (minimax + evaluation)
├── chess_logic.py       # Core chess rules and move validation
├── chess_save.json      # Auto-saved game data
├── LICENSE              # License file
└── README.md            # Project documentation
```

---

## ⚙️ Requirements
Install dependencies before running:
```bash
pip install pillow opencv-python numpy
```

---

## ▶️ How to Run
1. Make sure the folders **`/image`** and **`/video`** exist and contain required assets.  
2. Start the launcher:
   ```bash
   python chess_button.py
   ```
3. Click the **pawn animation** to open or close the main chess window.

---

## ⌨️ Hotkeys
| Key | Action |
|-----|---------|
| `W` | Toggle continuous AI |
| `E` | Single AI move |
| `R` | Reset board |
| `T` | Flip board |
| `S` | Random move |
| `D` | Undo |
| `F` | Redo |
| `G` | Replay game |

---

## 🧠 Tech Stack
- **Python 3.9+**
- **Tkinter** – GUI framework  
- **OpenCV & Pillow** – Image/video processing  
- **JSON** – Save system

---

## 📜 License
This project is released under the **MIT License**.  
Feel free to modify and use for learning or personal projects.
