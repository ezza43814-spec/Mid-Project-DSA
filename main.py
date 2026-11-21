import tkinter as tk
from Game import Game
from Tableau import is_red

CARD_W = 80
CARD_H = 110
GAP = 20
MARGIN = 20
SLOT = CARD_W + GAP
BOARD_W = MARGIN * 2 + 7 * CARD_W + 6 * GAP
TOP_Y = 45
TABLEAU_Y = 195
DOWN_STEP = 15
UP_STEP = 25
FAN = 18
BG = "#0b6623"
BAR_BG = "#064016"
CARD_BACK = "#1f4e9c"
CARD_BACK_INNER = "#5b8bd6"
SLOT_COLOR = "#9fd3a8"
SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
SYMBOLS = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}


class SolitaireApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Klondike Solitaire")
        self.root.configure(bg=BG)
        self.root.minsize(BOARD_W, 600)

        self.game = Game()
        self.sel_type = None
        self.sel_pile = None
        self.sel_count = 0
        self.seconds = 0
        self.offset = 0

        self.make_toolbar()

        self.message = tk.Label(root, text="Click the stock to draw a card.",
                                bg=BAR_BG, fg="white", font=("Arial", 12), pady=6)
        self.message.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(root, width=BOARD_W, height=620, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Configure>", self.on_resize)
        self.refresh()
        self.tick()

    def make_toolbar(self):
        bar = tk.Frame(self.root, bg=BAR_BG, pady=8)
        bar.pack(side="top", fill="x")

        self.make_button(bar, "Undo", self.do_undo)
        self.make_button(bar, "Redo", self.do_redo)
        self.make_button(bar, "Hint", self.do_hint)
        self.make_button(bar, "New Game", self.new_game)

        self.moves_label = tk.Label(bar, text="Moves: 0", bg=BAR_BG, fg="white",
                                    font=("Arial", 12, "bold"))
        self.moves_label.pack(side="right", padx=15)

        self.time_label = tk.Label(bar, text="Time: 00:00", bg=BAR_BG, fg="white",
                                   font=("Arial", 12, "bold"))
        self.time_label.pack(side="right", padx=15)

    def make_button(self, parent, text, command):
        button = tk.Button(parent, text=text, command=command, bg="#f4d03f", fg="black",
                           font=("Arial", 11, "bold"), width=9, relief="flat", cursor="hand2")
        button.pack(side="left", padx=8)

    def tick(self):
        if not self.game.is_won():
            self.seconds = self.seconds + 1
            self.update_info()
        self.root.after(1000, self.tick)

    def update_info(self):
        minutes = self.seconds // 60
        secs = self.seconds % 60
        self.time_label.config(text="Time: %02d:%02d" % (minutes, secs))
        self.moves_label.config(text="Moves: " + str(self.game.history.size))

    def column_x(self, col):
        return self.offset + MARGIN + col * SLOT

    def column_at(self, x):
        position = x - self.offset - MARGIN
        if position < 0:
            return None
        col = position // SLOT
        if col > 6:
            return None
        if position % SLOT > CARD_W:
            return None
        return col

    def card_y_positions(self, cards):
        positions = []
        y = TABLEAU_Y
        for card in cards:
            positions.append(y)
            if card.face_up:
                y = y + UP_STEP
            else:
                y = y + DOWN_STEP
        return positions

    def clear_selection(self):
        self.sel_type = None
        self.sel_pile = None
        self.sel_count = 0

    def waste_shown_count(self):
        size = self.game.waste.size
        if size > 3:
            return 3
        if size < 1:
            return 1
        return size

    def draw_card(self, x, y, card, selected):
        if selected:
            outline = "yellow"
            line_width = 4
        else:
            outline = "black"
            line_width = 1

        self.canvas.create_rectangle(x + 2, y + 2, x + CARD_W + 2, y + CARD_H + 2,
                                     fill="#06310f", outline="")

        if not card.face_up:
            self.canvas.create_rectangle(x, y, x + CARD_W, y + CARD_H,
                                         fill=CARD_BACK, outline=outline, width=line_width)
            self.canvas.create_rectangle(x + 7, y + 7, x + CARD_W - 7, y + CARD_H - 7,
                                         outline=CARD_BACK_INNER, width=2)
            return

        if is_red(card):
            color = "#c0392b"
        else:
            color = "black"

        symbol = SYMBOLS[card.suit]
        self.canvas.create_rectangle(x, y, x + CARD_W, y + CARD_H,
                                     fill="white", outline=outline, width=line_width)
        self.canvas.create_text(x + 6, y + 4, text=card.rank + symbol, anchor="nw",
                                fill=color, font=("Arial", 13, "bold"))
        self.canvas.create_text(x + CARD_W // 2, y + CARD_H // 2 + 6, text=symbol,
                                fill=color, font=("Arial", 34))
        self.canvas.create_text(x + CARD_W - 6, y + CARD_H - 4, text=card.rank + symbol,
                                anchor="se", fill=color, font=("Arial", 13, "bold"))

    def draw_empty(self, x, y, label):
        self.canvas.create_rectangle(x, y, x + CARD_W, y + CARD_H,
                                     outline=SLOT_COLOR, width=2)
        self.canvas.create_text(x + CARD_W // 2, y + CARD_H // 2, text=label,
                                fill=SLOT_COLOR, font=("Arial", 14))

    def draw_heading(self, col, text):
        self.canvas.create_text(self.column_x(col), 20, text=text, anchor="w",
                                fill="white", font=("Arial", 11, "bold"))

    def draw_stock(self):
        stock_x = self.column_x(0)
        if self.game.stock.is_empty():
            self.draw_empty(stock_x, TOP_Y, "Recycle")
        else:
            self.canvas.create_rectangle(stock_x + 2, TOP_Y + 2, stock_x + CARD_W + 2,
                                         TOP_Y + CARD_H + 2, fill="#06310f", outline="")
            self.canvas.create_rectangle(stock_x, TOP_Y, stock_x + CARD_W, TOP_Y + CARD_H,
                                         fill=CARD_BACK, outline="black")
            self.canvas.create_rectangle(stock_x + 7, TOP_Y + 7, stock_x + CARD_W - 7,
                                         TOP_Y + CARD_H - 7, outline=CARD_BACK_INNER, width=2)
            self.canvas.create_text(stock_x + CARD_W // 2, TOP_Y + CARD_H // 2,
                                    text=str(self.game.stock.size),
                                    fill="white", font=("Arial", 20, "bold"))

    def draw_waste(self):
        waste_x = self.column_x(1)
        if self.game.waste.is_empty():
            self.draw_empty(waste_x, TOP_Y, "Waste")
            return

        shown = self.game.waste.top_cards(3)
        shown.reverse()
        for i in range(len(shown)):
            is_top = (i == len(shown) - 1)
            selected = is_top and self.sel_type == "waste"
            self.draw_card(waste_x + i * FAN, TOP_Y, shown[i], selected)

        self.canvas.create_text(waste_x, TOP_Y + CARD_H + 14,
                                text=str(self.game.waste.size) + " cards", anchor="w",
                                fill=SLOT_COLOR, font=("Arial", 9))

    def draw_foundation(self):
        for i in range(4):
            suit = SUITS[i]
            x = self.column_x(3 + i)
            top = self.game.foundation[suit].peek()
            if top is None:
                self.draw_empty(x, TOP_Y, SYMBOLS[suit])
            else:
                self.draw_card(x, TOP_Y, top, False)

    def draw_tableau(self):
        for col in range(7):
            x = self.column_x(col)
            cards = self.game.tableau[col].to_list()
            if len(cards) == 0:
                self.draw_empty(x, TABLEAU_Y, "Empty")
            else:
                positions = self.card_y_positions(cards)
                for index in range(len(cards)):
                    selected = (self.sel_type == "tableau"
                                and self.sel_pile == col
                                and index >= len(cards) - self.sel_count)
                    self.draw_card(x, positions[index], cards[index], selected)

    def draw_win_banner(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        middle = height // 2
        self.canvas.create_rectangle(width // 2 - 280, middle - 70, width // 2 + 280, middle + 70,
                                     fill="#f4d03f", outline="black", width=3)
        self.canvas.create_text(width // 2, middle - 20, text="YOU WON!",
                                fill="black", font=("Arial", 32, "bold"))
        self.canvas.create_text(width // 2, middle + 30,
                                text="Moves: " + str(self.game.history.size)
                                + "   Time: %02d:%02d" % (self.seconds // 60, self.seconds % 60),
                                fill="black", font=("Arial", 14, "bold"))

    def draw_board(self):
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        self.offset = max(0, (width - BOARD_W) // 2)

        self.draw_heading(0, "Stock")
        self.draw_heading(1, "Waste")
        self.draw_heading(3, "Foundation")

        self.draw_stock()
        self.draw_waste()
        self.draw_foundation()
        self.draw_tableau()

        if self.game.is_won():
            self.draw_win_banner()

    def refresh(self):
        self.draw_board()
        self.update_info()
        if self.game.is_won():
            self.message.config(text="Congratulations! All 52 cards are in the foundation.")

    def on_resize(self, event):
        self.draw_board()

    def do_undo(self):
        self.clear_selection()
        if self.game.undo():
            self.message.config(text="Undo done.")
        else:
            self.message.config(text="Nothing to undo.")
        self.refresh()

    def do_redo(self):
        self.clear_selection()
        if self.game.redo():
            self.message.config(text="Redo done.")
        else:
            self.message.config(text="Nothing to redo.")
        self.refresh()

    def do_hint(self):
        self.clear_selection()
        hint = self.game.hint()
        if hint is None:
            self.message.config(text="No moves are left.")
        else:
            self.message.config(text="Hint: " + hint)
        self.refresh()

    def new_game(self):
        self.game = Game()
        self.clear_selection()
        self.seconds = 0
        self.message.config(text="New game started. Click the stock to draw a card.")
        self.refresh()

    def finish_move(self, ok):
        self.clear_selection()
        if ok:
            self.message.config(text="Move done.")
        else:
            self.message.config(text="That move is not allowed.")

    def click_stock(self):
        self.clear_selection()
        if self.game.draw_from_stock():
            self.message.config(text="")
        else:
            self.message.config(text="Stock and waste are both empty.")

    def click_waste(self):
        if self.game.waste.is_empty():
            return
        if self.sel_type == "waste":
            self.clear_selection()
            self.message.config(text="")
        else:
            self.sel_type = "waste"
            self.sel_pile = None
            self.sel_count = 1
            self.message.config(text="Waste card selected. Click a destination.")

    def click_foundation(self):
        if self.sel_type is None:
            self.message.config(text="Select a card first.")
            return
        if self.sel_type == "waste":
            ok = self.game.waste_to_foundation()
        elif self.sel_count == 1:
            ok = self.game.send_to_foundation(self.sel_pile)
        else:
            ok = False
        self.finish_move(ok)

    def click_tableau(self, col, y):
        if self.sel_type is not None and not (self.sel_type == "tableau" and self.sel_pile == col):
            if self.sel_type == "waste":
                ok = self.game.waste_to_tableau(col)
            else:
                ok = self.game.move_cards(self.sel_pile, col, self.sel_count)
            self.finish_move(ok)
            return

        cards = self.game.tableau[col].to_list()
        if len(cards) == 0:
            return

        positions = self.card_y_positions(cards)
        clicked = None
        for index in range(len(cards) - 1, -1, -1):
            if positions[index] <= y <= positions[index] + CARD_H:
                clicked = index
                break

        if clicked is None:
            return

        if not cards[clicked].face_up:
            self.message.config(text="You cannot select a face-down card.")
            return

        count = len(cards) - clicked
        if self.sel_type == "tableau" and self.sel_pile == col and self.sel_count == count:
            self.clear_selection()
            self.message.config(text="")
        else:
            self.sel_type = "tableau"
            self.sel_pile = col
            self.sel_count = count
            self.message.config(text="Cards selected. Click a destination.")

    def on_click(self, event):
        if self.game.is_won():
            return

        if TOP_Y <= event.y <= TOP_Y + CARD_H:
            waste_x = self.column_x(1)
            waste_right = waste_x + CARD_W + (self.waste_shown_count() - 1) * FAN
            if waste_x <= event.x <= waste_right:
                self.click_waste()
            else:
                col = self.column_at(event.x)
                if col == 0:
                    self.click_stock()
                elif col is not None and col >= 3:
                    self.click_foundation()
        elif event.y >= TABLEAU_Y:
            col = self.column_at(event.x)
            if col is not None:
                self.click_tableau(col, event.y)

        self.refresh()


def main():
    root = tk.Tk()
    SolitaireApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()  