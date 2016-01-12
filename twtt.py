import logging
import re


class TweetTokenizer:
    GID = 0
    ASCII_TABLE = "./ascii.csv"
    ASCII_DELIM = "xxDELIMxx"
    LOG_FILE = "./parser.log"
    HTML_TAGS = "<[^>]+>"
    DEBUG_LIMIT = 100

    def __init__(self, input_file, group_name, output_file):
        self.input_file = input_file
        self.group_name = group_name
        self.output_file = output_file
        self.ascii_table = None

        # set up logging
        logging.basicConfig(
                level=logging.DEBUG,
                filename=TweetTokenizer.LOG_FILE, 
                format="%(asctime)-15s %(name)-12s %(levelname)s %(message)s",
                datefmt='%y-%m-%d %H:%M:%S',
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.load_ascii_table()

    def load_ascii_table(self):
        """ Load ASCII table from file TweetTokenizer.ASCII_TABLE
        """

        self.logger.info("Loading ascii table")
        self.ascii_table = dict()
        with open(TweetTokenizer.ASCII_TABLE, "r") as f:
            for line in f:
                value, key = line.split(TweetTokenizer.ASCII_DELIM)
                self.ascii_table[key.strip()] = value.strip()
        self.logger.info("Table: " + str(self.ascii_table))

    def get_tweet(self):
        """ Get tweets based on GID
        """
        class_0_lb = TweetTokenizer.GID * 5500
        class_0_ub = (TweetTokenizer.GID + 1) * 5500 - 1

        class_4_lb = class_0_lb + 800000
        class_4_ub = class_0_ub + 800000

        line_count = 0
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
        for tweet in self.get_tweet():
            if TweetTokenizer.DEBUG_LIMIT and tweet_count > TweetTokenizer.DEBUG_LIMIT:
                return
            tweet_count += 1
            tclass, tid, date, query, user, text = tweet.split(",")

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

    
if __name__ == "__main__":
    twt = TweetTokenizer("training.1600000.processed.noemoticon.csv", "Group", "test")
    twt.parse_tweet()
