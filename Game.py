from Cards import Card, create_shuffled_deck
from Tableau import (
    Stack,
    create_tableau,
    create_foundation,
    deal_tableau,
    can_place_on_tableau,
    can_place_on_foundation,
    move_tableau_to_tableau,
    move_tableau_to_foundation,
    print_tableau,
    print_foundation,
)


def turn_face_up(card):
    card.face_up = True


def turn_face_down(card):
    card.face_up = False


class Move:
    def __init__(self, kind, source=None, destination=None, count=1, flipped=False):
        self.kind = kind
        self.source = source
        self.destination = destination
        self.count = count
        self.flipped = flipped


class Game:
    def __init__(self, deck=None):
        if deck is None:
            deck = create_shuffled_deck()

        self.tableau = create_tableau()
        self.foundation = create_foundation()
        self.stock = Stack()
        self.waste = Stack()
        self.history = Stack()
        self.redo_stack = Stack()

        deal_tableau(self.tableau, deck)
        for card in deck:
            self.stock.push(card)

    def valid_pile_number(self, index):
        return index >= 0 and index <= 6

    def clear_redo(self):
        self.redo_stack = Stack()

    def can_move_tableau_to_tableau(self, from_index, to_index, count=1):
        if not self.valid_pile_number(from_index):
            return False
        if not self.valid_pile_number(to_index):
            return False
        if from_index == to_index:
            return False

        source = self.tableau[from_index]
        if count < 1 or count > source.size:
            return False

        moving = source.top_cards(count)
        for card in moving:
            if not card.face_up:
                return False

        return can_place_on_tableau(moving[-1], self.tableau[to_index])

    def can_move_tableau_to_foundation(self, from_index):
        if not self.valid_pile_number(from_index):
            return False

        card = self.tableau[from_index].peek()
        if card is None or not card.face_up:
            return False

        return can_place_on_foundation(card, self.foundation[card.suit])

    def can_move_waste_to_tableau(self, to_index):
        if not self.valid_pile_number(to_index):
            return False

        card = self.waste.peek()
        if card is None:
            return False

        return can_place_on_tableau(card, self.tableau[to_index])

    def can_move_waste_to_foundation(self):
        card = self.waste.peek()
        if card is None:
            return False

        return can_place_on_foundation(card, self.foundation[card.suit])

    def will_flip_card(self, from_index, count):
        source = self.tableau[from_index]
        if source.size <= count:
            return False
        card_below = source.top_cards(count + 1)[-1]
        return not card_below.face_up

    def face_up_count(self, index):
        total = 0
        for card in self.tableau[index].to_list():
            if card.face_up:
                total = total + 1
        return total

    def move_cards(self, from_index, to_index, count=1):
        if not self.can_move_tableau_to_tableau(from_index, to_index, count):
            return False

        flipped = self.will_flip_card(from_index, count)
        move_tableau_to_tableau(self.tableau, from_index, to_index, count)
        self.history.push(Move("tableau_to_tableau", from_index, to_index, count, flipped))
        self.clear_redo()
        return True

    def send_to_foundation(self, from_index):
        if not self.can_move_tableau_to_foundation(from_index):
            return False

        card = self.tableau[from_index].peek()
        flipped = self.will_flip_card(from_index, 1)
        move_tableau_to_foundation(self.tableau, self.foundation, from_index)
        self.history.push(Move("tableau_to_foundation", from_index, card.suit, 1, flipped))
        self.clear_redo()
        return True

    def waste_to_tableau(self, to_index):
        if not self.can_move_waste_to_tableau(to_index):
            return False

        card = self.waste.pop()
        self.tableau[to_index].push(card)
        self.history.push(Move("waste_to_tableau", None, to_index))
        self.clear_redo()
        return True

    def waste_to_foundation(self):
        if not self.can_move_waste_to_foundation():
            return False

        card = self.waste.pop()
        self.foundation[card.suit].push(card)
        self.history.push(Move("waste_to_foundation", None, card.suit))
        self.clear_redo()
        return True

    def draw_from_stock(self):
        if not self.stock.is_empty():
            card = self.stock.pop()
            turn_face_up(card)
            self.waste.push(card)
            self.history.push(Move("draw"))
            self.clear_redo()
            return True

        if not self.waste.is_empty():
            count = self.waste.size
            while not self.waste.is_empty():
                card = self.waste.pop()
                turn_face_down(card)
                self.stock.push(card)
            self.history.push(Move("recycle", None, None, count))
            self.clear_redo()
            return True

        return False

    def undo(self):
        move = self.history.pop()
        if move is None:
            return False

        if move.kind == "draw":
            card = self.waste.pop()
            turn_face_down(card)
            self.stock.push(card)

        elif move.kind == "recycle":
            while not self.stock.is_empty():
                card = self.stock.pop()
                turn_face_up(card)
                self.waste.push(card)

        elif move.kind == "waste_to_tableau":
            card = self.tableau[move.destination].pop()
            self.waste.push(card)

        elif move.kind == "waste_to_foundation":
            card = self.foundation[move.destination].pop()
            self.waste.push(card)

        elif move.kind == "tableau_to_foundation":
            card = self.foundation[move.destination].pop()
            if move.flipped:
                turn_face_down(self.tableau[move.source].peek())
            self.tableau[move.source].push(card)

        elif move.kind == "tableau_to_tableau":
            source = self.tableau[move.source]
            destination = self.tableau[move.destination]
            if move.flipped:
                turn_face_down(source.peek())
            temp = []
            for i in range(move.count):
                temp.append(destination.pop())
            temp.reverse()
            for card in temp:
                source.push(card)

        self.redo_stack.push(move)
        return True

    def redo(self):
        move = self.redo_stack.pop()
        if move is None:
            return False

        if move.kind == "draw":
            card = self.stock.pop()
            turn_face_up(card)
            self.waste.push(card)

        elif move.kind == "recycle":
            while not self.waste.is_empty():
                card = self.waste.pop()
                turn_face_down(card)
                self.stock.push(card)

        elif move.kind == "waste_to_tableau":
            card = self.waste.pop()
            self.tableau[move.destination].push(card)

        elif move.kind == "waste_to_foundation":
            card = self.waste.pop()
            self.foundation[move.destination].push(card)

        elif move.kind == "tableau_to_foundation":
            move_tableau_to_foundation(self.tableau, self.foundation, move.source)

        elif move.kind == "tableau_to_tableau":
            move_tableau_to_tableau(self.tableau, move.source, move.destination, move.count)

        self.history.push(move)
        return True

    def is_won(self):
        for suit in self.foundation:
            if self.foundation[suit].size != 13:
                return False
        return True

    def hint(self):
        if self.can_move_waste_to_foundation():
            card = self.waste.peek()
            return "Move " + str(card) + " from the waste to the foundation."

        for i in range(7):
            if self.can_move_tableau_to_foundation(i):
                card = self.tableau[i].peek()
                return "Move " + str(card) + " from column " + str(i + 1) + " to the foundation."

        for i in range(7):
            if self.can_move_waste_to_tableau(i):
                card = self.waste.peek()
                return "Move " + str(card) + " from the waste to column " + str(i + 1) + "."

        for i in range(7):
            source = self.tableau[i]
            for j in range(7):
                for count in range(1, self.face_up_count(i) + 1):
                    if not self.can_move_tableau_to_tableau(i, j, count):
                        continue
                    flips = self.will_flip_card(i, count)
                    empties = count == source.size and not self.tableau[j].is_empty()
                    if flips or empties:
                        card = source.top_cards(count)[-1]
                        return ("Move " + str(card) + " from column " + str(i + 1)
                                + " to column " + str(j + 1) + ".")

        if not self.stock.is_empty():
            return "Draw a card from the stock."

        if not self.waste.is_empty():
            return "Click the stock to turn the waste pile over again."

        return None

    def show(self):
        print_tableau(self.tableau)
        print_foundation(self.foundation)
        print("--- Stock and Waste ---")
        print("Cards in stock:", self.stock.size)
        top = self.waste.peek()
        if top is None:
            print("Waste: empty")
        else:
            print("Top card of waste:", top, "| cards =", self.waste.size)


