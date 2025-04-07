from agents.agent import QAAgent

# hack to suppress warning messages
import warnings
from pydantic_core import PydanticSerializationUnexpectedValue
warnings.filterwarnings("ignore", category=UserWarning, message='.*pydantic serializer warnings.*')


if __name__ == "__main__":
    agent = QAAgent()

    agent.run()
