import os
import streamlit as st
from llama_index.core import StorageContext, load_index_from_storage


def load_index():
    print("Loading index...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_path = os.path.join(base_dir, ".kb")

    storage_context = StorageContext.from_defaults(persist_dir=dir_path)
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    print("Done.")
    return query_engine


def main() -> None:
    st.title("RAG Chatbot")

    if "messages" not in st.session_state:
        system_prompt = (
            "Your purpose is to answer questions about specific documents only. "
            "Please answer the user's questions based on what you know about the document. "
            "If the question is outside scope of the document, please politely decline. "
            "If you don't know the answer, say `I don't know`. "
        )
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "assistant",
                "content": "何か手伝えることはありますか？なんでもおっしゃってください。",
            },
        ]

    if "query_engine" not in st.session_state:
        st.session_state.query_engine = load_index()

    for msg in st.session_state.messages:
        if msg["role"] not in ["user", "assistant"]:
            continue
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        response = st.session_state.query_engine.query(prompt)
        st.session_state.messages.append(
            {"role": "assistant", "content": f"{response}"}
        )
        st.chat_message("assistant").write(f"{response}")


if __name__ == "__main__":
    main()
