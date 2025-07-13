import os
from pathlib import Path
import sys
import traceback
from datetime import datetime

from dotenv import load_dotenv
import dspy
from rich.console import Console

from therapist.models import Message
from therapist.memory import Memory

console = Console()


class ChatBot:

    def __init__(self):
        load_dotenv()

        self.short_term_limit = 30
        self.summary_threshold = 15

        assert self.short_term_limit > self.summary_threshold

        current_file = Path(__file__).resolve()
        project_top = current_file.parent
        database_dir = project_top / os.getenv("DATABASE_DIR", "database/")

        self._init_lm()

        self.memory = Memory(
            persistence_path=database_dir,
            short_term_limit=self.short_term_limit,
        )

    def _init_lm(self):
        CONTEXT_PROMPT = (
            "You're a helpful, professional therapist. "
            "You care about people's feeling and know what to ask when they are feeling ok. "
            "Your first question is usually: how are you doing and how can I help you today? "
            "You'll help understand your client's request, analyze their feelings, and come up with a strategy with them "
            "to deal with their emotions"
        )

        lm = dspy.LM(
            api_key=os.getenv("LM_API_KEY"),
            model=os.getenv("LM_MODEL_NAME"),
            api_base=os.getenv("LM_BASE_URL", None),
            max_tokens=16384,
        )
        dspy.configure(lm=lm, track_usage=True)

        self.lm = dspy.ChainOfThought(
            "memory: list, relative_context: str, messages: list -> answer: str",
            instructions=CONTEXT_PROMPT,
        )

    def turn(self) -> Message:
        # format and save user message
        message = self.user_input()

        self.memory.save(message)
        self.pprint_message(message)

        # call predict
        try:

            resp = self.lm(
                memory=self.memory.get_long_term(),
                relative_context=self.memory.retrieve(query=message.content),
                messages=self.memory.get(),
            )
        except Exception as e:
            traceback.print_exc()
            print(e)
            raise e

        # format and save answer
        answer = Message(role="assistant", content=resp.answer)
        self.memory.save(answer)
        self.pprint_message(answer)

        return answer

    @staticmethod
    def pprint_message(m: Message):
        timestamp = m.created_at.strftime("%Y-%m-%d %H:%M:%S")

        if m.role == "assistant" or m.role == "system":
            role = f"[bright_cyan][bold]{m.role}[/bold][/bright_cyan]: "
            content = f"[cyan]{m.content}[/cyan]"
        elif m.role == "user":
            role = f"[bright_yellow][bold]{m.role}[/bold][/bright_yellow]: "
            content = f"{m.content}"
        elif m.role == "memory":
            role = f"[pink][bold]{m.role}[/bold][/pink]: "
            content = f"{m.content}"
        else:
            role = f"[grey][bold]{m.role}[/bold][/grey]: "
            content = f"{m.content}"

        console.print(
            f"[bright_black][{timestamp}][/bright_black] " + role + content,
        )

    @staticmethod
    def user_input() -> Message:
        user_input = console.input(r"[yellow][bold]user[/bold][/yellow]: ")

        # move cursor up 1 line
        sys.stdout.write(f"\x1b[1A")
        # clear line
        sys.stdout.write("\r\x1b[0K")

        return Message(
            role="user",
            created_at=datetime.now(),
            content=user_input,
        )

    def maybe_summary(self):
        """create long term memory by summarizing short term message short_term"""
        last_summary = self.memory.get_long_term(limit=1)
        last_summary_id = 0
        if last_summary:
            last_summary_id = last_summary[0].id

        short_term = self.memory.get()

        if short_term[-1].id - last_summary_id > self.summary_threshold:
            summary = self.memory.summarize(short_term)
            return summary

        return None

    def run(self):
        print(f"Starting conversation: {self.memory.conversation.name}")

        existing_messages = self.memory.get(limit=50)
        if not existing_messages:
            m = self.memory.save(
                Message(
                    role="assistant",
                    content=(
                        "Hello world! I'm here to help you with any questions or problems. "
                        "What's on your mind right now?"
                    ),
                )
            )
            existing_messages.append(m)

        for m in existing_messages:
            self.pprint_message(m)

        try:
            while True:
                self.turn()

                summary = self.maybe_summary()
                if summary:
                    self.memory.save(summary)
                    self.pprint_message(summary)

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
        except Exception as e:
            raise e
