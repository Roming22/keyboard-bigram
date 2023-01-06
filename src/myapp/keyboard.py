"""Representation of a keymap"""
import collections
import copy

from frozendict import frozendict

Layer = collections.namedtuple("Layer", ["keyboard", "rows", "score", "name"])
Keymap = collections.namedtuple(
    "Keymap", ["keys", "mapping", "rolls", "definition", "name"]
)

Char = collections.namedtuple("Char", ["char", "score"])
Key = collections.namedtuple("Key", ["fingering", "score", "char"])
Keyboard = collections.namedtuple("Keyboard", ["keys", "rolls"])
Fingering = collections.namedtuple("Fingering", ["layer", "row", "hand", "column"])


class KeymapHelper:
    """Helper methods for Keymap"""

    _name = "Keymap"
    count = 0

    @classmethod
    def add_constraints_to_keymap(cls, constraints, corpus, keymap: Keymap) -> Keymap:
        corpus_dict = {c.char: c for c in corpus}
        removed_chars = set()
        for layer, rows in constraints.items():
            for row, hands in rows.items():
                for hand, columns in hands.items():
                    for column, c in columns.items():
                        char = corpus_dict.get(c, Char(c, 0))
                        key = cls.get_key(keymap, Fingering(layer, row, hand, column))
                        if key is not None:
                            if char in corpus:
                                removed_chars.add(char)
                            keymap = cls.assign_char_to_key(keymap, char, key)
        for char in removed_chars:
            corpus.remove(char)
        return keymap

    @classmethod
    def assign_char_to_key(cls, keymap: Keymap, char: Char, key: Key) -> Keymap:
        key = Key(key.fingering, key.score * char.score, char.char)
        cls.count += 1
        name = f"{cls._name}{cls.count}"
        new_keymap = Keymap(
            list(keymap.keys),
            keymap.mapping,
            keymap.rolls,
            keymap.definition,
            name,
        )
        new_keymap.keys[keymap.mapping[key.fingering]] = key
        return new_keymap

    @staticmethod
    def get_fingerings(keymap) -> list:
        for layer in keymap.definition["layers"]:
            for row in keymap.definition["rows"]:
                for hand in keymap.definition["hands"]:
                    for column in keymap.definition["columns"][hand]:
                        yield Fingering(layer, row, hand, column)

    @classmethod
    def get_free_keys(cls, keymap: Keymap) -> list[Key]:
        # This can probably be optimized by storing the list at each level
        free_keys = []
        for layer in keymap.definition["layers"]:
            for row in keymap.definition["rows"]:
                for hand in keymap.definition["hands"]:
                    for column in keymap.definition["columns"][hand]:
                        key = cls.get_key(keymap, Fingering(layer, row, hand, column))
                        if key is not None and key.char is None:
                            free_keys.append(key)
        free_keys = sorted(free_keys, key=lambda x: x.score)
        return free_keys

    @staticmethod
    def get_key(keymap: Keymap, fingering: Fingering) -> Key:
        try:
            return keymap.keys[keymap.mapping[fingering]]
        except KeyError:
            return None

    @classmethod
    def get_key_rolls(cls, keymap: Keymap, key: Key, length: int) -> list[list[Key]]:
        layer, row, hand, column = key.fingering
        rolls = []
        roll_row = keymap.rolls[row][hand]
        key_index = roll_row.index((None, row, hand, column))
        start = max(0, key_index - length + 1)
        stop = min(len(roll_row) - length, key_index) + 1

        roll_fingering = [
            Fingering(layer, row, hand, column) for _, row, hand, column in roll_row
        ]

        for i in range(start, stop):
            rolls.append(roll_fingering[i : i + length])
        return rolls

    @classmethod
    def new(cls, config: dict, name: str = None) -> Keymap:
        keyboard = KeyboardHelper.new(config)
        cls.count += 1
        if not name:
            name = f"{cls._name}{cls.count}"

        keys = []
        mapping = {}
        for layer in config["layout"]["definitions"]["layers"]:
            for fingering, key in keyboard.keys.items():
                fingering = Fingering(layer, *fingering[1:])
                key_score = config["score"]["layers"][layer] + key.score
                mapping[fingering] = len(keys)
                keys.append(Key(fingering, key_score, None))
        return Keymap(
            keys,
            frozendict(mapping),
            frozendict(keyboard.rolls),
            frozendict(config["layout"]["definitions"]),
            name,
        )

    @classmethod
    def print(cls, keymap, mode="char") -> None:
        lines = [f"# {keymap.name}"]
        middle = 0
        for layer in keymap.definition["layers"]:
            lines.append(f"## {layer}")
            for row in keymap.definition["rows"]:
                hands = []
                for hand in keymap.definition["hands"]:
                    keys = []
                    for column in keymap.definition["columns"][hand]:
                        key = cls.get_key(keymap, Fingering(layer, row, hand, column))
                        if key:
                            char = " "
                            if mode == "char":
                                char = key.char if key.char else char
                            elif mode == "score":
                                char = key.score
                            char = f"[{char}]"
                            keys.append(char)
                    hands.append("".join(keys))
                line = " | ".join(hands)
                lines.append(line)
                middle = max(middle, line.index("|"))
        for line in lines:
            if "|" in line:
                line = " " * (middle - line.index("|")) + line
            print(line)
        print(flush=True)


class KeyboardHelper:
    """Helper methods for Keyboard"""

    @staticmethod
    def new(config: dict) -> Keyboard:
        keys: dict = {}
        rolls: dict = {}
        for row, hands in config["layout"]["rows"].items():
            rolls[row] = {}
            for hand, columns in hands.items():
                rolls[row][hand] = []
                for column in columns:
                    fingering = Fingering(None, row, hand, column)
                    score = config["score"]["rows"][row]
                    score += config["score"]["fingers"][hand][column]
                    keys[fingering] = Key(fingering, score, None)
                    rolls[row][hand].append(fingering)
        keyboard = Keyboard(frozendict(keys), frozendict(rolls))
        return keyboard
