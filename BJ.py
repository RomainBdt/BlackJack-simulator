#%%
import random
import pandas as pd

SUITS = ["Hearts", "Diamonds", "Spades", "Clubs"]
RANKS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

class Hand:
    def __init__(self, cards, value):
        self.cards = cards
        self.value = value
        self.options_available = ["Hit", "Stand"]
        self.status = 'Active'
        self.from_split = False
        
    def __str__(self):
        lst = []
        for card in self.cards:
            lst.append(str(card))
        return (' / '.join(lst))
    
    def evaluate(self):
        self.value = 0
        for card in self.cards:
            self.value += card.value
        if self.value > 21:
            self.ace_check()
            self.is_bust()
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
        if self.value > 21:            
            self.status = "Bust"
            return True
        else:
            return False
    
    def hit(self, deck):
        self.cards.append(deck.cards.pop())
        return self.cards
    
    def stand(self):
        self.status = "Stand"
        return self.status
    
    def split(self):
        if self.is_splitable():
            # re initialize self
            new_hand = Hand([self.cards[1], deck.cards.pop()], 0)
            new_hand.from_split = True
            self.__init__([self.cards[0], deck.cards.pop()], 0)
            self.from_split = True
            return new_hand
        else:
            print("Cannot split")
            return None
    
    def update_options(self):
        if self.is_blackjack() or self.is_bust():
            self.options_available = []
        elif self.is_splitable() and len(self.cards) == 2:
            self.options_available.append("Split")
        elif "Split" in self.options_available:
            self.options_available.remove("Split")
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
                    


deck = Deck(8)
deck.shuffle()
results = []
VERBOSE = False
invalid = []

for _ in range(100000):
    player_hands = [Hand([deck.cards.pop(), deck.cards.pop()], 0)]
    dealer_hand = Hand([deck.cards.pop(), deck.cards.pop()], 0)
    
    # Player's turn
    for i, hand in enumerate(player_hands):
        print('-'*50) if VERBOSE else None
        print("Your hand: ", hand) if VERBOSE else None
        print("Your hand value: ", hand.evaluate()) if VERBOSE else hand.evaluate()
        print("Dealer's 1st card: ", dealer_hand.cards[0]) if VERBOSE else None
        
        while hand.status == "Active":            
            if hand.is_blackjack():
                print("Blackjack!") if VERBOSE else None
            elif hand.is_bust():
                print("Bust!") if VERBOSE else None
            else:
                hand.update_options()
                print("Options: ", hand.options_available) if VERBOSE else None
                choice = random.choice(hand.options_available)
                print("Choice: ", choice) if VERBOSE else None
                if choice == "Hit":
                    hand.hit(deck)
                elif choice == "Stand":
                    hand.stand()
                elif choice == "Split":
                    player_hands.append(hand.split())
                    print("Split!") if VERBOSE else None
                else:
                    print("Invalid input")
                    invalid.append((hand, choice))
                    continue
            print("Your hand: ", hand) if VERBOSE else None
            print("Your hand value: ", hand.evaluate()) if VERBOSE else hand.evaluate()

    # Dealer's turn
    if dealer_hand.is_blackjack():
            print("Dealer has blackjack!") if VERBOSE else None
    else:
        while dealer_hand.status == "Active":
            dealer_hand.evaluate()
            if dealer_hand.is_bust():
                print("Dealer busts!") if VERBOSE else None
                continue
            elif dealer_hand.value < 17:
                dealer_hand.hit(deck)
            else:
                dealer_hand.stand()
        print("Dealer's hand: ", dealer_hand) if VERBOSE else None
        
    # Results
    for hand in player_hands:
        hand_value = hand.value
        hand_status = hand.status
            
        if hand.status == "Bust":
            gain = -1
            hand_value -= hand.cards[-1].value
            hand_status = "Hit"
            print("You lose!") if VERBOSE else None
        elif hand.status == "Blackjack":
            if dealer_hand.status == "Blackjack":
                gain = 0
                print("Push!") if VERBOSE else None
            else:
                gain = 1.5
                print("You win!") if VERBOSE else None
        elif dealer_hand.status == "Blackjack":
            gain = -1
            print("You lose!") if VERBOSE else None
        elif hand.status == "Stand":
            if hand.value > dealer_hand.value:
                gain = 1
                print("You win!") if VERBOSE else None
            elif hand.value == dealer_hand.value:
                gain = 0
                print("Push!") if VERBOSE else None
            else:
                gain = -1
                print("You lose!") if VERBOSE else None
        else:
            print("Invalid input")
                    
        results.append((hand_value, hand_status, dealer_hand.cards[0].value, gain))

        if hand.from_split:
            hand_value = 2 * hand.cards[0].value
            hand_status = "Split"
            gain /= 2
            results.append((hand_value, hand_status, dealer_hand.cards[0].value, gain))
 
    # Check if deck needs to be reshuffled 
    if len(deck.cards) < 52 * 4:
        deck = Deck(2)
        deck.shuffle()

print('END OF PROGRAM')

df = pd.DataFrame(results, columns = ['Hand Value', 'Hand Status', 'Dealer Card', 'Gain'])

group = df.groupby(['Hand Value', 'Hand Status', 'Dealer Card']).mean()
group.to_csv('results.csv')

# %%
