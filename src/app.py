import os
import streamlit as st
import pandas as pd
from functools import partial
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


def load_data() -> None:
    file_paths = st.session_state.file_uploader

    try:
        file_dfs = [
            pd.read_csv(file_path, header=2, encoding="utf-8-sig")
            for file_path in file_paths
        ]
        st.session_state.file_df = pd.concat(file_dfs, ignore_index=True)
    except FileNotFoundError:
        st.error("ファイルのアップロードに失敗しました。")
        st.button("最初の画面に戻る")
        st.stop()


def click_button(bullet_point: str):
    print(bullet_point)
    assistant_response = "以下の回答について、さらに質問することができます。" + "\n"
    assistant_response += f"- {bullet_point}\n"
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_response,
        }
    )


def main() -> None:
    st.markdown("# Adviser")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": """
                    Your purpose is to answer questions about specific documents only. 
                    Please answer the user's questions based on what you know about the document. 
                    If the question is outside scope of the document, please politely decline. 
                    If you don't know the answer, say `I don't know`.

                    Answer polite in Japanese.
                    """,
            },
        ]

    with st.chat_message("assistant"):
        st.write("数値変動が発生しているCSVファイルをアップロードしてください。")
        st.file_uploader(
            "",
            type=["csv"],
            accept_multiple_files=True,
            key="file_uploader",
            label_visibility="collapsed",
        )

    with st.chat_message("assistant"):
        st.write("以下のフォーマットに沿った質問を入力してください。")
        st.code(
            """
            案件名：〇〇
            比較時期：~~~に対して~~~
            質問：指標〇〇をこの時期あるいはこの数値まで上げたい。
            """
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
            Generate multiple bullet points only regarding factors and measures.
            Answer polite in Japanese.
            
            ### data ###
            {st.session_state.file_df.to_markdown(index=False)}
            """

        with st.spinner("回答を生成中..."):
            response = st.session_state.query_engine.query(prompt).response

            # responseが箇条書きの場合を想定
            # 現状、一番上のradioボタンしか取得できていないので、この部分を改善したい。
            bullet_points = response.split("-")
            if len(bullet_points) > 1:
                with st.chat_message("assistant"):
                    st.write("選択項目をさらに深ぼるか、新たに質問することができます。")
                    with st.form(key="bullet_points_form"):
                        bullet_point = st.radio(
                            "",
                            bullet_points[1:],
                            key="bullet_points_radio",
                        )
                        st.form_submit_button(
                            "決定", on_click=partial(click_button, bullet_point)
                        )

            else:
                st.chat_message("assistant").write(response)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )


if __name__ == "__main__":
    main()
