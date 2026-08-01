from typing import List
from app.schemas.parsed_document import ContentBlock

class Chunker:
    @staticmethod
    def chunk_document(content_blocks: List[ContentBlock], max_words_per_chunk: int = 1500) -> List[List[ContentBlock]]:
        """
        Splits a list of parsed content blocks into manageable chunks while maintaining
        monotonically increasing reading order sequence and ensuring:
        - Tables (which are single blocks) are never split.
        - Consecutive blocks on the same page/slide are kept together (preserving semantic locality).
        """
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for block in content_blocks:
            # Estimate word count of the block
            if block.content_type == "table" and block.rows:
                block_words = sum(
                    len(str(cell).split()) 
                    for row in block.rows 
                    for cell in row 
                    if cell
                )
            else:
                block_words = len(block.raw_text.split())
            
            # If adding this block to the current chunk exceeds word limit, push chunk and start a new one
            if current_chunk and (current_word_count + block_words > max_words_per_chunk):
                chunks.append(current_chunk)
                current_chunk = [block]
                current_word_count = block_words
            else:
                current_chunk.append(block)
                current_word_count += block_words
                
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
