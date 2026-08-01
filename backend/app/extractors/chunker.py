from typing import List
import re
from app.schemas.parsed_document import ContentBlock

class Chunker:
    @staticmethod
    def chunk_document(content_blocks: List[ContentBlock], max_words_per_chunk: int = 1500) -> List[List[ContentBlock]]:
        """
        Splits parsed content blocks into chunks without breaking cohesive boundaries:
        - Never splits a single block (e.g. tables are single blocks).
        - Keeps slide content together (if slide numbers match).
        - Keeps heading blocks and their immediately following block together.
        - Keeps consecutive bullet list items together.
        """
        chunks = []
        current_chunk: List[ContentBlock] = []
        current_word_count = 0
        
        def get_word_count(block: ContentBlock) -> int:
            if block.content_type == "table" and block.rows:
                return sum(
                    len(str(cell).split()) 
                    for row in block.rows 
                    for cell in row 
                    if cell
                )
            return len(block.raw_text.split())

        def is_heading(block: ContentBlock) -> bool:
            text = block.raw_text.strip()
            # Starts with MD headers or is short single-line text
            return (
                text.startswith(('#', '##', '###', '####')) or 
                (len(text.split()) < 15 and '\n' not in text and not text.startswith(('-', '*', '•')))
            )

        def is_list_item(block: ContentBlock) -> bool:
            text = block.raw_text.strip()
            return text.startswith(('-', '*', '•', '1.', '2.', '3.', '4.', '5.')) or bool(re.match(r'^\d+\.', text))

        for idx, block in enumerate(content_blocks):
            block_words = get_word_count(block)
            
            # Decide if we must force keeping the current block with the previous one
            force_together = False
            if current_chunk:
                prev_block = current_chunk[-1]
                
                # Rule 1: Keep blocks on the same slide/page together if possible
                if (
                    prev_block.slide is not None and 
                    block.slide is not None and 
                    prev_block.slide == block.slide
                ):
                    force_together = True
                
                # Rule 2: Do not split heading and the following block
                elif is_heading(prev_block):
                    force_together = True
                    
                # Rule 3: Keep consecutive bullet list items together
                elif is_list_item(prev_block) and is_list_item(block):
                    force_together = True
                    
                # Rule 4: Keep consecutive rows (e.g. tables on the same sheet)
                elif (
                    prev_block.sheet is not None and 
                    block.sheet is not None and 
                    prev_block.sheet == block.sheet and 
                    (prev_block.content_type == "table" or block.content_type == "table")
                ):
                    force_together = True

            if current_chunk and not force_together and (current_word_count + block_words > max_words_per_chunk):
                # Push the current chunk and start a new one
                chunks.append(current_chunk)
                current_chunk = [block]
                current_word_count = block_words
            else:
                current_chunk.append(block)
                current_word_count += block_words
                
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
