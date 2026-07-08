# =============================================================================
# chunker.py — PDF processing for PetroMind Knowledge AI
#
# Same proven pattern from OilMind — PyMuPDF page-by-page extraction
# with RecursiveCharacterTextSplitter for semantic chunk boundaries.
#
# Why reuse this pattern?
# It works. 568 chunks from OilMind produced 0.77 faithfulness on RAGAS.
# The chunking strategy is validated — no reason to change it.
# =============================================================================

import os
import sys
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from backend.core.config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Reads PDF page by page — preserving page number metadata.
    Page numbers are what enable source citations in answers.
    """
    filename = os.path.basename(pdf_path)
    pages = []
    doc = fitz.open(pdf_path)

    print(f"📄 Reading: {filename} ({len(doc)} pages)")

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")

        if len(text.strip()) < 50:
            continue

        pages.append({
            "page_number": page_num + 1,
            "text": text.strip(),
            "source": filename
        })

    doc.close()
    print(f"   ✅ Extracted {len(pages)} pages with content")
    return pages


def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Splits pages into CHUNK_SIZE token chunks with CHUNK_OVERLAP overlap.
    RecursiveCharacterTextSplitter respects paragraph and sentence
    boundaries — critical for oil & gas procedural documents.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
        length_function=len
    )

    all_chunks = []

    for page in pages:
        texts = splitter.split_text(page["text"])

        for chunk_index, chunk_text in enumerate(texts):
            chunk_id = (
                f"{page['source'].replace('.', '_')}"
                f"_p{page['page_number']}"
                f"_c{chunk_index}"
            )

            all_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "source": page["source"],
                "page_number": page["page_number"],
                "chunk_index": chunk_index
            })

    return all_chunks


def process_all_documents(corpus_dir: str) -> list[dict]:
    """
    Master function — processes every PDF in corpus directory.
    Called by indexer.py to build the Qdrant collection.
    """
    all_chunks = []

    pdf_files = [
        f for f in os.listdir(corpus_dir)
        if f.endswith('.pdf')
    ]

    if not pdf_files:
        raise ValueError(f"No PDF files found in {corpus_dir}")

    print(f"\n🗂️  Found {len(pdf_files)} documents:")
    for f in pdf_files:
        print(f"   - {f}")
    print()

    for pdf_file in pdf_files:
        pdf_path = os.path.join(corpus_dir, pdf_file)
        pages = extract_text_from_pdf(pdf_path)
        chunks = chunk_pages(pages)
        print(f"   📦 Created {len(chunks)} chunks from {pdf_file}")
        all_chunks.extend(chunks)

    print(f"\n✅ Total chunks: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    corpus_dir = os.path.join(
        os.path.dirname(__file__), '..', '..', '..', 'corpus', 'raw'
    )
    chunks = process_all_documents(corpus_dir)
    if chunks:
        sample = chunks[5]
        print(f"\nSample chunk:")
        print(f"  ID:     {sample['chunk_id']}")
        print(f"  Source: {sample['source']}")
        print(f"  Page:   {sample['page_number']}")
        print(f"  Text:   {sample['text'][:200]}...")