"""Generate input data from the corpus"""
import glob
import os

import git
import yaml


def generate_data(corpus_preferences: dict) -> dict:
    language_data = {}
    language_data.update(generate_i18_data(corpus_preferences["i18n"]))
    language_data.update(generate_code_data(corpus_preferences["code"]))
    corpus_data = consolidate_data(language_data)
    filter_corpus_data = filter_data(corpus_data)
    with open("corpus.yaml", "w") as outfile:
        yaml.dump(corpus_data, outfile, sort_keys=True)
    return corpus_data


def consolidate_data(language_data: dict) -> dict:
    corpus_data = {
        "letter_count": dict(),
        "bigrams": {},
    }

    for _, data in language_data.items():
        for char, value in data["letter_count"].items():
            corpus_data["letter_count"][char] = (
                corpus_data["letter_count"].get(char, 0) + value
            )

        for lchar, ldata in data["bigrams"].items():
            for rchar, value in ldata.items():
                corpus_data["bigrams"][lchar] = corpus_data["bigrams"].get(lchar, {})
                corpus_data["bigrams"][lchar][rchar] = (
                    corpus_data["bigrams"][lchar].get(rchar, 0) + value
                )
    return corpus_data


def filter_data(corpus_data: dict) -> None:
    delete = []
    for letter, count in corpus_data["letter_count"].items():
        if count < 500:
            delete.append(letter)
    for letter in delete:
        for _c, _v in corpus_data.items():
            for _k in dict(_v).keys():
                if letter in _k:
                    corpus_data[_c].pop(_k)


def list_files(path: str, extensions: list[str]) -> list[str]:
    files = []
    for ext in extensions:
        files += glob.glob(f"{path}/**/*.{ext}", recursive=True)
    return files


def generate_i18_data(languages: dict) -> dict:
    data = {}
    for language in languages.keys():
        print("\n", language)
        data[language] = load_dir_data(languages[language])
    return data


def load_dir_data(language: dict) -> dict:
    size = 0
    data = {
        "letter_count": {},
        "bigrams": {},
    }
    for _f in list_files(language["path"], language["extensions"]):
        with open(_f, "r") as file:
            size += load_file_data(file, data)

    # Weight the data based on user preferences
    print("size: ", size)
    for char, value in data["letter_count"].items():
        data["letter_count"][char] = (
            float(value) * language["weight"] * 1000000.0 / float(size)
        )

    for lchar, ldata in data["bigrams"].items():
        for rchar, value in ldata.items():
            data["bigrams"][lchar][rchar] = (
                float(value) * language["weight"] * 1000000.0 / float(size)
            )
    return data


def load_file_data(file, data) -> int:
    size = 0
    for line in file.readlines():
        line = line.strip()
        line = clean_line(line)
        for word in line.split():
            load_word_data(word, data)
            size += len(word)
            data["letter_count"]["\\s"] = data["letter_count"].get("\\s", 0) + 1
        data["letter_count"]["\\n"] = data["letter_count"].get("\\n", 0) + 1
    return size


def load_word_data(word, data):
    p0, p1 = None, None
    for char in word:
        p0, p1 = char, p0
        data["letter_count"][p0] = data["letter_count"].get(p0, 0) + 1
        if p1 and p1 != p0:
            for f, l in [(p0, p1), (p1, p0)]:
                data["bigrams"][f] = data["bigrams"].get(f, {})
                data["bigrams"][f][l] = data["bigrams"][f].get(l, 0) + 1


def clean_line(line: str) -> str:
    # That map may need to be per language
    translate_map = {
        "\u2014": "-",
        "\u2019": "'",
        "\u201C": '"',
        "\u201D": '"',
    }
    # That map may need to be per language.
    allowlist = "abcdefghijklmnopqrstuvwxyz"

    _line = list(line)
    for _i, _c in enumerate(_line):
        tr = None
        if _c not in allowlist:
            tr = " "
        elif _c in translate_map.keys():
            tr = translate_map[_c]
        else:
            tr = _c.lower()
        _line[_i] = tr
    line = "".join(_line)
    line = line.strip()
    return line


def generate_code_data(languages: dict) -> dict:
    data = {}
    for language in languages.keys():
        print()
        print(language)
        get_sources(languages[language]["git_urls"], languages[language]["path"])
        data[language] = load_dir_data(languages[language])
    return data


def get_sources(urls: list[str], path: str) -> None:
    for url in urls:
        clone_path = path + "/" + url.replace("https://", "").replace("/", "___")
        if not os.path.exists(clone_path):
            git.Repo.clone_from(url, clone_path)
