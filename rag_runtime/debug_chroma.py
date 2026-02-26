from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5"
)

db = Chroma(
    collection_name="jll_units",
    embedding_function=embeddings,
    persist_directory="./chroma_jll"
)

print("向量库中记录数:", db._collection.count())

docs = db.similarity_search("静安区 写字楼 租金", k=5)
print("检索到文档数:", len(docs))

for i, d in enumerate(docs):
    print(f"\n--- 文档 {i+1} ---")
    print(d.page_content[:200])
