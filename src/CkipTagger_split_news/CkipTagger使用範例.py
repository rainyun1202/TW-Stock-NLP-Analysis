from ckiptagger import WS, POS, NER

# ckiptagger 路徑
ws = WS('./ckip_data')
pos = POS('./ckip_data')
ner = NER('./ckip_data')

sentence_list = [
    "集團生產高爾夫小白球、球具及複合材料的明安國際(8938-TW)受惠市場需求回升"
]

word_sentence_list = ws(
    sentence_list,
    # sentence_segmentation = True, # To consider delimiters
    # segment_delimiter_set = {",", "。", ":", "?", "!", ";"}), # This is the defualt set of delimiters
    # recommend_dictionary = dictionary1, # words in this dictionary are encouraged
    # coerce_dictionary = dictionary2, # words in this dictionary are forced
)
pos_sentence_list = pos(word_sentence_list)
entity_sentence_list = ner(word_sentence_list, pos_sentence_list)

def print_word_pos_sentence(word_sentence, pos_sentence):
    assert len(word_sentence) == len(pos_sentence)
    for word, pos in zip(word_sentence, pos_sentence):
        print(f"{word}({pos})", end="\u3000")
    print()
    return
    
for i, sentence in enumerate(sentence_list):
    print()
    print(f"'{sentence}'")
    print_word_pos_sentence(word_sentence_list[i], pos_sentence_list[i])
    for entity in sorted(entity_sentence_list[i]):
        print(entity)
