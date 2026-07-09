import os
import sys
import json
import time
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from backend.modules.knowledge.agent import run_knowledge_query
from backend.modules.knowledge.indexer import search_qdrant


def load_test_set(path: str) -> list[dict]:
    with open(path, 'r') as f:
        data = json.load(f)
    return data['test_cases']


def collect_rag_results(test_cases: list[dict]) -> list[dict]:
    print(f"\n🔄 Running {len(test_cases)} questions through PetroMind Knowledge AI...")
    results = []

    for i, case in enumerate(test_cases, 1):
        print(f"   [{i}/{len(test_cases)}] {case['question'][:60]}...")
        try:
            result = run_knowledge_query(case['question'])
            chunks = search_qdrant(case['question'], top_k=5)
            contexts = [c['text'] for c in chunks]

            results.append({
                'question': case['question'],
                'answer': result['answer'],
                'contexts': contexts,
                'ground_truth': case['reference_answer'],
                'category': case['category']
            })
            time.sleep(1)
        except Exception as e:
            print(f"   Error on question {i}: {e}")
            continue

    print(f"\nCollected {len(results)} results")
    return results


def run_ragas_evaluation(results: list[dict]):
    ragas_data = {
        'question': [r['question'] for r in results],
        'answer': [r['answer'] for r in results],
        'contexts': [r['contexts'] for r in results],
        'ground_truth': [r['ground_truth'] for r in results]
    }
    dataset = Dataset.from_dict(ragas_data)

    judge_llm = AzureChatOpenAI(
        azure_deployment="gpt-4o",
        azure_endpoint="https://oilmind-openai.openai.azure.com/",
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-08-01-preview",
        temperature=0
    )
    judge_embeddings = AzureOpenAIEmbeddings(
        azure_deployment="text-embedding-3-large",
        azure_endpoint="https://oilmind-openai.openai.azure.com/",
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-08-01-preview"
    )

    from ragas.run_config import RunConfig

    scores = evaluate(
        dataset=dataset,
        metrics=[context_precision],
        llm=judge_llm,
        embeddings=judge_embeddings,
        run_config=RunConfig(timeout=300, max_workers=1)
    )
    return scores.to_pandas()


def display_results(df, results):
    import json
    from datetime import datetime

    print("\n" + "=" * 60)
    print("PetroMind - RAGAS Evaluation Results (Qdrant Retrieval)")
    print("=" * 60)

    metric_cols = ['faithfulness', 'answer_relevancy',
                   'context_precision', 'context_recall']
    scores = {}

    for col in metric_cols:
        if col in df.columns:
            scores[col] = float(df[col].mean())
            print(f"{col}: {scores[col]:.3f}")
        else:
            print(f"{col}: not computed in this run")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = {
        "timestamp": timestamp,
        "vector_db": "Qdrant",
        "scores": scores,
        "test_set_size": len(results)
    }
    with open(f"backend/evaluation/ragas_results_{timestamp}.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to ragas_results_{timestamp}.json")
    return scores


if __name__ == "__main__":
    test_cases = load_test_set(
        os.path.join(os.path.dirname(__file__), 'test_set.json')
    )
    results = collect_rag_results(test_cases)
    df = run_ragas_evaluation(results)
    display_results(df, results)
