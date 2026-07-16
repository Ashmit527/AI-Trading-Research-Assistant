import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Load once, at import time - reused across all calls
print("Loading embedding model and FAISS index for document search...")
_embed_model = SentenceTransformer('all-MiniLM-L6-v2')
_index = faiss.read_index("data/faiss_index.bin")

with open("data/chunk_metadata.pkl", "rb") as f:
    _metadata = pickle.load(f)

print("Document search tool ready.\n")


def search_documents(query: str, company_key: str = None, k: int = 5) -> dict:
    """
    Search annual report filings for relevant text passages.
    Use this for qualitative/narrative questions - risk factors, strategy,
    management commentary, business descriptions. NOT good for precise
    numeric lookups (use live data tools instead for those).

    query: the search question
    company_key: optional filter, e.g. 'tatamotors_ar25' - if provided,
                 only returns chunks from that company's filing
    k: number of chunks to retrieve
    """
    query_embedding = _embed_model.encode([query]).astype("float32")

    # Retrieve more than k if filtering by company, since some may get filtered out
    search_k = k * 4 if company_key else k
    distances, indices = _index.search(query_embedding, search_k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        chunk_info = _metadata[idx]

        if company_key and chunk_info["company"] != company_key:
            continue

        results.append({
            "company": chunk_info["company"],
            "page_number": chunk_info["page_number"],
            "text": chunk_info["text"],
            "relevance_distance": float(dist)
        })

        if len(results) >= k:
            break

    if not results:
        return {
            "query": query,
            "results": [],
            "note": f"No relevant chunks found{' for ' + company_key if company_key else ''}."
        }

    return {
        "query": query,
        "results": results
    }


if __name__ == "__main__":
    # Test without company filter
    result = search_documents("What risks does the company face related to raw material costs?")
    print(f"Found {len(result['results'])} results (no filter)")
    for r in result['results'][:2]:
        print(f"  - {r['company']}, page {r['page_number']}, distance {r['relevance_distance']:.3f}")

    # Test with company filter
    result2 = search_documents("What is the company's growth strategy?", company_key="tatamotors_ar25")
    print(f"\nFound {len(result2['results'])} results (filtered to tatamotors_ar25)")
    for r in result2['results'][:2]:
        print(f"  - {r['company']}, page {r['page_number']}, distance {r['relevance_distance']:.3f}")