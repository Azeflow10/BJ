import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from game.game import BlackjackGame

CARD_PATH = os.path.abspath("assets/cards/")
CARD_BACK_IMAGE = os.path.join(CARD_PATH, "back.png")


class BlackjackInterface:
    def __init__(self, master):
        self.master = master
        self.game = BlackjackGame()

        master.title("Blackjack 21")
        master.geometry("1000x600")
        master.configure(bg="darkgreen")

        self.croupier_card_hidden = True  # Flag pour savoir si la carte du croupier est cachée

        self.setup_ui()

    def setup_ui(self):
        self.balance_label = tk.Label(self.master, text=f"Solde: {self.game.balance}€", font=("Arial", 18), bg="darkgreen", fg="white")
        self.balance_label.pack(pady=10)

        self.bet_entry = tk.Entry(self.master, font=("Arial", 14))
        self.bet_entry.pack()

        self.bet_button = tk.Button(self.master, text="Parier", command=self.place_bet, font=("Arial", 14), bg="yellow")
        self.bet_button.pack(pady=5)

        self.dealer_frame = tk.Frame(self.master, bg="darkgreen")
        self.dealer_frame.pack(pady=20)

        self.player_frame = tk.Frame(self.master, bg="darkgreen")
        self.player_frame.pack(pady=20)

        self.button_frame = tk.Frame(self.master, bg="darkgreen")
        self.button_frame.pack(pady=20)

        self.hit_button = tk.Button(self.button_frame, text="Tirer", command=self.hit, font=("Arial", 14), state="disabled")
        self.hit_button.grid(row=0, column=0, padx=20)

        self.stand_button = tk.Button(self.button_frame, text="Rester", command=self.stand, font=("Arial", 14), state="disabled")
        self.stand_button.grid(row=0, column=1, padx=20)

        self.double_button = tk.Button(self.button_frame, text="Doubler", command=self.double, font=("Arial", 14), state="disabled")
        self.double_button.grid(row=0, column=2, padx=20)

        self.split_button = tk.Button(self.button_frame, text="Séparer", command=self.split, font=("Arial", 14), state="disabled")
        self.split_button.grid(row=0, column=3, padx=20)

        self.new_game_button = tk.Button(self.master, text="Nouvelle Partie", command=self.new_game, font=("Arial", 14), bg="lightblue")
        self.new_game_button.pack(pady=10)

        self.quit_button = tk.Button(self.master, text="Quitter", command=self.quit_game, font=("Arial", 14), bg="red")
        self.quit_button.pack(pady=10)

    def place_bet(self):
        try:
            bet = int(self.bet_entry.get())
            self.game.place_bet(bet)
        except ValueError:
            messagebox.showerror("Erreur", "Mise invalide")
            return

        self.bet_entry.config(state="disabled")
        self.bet_button.config(state="disabled")
        self.hit_button.config(state="normal")
        self.stand_button.config(state="normal")
        self.double_button.config(state="normal")
        if self.game.player.hand[0][0] == self.game.player.hand[1][0]:
            self.split_button.config(state="normal")

        self.game.start_round()
        self.display_cards()

        if self.game.player.hand[0][0] == self.game.player.hand[1][0]:
            self.split_button.config(state="normal")

    def hit(self):
        self.game.player_hit()
        self.display_cards()

        if self.game.player.get_value() > 21:
            self.croupier_card_hidden = False
            self.display_cards()
            self.end_round("Perdu ! Vous avez dépassé 21.")

    def stand(self):
        self.croupier_card_hidden = False
        self.display_cards()

        self.game.dealer_play()
        self.display_cards()

        self.end_round(self.game.evaluate())

    def double(self):
        try:
            self.game.place_bet(self.game.bet)  # Double la mise
            self.game.player_hit()
            self.croupier_card_hidden = False
            self.display_cards()
            self.game.dealer_play()
            self.display_cards()
            self.end_round(self.game.evaluate())
        except ValueError:
            messagebox.showerror("Erreur", "Impossible de doubler.")

    def split(self):
        try:
            if self.game.player.hand[0][0] != self.game.player.hand[1][0]:
                raise ValueError("Vous ne pouvez splitter que des cartes de même valeur.")
            first_card = self.game.player.hand.pop()
            second_card = self.game.player.hand.pop()

            self.split_hand = [first_card]
            self.main_hand = [second_card]

            self.game.player.hand = self.main_hand

            # Pioche une carte pour chaque main
            self.split_hand.append(self.game.deck.draw())
            self.game.player.add_card(self.game.deck.draw())

            self.display_cards()

            self.split_button.config(state="disabled")
            self.double_button.config(state="disabled")

            messagebox.showinfo("Split", "Split effectué. Jouez votre première main.")

        except ValueError as e:
            messagebox.showerror("Erreur", str(e))

    def end_round(self, result):
        if self.croupier_card_hidden:
            self.croupier_card_hidden = False
            self.display_cards()

        self.game.save_score()

        messagebox.showinfo("Résultat", result)
        self.balance_label.config(text=f"Solde: {self.game.balance}€")

        # Désactiver boutons de jeu
        self.hit_button.config(state="disabled")
        self.stand_button.config(state="disabled")

        # Réactiver la saisie de la mise pour rejouer
        self.bet_entry.config(state="normal")
        self.bet_button.config(state="normal")
        self.bet_entry.delete(0, tk.END)

        # Nettoyer les cartes
        self.clear_frames()

        # Réinitialiser la carte cachée
        self.croupier_card_hidden = True

        # Message pour dire "Nouvelle manche !"
        messagebox.showinfo("Nouvelle Manche", "Entrez votre nouvelle mise pour rejouer ! 🎲")

    def new_game(self):
        self.bet_entry.config(state="normal")
        self.bet_button.config(state="normal")
        self.bet_entry.delete(0, tk.END)
        self.clear_frames()
        self.croupier_card_hidden = True

    def quit_game(self):
        self.master.quit()

    def clear_frames(self):
        for frame in (self.player_frame, self.dealer_frame):
            for widget in frame.winfo_children():
                widget.destroy()

    def display_cards(self):
        self.clear_frames()

        # Affichage des cartes du croupier
        for idx, card in enumerate(self.game.dealer.hand):
            if idx == 0 and self.croupier_card_hidden:
                img_path = CARD_BACK_IMAGE
            else:
                img_path = self.get_card_image(card)
            self.display_card(self.dealer_frame, img_path)

        if not self.croupier_card_hidden and self.game.dealer.hand:
            dealer_score = tk.Label(
                self.dealer_frame,
                text=f"Score: {self.game.dealer.get_value()}",
                font=("Arial", 12),
                bg="darkgreen",
                fg="white"
            )
            dealer_score.pack(side="left", padx=20)

        for card in self.game.player.hand:
            img_path = self.get_card_image(card)
            self.display_card(self.player_frame, img_path)

        if self.game.player.hand:
            player_score = tk.Label(
                self.player_frame,
                text=f"Score: {self.game.player.get_value()}",
                font=("Arial", 12),
                bg="darkgreen",
                fg="white"
            )
            player_score.pack(side="left", padx=20)

    def get_card_image(self, card):
        value, suit = card

        value_map = {
            1: "A",
            2: "2",
            3: "3",
            4: "4",
            5: "5",
            6: "6",
            7: "7",
            8: "8",
            9: "9",
            10: "10",
            11: "J",
            12: "Q",
            13: "K"
        }

        suit_map = {
            "HEARTS": "HEARTS",
            "DIAMONDS": "DIAMONDS",
            "CLUBS": "CLUBS",
            "SPADES": "SPADES"
        }

        value_str = value_map.get(value, str(value))
        suit_str = suit_map.get(suit, str(suit))

        return os.path.join(CARD_PATH, f"{value_str}_{suit_str}.png")

    def display_card(self, frame, path):
        if not os.path.exists(path):
            print(f"Erreur : L'image {path} est introuvable.")
            path = CARD_BACK_IMAGE

        try:
            img = Image.open(path).resize((100, 150))
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(frame, image=photo, bg="darkgreen")
            label.image = photo
            label.pack(side="left", padx=10)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")
            label = tk.Label(frame, text="Image non trouvée", bg="darkgreen", fg="white")
            label.pack(side="left", padx=10)
