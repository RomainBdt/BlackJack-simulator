#%%
import random
import pandas as pd
from tqdm import trange

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
    
    def is_soft_17(self):
        if self.value == 17:
            for card in self.cards:
                if card.rank == "Ace" and card.value == 11:
                    return True
        return False
    
    
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
                    

n_decks = 8
deck = Deck(n_decks)
deck.shuffle()
results = []
VERBOSE = False
invalid = []
hit_on_soft_17 = True
cum_gain = 0

for _ in trange(100000):
    print('-'*50) if VERBOSE else None
    player_hands = [Hand([deck.cards.pop(), deck.cards.pop()], 0)]
    dealer_hand = Hand([deck.cards.pop(), deck.cards.pop()], 0)
    
    # Player's turn
    for i, hand in enumerate(player_hands):    
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
            print("Your hand: ", hand) if VERBOSE else None
            print("Your hand value: ", hand.evaluate()) if VERBOSE else hand.evaluate()

    # Dealer's turn
    dealer_hand.evaluate()
    dealer_hand.ace_check()
    if dealer_hand.is_blackjack():
            print("Dealer has blackjack!") if VERBOSE else None
    else:
        while dealer_hand.status == "Active":
            dealer_hand.evaluate()
            if dealer_hand.is_bust():
                print("Dealer busts!") if VERBOSE else None
            elif dealer_hand.value < 17:
                dealer_hand.hit(deck)
            elif hit_on_soft_17 and dealer_hand.is_soft_17():
                print("Dealer hits on soft 17") if VERBOSE else None
                dealer_hand.hit(deck)
            else:
                dealer_hand.stand()
        print("Dealer's hand: ", dealer_hand) if VERBOSE else None
        
    # Results
    cum_split_gain = 0
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
        elif dealer_hand.status == "Bust":
            gain = 1
            print("You win!") if VERBOSE else None
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
            hand_value_hit = hand_value - hand.cards[-1].value
            results.append((hand_value_hit, "Hit", dealer_hand.cards[0].value, gain))  # when status == Stand, add into the results the hand value before drawing the last card
        else:
            print("Invalid input")
                    
        print("Results player:", hand, hand_value, hand_status, gain) if VERBOSE else None
        print("Results dealer:", dealer_hand, dealer_hand.value, dealer_hand.status) if VERBOSE else None 
        results.append((hand_value, hand_status, dealer_hand.cards[0].value, gain))
        cum_gain += gain
        cum_bet += 1
        
        # Count split gains
        if len(player_hands) > 1:
            cum_split_gain += gain
        
    # Count split gains
    if len(player_hands) > 1:
        hand_value = 2 * player_hands[0].cards[0].value
        hand_status = "Split"
        hand = player_hands[0]
        print('Split results') if VERBOSE else None
        print("Results player:", hand, hand_value, hand_status, cum_split_gain / len(player_hands)) if VERBOSE else None
        print("Results dealer:", dealer_hand, dealer_hand.value, dealer_hand.status) if VERBOSE else None 
        results.append((hand_value, hand_status, dealer_hand.cards[0].value, cum_split_gain / len(player_hands)))
 
    # Check if deck needs to be reshuffled 
    if len(deck.cards) < 52 * n_decks // 2:
        deck = Deck(n_decks)
        deck.shuffle()

# Format and export results
df = pd.DataFrame(results, columns = ['Hand Value', 'Hand Status', 'Dealer Card', 'Gain'])
group = df.groupby(['Hand Value', 'Hand Status', 'Dealer Card']).mean()
group.to_csv('results.csv')

group_cnt = df.groupby(['Hand Value', 'Hand Status', 'Dealer Card']).count()

print('Cumulative gain:', cum_gain)
print('END OF PROGRAM')
# %%
