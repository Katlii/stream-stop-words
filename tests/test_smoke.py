from pathlib import Path
from typing import Generator, List
import sys
import re
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stream_stop_words.streaming import cut_stream_stop_words


def make_stream(tokens: List[str]) -> Generator[str, None, None]:
    for t in tokens:
        yield t


def load_tokens_from_quoted_file(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8")
    return re.findall(r'"(.*?)"', text) # will extract all quoted tokens

def test_big_dataset_smoke():
    tokens = load_tokens_from_quoted_file(
        Path(__file__).parent / "data" / "big_tokens.txt"
    )
    stop_words = ["svet"]

    result = list(cut_stream_stop_words(make_stream(tokens), stop_words))
    print(result)
