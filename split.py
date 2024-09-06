import re

async def splitmsg(text, max_length=2000):
    def split_large_segment(segment, max_length):
        parts = []
        while len(segment) > max_length:
            last_space = segment.rfind(' ', 0, max_length)
            if last_space == -1:
                last_space = max_length
            parts.append(segment[:last_space])
            segment = segment[last_space:].lstrip()
        parts.append(segment)
        return parts

    segments = []
    pattern = re.compile(r'```(.*?)```', re.DOTALL)
    pos = 0

    for match in pattern.finditer(text):
        pre_text = text[pos:match.start()]
        if pre_text:
            pre_segments = split_large_segment(pre_text, max_length)
            if pre_segments:
                code_block = match.group()
                if len(pre_segments[-1] + code_block) <= max_length:
                    pre_segments[-1] += code_block
                    code_block = None
                segments.extend(pre_segments)
        if code_block:
            if len(code_block) > max_length:
                language = re.match(r'```(\w+)', code_block)
                lang = language.group(1) if language else ''
                code_content = code_block[len(lang)+3:-3]
                block_parts = split_large_segment(code_content, max_length-len(lang)-6)
                segments.extend([f'```{lang}\n{part}\n```' for part in block_parts])
            else:
                segments.append(code_block)
        pos = match.end()
    if pos < len(text):
        segments.extend(split_large_segment(text[pos:], max_length))
    
    final_segments = []
    for segment in segments:
        if len(segment) > max_length:
            final_segments.extend(split_large_segment(segment, max_length))
        else:
            final_segments.append(segment)
    
    return final_segments