def demo_draw_and_undo():
    game = Game()
    print("At the start:")
    game.show()

    print()
    print("Drawing 3 cards from the stock:")
    game.draw_from_stock()
    game.draw_from_stock()
    game.draw_from_stock()
    print("Stock:", game.stock.size, "| Waste:", game.waste.size)

    print()
    print("Undoing 3 times:")
    game.undo()
    game.undo()
    game.undo()
    print("Stock:", game.stock.size, "| Waste:", game.waste.size)

    print()
    print("Redoing 2 times:")
    game.redo()
    game.redo()
    print("Stock:", game.stock.size, "| Waste:", game.waste.size)

    print()
    print("Hint:", game.hint())
    print("Won?", game.is_won())


def demo_moves_and_undo():
    game = Game()
    game.tableau = create_tableau()
    game.foundation = create_foundation()

    game.tableau[0].push(Card("Clubs", "3", False))
    game.tableau[0].push(Card("Hearts", "A", True))
    game.tableau[1].push(Card("Diamonds", "9", True))
    game.tableau[1].push(Card("Clubs", "8", True))
    game.tableau[2].push(Card("Spades", "10", True))

    print_tableau(game.tableau)
    print()

    print("Test 1: move to pile 99 (should be False):", game.move_cards(0, 99))
    print("Test 2: empty pile 5 to foundation (should be False):", game.can_move_tableau_to_foundation(5))
    print("Test 3: A of Hearts to foundation (should be True):", game.send_to_foundation(0))
    print("        Is 3 of Clubs face-up now?", game.tableau[0].peek().face_up)
    print("Test 4: move 9D and 8C onto 10S (should be True):", game.move_cards(1, 2, 2))
    print("Test 5: move 3 of Clubs onto 10S (should be False):", game.move_cards(0, 2, 1))

    print()
    print_tableau(game.tableau)

    print()
    print("Undoing 2 times:")
    print(game.undo())
    print(game.undo())
    print("        Is 3 of Clubs face-down again?", not game.tableau[0].to_list()[0].face_up)

    print()
    print("Redoing 2 times:")
    print(game.redo())
    print(game.redo())
    print("        Is 3 of Clubs face-up again?", game.tableau[0].peek().face_up)
    print("Nothing left to redo:", game.redo())

    print()
    print("Undo 2 times and make a new move (redo should be cleared):")
    game.undo()
    game.undo()
    game.send_to_foundation(0)
    print("Redo after a new move (should be False):", game.redo())

    print()
    print_tableau(game.tableau)


if __name__ == "__main__":
    print("===== Draw, Undo and Redo =====")
    demo_draw_and_undo()
    print()
    print("===== Moves, Flip, Undo and Redo =====")
    demo_moves_and_undo()