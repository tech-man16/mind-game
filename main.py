import tkinter as tk
import random
import math


class MindNim:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 MindNim")
        self.root.geometry("650x550")
        self.root.configure(bg="#0f172a")

        self.piles = [random.randint(3, 8) for _ in range(3)]
        self.coin_ids = []
        self.buttons = []
        self.current_turn = "user"

        # -------- UI --------
        self.status = tk.Label(
            root, text="Your Turn",
            font=("Arial", 20, "bold"),
            fg="#e2e8f0", bg="#0f172a"
        )
        self.status.pack(pady=15)

        self.canvas = tk.Canvas(
            root, width=600, height=320,
            bg="#1e293b", highlightthickness=0
        )
        self.canvas.pack()

        self.controls = tk.Frame(root, bg="#0f172a")
        self.controls.pack(pady=10)

        self.restart_btn = tk.Button(
            root, text="Restart",
            command=self.restart,
            bg="#334155", fg="white"
        )
        self.restart_btn.pack(pady=10)

        self.draw_piles()

    # -------- SOUND (built-in) --------
    def play_click(self):
        self.root.bell()

    # -------- AI --------
    def nim_sum(self):
        result = 0
        for p in self.piles:
            result ^= p
        return result

    def random_move(self):
        non_empty = [i for i, p in enumerate(self.piles) if p > 0]
        pile = random.choice(non_empty)
        return pile, random.randint(1, min(3, self.piles[pile]))

    def bot_move(self):
        total = sum(self.piles)

        # -------- EARLY GAME --------
        if total > 10 and random.random() < 0.7:
            return self.random_move()

        # -------- MID GAME --------
        if total > 5 and random.random() < 0.4:
            return self.random_move()

        # -------- BLUNDER MASKING --------
        if random.random() < 0.15:
            return self.random_move()

        # -------- LIMITED STRATEGY (1–3 ONLY) --------
        xor = self.nim_sum()

        best_moves = []

        for i in range(len(self.piles)):
            for remove in range(1, min(4, self.piles[i] + 1)):
                new_piles = self.piles.copy()
                new_piles[i] -= remove

                # Check if this move leads toward winning position
                new_xor = 0
                for p in new_piles:
                    new_xor ^= p

                if new_xor == 0:
                    best_moves.append((i, remove))

        if best_moves:
            return random.choice(best_moves)

        return self.random_move()

    # -------- DRAW --------
    def draw_piles(self):
        self.canvas.delete("all")
        self.coin_ids.clear()

        for b in self.buttons:
            b.destroy()
        self.buttons.clear()

        spacing = 170

        for i, count in enumerate(self.piles):
            x = 100 + i * spacing
            pile_coins = []

            for j in range(count):
                y = 260 - j * 22
                coin = self.canvas.create_oval(
                    x, y, x + 45, y + 18,
                    fill="#facc15", outline=""
                )
                pile_coins.append(coin)

            self.coin_ids.append(pile_coins)

            # Buttons
            for n in range(1, 4):
                btn = tk.Button(
                    self.controls,
                    text=f"P{i+1} -{n}",
                    command=lambda i=i, n=n: self.user_move(i, n),
                    bg="#475569", fg="white", width=6
                )
                btn.grid(row=i, column=n-1, padx=6, pady=3)

                # Hover effect
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#64748b"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#475569"))

                self.buttons.append(btn)

    # -------- GAME FLOW --------
    def user_move(self, pile_index, remove):
        if self.current_turn != "user":
            return
        if remove > self.piles[pile_index]:
            return

        self.play_click()
        self.disable_buttons()
        self.status.config(text="Removing...")

        self.animate_removal(
            pile_index, remove,
            lambda: self.after_user_move(pile_index, remove)
        )

    def after_user_move(self, pile_index, remove):
        self.piles[pile_index] -= remove

        if sum(self.piles) == 0:
            self.status.config(text="🎉 You Win!")
            return

        self.current_turn = "bot"
        self.status.config(text="🤖 Thinking...")
        delay = 700 + random.randint(0, 1000)
        self.root.after(delay, self.bot_turn)

    def bot_turn(self):
        pile, remove = self.bot_move()

        self.animate_removal(
            pile, remove,
            lambda: self.after_bot_move(pile, remove)
        )

    def after_bot_move(self, pile, remove):
        self.piles[pile] -= remove

        if sum(self.piles) == 0:
            self.status.config(text="💀 Bot Wins!")
            return

        self.current_turn = "user"
        self.status.config(text="Your Turn")
        self.draw_piles()
        self.enable_buttons()

    # -------- SMOOTH ANIMATION (EASING) --------
    def animate_removal(self, pile_index, count, callback):
        coins = self.coin_ids[pile_index][-count:]

        def ease_out(t):
            return 1 - (1 - t) ** 3  # cubic easing

        def animate(step=0):
            if step > 20:
                for c in coins:
                    self.canvas.delete(c)
                callback()
                return

            progress = ease_out(step / 20)
            dy = 8 * progress

            for c in coins:
                self.canvas.move(c, 0, dy)

            self.root.after(20, lambda: animate(step + 1))

        animate()

    # -------- CONTROLS --------
    def disable_buttons(self):
        for b in self.buttons:
            b.config(state=tk.DISABLED)

    def enable_buttons(self):
        for b in self.buttons:
            b.config(state=tk.NORMAL)

    def restart(self):
        self.piles = [3, 5, 7]
        self.current_turn = "user"
        self.status.config(text="Your Turn")
        self.draw_piles()


# -------- RUN --------
if __name__ == "__main__":
    root = tk.Tk()
    game = MindNim(root)
    root.mainloop()