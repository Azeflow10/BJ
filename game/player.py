class Player:
    def __init__(self, name="Player", balance=1000):
        self.name = name
        self.balance = balance
        self.hand = []  # La main principale du joueur
        self.split_hand = None  # Deuxieme main si on fait un split
        self.bet = 0  # Mise actuelle
        self.split_bet = 0  # Mise pour la main split si y en a une

    def add_card(self, card, split=False):
        # Ajoute une carte a la main principale ou la main split
        if split and self.split_hand is not None:
            self.split_hand.append(card)
        else:
            self.hand.append(card)

    def clear_hand(self):
        # Vide la main du joueur et réinitialise les mise
        self.hand.clear()
        self.split_hand = None
        self.bet = 0
        self.split_bet = 0

    def get_value(self, split=False):
        # Calcule la valleur total d'une main
        hand = self.split_hand if split and self.split_hand else self.hand
        values = {1: 11, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7,
                  8: 8, 9: 9, 10: 10, 11: 10, 12: 10, 13: 10}  # 11 = valet, dame, roi

        total = 0
        aces = 0  # Compte les as

        for card in hand:
            card_value = card[0]
            if card_value in values:
                total += values[card_value]
                if card_value == 1:
                    aces += 1  # Un as compte comme 11 d'abord

        while total > 21 and aces:
            total -= 10  # Si on dépasse 21, on transforme un As en 1
            aces -= 1

        return total

    def can_split(self):
        # Verifie si le joueur peut splitter ses cartes
        return len(self.hand) == 2 and self.hand[0][0] == self.hand[1][0]

    def split(self):
        # Fait le split des cartes
        if self.can_split():
            self.split_hand = [self.hand.pop()]  # Prend une carte pour la deuxieme main
            self.split_bet = self.bet
            return True
        return False

    def double_bet(self):
        # Permet de doubler la mise si le solde est suffisant
        if self.balance >= self.bet:
            self.balance -= self.bet
            self.bet *= 2
            return True
        return False
