# define special symbols to handle padding etc
UNK_TOKEN = "__UNK__"   # unknown token
PAD_TOKEN = "__PAD__"   # padding
BOS_TOKEN = "__BOS__"   # Beginning of sentence token
EOS_TOKEN = "__EOS__"   # End of sentence token


""" define different pre-trained flat embedding locations"""
glove = '../../Embeddings/glove.6B/glove.6B.50d.txt'
encoder_embed_cache = 'encoder_cached_embedding'
decoder_embed_cache = 'decoder_cached_embedding'
