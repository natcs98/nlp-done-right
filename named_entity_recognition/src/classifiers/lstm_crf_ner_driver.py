from src.data_utils.definitions import Indexer, LabeledSentence
from src.feature_extractors.emission_features import extract_emission_features
from src.models.lstm_crf import LSTMCrfNerModel
import src.config as conf
from src.data_utils.utils import get_word_index
from src.models.utils import prepare_data_point, prepare_label_point
import numpy as np

from collections import Counter
from nltk.corpus import stopwords
from string import punctuation
import torch.optim as optim
import torch


# stops = set(stopwords.words("english"))
# stops = set(punctuation)
# stops.update(set(punctuation))
# stops.update({'-X-', ',', '$', ':', '-DOCSTART-'})
stops = set()


# Trains a CrfNerModel on the given corpus of sentences.
def train_crf_ner(sentences: [LabeledSentence]):
    tag_indexer = Indexer()
    word_indexer = Indexer()
    word_counter = Counter()

    tag_indexer.add_and_get_index(conf.PAD_TOKEN)   # padding
    word_indexer.add_and_get_index(conf.PAD_TOKEN)
    tag_indexer.add_and_get_index(conf.EOS_TOKEN)   # End of Sentence
    word_indexer.add_and_get_index(conf.EOS_TOKEN)
    tag_indexer.add_and_get_index(conf.BOS_TOKEN)   # Beginning of Sentence
    word_indexer.add_and_get_index(conf.BOS_TOKEN)
    tag_indexer.add_and_get_index(conf.UNK_TOKEN)   # Unk Words
    word_indexer.add_and_get_index(conf.UNK_TOKEN)

    for sentence in sentences:
        for token in sentence.tokens:
            word_counter[token.word] += 1.0

    for sentence in sentences:
        for token in sentence.tokens:
            # If the word occurs fewer than two times, don't index it -- we'll treat it as UNK
            get_word_index(word_indexer=word_indexer, word_counter=word_counter, stops=stops, word=token.word)
        for tag in sentence.get_bio_tags():
            tag_indexer.add_and_get_index(tag)

    feature_indexer = Indexer()
    # 4-d list indexed by sentence index, word index, tag index, feature index
    # feature_cache = [[[[] for k in range(0, len(tag_indexer))] for j in
    #                   range(0, len(sentences[i]))] for i in range(0, len(sentences))]
    # for sentence_idx in range(0, len(sentences)):
    #     if sentence_idx % 100 == 0:
    #         print("Ex %i/%i" % (sentence_idx, len(sentences)))
    #     for word_idx in range(0, len(sentences[sentence_idx])):
    #         for tag_idx in range(0, len(tag_indexer)):
    #             feature_cache[sentence_idx][word_idx][tag_idx] = \
    #                 extract_emission_features(sentences[sentence_idx].tokens, word_idx,
    #                                           tag_indexer.get_object(tag_idx), feature_indexer, add_to_indexer=True)

    # Call to the crf model which learns features jointly
    crf_model = LSTMCrfNerModel(word_ix=word_indexer, tag_ix=tag_indexer,
                                embedding_dim=conf.embedding_dim, hidden_dim=conf.hidden_dim)
    # optimizer = optim.SGD(crf_model.parameters(), lr=conf.initial_lr, weight_decay=conf.weight_decay)
    PAD_ID = word_indexer.objs_to_ints[conf.PAD_TOKEN]
    PAD_TAG_ID = tag_indexer.objs_to_ints[conf.PAD_TOKEN]

    lr = conf.initial_lr
    for epoch in range(conf.epochs):
        # optimizer = optim.SGD(crf_model.parameters(), lr=lr, weight_decay=conf.weight_decay)
        optimizer = torch.optim.Adam(crf_model.parameters(), lr=lr)
        with torch.no_grad():
            x1 = prepare_data_point(sentences[1], word_indexer=word_indexer)
            x_test = torch.full((1, len(x1)), PAD_ID, dtype=torch.long)
            x_test[0, :x1.shape[0]] = x1
            print("predicted labels :", crf_model(x_test))
            print("true labels:", prepare_label_point(sentence=sentences[1], tag_indexer=tag_indexer))
        # for i in range(0, len(sentences), conf.batch_size):
        #     crf_model.zero_grad()
        #
        #     if len(sentences[i:]) <= conf.batch_size:
        #         data_batch = sentences[i:]
        #     else:
        #         data_batch = sentences[i: i + conf.batch_size]
        #
        #     max_sent_size = max([len(sentence) for sentence in data_batch])
        #
        #     x = torch.full((len(data_batch), max_sent_size), PAD_ID, dtype=torch.long)
        #     y = torch.full((len(data_batch), max_sent_size), PAD_TAG_ID, dtype=torch.long)
        #
        #     for i in range(0, len(data_batch)):
        #         x1 = prepare_data_point(sentence=data_batch[i], word_indexer=word_indexer)
        #         y1 = prepare_label_point(sentence=data_batch[i], tag_indexer=tag_indexer)
        #         x[i, : x1.shape[0]] = x1
        #         y[i, : y1.shape[0]] = y1
        #
        #     mask = (y != PAD_TAG_ID).float()
        #     loss = crf_model.nll(x, y, mask=mask)
        #     loss.backward()
        #     optimizer.step()
        for ix, sentence in enumerate(sentences):
            #x = np.array(feature_cache[ix])
            x = prepare_data_point(sentence, word_indexer)
            y = prepare_label_point(sentence, tag_indexer)
            crf_model.zero_grad()
            loss = crf_model.nll(x, y)
            loss.backward()
            optimizer.step()
        lr = lr/2
        if (epoch + 1) % 5 == 0:
            lr = conf.initial_lr
    return crf_model
