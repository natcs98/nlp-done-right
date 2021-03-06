import re
from nltk.corpus import stopwords
from string import punctuation
import torch
import numpy as np
from typing import List
import random

"""
Author: Anish Acharya <anishacharya@utexas.edu>
Adopted From: Greg Durret <gdurrett@cs.utexas.edu>
"""


class TextCleaning:
    def __init__(self):
        """ Define Your stop word List here"""
        stops = set(stopwords.words("english"))
        stops.update(set(punctuation))

        self.stops = stops

    def text_cleaning(self, text):
        """Define your Text Cleaning Rules here"""
        # *** Remove this if you are using capitalization as feature ex. NER **
        text = text.lower()

        text = re.sub(r"\. \. \.", "\.", text)
        text = re.sub(r"[^A-Za-z0-9(),!?\'\`\.]", " ", text)
        text = re.sub(r'[0-9]+', '', text)
        text = re.sub(r"\'s", " \'s", text)
        text = re.sub(r"\'ve", " \'ve", text)
        text = re.sub(r"n\'t", " n\'t", text)
        text = re.sub(r"\'re", " \'re", text)
        text = re.sub(r"\'d", " \'d", text)
        text = re.sub(r"\'ll", " \'ll", text)
        text = re.sub(r",", "", text)
        text = re.sub(r"!", "", text)
        text = re.sub(r"\(", "", text)
        text = re.sub(r"\)", "", text)
        text = re.sub(r"\?", "", text)
        text = re.sub(r"\s{2,}", " ", text)
        text = re.sub(r"<br />", " ", text)
        text = re.sub(r'[^\w\s]', '', text)
        text = text.split(" ")
        # text = [w for w in text if w not in self.stops]
        return text


# Print iterations progress
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def flatten(lst):
    """Flattens a list of lists"""
    return [sub_elem for elem in lst
            for sub_elem in elem]


def argmax_from_onehot(vec):
    _, idx = torch.max(vec, 0)
    return idx


def pad_to_length(sentence: List, length: int, pad_ix: int) -> List:
    """
    Forces np_arr to length by either truncation (if longer) or zero-padding (if shorter)
    :param pad_ix:
    :param np_arr:
    :param length: Length to pad to
    :return: a new numpy array with the data from np_arr padded to be of length length. If length is less than the
    length of the base array, truncates instead.
    """
    result = [pad_ix] * length
    result[0:len(sentence)] = sentence
    return result


def get_batch(data: List, batch_size: int, start_ix: int) -> List:
    """ given a start ix and batch size this will return truncated data(list) as batch """
    if len(data) == 0: return []
    return data[start_ix:] if len(data[start_ix:]) <= batch_size else data[start_ix: start_ix + batch_size]


def word_dropout(dropout_prob: float) -> bool:
    """ Toss a biased coin and return bool if to drop this token"""
    if random.random() < dropout_prob:
        return True
    return False


def get_onehot_np(y: np.array, no_classes: int):
    # np.eye won't work for float which we use to get one hot
    y_onehot_np = np.eye(no_classes, dtype=np.int32)[y]
    y_onehot_np = np.squeeze(y_onehot_np, axis=0)
    return y_onehot_np


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
