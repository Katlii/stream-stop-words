from typing import Generator, List
from collections import deque


def cut_stream_stop_words(token_stream: Generator[str, None, None],
    stop_words: List[str],) -> Generator[str, None, None]:

    # If stop words list is empty, yield all tokens as is
    if not stop_words:
        yield from token_stream
        return
    buffer = deque()  # holds tokens to be emitted               
    tail = ""         # holds the end of the current processed stream              
    processing_length = 0   # total length of processed characters       
    emitted_length = 0       # total length of emitted characters      

    max_stop_word_length = max(len(sw) for sw in stop_words)

    for token in token_stream:
        buffer.append(token)

        for char_in_token in token:
            processing_length += 1
            tail += char_in_token

            # Keep tail length manageable
            if len(tail) > max_stop_word_length: 
                tail = tail[-max_stop_word_length:]

            cut_index = None  # position to cut the stream if a stop word is found, None otherwise

            for stop_word in stop_words:
                l = len(stop_word)
                # Check if the stop word matches the end of the tail, we use l because stop_word can be shorter than tail
                if l <= len(tail) and tail[-l:] == stop_word:
                    start_index = processing_length - l
                    if cut_index is None or start_index < cut_index:
                        cut_index = start_index

            # If we found a stop word, cut the stream
            if cut_index is not None:
                remaining_length = cut_index - emitted_length # how many characters we can still emit before the cut

                # Emit up to remaining_length characters from the buffer
                while buffer and remaining_length > 0:
                    t = buffer[0] 
                    # Try to emit the whole token, otherwise emit part of it and stop
                    if len(t) <= remaining_length:
                        yield t
                        emitted_length += len(t)
                        remaining_length -= len(t)
                        buffer.popleft()
                    else:
                        yield t[:remaining_length]
                        emitted_length += remaining_length
                        return  
                # If we emitted exactly up to the cut index, we stop processing further
                return  

            # Calculate safe yield length for stream continuation, ensuring no stop word can be formed
            # Safe charecter are considered those that are beyond the length of the longest stop word minus one
            # Like if we have "abcdef" and the longest stop word is "defg" (length 4), we can safely emit up to "abc"
            safe_yield_length = processing_length - (max_stop_word_length - 1)

            can_emit = safe_yield_length - emitted_length
            if can_emit <= 0:
                continue # nothing to emit yet
            
            # Emit safe characters from the buffer while we can emit 
            while buffer and can_emit > 0:
                t = buffer[0]
                if len(t) <= can_emit:
                    yield t
                    emitted_length += len(t)
                    can_emit -= len(t)
                    buffer.popleft()
                else:
                    break

    # If no stop words were found in the entire stream, emit the rest of the buffer
    while buffer:
        yield buffer.popleft()
