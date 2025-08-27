from pathlib import Path
from langchain.memory import ConversationBufferMemory, CombinedMemory
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

class LongTermStore:
    """Simple FAISS-based long-term memory."""
    def __init__(self, persist_dir: str = "data/vectorstore", model: str = "gemini-embedding-001"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings = GoogleGenerativeAIEmbeddings(model=model)
        self.vs_path = self.persist_dir / "faiss.index"
        self.docstore_path = self.persist_dir / "docstore.pkl"
        self.index_to_docstore_id_path = self.persist_dir / "index_to_id.pkl"
        self.vs = None
        self._load_or_init()

    def _load_or_init(self):
        if all(p.exists() for p in [self.vs_path, self.docstore_path, self.index_to_docstore_id_path]):
            self.vs = FAISS.load_local(str(self.persist_dir), self.embeddings, allow_dangerous_deserialization=True)
        else:
            self.vs = FAISS.from_texts(["Boot memory for ADE."], self.embeddings)
            self.vs.save_local(str(self.persist_dir))

    def add_text(self, text: str, meta: dict | None = None):
        if self.vs is None:
            self._load_or_init()
        if self.vs is not None:
            self.vs.add_texts([text], metadatas=[meta or {}])
            self.vs.save_local(str(self.persist_dir))
        else:
            raise RuntimeError("Vector store (self.vs) could not be initialized.")

    def as_retriever(self, k: int = 4):
        if self.vs is None:
            self._load_or_init()
        if self.vs is not None:
            return self.vs.as_retriever(search_kwargs={"k": k})
        else:
            raise RuntimeError("Vector store (self.vs) could not be initialized.")

def build_memories():
    # Short-term running chat history
    buffer = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="input",
        return_messages=True
    )

    # For now, use simple memory to avoid API errors
    # Long-term vector memory will be initialized later if needed
    ltm = None
    try:
        ltm = LongTermStore()
        from langchain.memory import VectorStoreRetrieverMemory
        retriever_mem = VectorStoreRetrieverMemory(
            retriever=ltm.as_retriever(),
            memory_key="history",
            input_key="input"
        )
        return CombinedMemory(memories=[buffer, retriever_mem]), ltm
    except Exception as e:
        print(f"Warning: Could not initialize vector memory: {e}")
        print("Falling back to simple buffer memory...")
        return buffer, ltm
