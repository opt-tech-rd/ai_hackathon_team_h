import streamlit as st
import os
import sys
import openai
from llama_index.core import StorageContext, load_index_from_storage


def load_index():
    print("Loading index...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.join(base_dir, ".kb")

    storage_context = StorageContext.from_defaults(persist_dir=dir_path)
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    print("Done.")
    return query_engine
