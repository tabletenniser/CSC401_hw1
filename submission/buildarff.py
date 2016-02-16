import sys
import re
import logging
import argparse

class Arff:
    TAG_REGEX = "^<A=(\d)>$"
    LOG_FILE = "buildarff.log"

    def __init__(self, input_fn, output_fn, max_tweet=0):
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.max_tweet = int(max_tweet)
        # set up logging
        logging.basicConfig(
                level=logging.DEBUG,
                filename=Arff.LOG_FILE,
                format="%(asctime)-15s %(name)-12s %(levelname)s %(message)s",
                datefmt='%y-%m-%d %H:%M:%S',
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.stats = Statistics(output_fn)

    def input_file(self):
        with open(self.input_fn, "r") as f:
            for line in f:
                yield line

    def gen_arff(self):
        tag_matcher = re.compile(Arff.TAG_REGEX)
        limits = dict()
        skip_til_next_header = False
        for line in self.input_file():
            # check if the line read is a tag
            self.logger.info("Matching line " + line.strip())
            match = tag_matcher.match(line)
            if match:
                skip_til_next_header = False
                # header =>
                tclass = match.group(1)
                if tclass not in limits:
                    limits[tclass] = 1
                    if len(limits) > 2:
                        raise ValueError("Not expecting > 2 classes")
                elif self.max_tweet != 0 and limits[tclass] >= self.max_tweet:
                    skip_til_next_header = True
                    continue
                else:
                    limits[tclass] += 1

                self.stats.feed_header(tclass)
            else:
                if not skip_til_next_header:
                    self.stats.feed_line(line)
        self.stats.print_stats()
        self.logger.info("Processed " + str(limits))


class Statistics:
    """
    Generates statistics of tweets
    """
    TOKEN_REGEX = '^(.+)/([^/]+)$'
    STATS = [
        "first_person_pronouns",
        "second_person_pronouns",
        "third_person_pronouns",
        "coordinating_conjunctions",
        "past_tense_verbs",
        "future_tense_verbs",
        "commas",
        "colons_and_semicolons",
        "dashes",
        "parentheses",
        "ellipses",
        "common_nouns",
        "proper_nouns",
        "adverbs",
        "wh_words",
        "modern_slang_acroynms",
        "all_upper_case_words",
    ]

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
             "wh_words": 0,
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
        self.stats = None
        self.ntweets = 0
        self.load_tables()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.token_matcher = re.compile(Statistics.TOKEN_REGEX)
        with open(output_file, "w") as out:
            # write header before writing stats
            out.write(self.get_header())

    def feed_header(self, tclass):
        """
        Each header signifies the begining of a new tweet
        """
        self.ntweets += 1

        if self.stats is None:
            self.stats = self.new_stats()
        else:
            # output stats for the previous tweet
            self.print_stats()
            self.clear_stats()
        self.tclass = tclass

    def print_stats(self):
        with open(self.output_file, "a") as out:
            self.logger.debug(self.stats)
            stats = self.gen_stats()
            out.write(stats + "\n")

    def gen_stats(self):
        # generate required fields
        stats = ",".join([str(self.stats[k]) for k in Statistics.STATS])

        # special cases that need more attention
        # these statistics cannot be computed on the fly (or hard to do so)
        try:
            avg_sentence_len = 1.0 * self.stats["n_tokens"] / (1.0 * self.stats["n_sentence"])
        except ZeroDivisionError:
            avg_sentence_len = 0

        try:
            avg_token_len = 1.0 * self.stats["n_chars"] / (1.0 * self.stats["n_tokens_excluding_punc"])
        except ZeroDivisionError:
            avg_token_len = 0

        stats += "," + str(avg_sentence_len)
        stats += "," + str(avg_token_len)
        stats += "," + str(self.stats["n_sentence"])
        stats += "," + str(self.tclass)
        return stats


    def get_header(self):
        header = "" \
            "% 1. Title: Tweet NLP Database\n" \
            "% \n" \
            "% 2. Sources:\n" \
            "%      (a) Creator: Y. Kang and Z. Wang\n" \
            "%      (b) Date: Feb, 2016\n" \
            "@RELATION NLP_project\n" \
            "\n" \
            "@ATTRIBUTE first_person_pronouns  NUMERIC\n" \
            "@ATTRIBUTE second_person_pronouns  NUMERIC\n" \
            "@ATTRIBUTE third_person_pronouns  NUMERIC\n" \
            "@ATTRIBUTE coordinating_conjunctions  NUMERIC\n" \
            "@ATTRIBUTE past_tense_verbs  NUMERIC\n" \
            "@ATTRIBUTE future_tense_verbs  NUMERIC\n" \
            "@ATTRIBUTE commas  NUMERIC\n" \
            "@ATTRIBUTE colons_and_semicolons  NUMERIC\n" \
            "@ATTRIBUTE dashes  NUMERIC\n" \
            "@ATTRIBUTE parentheses  NUMERIC\n" \
            "@ATTRIBUTE ellipses  NUMERIC\n" \
            "@ATTRIBUTE common_nouns  NUMERIC\n" \
            "@ATTRIBUTE proper_nouns  NUMERIC\n" \
            "@ATTRIBUTE adverbs  NUMERIC\n" \
            "@ATTRIBUTE wh_words  NUMERIC\n" \
            "@ATTRIBUTE modern_slang_acroynms  NUMERIC\n" \
            "@ATTRIBUTE all_upper_case_words  NUMERIC\n" \
            "@ATTRIBUTE avg_sentence_len NUMERIC\n" \
            "@ATTRIBUTE avg_token_len NUMERIC\n" \
            "@ATTRIBUTE n_sentences NUMERIC\n" \
            "@ATTRIBUTE tclass {0, 4}\n" \
            "\n" \
            "@DATA \n"
        return header

    def feed_line(self, line):
        tokens = self.tokenize(line)

        # initialize FSM
        self.going_to_VB = 0

        # number of sentences += 1
        self.stats["n_sentence"] += 1
        for token in tokens:
            # number of tokens += 1
            self.stats["n_tokens"] += 1
            word, tag = token
            self.recognize_token(word, tag)

    def recognize_token(self, word, tag):
        # recognize first person
        if word.lower() in self.list_first_person:
            self.stats["first_person_pronouns"] += 1
        # recognize second person
        elif word.lower() in self.list_second_person:
            self.stats["second_person_pronouns"] += 1
        # recognize third person
        elif word.lower() in self.list_third_person:
            self.stats["third_person_pronouns"] += 1
        # recognize future tense
        elif word.lower() in self.list_future_tense:
            self.stats["future_tense_verbs"] += 1
        # common Nouns
        elif tag in self.list_common_noun_tag:
            self.stats["common_nouns"] += 1
        # proper Nouns
        elif tag in self.list_proper_noun_tag:
            self.stats["proper_nouns"] += 1
        # adverbs
        elif tag in self.list_adverb_tag:
            self.stats["adverbs"] += 1
        # wh words
        elif tag in self.list_wh_words_tag:
            self.stats["wh_words"] += 1
        # modern slang
        elif word.lower() in self.list_modern_slang:
            self.stats["modern_slang_acroynms"] += 1
        # coordinating conjunctions
        elif word.lower() in self.coordinating_conjunctions:
            self.stats["coordinating_conjunctions"] += 1
        # past tense verbs
        elif tag == "VBD":
            self.stats["past_tense_verbs"] += 1

        # punctuation stats:
        self.stats["commas"] += word.count(",")
        self.stats["colons_and_semicolons"] += word.count(";") + word.count(":")
        self.stats["dashes"] += word.count("-")
        self.stats["parentheses"] += word.count(")") + word.count(")")
        self.stats["ellipses"] += word.count("...")

        # a mini FSM to recognize going+to+VB
        if word.lower() == "going" and self.going_to_VB == 0:
            self.logger.debug("Future tense vb at " + word)
            self.going_to_VB += 1
        elif word.lower() == "to" and self.going_to_VB == 1:
            self.logger.debug("Future tense vb at " + word)
            self.going_to_VB += 1
        elif tag  == "VB" and self.going_to_VB == 2:
            self.going_to_VB = 0
            self.stats["future_tense_verbs"] += 1
            self.logger.debug("Matched future tense vb at verb " + word)
        else:
            self.going_to_VB = 0

        # word in all cap
        if word.upper() == word and len(word) >= 2:
            self.stats["all_upper_case_words"] += 1

        # for avg token len
        if word not in self.list_punctuations:
            self.stats["n_chars"] += len(word)
            self.stats["n_tokens_excluding_punc"] += 1

    def tokenize(self, sentencse):
        tokens = []
        for token in sentencse.split():
            m = self.token_matcher.match(token)
            if m is None:
                self.logger.error("Unable to parse token " + token)
                continue
            else:
                tokens.append(m.groups())
        return tokens

    def load_tables(self):
        # hard code these in
        self.list_first_person = [
            "i", "me", "my", "mine", "we", "us", "our", "ours",
        ]
        self.list_second_person = [
            "you", "your", "yours", "u", "ur", "urs",
        ]
        self.list_third_person = [
            "he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their", "theirs",
        ]
        self.list_future_tense = [
            "'ll", "will", "gonna", # going + to + VB
        ]
        self.list_modern_slang = [
            "smh", "fwb", "lmfao", "lmao", "lms", "tbh", "ro,"
            "wtf", "bff", "wyd", "lylc", "brb", "atm", "imao", "sml", "btw",
            "bw", "imho", "fyi", "ppl", "sob", "ttyl", "imo", "ltr",
            "thx", "kk", "omg", "ttys", "afn", "bbs", "cya", "ez", "f2f", "gtr",
            "ic", "jk", "k", "ly", "ya", "nm", "np", "plz", "ru",
            "so", "tc", "tmi", "ym", "ur", "u", "sol",
        ]
        self.list_common_noun_tag = ["NN", "NNS"]
        self.list_proper_noun_tag = ["NNP", "NNPS"]
        self.list_adverb_tag = ["RB", "RBR", "RBS"]
        self.list_wh_words_tag = ["WDT", "WP", "WP$", "WRB"]
        self.list_punctuations = "?!,;:-.\"'"
        self.coordinating_conjunctions = ['for', 'and', 'nor', 'but', 'or', 'yet', 'so']

    def clear_stats(self):
        self.stats = self.new_stats()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help='Input .twtt file')
    parser.add_argument("output_file", type=str, help='Output .arff file')
    parser.add_argument("max_tweet", nargs='?', type=str, default=0, help='Max number of tweets')
    args = parser.parse_args()

    # argv = sys.argv[1:]
    arff = Arff(args.input_file, args.output_file, args.max_tweet)
    arff.gen_arff()
