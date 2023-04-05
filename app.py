#!/usr/bin/env python3

from collections import defaultdict, Counter
import random
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


def normalize_model(
    model: defaultdict[tuple, Counter]
) -> dict[tuple, dict[str, float]]:
    # Normalization gives more weight to the higher-n models, where there are fewer
    # alternatives for any given context. These alternatives also have lower absolute
    # counts, so unless relativized, they would be heavily disadvantaged, when in fact
    # we want to advantage them, as they'll typically be more pertinent.
    normalized = {}
    for ctx, freq_dist in model.items():
        normalized[ctx] = {}
        total = freq_dist.total()
        for type_, freq in freq_dist.items():
            normalized[ctx][type_] = freq / total
    return normalized


uni = defaultdict(Counter)
bi = defaultdict(Counter)
tri = defaultdict(Counter)
four = defaultdict(Counter)
five = defaultdict(Counter)
with open("pdt3.train.vrt", encoding="utf-8") as file:
    for sent in vert_sents(file):
        update_counts(1, uni, sent)
        update_counts(2, bi, sent)
        update_counts(3, tri, sent)
        update_counts(4, four, sent)
        update_counts(5, five, sent)
uni = normalize_model(uni)
bi = normalize_model(bi)
tri = normalize_model(tri)
four = normalize_model(four)
five = normalize_model(five)


def candidates_with_weights(
    n: int, model: dict[tuple, dict[str, float]], sent: list[str]
) -> tuple[list[str], list[float]]:
    ctx = tuple(sent[-n + 1 :]) if n > 1 else ()
    freq_dist = model.get(ctx, {})
    return list(freq_dist.keys()), list(freq_dist.values())


def generate(prompt: list[str]) -> list[str]:
    ans = prompt.copy()
    sources = Counter()
    for _ in range(15):
        candidates, weights = [], []
        for n, model in enumerate((uni, bi, tri, four, five), start=1):
            cs, ws = candidates_with_weights(n, model, ans)
            candidates.extend((c, n) for c in cs)
            weights.extend(ws)
        completion, source = random.choices(candidates, weights)[0]
        sources[source] += 1
        ans.append(completion)
    print("Completion sources:", sources.most_common())
    return ans[len(prompt) :]


while True:
    prompt = input("> ").split()
    print(" ", " ".join(generate(prompt)))
