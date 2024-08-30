import logging
import os
import sys
from shutil import rmtree

from llama_index.core import Settings, SimpleDirectoryReader, TreeIndex
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

Settings.llm = OpenAI(model="gpt-4o-mini")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large")


def build_index(data_dir: str, knowledge_base_dir: str) -> None:
    print("Building vector index...")
    documents = SimpleDirectoryReader(data_dir).load_data()

    index = TreeIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=knowledge_base_dir)
    print("Done.")


def main() -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    knowledge_base_dir = os.path.join(base_dir, ".kb")

    if os.path.exists(knowledge_base_dir):
        rmtree(knowledge_base_dir)
    data_dir = os.path.join(base_dir, "data")
    build_index(data_dir, knowledge_base_dir)


if __name__ == "__main__":
    main()
