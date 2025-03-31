
import dspy
from dspy.retrieve.chromadb_rm import ChromadbRM
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

from dotenv import load_dotenv


class QAAgent:

    def __init__(self):
        load_dotenv()

        self._init_lm()
        self._init_embed_retriever()

    def _init_lm(self):
        lm = dspy.LM(
            api_base=os.getenv("LM_BASE_URL"),
            api_key=os.getenv("LM_API_KEY"),
            model=os.getenv("LM_MODEL_NAME"),
        )
        dspy.configure(lm=lm)

        self.lm = dspy.ReAct(
            "question -> answer: float",
            tools=[evaluate],
        )

    def _init_embed_retriever(self):
        client = chromadb.Client(Settings(
            persist_directory="chroma",
            is_persistent=True,
        ))
        self.embed_coll = client.create_collection('embedding')

    def _create_context(self, message: str):
        # retrieve user context

        pass

    def turn(self, message: str):
        lm_ctx = self._create_context()

        # call predict
        resp = self.lm(
            context=lm_ctx,
            message=message,
        )

        print(resp.response)

        # save info
        self.save_message({
            'user': message,
            'response': resp.response,
        })

    def run(self):
        ...

