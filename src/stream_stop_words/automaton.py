from collections import deque
from typing import Deque, Generator, List

"""
This version uses an Aho–Corasick automaton built from all stop words.
The input stream is processed character by character by moving through the automaton.
When a stop word is detected, the exact start position is computed, all characters
before it are emitted, and the stream stops immediately. A safe prefix is emitted
eagerly to guarantee low latency. The algorithm works in O(N) time and supports
efficient matching of many long stop words in streaming mode.

Can read more here: https://www.geeksforgeeks.org/dsa/aho-corasick-algorithm-in-python/
"""

class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.output: List[str] = []
        self.fail: "TrieNode | None" = None


def build_automaton(stop_words: List[str]) -> TrieNode:
    root = TrieNode()
    for word in stop_words:
        node = root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.output.append(word)

    queue: List[TrieNode] = []
    for child in root.children.values():
        child.fail = root
        queue.append(child)

    while queue:
        current_node = queue.pop(0)
        for char, child in current_node.children.items():
            queue.append(child)
            fail_node = current_node.fail
            while fail_node is not None and char not in fail_node.children:
                fail_node = fail_node.fail
            child.fail = fail_node.children[char] if fail_node and char in fail_node.children else root
            if child.fail:
                child.output += child.fail.output

    return root


def cut_stream_stop_words_automaton(token_stream: Generator[str, None, None],
                                    stop_words: List[str],) -> Generator[str, None, None]:
    stop_words = [w for w in stop_words if w]
    if not stop_words:
        for token in token_stream:
            yield token
        return

    root = build_automaton(stop_words)

    buffer: Deque[str] = deque()
    processing_length = 0
    emitted_length = 0
    max_stop_word_length = max(len(w) for w in stop_words)
    state: TrieNode = root

    for token in token_stream:
        buffer.append(token)

        for ch in token:
            processing_length += 1

            while state is not None and ch not in state.children:
                state = state.fail
                if state is None:
                    state = root
                    break
            if ch in state.children:
                state = state.children[ch]

            cut_index = None

            if state.output:
                for pattern in state.output:
                    start_index = processing_length - len(pattern)
                    if cut_index is None or start_index < cut_index:
                        cut_index = start_index

            if cut_index is not None:
                remaining_length = cut_index - emitted_length
                while buffer and remaining_length > 0:
                    t = buffer[0]
                    if len(t) <= remaining_length:
                        yield t
                        emitted_length += len(t)
                        remaining_length -= len(t)
                        buffer.popleft()
                    else:
                        yield t[:remaining_length]
                        emitted_length += remaining_length
                        return
                return

            safe_yield_length = processing_length - (max_stop_word_length - 1)
            can_emit = safe_yield_length - emitted_length
            if can_emit <= 0:
                continue

            while buffer and can_emit > 0:
                t = buffer[0]
                if len(t) <= can_emit:
                    yield t
                    emitted_length += len(t)
                    can_emit -= len(t)
                    buffer.popleft()
                else:
                    break

    while buffer:
        yield buffer.popleft()

if __name__ == "__main__":
    # Example usage
    def example_stream() -> Generator[str, None, None]:
        for token in ["hello ab", "cd ef", "gh"]:
            yield token

    stop_words = ["efg", "o a"]
    result = list(cut_stream_stop_words_automaton(example_stream(), stop_words))
    print(result) 
