"""ReAct output parser."""

import re
from typing import Tuple
import dirtyjson as json

from llama_index.core.agent.react.types import (
    ActionReasoningStep,
    BaseReasoningStep,
    ResponseReasoningStep,
)
from llama_index.core.output_parsers.utils import extract_json_str
from llama_index.core.types import BaseOutputParser


def extract_tool_use(input_text: str) -> Tuple[str, str, str]:
    pattern = (
        r"Thought:\s*(.*?)[\n\r]+\s*Action:\s*([^\n\r]+)[\n\r]+\s*Action Input:\s*(\{[^}]+\})"
    )

    match = re.search(pattern, input_text, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse output. Please follow the thought-action-input format: {input_text}")

    thought = match.group(1).strip()
    action = match.group(2).strip()
    action_input = match.group(3).strip()
    
    return thought, action, action_input


def action_input_parser(json_str: str) -> dict:
    processed_string = re.sub(r"(?<!\w)\'|\'(?!\w)", '"', json_str)
    pattern = r'"(\w+)":\s*"([^"]*)"'
    matches = re.findall(pattern, processed_string)
    return dict(matches)


def extract_final_response(input_text: str) -> Tuple[str, str]:
    # Pattern 1: Normal case with Thought and Answer
    pattern1 = r"\s*Thought:(.*?)Answer:(.*?)(?:$)"
    # Pattern 2: Case with Action: None and answer in the last line
    pattern2 = r"\s*Thought:(.*?)Action:\s*None\s*(.*?)(?:$)"
    # Pattern 3: Case with only Thought
    pattern3 = r"\s*Thought:(.*?)(?:$)"

    match1 = re.search(pattern1, input_text, re.DOTALL)
    match2 = re.search(pattern2, input_text, re.DOTALL)
    match3 = re.search(pattern3, input_text, re.DOTALL)

    if match1:
        thought = match1.group(1).strip()
        answer = match1.group(2).strip()
    elif match2:
        thought = match2.group(1).strip()
        answer = match2.group(2).strip()
    elif match3:
        thought = match3.group(1).strip()
        answer = thought  # Return thought as the answer
    else:
        raise ValueError(
            f"Could not extract final answer from input text: {input_text}"
        )

    return thought, answer

    
def parse_action_reasoning_step(output: str) -> ActionReasoningStep:
    """Parse an action reasoning step from the LLM output."""
    thought, action, action_input = extract_tool_use(output)
    json_str = extract_json_str(action_input)
    try:
        action_input_dict = json.loads(json_str)
    except Exception:
        action_input_dict = action_input_parser(json_str)
    return ActionReasoningStep(
        thought=thought, action=action, action_input=action_input_dict
    )


class ReActOutputParser(BaseOutputParser):
    """ReAct Output parser."""

    def parse(self, output: str, is_streaming: bool = False) -> BaseReasoningStep:
        """Parse output from ReAct agent.

        We expect the output to be in one of the following formats:
        1. If the agent need to use a tool to answer the question:
            ```
            Thought: <thought>
            Action: <action>
            Action Input: <action_input>
            ```
        2. If the agent can answer the question without any tools:
            ```
            Thought: <thought>
            Answer: <answer>
            ```
        """
        # Clean up output by removing extra backticks
        output = re.sub(r'`{3,}', '', output)
        
        print(f"output-ReActOutputParser: {output}")
        
        if "Thought:" not in output:
            # NOTE: handle the case where the agent directly outputs the answer
            # instead of following the thought-answer format
            return ResponseReasoningStep(
                thought="(Implicit) I can answer without any more tools!",
                response=output,
                is_streaming=is_streaming,
            )

        # An "Action" should take priority over an "Answer"
        if "Action:" in output and "Action: None" not in output:
            return parse_action_reasoning_step(output)

        if "Answer:" in output:
            thought, answer = extract_final_response(output)
            return ResponseReasoningStep(
                thought=thought, response=answer, is_streaming=is_streaming
            )

        raise ValueError(f"Could not parse output: {output}")

    def format(self, output: str) -> str:
        """Format a query with structured output formatting instructions."""
        raise NotImplementedError
