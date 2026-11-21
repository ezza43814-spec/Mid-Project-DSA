import random


class Card:
    def __init__(self, suit, rank, face_up=False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up

    def __str__(self):
        return self.rank + " of " + self.suit


def create_shuffled_deck():
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    deck = []
    for suit in suits:
        for rank in ranks:
            deck.append(Card(suit, rank))

    random.shuffle(deck)
    return deck


if __name__ == "__main__":
    deck = create_shuffled_deck()
    print("Total cards:", len(deck))
    for card in deck:
        print(card)