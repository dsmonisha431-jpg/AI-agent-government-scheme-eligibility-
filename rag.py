import os
import tempfile
from pathlib import Path
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

class SchemeRAG:
    def __init__(self, api_key: str, model: str, embedding_model: str, base_url: Optional[str] = None):
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            api_key=api_key,
            base_url=base_url,
            check_embedding_ctx_length=base_url is None,
        )
        self.vectorstore = Chroma(
            collection_name="official_government_schemes",
            embedding_function=self.embeddings,
            persist_directory="data/chroma_db"
        )
        self.llm = ChatOpenAI(model=model, temperature=0, api_key=api_key, base_url=base_url)
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)

    def add_uploaded_files(self, uploaded_files) -> int:
        docs = []
        for file in uploaded_files:
            suffix = Path(file.name).suffix.lower()
            if suffix not in {".pdf", ".txt", ".md"}:
                continue
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file.getvalue())
                temp_path = tmp.name
            try:
                if suffix == ".pdf":
                    from langchain_community.document_loaders import PyPDFLoader
                    loaded = PyPDFLoader(temp_path).load()
                else:
                    loaded = TextLoader(temp_path, encoding="utf-8").load()
                for doc in loaded:
                    doc.metadata["source"] = file.name
                docs.extend(loaded)
            finally:
                os.unlink(temp_path)
        chunks = self.splitter.split_documents(docs)
        if chunks:
            self.vectorstore.add_documents(chunks)
        return len(chunks)

    def retrieve(self, question: str, k: int = 5) -> str:
        docs = self.vectorstore.similarity_search(question, k=k)
        if not docs:
            return "No matching content was found in the indexed scheme documents. Do not infer scheme rules."
        return "\n\n".join(
            f"[Source: {d.metadata.get('source', 'unknown')}, page: {d.metadata.get('page', 'n/a')}]\n{d.page_content}"
            for d in docs
        )
