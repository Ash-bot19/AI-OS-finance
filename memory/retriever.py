from typing import List

def retrieve(query: str, top_k: int = 5) -> List[str]:
    """
    Retrieval hook.
    MUST be called before any generation.
    v1 returns empty list or mock docs.
    """
    return []
