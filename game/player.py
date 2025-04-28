class Player:
    def __init__(self, name="Player", balance=1000):
        self.name = name
        self.balance = balance
        self.hand = []
        self.split_hand = None
        self.bet = 0
        self.split_bet = 0

    def add_card(self, card, split=False):
        if split and self.split_hand is not None:
            self.split_hand.append(card)
        else:
            self.hand.append(card)

    def clear_hand(self):
        self.hand.clear()
        self.split_hand = None
        self.bet = 0
        self.split_bet = 0

    def get_value(self, split=False):
        hand = self.split_hand if split and self.split_hand else self.hand
        values = {1: 11, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7,
                  8: 8, 9: 9, 10: 10, 11: 10, 12: 10, 13: 10}

        total = 0
        aces = 0

        for card in hand:
            card_value = card[0]
            if card_value in values:
                total += values[card_value]
                if card_value == 1:
                    aces += 1

        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    def can_split(self):
        return len(self.hand) == 2 and self.hand[0][0] == self.hand[1][0]

    def split(self):
        if self.can_split():
            self.split_hand = [self.hand.pop()]
            self.split_bet = self.bet
            return True
        return False

    def double_bet(self):
        if self.balance >= self.bet:
            self.balance -= self.bet
            self.bet *= 2
            return True
        return False
