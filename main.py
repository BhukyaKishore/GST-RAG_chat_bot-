import argparse
import sys
from app.ingestion.ingest import ingest_data
from app.rag.chain import build_rag_chain

def main():
    parser = argparse.ArgumentParser(description="Modular RAG Application")
    parser.add_argument("--ingest", action="store_true", help="Run data ingestion")
    args = parser.parse_args()

    if args.ingest:
        ingest_data()
        sys.exit(0)

    print("Initializing RAG Chain...")
    try:
        rag_chain = build_rag_chain()
    except Exception as e:
        print(f"Error initializing RAG chain: {e}")
        print("Make sure you have set OPENAI_API_KEY in .env and installed dependencies.")
        sys.exit(1)

    print("\n---------------------------------------------------------")
    print("RAG Application Ready! Type 'exit' or 'quit' to stop.")
    print("---------------------------------------------------------")

    while True:
        try:
            query = input("\nEnter your question: ")
            if query.lower() in ["exit", "quit"]:
                break
            
            if not query.strip():
                continue

            print("Thinking...")
            response = rag_chain.invoke({"input": query})
            print(f"\nAnswer: {response['answer']}")
            
            # Optional: Print source documents
            # print("\nSources:")
            # for doc in response['context']:
            #     print(f"- {doc.metadata.get('source', 'Unknown')}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
