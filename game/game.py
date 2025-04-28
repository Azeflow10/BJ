import os
from .deck import Deck
from .player import Player
from database.db_manager import DBManager

class BlackjackGame:
    def __init__(self):
        self.db = DBManager()  # Connexion à la base de données
        self.deck = Deck()
        self.player = Player("Joueur")
        self.dealer = Player("Croupier")
        
        # Charger le score et le highscore du joueur depuis la base de données
        player_data = self.db.get_player(self.player.name)
        if player_data:
            self.balance, _ = player_data
        else:
            self.db.create_player(self.player.name)  # Si le joueur n'existe pas, le créer
            self.balance = 1000  # Solde initial par défaut
        
        self.bet = 0
        self.current_hand = "main"  # pour gérer split main / main normale

    def save_score(self):
        # Sauvegarde du score actuel dans la base de données
        _, highscore = self.db.get_player(self.player.name)
        
        # Si le solde actuel est supérieur au highscore, on met à jour
        if self.balance > highscore:
            highscore = self.balance
        
        self.db.update_player(self.player.name, self.balance, highscore)

    def place_bet(self, amount):
        # Permet de faire une mise si elle est valide
        if amount > self.balance or amount <= 0:
            raise ValueError("Mise invalide")
        self.bet = amount
        self.balance -= amount

    def start_round(self):
        # Démarre une nouvelle manche
        self.player.clear_hand()
        self.dealer.clear_hand()
        self.deck.shuffle()
        self.player.add_card(self.deck.draw())
        self.player.add_card(self.deck.draw())
        self.dealer.add_card(self.deck.draw())
        self.dealer.add_card(self.deck.draw())
        self.current_hand = "main"

    def player_hit(self):
        # Le joueur tire une carte supplémentaire
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
                self.player.add_card(self.deck.draw())  # Tire sur la première main
                self.player.add_card(self.deck.draw(), split=True)  # Tire sur la deuxième main
                self.current_hand = "main"
            else:
                raise ValueError("Solde insuffisant pour split")
        else:
            raise ValueError("Impossible de séparer ces cartes")

    def stand(self):
        # Arrêter de tirer des cartes
        if self.current_hand == "main" and self.player.split_hand:
            self.current_hand = "split"
            return "continue_split"
        else:
            self.dealer_play()
            return self.evaluate()

    def dealer_play(self):
        # Le croupier joue jusqu'à atteindre au moins 17
        while self.dealer.get_value() < 17:
            self.dealer.add_card(self.deck.draw())

    def evaluate(self):
        # Évalue la manche et donne le résultat
        results = {}
        player_score = self.player.get_value()
        dealer_score = self.dealer.get_value()

        results['main'] = self.evaluate_hand(player_score, dealer_score, self.bet)

        if self.player.split_hand:
            split_score = self.player.get_value(split=True)
            results['split'] = self.evaluate_hand(split_score, dealer_score, self.player.split_bet)

        self.save_score()  # Sauvegarde les scores après la manche
        return results

    def evaluate_hand(self, player_score, dealer_score, bet_amount):
        # Détermine le résultat d'une main
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
