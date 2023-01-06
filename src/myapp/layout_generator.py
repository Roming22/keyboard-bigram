"""Generate keymap layouts"""

from keyboard import Char, Fingering, Key, KeymapHelper


def generate(corpus: dict, config: dict):
    keymap = KeymapHelper.new(config["keyboard"])
    print()
    KeymapHelper.print(keymap, "score")
    corpus_chars = [
        Char(c, v)
        for c, v in sorted(corpus["letter_count"].items(), key=lambda x: x[1])
    ]
    add_space(corpus)
    keymap = KeymapHelper.add_constraints_to_keymap(
        config["keyboard"]["constraints"], corpus_chars, keymap
    )
    print()
    KeymapHelper.print(keymap)

    corpus_chars = [c.char for c in corpus_chars]
    keymap = generate_keymap(keymap, corpus_chars, corpus["bigrams"], config)
    print()
    KeymapHelper.print(keymap)


def add_space(corpus):
    corpus["bigrams"][" "] = {" ": 0}
    for data in corpus["bigrams"].values():
        data[" "] = 0


def generate_keymap(keymap, chars, corpus, config):
    for layer in sorted(
        keymap.definition["layers"],
        key=lambda x: config["keyboard"]["score"]["layers"][x],
    ):
        for row in sorted(
            keymap.definition["rows"],
            key=lambda x: config["keyboard"]["score"]["rows"][x],
        ):
            for hand in sorted(
                keymap.definition["hands"],
                key=lambda x: config["keyboard"]["score"]["hands"][x],
            ):
                keys = config["keyboard"]["layout"]["rows"][row][hand]
                size = len(keys)
                if layer == "layer2":
                    size = 3
                print(layer, row, hand, len(keys))

                char = chars.pop()
                print("Char", char)
                if size < 4:
                    lchar, rchar = get_bigrams(char, corpus)
                    keymap = assign_key(
                        keymap, layer, row, hand, keys[1], char, corpus, chars
                    )
                    if size > 1:
                        keymap = assign_key(
                            keymap, layer, row, hand, keys[0], lchar, corpus, chars
                        )
                    if size > 1:
                        keymap = assign_key(
                            keymap, layer, row, hand, keys[2], rchar, corpus, chars
                        )
                if size == 4:
                    lchar, rchar = get_bigrams(char, corpus)
                    keymap = assign_key(
                        keymap, layer, row, hand, keys[1], char, corpus, chars
                    )
                    llchar, l_lchar = get_bigrams(lchar, corpus)
                    rrchar, r_rchar = get_bigrams(rchar, corpus)
                    if llchar == rchar:
                        llchar = l_lchar
                    if rrchar == lchar:
                        rrchar = r_rchar
                    if corpus[lchar][llchar] > corpus[rchar][rrchar]:
                        keymap = assign_key(
                            keymap, layer, row, hand, keys[0], rchar, corpus, chars
                        )
                        keymap = assign_key(
                            keymap, layer, row, hand, keys[2], lchar, corpus, chars
                        )
                        keymap = assign_key(
                            keymap, layer, row, hand, keys[3], llchar, corpus, chars
                        )
                    else:
                        keymap = assign_key(
                            keymap, layer, row, hand, keys[0], lchar, corpus, chars
                        )
                        keymap = assign_key(
                            keymap, layer, row, hand, keys[2], rchar, corpus, chars
                        )
                        keymap = assign_key(
                            keymap, layer, row, hand, keys[3], rrchar, corpus, chars
                        )

    return keymap


def get_bigrams(char, corpus):
    bigrams = corpus[char]
    next_char = sorted([c for c in bigrams.keys()], key=lambda x: bigrams[x])
    try:
        lchar = next_char[-1]
    except IndexError:
        lchar = " "
    try:
        rchar = next_char[-2]
    except IndexError:
        rchar = " "
    return lchar, rchar


def assign_key(keymap, layer, row, hand, key, char, corpus, chars):
    key = Key(Fingering(layer, row, hand, key), 0, None)
    keymap = KeymapHelper.assign_char_to_key(
        keymap,
        Char(char, 0),
        key,
    )
    remove_char(char, corpus, chars)
    return keymap


def remove_char(char, corpus, chars):
    if char == " ":
        return
    print(f"Removing {char}")
    corpus.pop(char)
    if char in chars:
        chars.remove(char)
    for k in corpus.keys():
        # print(f"Removing {char} from {k}")
        try:
            corpus[k].pop(char)
        except KeyError:
            pass
