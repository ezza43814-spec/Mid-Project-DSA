from Cards import Card, create_shuffled_deck


def rank_value(card):
    if card.rank == "A":
        return 1
    elif card.rank == "J":
        return 11
    elif card.rank == "Q":
        return 12
    elif card.rank == "K":
        return 13
    else:
        return int(card.rank)


def is_red(card):
    return card.suit == "Hearts" or card.suit == "Diamonds"


class Node:
    def __init__(self, card):
        self.card = card
        self.next = None


class Stack:
    def __init__(self):
        self.top = None
        self.size = 0

    def is_empty(self):
        return self.top is None

    def push(self, card):
        new_node = Node(card)
        new_node.next = self.top
        self.top = new_node
        self.size = self.size + 1

    def pop(self):
        if self.is_empty():
            return None
        card = self.top.card
        self.top = self.top.next
        self.size = self.size - 1
        return card

    def peek(self):
        if self.is_empty():
            return None
        return self.top.card

    def top_cards(self, count):
        cards = []
        current = self.top
        while current is not None and len(cards) < count:
            cards.append(current.card)
            current = current.next
        return cards

    def to_list(self):
        cards = []
        current = self.top
        while current is not None:
            cards.append(current.card)
            current = current.next
        cards.reverse()
        return cards


def create_tableau():
    tableau = []
    for i in range(7):
        tableau.append(Stack())
    return tableau


def create_foundation():
    foundation = {}
    for suit in ["Hearts", "Diamonds", "Clubs", "Spades"]:
        foundation[suit] = Stack()
    return foundation


def deal_tableau(tableau, deck):
    for i in range(7):
        for j in range(i + 1):
            card = deck.pop()
            if j == i:
                card.face_up = True
            tableau[i].push(card)


def can_place_on_tableau(card, pile):
    if pile.is_empty():
        return card.rank == "K"
    top = pile.peek()
    if not top.face_up:
        return False
    different_color = is_red(card) != is_red(top)
    one_lower = rank_value(card) == rank_value(top) - 1
    return different_color and one_lower


def can_place_on_foundation(card, pile):
    if pile.is_empty():
        return card.rank == "A"
    top = pile.peek()
    same_suit = card.suit == top.suit
    one_higher = rank_value(card) == rank_value(top) + 1
    return same_suit and one_higher


def flip_top_card(pile):
    if not pile.is_empty():
        pile.peek().face_up = True


def move_tableau_to_foundation(tableau, foundation, from_index):
    source = tableau[from_index]
    if source.is_empty():
        return False

    card = source.peek()
    if not card.face_up:
        return False

    destination = foundation[card.suit]
    if not can_place_on_foundation(card, destination):
        return False

    source.pop()
    destination.push(card)
    flip_top_card(source)
    return True


def move_tableau_to_tableau(tableau, from_index, to_index, count=1):
    if from_index == to_index:
        return False

    source = tableau[from_index]
    destination = tableau[to_index]

    if count < 1 or count > source.size:
        return False

    moving = source.top_cards(count)

    for card in moving:
        if not card.face_up:
            return False

    bottom_card = moving[-1]
    if not can_place_on_tableau(bottom_card, destination):
        return False

    temp = []
    for i in range(count):
        temp.append(source.pop())
    temp.reverse()
    for card in temp:
        destination.push(card)

    flip_top_card(source)
    return True


def card_text(card):
    if card.face_up:
        return str(card)
    return "[?]"


def print_tableau(tableau):
    print("--- Tableau ---")
    for i in range(7):
        names = []
        for card in tableau[i].to_list():
            names.append(card_text(card))
        if len(names) == 0:
            print("Pile", i, ": (empty)")
        else:
            print("Pile", i, ":", ", ".join(names))


def print_foundation(foundation):
    print("--- Foundation ---")
    for suit in foundation:
        pile = foundation[suit]
        if pile.is_empty():
            print(suit, ": empty")
        else:
            print(suit, ": top =", pile.peek(), "| cards =", pile.size)


def test_moves():
    tableau = create_tableau()
    foundation = create_foundation()

    tableau[0].push(Card("Clubs", "3", False))
    tableau[0].push(Card("Hearts", "A", True))
    tableau[1].push(Card("Diamonds", "9", True))
    tableau[1].push(Card("Clubs", "8", True))
    tableau[2].push(Card("Spades", "10", True))
    tableau[3].push(Card("Hearts", "K", True))

    print_tableau(tableau)
    print()

    print("Test 1: A of Hearts ko foundation mein bhejna (True hona chahiye)")
    print(move_tableau_to_foundation(tableau, foundation, 0))

    print("Test 2: Pile 1 ki 2 cards (9D, 8C) ko pile 2 (10S) par rakhna (True)")
    print(move_tableau_to_tableau(tableau, 1, 2, 2))

    print("Test 3: 3 of Clubs ko pile 2 par rakhna (False, kyunke rank ghalat hai)")
    print(move_tableau_to_tableau(tableau, 0, 2, 1))

    print("Test 4: K of Hearts ko khali pile 1 mein rakhna (True)")
    print(move_tableau_to_tableau(tableau, 3, 1, 1))

    print()
    print_tableau(tableau)
    print_foundation(foundation)


if __name__ == "__main__":
    print("===== Asli shuffled deck se tableau deal karna =====")
    deck = create_shuffled_deck()
    tableau = create_tableau()
    foundation = create_foundation()

    deal_tableau(tableau, deck)
    print_tableau(tableau)
    print()
    print_foundation(foundation)
    print()
    print("Deck mein bachi hui cards:", len(deck))

    print()
    print("===== Move functions ka test =====")
    test_moves()