# Stream Stop Words

Stream Stop Words is a small Python utility for real-time stop-word filtering in token streams. Tokens are processed one by one, and the stream is stopped immediately when a stop word appears in the concatenated text. The stop word itself and everything after it are never returned. 

The algorithm processes the input stream character by character and keeps only a short sliding buffer called `tail`, which stores the last L characters, where L is the length of the longest stop word. 
Each new character is appended to this buffer and the algorithm checks whether any stop word matches the suffix of `tail`. If a stop word is detected, the exact start position of this stop word is computed, only the characters before this position are emitted, and the stream stops immediately. 
If no stop word is detected, safe parts of the already processed data are emitted early to guarantee low latency. The algorithm never loads the entire input into memory and works in true streaming mode.

Time complexity is O(N · K · L), where N is the total number of characters in the stream, K is the number of stop words (≤ 10), and L is the maximum stop-word length (≤ 50). Since K and L are small constants, the effective time complexity is O(N). Space complexity is O(1), because only a fixed-size suffix buffer and a small queue of un-emitted tokens are stored.


Basic usage:

from stream_stop_words.streaming import cut_stream_stop_words

def token_stream():
    yield "Ah"
    yield "oj,"
    yield " sv"
    yield "ete"
    yield "!"

stop_words = ["svet"]

result = list(cut_stream_stop_words(token_stream(), stop_words))
print(result)

Expected output:
['Ah', 'oj,', ' ']

# Example of usage with a file. 
You can create a large token file at tests/data/big_tokens.txt (tokens quoted and comma-separated, e.g. "Hello", "this", "is", "svet", ...).

Then run the smoke test from the repo root:

```bash
# with venv activated
python -m pytest -s tests/test_smoke.py

# or if pytest is on PATH
pytest -s tests/test_smoke.py
```

This will stream the tokens from tests/data/big_tokens.txt and show test output in real time.

# Other approach

This can be implemented with different automaton-based techniques:

- Aho–Corasick: build a trie of all stop words with failure links to detect matches in a single pass (linear time in the total input length).
- Simple state-based automaton: track prefix-match lengths for each stop word and update them per character; simpler to implement and often sufficient when the number of stop words and their lengths are small. This approach is almost the same as using a `tail`.
