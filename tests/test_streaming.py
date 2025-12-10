# tests/test_streaming.py

from pathlib import Path
from typing import Generator, List
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stream_stop_words.streaming import cut_stream_stop_words


def make_stream(tokens: List[str]) -> Generator[str, None, None]:
    for t in tokens:
        yield t


def test_example_1():
    tokens = ["Ah", "oj,", " sv", "ete", "!"]
    stop_words = ["svet"]
    expected = ["Ah", "oj,", " "]
    assert list(cut_stream_stop_words(make_stream(tokens), stop_words)) == expected


def test_no_stop_word():
    tokens = ["ah", "oj", "ka", "da"]
    stop_words = ["svet"]
    expected = ["ah", "oj", "ka", "da"]
    assert list(cut_stream_stop_words(make_stream(tokens), stop_words)) == expected


def test_inside_one_token():
    tokens = ["hello svet world"]
    stop_words = ["svet"]
    expected = ["hello "]
    assert list(cut_stream_stop_words(make_stream(tokens), stop_words)) == expected


def test_across_tokens():
    tokens = ["ka sv", "et"]
    stop_words = ["svet"]
    expected = ["ka "]
    assert list(cut_stream_stop_words(make_stream(tokens), stop_words)) == expected


def test_multiple_stop_words():
    tokens = ["hello ab", "cd ef", "gh"]
    stop_words = ["efg", "o a"]
    expected = ["hell"]
    assert list(cut_stream_stop_words(make_stream(tokens), stop_words)) == expected


def test_empty_stop_words():
    tokens = ["foo", "bar"]
    stop_words: List[str] = []
    expected = ["foo", "bar"]
    assert list(cut_stream_stop_words(make_stream(tokens), stop_words)) == expected

def test_stop_word_at_the_beginning():
    tokens = ["svet hello", "world"]
    stop_words = ["svet"]
    expected = []
    assert list(cut_stream_stop_words(make_stream(tokens), stop_words)) == expected

def test_stop_word_at_the_end():
    tokens = ["hello world svet"]
    stop_words = ["svet"]
    expected = ["hello world "]
    assert list(cut_stream_stop_words(make_stream(tokens), stop_words)) == expected

def test_overlapping_stop_words():
    tokens = ["ab", "cde", "fgh"]
    stop_words = ["cde", "def"]
    expected = ["ab"]
    assert list(cut_stream_stop_words(make_stream(tokens), stop_words)) == expected 

def test_stop_word_longer_than_tokens():
    tokens = ["hi", "there"]
    stop_words = ["hitheree"]
    expected = ["hi", "there"]
    assert list(cut_stream_stop_words(make_stream(tokens), stop_words)) == expected

