import os
import sys
import time
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from backend.core.llm import get_llm
from backend.modules.knowledge.indexer import search_qdrant


class KnowledgeState(TypedDict):
    query: str
    retrieved_chunks: list[dict]
    answer: str
    sources: list[str]
    latency_seconds: float
    chunks_retrieved: int


def retrieve_node(state: KnowledgeState) -> KnowledgeState:
    chunks = search_qdrant(state["query"], top_k=5)
    state["retrieved_chunks"] = chunks
    state["chunks_retrieved"] = len(chunks)
    return state


def generate_node(state: KnowledgeState) -> KnowledgeState:
    llm = get_llm(temperature=0.0)

    context = "\n\n".join([
        f"[Source: {c['source']}, Page {c['page_number']}]\n{c['text']}"
        for c in state["retrieved_chunks"]
    ])

    sources = list(set([
        f"{c['source']}, Page {c['page_number']}"
        for c in state["retrieved_chunks"]
    ]))

    system_prompt = """You are PetroMind Knowledge AI — an expert technical
assistant for oil and gas operations.
Answer questions using ONLY the provided context.
Every claim must be supported by the retrieved documents.
If the answer is not in the context, say so clearly.
Always cite your sources by document name and page number.
Be precise and technical — your answers inform operational decisions."""

    user_prompt = f"""Context from technical documents:

{context}

Question: {state['query']}

Provide a precise, cited answer based strictly on the context above."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    state["answer"] = response.content
    state["sources"] = sources
    return state


def build_knowledge_agent():
    graph = StateGraph(KnowledgeState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()


def run_knowledge_query(query: str) -> dict:
    start_time = time.time()
    agent = build_knowledge_agent()

    initial_state = KnowledgeState(
        query=query,
        retrieved_chunks=[],
        answer="",
        sources=[],
        latency_seconds=0.0,
        chunks_retrieved=0
    )

    result = agent.invoke(initial_state)
    latency = round(time.time() - start_time, 2)
    result["latency_seconds"] = latency

    return {
        "query": query,
        "answer": result["answer"],
        "sources": result["sources"],
        "chunks_retrieved": result["chunks_retrieved"],
        "latency_seconds": latency,
        "module": "knowledge_ai"
    }


if __name__ == "__main__":
    print("Testing Knowledge AI Agent...")
    print("=" * 60)
    result = run_knowledge_query(
        "What is the H2S exposure limit for workers in oil and gas?"
    )
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources: {result['sources']}")
    print(f"Chunks retrieved: {result['chunks_retrieved']}")
    print(f"Latency: {result['latency_seconds']}s")
