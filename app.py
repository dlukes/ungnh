#!/usr/bin/env python3

from collections import defaultdict, Counter
import typing as t


def vert_sents(vert: t.Iterable[str]) -> t.Iterator[list[str]]:
    sent = []
    for line in vert:
        line = line.rstrip("\n")
        if line == "<s>":
            sent = []
        elif line == "</s>":
            yield sent
        else:
            word, _, _ = line.split("\t")
            sent.append(word)


def ngrams(n: int, tokens: list[str]) -> t.Iterator[tuple[str]]:
    for i in range(len(tokens)):
        ngram = tokens[i : i + n]
        if len(ngram) == n:
            yield tuple(ngram)
        else:
            return


def update_counts(n: int, model: defaultdict[tuple, Counter], tokens: list[str]):
    for ngram in ngrams(n, tokens):
        ctx, rest = ngram[: n - 1], ngram[n - 1]
        model[ctx][rest] += 1


uni = defaultdict(Counter)
bi = defaultdict(Counter)
tri = defaultdict(Counter)
with open("pdt3.train.vrt", encoding="utf-8") as file:
    for sent in vert_sents(file):
        update_counts(1, uni, sent)
        update_counts(2, bi, sent)
        update_counts(3, tri, sent)


def complete_one(
    n: int, model: defaultdict[tuple, Counter], sent: list[str]
) -> str | None:
    ctx = tuple(sent[-n + 1 :]) if n > 1 else ()
    completion = model[ctx].most_common(1)
    if len(completion) == 1:
        return completion[0][0]


def generate(prompt: list[str]) -> list[str]:
    ans = prompt.copy()
    for _ in range(15):
        for n, model in zip(range(3, 0, -1), (tri, bi, uni)):
            completion = complete_one(n, model, ans)
            if completion is not None:
                ans.append(completion)
                break
    return ans[len(prompt) :]


while True:
    prompt = input("> ").split()
    print(" ", " ".join(generate(prompt)))
