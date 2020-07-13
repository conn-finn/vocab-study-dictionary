import bisect
import re
import os

class Dictionary:

    CAPITALS = re.compile("[A-Z]")
    PUNCTUATION = re.compile("[.!?]")
    MAGOOSH_DIFFICULTIES = ["Unknown", "Common", "Basic", "Advanced", "Unknown"] # 3 levels of "difficulty" for the magoosh vocab list

    # - filename is the text file containing the vocabulary words, as well as their definitions and examples (if existent)
    # each line of the file follows the following form: "word: definition ([a-z]+) example ([A-Z].*\.)"
    # - allowDuplicates is a boolean which controls whether the dictionary will accept the same word multiple times 
    # if there are multiple definitions or sources for it
    # - blacklist_file is a text file which contains the words seperated by spaces that should not be stored in the dictionary(ie words that have been "mastered" already)
    def __init__(self, filename="", allowDuplicates=False, blacklist_file=""):
        self.deck = set([])
        self.orderedDeck = []
        self.allowDuplicates = allowDuplicates
        self.blacklisted_words = []
        if blacklist_file:
            self.add_blacklisted_words(blacklist_file)
        if filename: self.add_from_file(filename)

    def add_blacklisted_words(self, filename):
        if not os.path.exists(filename): return
        with open(filename, 'r') as f:
            self.blacklisted_words.extend([word for line in f for word in line.split()])

    def in_blacklist(self, word):
        return any(word.word == elt for elt in self.blacklisted_words)

    def contains_word(self, word):
        return any(word.word == elt.word for elt in self.orderedDeck)

    # returns true if word was successfully added
    def add_word(self, newWord):
        if (not self.allowDuplicates and self.contains_word(newWord)) or self.in_blacklist(newWord): return False
        self.deck.add(newWord)
        bisect.insort(self.orderedDeck, newWord)
        return True

    def remove_word(self, word):
        self.deck.discard(word)
        self.orderedDeck.remove(word)

    def size(self):
        return len(self.orderedDeck)

    def add_words(self, word_list):
        for word in word_list:
            self.add_word(word)

    def add_from_file(self, filename):
        f = open(filename, "r")
        difficulty_counter = 0
        total_counter = 0
        text = f.read()
        for dif in text.split("Words"):
            for line in self.PUNCTUATION.split(dif):
                word_list = line.split()
                if len(word_list) < 1: continue
                word = word_list[0]
                if len(word) < 3: continue
                rest = line[len(word) + 1:]
                definition = self.CAPITALS.split(rest)[0]
                exampleStart = len(word) + len(definition) + 1
                example = line[exampleStart:]
                if word and definition and example:
                    vocab = VocabWord(word, definition, example, self.MAGOOSH_DIFFICULTIES[difficulty_counter])
                    if self.add_word(vocab): total_counter += 1
            difficulty_counter += 1
        print(f'added {total_counter} words to dictionary')
        f.close()

    def create_html(self, filename, random=True, stylesheet="card_grid_stylesheet.css"):
        if os.path.exists(filename):
            # used to overwrite content if the file already exists
            with open(filename, 'r') as f:
                f.read()
        with open(filename, 'w') as f:
            boilerplateHTML = [f'<html><head><link rel="stylesheet" href="{stylesheet}"></head><body>', f'</body></html>']
                
            f.write(boilerplateHTML[0])
            f.write(f'<div id="content">')

            deck = self.deck if random else self.orderedDeck
            for vocab in deck:
                f.write(vocab.create_tag())
                
            f.write("</div>")
            f.write(boilerplateHTML[1])

    # getters:

    def ordered_list(self):
        return self.orderedDeck
    
    def random_set(self):
        return self.deck
    
    def blacklist(self):
        return self.blacklisted_words

    def allows_duplicates(self):
        return self.allowDuplicates

    

class VocabWord:

    def __init__(self, word, definition, example, difficulty):
        self.word = word
        self.definition = definition
        self.example = example
        self.difficulty = difficulty

    def __lt__(self, other):
        return self.word < other.word

    def create_tag(self):
        return f'<article><div class="vocab-word"><div class="header"><h3 class="word">{self.word}:</h3><h5 class="difficulty"><sup>{self.difficulty}</sup></h5></div><h5 class="definition">{self.definition}</h5><p class="example">{self.example}.</p></div></article>'


def main():
    gre_dictionary = Dictionary("gre_words_magoosh.txt", False, "blacklist.txt")
    gre_dictionary.add_from_file("graduateshotline_gre_words.txt")
    gre_dictionary.create_html("StudySet.html", False)
    print(f'disregarded {len(gre_dictionary.blacklist())} blacklisted words.')
    # gre_dictionary.create_html("gre_words.html", True, "card_grid_stylesheet.css")
    # gre_dictionary.create_html("ordered_gre_words.html", False, "card_grid_stylesheet.css")

if __name__ == "__main__":
    main()
