from collections import deque

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
        self.children = {}
        self.output = []
        self.fail = None


def build_automaton(keywords):
    root = TrieNode()

    # Build trie
    for word in keywords:
        node = root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.output.append(word)

    # Build failure links (BFS)
    queue = []
    for node in root.children.values():
        node.fail = root
        queue.append(node)

    while queue:
        current = queue.pop(0)
        for ch, child in current.children.items():
            queue.append(child)
            fail_node = current.fail
            while fail_node and ch not in fail_node.children:
                fail_node = fail_node.fail
            child.fail = fail_node.children[ch] if fail_node else root
            child.output += child.fail.output

    return root


def cut_stream_stop_words_automaton(token_stream, stop_words):
    stop_words = [w for w in stop_words if w]
    if not stop_words:
        for token in token_stream:
            yield token
        return

    root = build_automaton(stop_words)

    buffer = deque()
    processing_length = 0
    emitted_length = 0
    max_stop_word_length = max(len(w) for w in stop_words)

    state = root

    for token in token_stream:
        buffer.append(token)

        for ch in token:
            processing_length += 1

            while state and ch not in state.children:
                state = state.fail
            if not state:
                state = root
                continue
            state = state.children[ch]

            cut_index = None

            if state.output:
                for word in state.output:
                    start_index = processing_length - len(word)
                    if cut_index is None or start_index < cut_index:
                        cut_index = start_index

            if cut_index is not None:
                remaining = cut_index - emitted_length

                while buffer and remaining > 0:
                    t = buffer[0]
                    if len(t) <= remaining:
                        yield t
                        emitted_length += len(t)
                        remaining -= len(t)
                        buffer.popleft()
                    else:
                        yield t[:remaining]
                        emitted_length += remaining
                        return
                return

            safe_yield = processing_length - (max_stop_word_length - 1)
            can_emit = safe_yield - emitted_length

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

# example usage
def example_stream():
    for token in ["hello ab", "cd ef", "gh"]:
        yield token

stop_words = ["efg", "o a"]

print(list(cut_stream_stop_words_automaton(example_stream(), stop_words)))