import os
import json
from .deck import Deck
from .player import Player
from database.db_manager import DBManager

SCORE_FILE = "data/scores.json"

class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player = Player("Joueur")
        self.dealer = Player("Croupier")
        self.balance = self.load_score()  # Charger le score sauvegardé
        self.bet = 0
        self.current_hand = "main"  # pour gérer split main / main normale

    def load_score(self):
        # Charge le score depuis un fichier json
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, 'r') as f:
                return json.load(f).get("balance", 1000)
        return 1000  # retourne 1000 si aucun fichier n'existe

    def save_score(self):
        # Sauvgarde le score actuelle dans un fichier json
        with open(SCORE_FILE, 'w') as f:
            json.dump({"balance": self.balance}, f)

    def place_bet(self, amount):
        # Permet de faire une mise si elle est valide
        if amount > self.balance or amount <= 0:
            raise ValueError("Mise invalide")
        self.bet = amount
        self.balance -= amount

    def start_round(self):
        # Démmare une nouvelle manche
        self.player.clear_hand()
        self.dealer.clear_hand()
        self.deck.shuffle()
        self.player.add_card(self.deck.draw())
        self.player.add_card(self.deck.draw())
        self.dealer.add_card(self.deck.draw())
        self.dealer.add_card(self.deck.draw())
        self.current_hand = "main"

    def player_hit(self):
        # Le joueur tire une carte suplementaire
        if self.current_hand == "main":
            self.player.add_card(self.deck.draw())
        else:
            self.player.add_card(self.deck.draw(), split=True)

    def player_double(self):
        # Le joueur double sa mise et tire une carte
        if self.player.double_bet():
            self.player_hit()
            return self.stand()
        else:
            raise ValueError("Solde insuffisant pour doubler")

    def player_split(self):
        # Permet au joueur de splitter sa main si possible
        if self.player.can_split():
            if self.balance >= self.bet:
                self.balance -= self.bet
                self.player.split()
                self.player.add_card(self.deck.draw())  # Tire sur la premiere main
                self.player.add_card(self.deck.draw(), split=True)  # Tire sur la deuxieme
                self.current_hand = "main"
            else:
                raise ValueError("Solde insuffisant pour split")
        else:
            raise ValueError("Impossible de séparer ces cartes")

    def stand(self):
        # Arreter de tirer des cartes
        if self.current_hand == "main" and self.player.split_hand:
            self.current_hand = "split"
            return "continue_split"
        else:
            self.dealer_play()
            return self.evaluate()

    def dealer_play(self):
        # Le croupier joue jusqu'a au moin 17
        while self.dealer.get_value() < 17:
            self.dealer.add_card(self.deck.draw())

    def evaluate(self):
        # Evalue la manche et donne le resultat
        results = {}
        player_score = self.player.get_value()
        dealer_score = self.dealer.get_value()

        results['main'] = self.evaluate_hand(player_score, dealer_score, self.bet)

        if self.player.split_hand:
            split_score = self.player.get_value(split=True)
            results['split'] = self.evaluate_hand(split_score, dealer_score, self.player.split_bet)

        self.save_score()
        return results

    def evaluate_hand(self, player_score, dealer_score, bet_amount):
        # Determine le resultat d'une main
        if player_score > 21:
            return "Perdu"
        elif dealer_score > 21 or player_score > dealer_score:
            self.balance += bet_amount * 2
            return "Gagné"
        elif dealer_score == player_score:
            self.balance += bet_amount
            return "Égalité"
        else:
            return "Perdu"
