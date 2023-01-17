#%%
import random

SUITS = ["Hearts", "Diamonds", "Spades", "Clubs"]
RANKS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

class Hand:
    def __init__(self, cards, value):
        self.cards = cards
        self.value = value
        self.options_available = ["Hit", "Stand"]
        self.status = 'Active'
        
    def __str__(self):
        for card in self.cards:
            print(card)
    
    def evaluate(self):
        self.value = 0
        for card in self.cards:
            self.value += card.value
        return self.value
    
    def ace_check(self):
        for card in self.cards:
            if card.rank == "Ace" and self.value > 21:
                card.value = 1
                self.value -= 10
        return self.value
    
    def is_blackjack(self):
        if self.value == 21 and len(self.cards) == 2:
            self.status = "Blackjack"
            return True
        else:
            return False
        
    def is_splitable(self):
        if self.cards[0].rank == self.cards[1].rank:
            return True
        else:
            return False
        
    def is_bust(self):
        if self.ace_check() > 21:            
            self.status = "Bust"
            return True
        else:
            return False
    
    def hit(self, deck):
        self.cards.append(deck.cards.pop())
        self.evaluate()
        self.ace_check()
        return self.cards
    
    def stand(self):
        self.status = "Stand"
        return self.status
    
    def update_options(self):
        if self.is_blackjack() or self.is_bust():
            self.options_available = []
        elif self.is_splitable():
            self.options_available.append("Split")
        return self.options_available
    
    
class Card:
    def __init__(self, suit, rank, value):
        self.suit = suit
        self.rank = rank
        self.value = value
        
    def __str__(self):
        return str(self.rank) + " of " + str(self.suit)


class Deck:
    def __init__(self, number_of_decks):
        self.number_of_decks = number_of_decks
        self.cards = []
        self.build()
        
    def __str__(self):
        for card in self.cards:
            print(card)
        
    def build(self):
        for _ in range(self.number_of_decks):
            for suit in SUITS:
                for rank in RANKS:
                    if rank.isdigit():
                        self.cards.append(Card(suit, rank, int(rank)))
                    elif rank == "Ace":
                        self.cards.append(Card(suit, rank, 11))
                    else:
                        self.cards.append(Card(suit, rank, 10))
                    
    def shuffle(self):
        random.shuffle(self.cards)
                    


deck = Deck(2)
deck.shuffle()

for _ in range(2):
    player_hands = [Hand([deck.cards.pop(), deck.cards.pop()], 0)]
    dealer_hand = Hand([deck.cards.pop(), deck.cards.pop()], 0)
    
    for hand in player_hands:
        print('-'*50)
        print("Your hand: ", hand)
        print("Your hand value: ", hand.evaluate())
        print("Dealer's 1st card: ", dealer_hand.cards[0])
        if hand.is_blackjack():
            print("Blackjack!")
            continue
        else:
            while hand.status == "Active":
                hand.evaluate()
                if hand.is_bust():
                    print("Bust!")
                    continue
                hand.update_options()
                print("Options: ", hand.options_available)
                choice = random.choice(hand.options_available)
                if choice == "Hit":
                    hand.hit(deck)
                elif choice == "Stand":
                    hand.stand()
                else:
                    print("Invalid input")
                    continue
    if dealer_hand.is_blackjack():
            print("Dealer has blackjack!")
    else:
        while dealer_hand.status == "Active":
            dealer_hand.evaluate()
            if dealer_hand.is_bust():
                print("Dealer busts!")
                continue
            elif dealer_hand.value < 17:
                dealer_hand.hit(deck)
            else:
                dealer_hand.stand()
    
    

print('END OF PROGRAM')

# %%
