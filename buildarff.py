import re

class Arff:
    TAG_REGEX = "^<A=(\d)>$"

    def __init__(self, input_fn, output_fn, max_tweet):
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.max_tweet = max_tweet
    
    def input_file(self):
        with open(self.input_fn, "r") as f:
            for line in f:
                yield line

    def gen_arff(self):
        with open(self.output_fn, "w") as self.output:
            tag_matcher = re.compile(Arff.TAG_REGEX)
            for line in self.input_file():
                # check if the line read is a tag


class Statistics:
    """
    Counts:
        | First person pronouns
        | Second person pronouns
        | Third person pronouns
        | Coordinating conjunctions
        | Past-tense verbs
        | Future-tense verbs
        | Commas
        | Colons and semi-colons
        | Dashes
        | Parentheses
        | Ellipses
        | Common nouns
        | Proper nouns
        | Adverbs
        | wh-words
        | Modern slang acroynms
        | Words all in upper case (at least 2 letters long)

     Average length of sentences (in tokens)
    "Average length of tokens, excluding punctuation tokens (in characters)
    "Number of sentences"
    """
     def new_stats(self):
         return {
             "first_person_pronouns": 0,
             "second_person_pronouns": 0,
             "third_person_pronouns": 0,
             "coordinating_conjunctions": 0,
             "past_tense_verbs": 0,
             "future_tense_verbs": 0,
             "commas": 0,
             "colons_and_semicolons": 0,
             "dashes": 0,
             "parentheses": 0,
             "ellipses": 0,
             "common_nouns": 0,
             "proper_nouns": 0,
             "adverbs": 0,
             "wh-words": 0,
             "modern_slang_acroynms": 0,
             "all_upper_case_words": 0,
             #avg_sentence_len = n_tokens/n_sentence
             "n_sentence": 0,
             "n_tokens": 0,
             #avg_token_len = n_chars/n_tokens_excluding_punc
             "n_chars": 0,
             "n_tokens_excluding_punc": 0,
             #number of sentences = n_sentence
        }

    def __init__(self, output_file):
        self.output_file = output_file
        self.stats = self.new_stats()
        self.load_tables()
        pass

    def feed_header(self, tclass):
        self.tclass = tclass

    def output_stats(self):
        pass

    def feed_line(self, line):
        pass

    def load_tables(self):
        pass

    def clear_stats(self):
        self.stats = new_stats()
