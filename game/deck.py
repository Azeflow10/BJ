import numpy as np
import os
import random

class Deck:
    def __init__(self):
        # Création du deck avec des cartes représentées par (valeur, symbole)
        self.cards = [(v, s) for v in range(1, 14) for s in ['S', 'H', 'D', 'C']]
        self.shuffle()  # Mélanger les cartes lors de la création du deck

    def shuffle(self):
        # Mélanger les cartes en utilisant numpy
        np.random.shuffle(self.cards)

    def draw(self):
        # Tirer une carte, si le deck est vide, réinitialiser le deck
        if not self.cards:
            self.__init__()  # Réinitialise le deck s'il est vide
        return self.cards.pop()  # Retirer et retourner la dernière carte du deck
