import os
import streamlit as st
import pandas as pd
from llama_index.core import StorageContext, load_index_from_storage


def convert_df_to_markdown(input_df: pd.DataFrame) -> str:
    return input_df.to_markdown(index=False)


def load_data() -> None:
    file_path = st.session_state.file_uploader

    try:
        st.session_state.file_df = pd.read_csv(
            file_path, header=2, encoding="utf-8-sig"
        )
    except FileNotFoundError:
        st.error("ファイルのアップロードに失敗しました。")
        st.button("最初の画面に戻る")
        st.stop()


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
    st.markdown("### 運用施策回答BOT")

    if "messages" not in st.session_state:
        system_prompt = """
            Your purpose is to answer questions about specific documents only. 
            Please answer the user's questions based on what you know about the document. 
            If the question is outside scope of the document, please politely decline. 
            If you don't know the answer, say `I don't know`.

            Answer polite in Japanese.
            """

        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            # {
            #     "role": "assistant",
            #     "content": "ファイルをアップロードして、要因分析に関する質問をしてください。",
            # },
        ]

    with st.chat_message("assistant"):
        st.write(
            "ファイルをアップロードして、変動要因の箇所を示した上で質問してください。"
        )
        st.file_uploader(
            "",
            type=["csv"],
            key="file_uploader",
            label_visibility="collapsed",
        )

    if "query_engine" not in st.session_state:
        st.session_state.query_engine = load_index()

    for msg in st.session_state.messages:
        if msg["role"] not in ["user", "assistant"]:
            continue
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        load_data()
        prompt += f"""
            See attached data below.
            Answer polite in Japanese.
            
            ### data ###
            {convert_df_to_markdown(st.session_state.file_df)}
        """
        response = st.session_state.query_engine.query(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(f"{response}")


if __name__ == "__main__":
    main()
