from llm_token_util import create_vector_store
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings

def create_vector_store():
    # Use a lightweight model like all-MiniLM-L6-v2
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        collection_name="ai_learning",
        embedding_function=embeddings,
        persist_directory="vectordb"
    )
    return vectorstore

def create_retriever(vectorstore):
    retriever = vectorstore.as_retriever(search_type="similarity")
    return retriever

def load_document_to_vector_store(file_path, vectorstore):
    vectorstore = create_vector_store()
    loader = TextLoader(file_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore = create_vector_store()
    vectorstore.add_documents(splits)
    return vectorstore

if __name__ == "__main__":
    vectorstore = create_vector_store()
    file_path = "analects.txt"
    vectorstore = load_document_to_vector_store(file_path, vectorstore)
    documents = vectorstore.similarity_search("有朋友自远方来, 如何？")
    print(documents)