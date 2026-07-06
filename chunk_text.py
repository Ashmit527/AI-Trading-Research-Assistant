import json
import os
import re

def is_table_heavy_chunk(text, digit_ratio_threshold=0.12, avg_word_len_threshold=4.2, symbol_ratio_threshold=0.05):
    """
    Flags a CHUNK (not a whole page) as table-heavy.
    Applied after chunking since tables and narrative text are often
    mixed on the same page.
    """
    if not text or len(text.strip()) < 30:
        return True  # empty/near-empty chunks are useless either way

    total_chars = len(text)
    digit_chars = sum(c.isdigit() for c in text)
    digit_ratio = digit_chars / total_chars

    # Symbols common in financial tables: – (nil), %, (), | 
    symbol_chars = sum(c in "–—|()%`" for c in text)
    symbol_ratio = symbol_chars / total_chars

    words = text.split()
    if len(words) == 0:
        return True
    avg_word_len = sum(len(w) for w in words) / len(words)

    # Real sentences have periods followed by space + capital letter
    sentence_like = len(re.findall(r'\.\s+[A-Z]', text))
    words_per_sentence_marker = len(words) / max(sentence_like, 1)

    # Flag as table-heavy if digit density is high AND
    # (words are short, OR symbols are dense, OR almost no real sentence breaks)
    if digit_ratio > digit_ratio_threshold and (
        avg_word_len < avg_word_len_threshold
        or symbol_ratio > symbol_ratio_threshold
        or words_per_sentence_marker > 40
    ):
        return True
    return False
def chunk_text(text, chunk_size=700, overlap=100):
    """
    Split text into overlapping chunks, measured in words (a rough proxy for tokens).
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start += chunk_size - overlap  # move forward, but overlap with previous chunk
    return chunks
def process_company(json_path, company_name):
    with open(json_path, "r", encoding="utf-8") as f:
        pages = json.load(f)

    all_chunks = []
    skipped_chunks = 0

    for page in pages:
        text = page["text"]
        page_num = page["page_number"]

        if not text or len(text.strip()) < 30:
            continue  # skip empty pages entirely

        page_chunks = chunk_text(text)
        for chunk in page_chunks:
            if is_table_heavy_chunk(chunk):
                skipped_chunks += 1
                continue  # skip this specific chunk
            all_chunks.append({
                "company": company_name,
                "page_number": page_num,
                "text": chunk
            })

    print(f"{company_name}: {len(pages)} pages, {skipped_chunks} chunks skipped (table-heavy), {len(all_chunks)} chunks kept")
    return all_chunks
if __name__ == "__main__":
    extracted_folder = "data/extracted_text"
    output_folder = "data/chunks"
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(extracted_folder):
        if filename.endswith(".json"):
            company_name = filename.replace(".json", "")
            json_path = os.path.join(extracted_folder, filename)

            chunks = process_company(json_path, company_name)

            output_path = os.path.join(output_folder, f"{company_name}_chunks.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, ensure_ascii=False, indent=2)