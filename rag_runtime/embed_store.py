import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

COLLECTION_NAME = "jll_units"


def is_valid_unit(u):
    text = u["text"].strip()
    if len(text) < 15:
        return False
    if text.startswith("|"):
        return False
    return True


def build_vector_store(units_path: str, persist_dir: str):
    with open(units_path, "r", encoding="utf-8") as f:
        units = json.load(f)

    texts = []
    metadatas = []

    for u in units:
        if not is_valid_unit(u):
            continue
        texts.append(u["text"])
        metadatas.append(u.get("meta", {}))

    print(f"准备写入向量条数: {len(texts)}")

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-zh-v1.5"
    )

    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=persist_dir
    )

    vectordb.add_texts(
        texts=texts,
        metadatas=metadatas
    )

    print("向量写入完成（自动持久化）")


if __name__ == "__main__":
    build_vector_store(
        units_path="units.json",
        persist_dir="./chroma_jll"
    )
