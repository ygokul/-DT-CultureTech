import argparse
import json
import re
from pathlib import Path


class ReflectionAgent:
    def __init__(self, tree_path: Path):
        data = json.loads(tree_path.read_text(encoding="utf-8"))
        self.title = data["title"]
        self.start_node = data["startNode"]
        self.axes = data["axes"]
        self.nodes = {node["id"]: node for node in data["nodes"]}
        self.state = {
            "answers": {},
            "signals": {
                axis: {"positive": 0, "negative": 0}
                for axis in self.axes
            },
        }
        self.transcript = []

    def render(self, text: str) -> str:
        def replace(match):
            token = match.group(1)
            if "." not in token:
                return match.group(0)

            left, right = token.split(".", 1)
            if left in self.state["answers"]:
                answer = self.state["answers"][left]
                if right == "answer":
                    return answer["id"]
                if right == "answerLabel":
                    return answer["label"]

            if left in self.axes:
                counts = self.state["signals"][left]
                dominant = self.dominant(left)
                if right == "dominant":
                    return dominant
                if right == "dominantLabel":
                    return self.axes[left][dominant]

            return match.group(0)

        return re.sub(r"\{([^}]+)\}", replace, text)

    def dominant(self, axis: str) -> str:
        counts = self.state["signals"][axis]
        if counts["positive"] > counts["negative"]:
            return "positive"
        if counts["negative"] > counts["positive"]:
            return "negative"
        return "tie"

    def apply_signals(self, signals):
        for signal in signals or []:
            axis, polarity = signal.split(":", 1)
            self.state["signals"][axis][polarity] += 1

    def ask_question(self, node, choice_value=None):
        text = self.render(node["text"])
        self.transcript.append(f"Agent: {text}")
        print(f"\n{text}")
        for index, option in enumerate(node["options"], start=1):
            print(f"  {index}. {option['label']}")

        if choice_value is None:
            while True:
                try:
                    raw = input("Choose an option number: ").strip()
                except EOFError as exc:
                    raise RuntimeError(
                        f"Input ended before node {node['id']} received an answer. "
                        "If you are using --choices, provide one option number for every question on the path."
                    ) from exc
                if raw.isdigit() and 1 <= int(raw) <= len(node["options"]):
                    chosen = node["options"][int(raw) - 1]
                    break
                print("Please choose a valid option number.")
        else:
            chosen = node["options"][choice_value - 1]
            print(f"Auto choice: {choice_value}. {chosen['label']}")

        self.state["answers"][node["id"]] = {
            "id": chosen["id"],
            "label": chosen["label"],
        }
        self.apply_signals(chosen.get("signals"))
        self.transcript.append(f"User: {chosen['label']}")
        return node.get("next")

    def decide(self, node):
        for rule in node["rules"]:
            if "whenAnswerIn" in rule:
                payload = rule["whenAnswerIn"]
                answer = self.state["answers"].get(payload["node"], {})
                if answer.get("id") in payload["values"]:
                    return rule["goTo"]
            if "whenDominantEquals" in rule:
                payload = rule["whenDominantEquals"]
                if self.dominant(payload["axis"]) == payload["value"]:
                    return rule["goTo"]
        raise ValueError(f"No decision rule matched for node {node['id']}")

    def show_text_node(self, node):
        text = self.render(node["text"])
        self.transcript.append(f"Agent: {text}")
        print(f"\n{text}")
        return node.get("next")

    def run(self, choices=None):
        choices = choices or []
        choice_index = 0
        current = self.start_node

        while current:
            node = self.nodes[current]
            node_type = node["type"]

            if node_type == "question":
                choice_value = None
                if choice_index < len(choices):
                    choice_value = choices[choice_index]
                    choice_index += 1
                current = self.ask_question(node, choice_value)
            elif node_type == "decision":
                current = self.decide(node)
            elif node_type in {"start", "reflection", "bridge", "summary", "end"}:
                current = self.show_text_node(node)
            else:
                raise ValueError(f"Unsupported node type: {node_type}")

        return self.transcript


def parse_choices(raw):
    if not raw:
        return []
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def main():
    parser = argparse.ArgumentParser(description="Run the deterministic daily reflection agent.")
    parser.add_argument(
        "--tree",
        default=str(Path(__file__).resolve().parents[1] / "tree" / "reflection-tree.json"),
        help="Path to the reflection tree JSON file.",
    )
    parser.add_argument(
        "--choices",
        default="",
        help="Comma-separated option numbers for non-interactive runs.",
    )
    parser.add_argument(
        "--transcript-out",
        default="",
        help="Optional file path to save the transcript.",
    )
    args = parser.parse_args()

    agent = ReflectionAgent(Path(args.tree))
    transcript = agent.run(parse_choices(args.choices))

    if args.transcript_out:
        output_path = Path(args.transcript_out)
        output_path.write_text("\n".join(transcript) + "\n", encoding="utf-8")
        print(f"\nTranscript saved to {output_path}")


if __name__ == "__main__":
    main()
