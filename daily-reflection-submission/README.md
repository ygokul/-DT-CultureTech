# Daily Reflection Tree Submission

This folder contains a complete submission for the DeepThought Daily Reflection Tree assignment, including the optional runnable agent.

## Structure

```text
/tree
  reflection-tree.json
  tree-diagram.md
/agent
  run_reflection.py
/transcripts
  persona-1-transcript.md
  persona-2-transcript.md
write-up.md
voice-note-script.md
README.md
```

## What is included

- `tree/reflection-tree.json`: the deterministic reflection tree as readable data
- `tree/tree-diagram.md`: a Mermaid diagram of the branching structure
- `agent/run_reflection.py`: a CLI agent that loads the tree from JSON and walks it deterministically
- `transcripts/`: two sample paths showing different personas and different reflections
- `write-up.md`: design choices, psychological grounding, trade-offs, and hallucination guardrails
- `voice-note-script.md`: a concise script you can use to record the required spoken explanation

## Runtime guardrails

The product itself has strict guardrails against hallucination:

- No LLM or API calls at runtime
- No free-text input from the employee
- No hidden classification model
- Every option maps directly to a known signal
- Every branch is defined in the JSON tree
- Every summary is assembled with template interpolation only

## How to run

From this folder:

```bash
python agent/run_reflection.py
```

For a non-interactive run with fixed choices:

```bash
python agent/run_reflection.py --choices 2,1,3,1,1,4,4,4
```

To save a transcript:

```bash
python agent/run_reflection.py --choices 1,2,2,3,2,1,1,1 --transcript-out transcripts/sample.txt
```

## Notes on AI usage

AI was used as a design accelerator, critique partner, and wording sparring tool. It was not used as the runtime engine. The runtime logic is deterministic and auditable. Any claim that felt unsupported or too polished was removed rather than padded.
