import logging
import re
import hashlib
import NLPlib


class TweetTokenizer:
    GID = 0
    ASCII_TABLE = "./ascii.csv"
    ABBRV_TABLE = "./abbrev.english"
    ASCII_DELIM = "xxDELIMxx"
    LOG_FILE = "./parser.log"
    HTML_TAGS = '<[^>]+>'
    TWEET_REGEX = '^\"(\d)\",\"(\d+)\",\"([^\"]+)\",\"([^\"]+)\",\"([^\"]+)\",\"(.+)\"$'
    END_SENTENCE_REGEX = '^([^?!\.]+)([?!]+|\.+)$'
    PUNCTUATION_REGEX = '^([^?!\.]+)([?!]+|\.+)$'
    PUNCTUATION_REGEX_2 = '^([^,;/]+)([,;/])([^,;/]+)?$'
    POSSESSIVE_REGEX = '^([^\']+)(\'[smS]?)$'
    CLITICS_REGEX = '([^\']+)(n\'t)'
    DEBUG_LIMIT = 100


    def __init__(self, input_file, group_name, output_file):
        self.input_file = input_file
        self.group_name = group_name
        self.output_file_name = output_file
        self.output_file = None
        self.ascii_table = None
        self.abbrv_table = None
        self.rabbrv_table = None

        # set up logging
        logging.basicConfig(
                level=logging.DEBUG,
                filename=TweetTokenizer.LOG_FILE, 
                format="%(asctime)-15s %(name)-12s %(levelname)s %(message)s",
                datefmt='%y-%m-%d %H:%M:%S',
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        # output to log
        self.logger.info("++++++++ What a good day to tweet! ++++++++")

        # load some tables
        self.load_ascii_table()
        self.load_abbrv_table()

    def output_file_write(self, line):
        if self.output_file is None:
            raise ValueError("Output file is not yet opened!")
        self.output_file.write(line + "\n")

    def load_ascii_table(self):
        """ Load ASCII table from file TweetTokenizer.ASCII_TABLE
        """

        self.logger.info("Loading ascii table")
        self.ascii_table = dict()
        with open(TweetTokenizer.ASCII_TABLE, "r") as f:
            for line in f:
                value, key = line.split(TweetTokenizer.ASCII_DELIM)
                self.ascii_table[key.strip()] = value.strip()
        #self.logger.info("Table: " + str(self.ascii_table))

    def get_tweet(self):
        """ Get tweets based on GID
        """
        class_0_lb = TweetTokenizer.GID * 5500
        class_0_ub = (TweetTokenizer.GID + 1) * 5500 - 1

        class_4_lb = class_0_lb + 800000
        class_4_ub = class_0_ub + 800000

        line_count = 0
        self.logger.info("Class 0 from: {lb} to {ub}".format(lb=class_0_lb, ub=class_0_ub))
        self.logger.info("Class 4 from: {lb} to {ub}".format(lb=class_4_lb, ub=class_4_ub))
        if TweetTokenizer.DEBUG_LIMIT:
            self.logger.warn("Output is limited to " + str(TweetTokenizer.DEBUG_LIMIT))
        with open(self.input_file, "r") as f:
            for line in f:
                line_count += 1
                if ((line_count >= class_0_lb and line_count <= class_0_ub) or
                    (line_count >= class_4_lb and line_count <= class_4_ub)):
                    yield line

    def parse_tweet(self):
        """ Parse tweets based on rules specified in the handout
        """
        tweet_count = 0

        # open output file
        with open(self.output_file_name, "w") as self.output_file:
            for tweet in self.get_tweet():
                if TweetTokenizer.DEBUG_LIMIT and tweet_count > TweetTokenizer.DEBUG_LIMIT:
                    return
                tweet_count += 1
                tweet_match = re.match(TweetTokenizer.TWEET_REGEX, tweet)
                try:
                    tclass, tid, date, query, user, text = tweet_match.groups()
                    self.logger.debug(
                            ("Parsed tclass: '{t}' tid: '{tid}' date: '{d}'"
                            "query: '{q}' user: '{u}' text: '{txt}'")
                            .format(t=tclass, tid=tid, d=date, q=query, u=user, txt=text)
                    )
                except Exception as e:
                    self.logger.error("Unable to parse tweet " + tweet)
                    continue

                if tclass not in "01234":
                    self.logger.error("Tweet has incorrect tag " + tclass)
                    continue

                self.logger.debug("step0: " + text)

                # 0- Remove all tailing and leading spaces
                text = text.strip()

                # 1- Remove all HTML tags
                text = re.sub(TweetTokenizer.HTML_TAGS, "", text)
                self.logger.debug("step1: " + text)

                # 2- HTML char codes replaced with ASCII (screw regex, just brute force it)
                for key in self.ascii_table:
                    text = text.replace(key, self.ascii_table[key])
                self.logger.debug("step2: " + text)
                
                # 3- filter out all HTTP/WWW tags
                text = " ".join(
                        filter(
                            lambda k: not k.lower().startswith("http") and not k.lower().startswith("www"),
                            text.split(" "),
                        )
                )
                self.logger.debug("step3: " + text)

                # 4- filter out @ and #
                text = text.replace("@", "")
                text = text.replace("#", "")
                self.logger.debug("step4: " + text)

                # 5,6- Break tweet into multiple lines
                texts = self.build_linebreak(text)
                self.logger.debug("step5,6: " + str(texts))

                # 7- separate punctuation and clitics
                texts = self.break_punctuations(texts)
                self.logger.debug("step7: " + str(texts))

                # 8- Tag PoS info
                texts = self.tag_PoS(texts)
                self.logger.debug("step8: " + str(texts))

                # 9- demarcation
                self.assemble(texts, tclass)
        self.logger.info("-------- What a good day to tweet! --------")

    def assemble(self, texts, tclass):
        self.output_file_write("<A={cls}>".format(cls=tclass))
        map(lambda sentence: self.output_file_write(" ".join(sentence)), texts)
    
    def tag_PoS(self, texts):
        tagger = NLPlib.NLPlib()
        processed_texts = []
        for sentence in texts:
            tags = tagger.tag(sentence)
            processed_texts.append(
                    [ x + '/' + y for x, y in zip(sentence, tags)]
            )
        return processed_texts 

    def proc_token(self, token):
        if isinstance(token, list):
            # nope
            self.logger.error(
                    "Got list in proc_token, string expected! '{tok}'"
                    .format(tok=token)
            )
            raise ValueError("Got list when string is expected")

        #END_SENTENCE_REGEX = '^[^?!\.]+([?!]+|\.+)$'
        #PUNCTUATION_REGEX = '^(^?!\.)+([?!]+|\.+)$'
        #POSSESSIVE_REGEX = '^([^\']+)(\'S?)$'

        # test cases:
        # go!
        # go??!
        # shouldn't
        # ryan's
        # jim's!
        # dogs'
        pun_matcher = re.compile(TweetTokenizer.PUNCTUATION_REGEX)
        cli_matcher = re.compile(TweetTokenizer.CLITICS_REGEX)
        pos_matcher = re.compile(TweetTokenizer.POSSESSIVE_REGEX)

        # break up punctuations
        pun_match = pun_matcher.match(token)
        tokens = [token]
        
        if pun_match:
            tokens = list(pun_match.groups())
        
        # break clitics and/or possessive
        cli_match = cli_matcher.match(tokens[0])
        pos_match = pos_matcher.match(tokens[0])

        if cli_match and pos_match:
            self.logger.error(
                    "Matched both clitics and possessive on '{s}'".format(s=tokens[0])
            )
        if cli_match:
            tokens = list(cli_match.groups()) + tokens[1:]
            self.logger.info("Matched clitic at '{c}'".format(c=tokens[0]))
        elif pos_match:
            self.logger.info("Matched possessive at '{c}'".format(c=tokens[0]))
            tokens = list(pos_match.groups()) + tokens[1:]
        
        self.logger.debug("{tok} ==> {stok}".format(tok=token, stok=str(tokens)))

        # break by other punctuations
        # comma, semicolon, forward and backward slashes
        original_tokens = tokens
        tokens = []

        pun_matcher2 = re.compile(TweetTokenizer.PUNCTUATION_REGEX_2)
        for token in original_tokens:
           pmatch = pun_matcher2.match(token)
           if pmatch:
               tokens += filter(lambda x: x is not None, pmatch.groups())
           else:
               tokens.append(token)
            
        return tokens
    
    def break_punctuations(self, texts):
        result = [[] for _ in xrange(len(texts))]
        for level in xrange(len(texts)):
            for token in texts[level]:
                tokens = self.proc_token(token)
                result[level].extend(tokens)
        return result

    def load_abbrv_table(self): 
        self.logger.info("Loading abbrv table")
        self.abbrv_table = dict()
        self.rabbrv_table = dict()

        with open(TweetTokenizer.ABBRV_TABLE, "r") as f:
            for line in f:
                # build abbrv -> sha1 and sha1 -> abbrv tables
                line = line.strip()
                sha =  hashlib.sha1(line.strip()).hexdigest()

                self.abbrv_table[line] = sha
                self.rabbrv_table[sha] = line

        #self.logger.debug("Table: " + str(self.abbrv_table))

    def abbrv_ends_sentence(self, tokens, index):
        index += 1
        upper_case = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        while index < len(tokens):
            if len(tokens[index]):
                if tokens[index][0] in upper_case:
                    return True
                else:
                    return False
            index += 1
        return False

    def build_linebreak(self, text):
        """ Break a single text into multiple lines
        with constraints and rules specified in handout
        """
        # tokenize
        tokens = text.split()

        # replace all abbrv. with its sha, unless we 
        # have reasons to believe that this abbrv ends
        # a particular sentence
        for token_idx in xrange(len(tokens)):
            if tokens[token_idx] in self.abbrv_table:
                # If the token follows immediately by an upper case
                # we consider this abbrv ends a sentence
                self.logger.info("Abbr detected at " + tokens[token_idx])

                if not self.abbrv_ends_sentence(tokens, token_idx):
                    # replace abbrv. with sha
                    tokens[token_idx] = self.abbrv_table[tokens[token_idx]]
                else:
                    self.logger.debug(
                            "End of sentence detected near abbr '{tok}' in {s}"
                            .format(tok=tokens[token_idx], s="".join(tokens))
                    )

        # construct sentences
        matcher = re.compile(TweetTokenizer.END_SENTENCE_REGEX)
        texts = []
        level = 0
        for tok in tokens:
            if len(texts) <= level:
                # new sentence
                texts.append([])
            match = matcher.match(tok)
            if tok in self.rabbrv_table:
                # sha back to abbrv
                texts[level].append(self.rabbrv_table[tok])
            else:
                texts[level].append(tok)
            if match is not None:
                # end of line ... possibly!
                self.logger.debug(
                        "End of sentence detected at '{token}', due to '{match}'"
                        .format(token=tok, match=match.group(2))
                )
                level += 1
        return texts
    
if __name__ == "__main__":
    twt = TweetTokenizer("training.1600000.processed.noemoticon.csv", "Group", "test.out")
    twt.parse_tweet()
