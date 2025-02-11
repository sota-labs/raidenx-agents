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
    """Extract thought, action and action input from the input text."""
    pattern = (
        r"Thought:\s*(.*?)[\n\r]+\s*Action:\s*([^\n\r]+)[\n\r]+\s*Action Input:\s*(\{.*\}|\{\})"
    )

    match = re.search(pattern, input_text, re.DOTALL)
    if not match:
        # Try alternative pattern for empty action input
        alt_pattern = r"Thought:\s*(.*?)[\n\r]+\s*Action:\s*([^\n\r]+)[\n\r]+\s*Action Input:\s*\{\}"
        alt_match = re.search(alt_pattern, input_text, re.DOTALL)
        if alt_match:
            return alt_match.group(1).strip(), alt_match.group(2).strip(), "{}"
        raise ValueError(
            "INVALID_FORMAT: Output must follow the format:\nThought: [your reasoning]\nAction: [action name]\nAction Input: [parameters as json]" + 
            f"\nReceived output: {input_text}"
        )

    thought = match.group(1).strip()
    action = match.group(2).strip()
    action_input = match.group(3).strip()
    
    return thought, action, action_input


def action_input_parser(json_str: str) -> dict:
    """Parse action input string into dictionary."""
    if json_str == "{}" or not json_str:
        return {}
        
    processed_string = re.sub(r"(?<!\w)\'|\'(?!\w)", '"', json_str)
    pattern = r'"(\w+)":\s*"([^"]*)"'
    matches = re.findall(pattern, processed_string)
    return dict(matches)


def extract_final_response(input_text: str) -> Tuple[str, str]:
    # Pattern 1: Normal case with Thought and Answer
    pattern1 = r"\s*Thought:(.*?)Answer:(.*?)(?:$)"
    # Pattern 2: Case with Action: None - this should raise an error
    pattern2 = r"\s*Thought:(.*?)Action:\s*None\s*"
    # Pattern 3: Case with only Thought
    pattern3 = r"\s*Thought:(.*?)(?:$)"

    match1 = re.search(pattern1, input_text, re.DOTALL)
    match3 = re.search(pattern3, input_text, re.DOTALL)

    if match1:
        thought = match1.group(1).strip()
        answer = match1.group(2).strip()
    elif re.search(pattern2, input_text, re.DOTALL):
        raise ValueError(
            "INVALID_ACTION_NONE: Found 'Action: None' in response. The model should either provide a clear answer or use a tool." +
            f"\nReceived output: {input_text}"
        )   
    elif match3:
        thought = match3.group(1).strip()
        answer = thought.split(".")[-1].strip() if len(thought.split(".")[-1]) > 3 else thought.split(".")[-2].strip()
    else:
        raise ValueError(
            "INVALID_FORMAT: Could not extract final answer. Output must either:" +
            "\n1. Include 'Thought: [reasoning]' and 'Answer: [answer]'" +
            "\n2. Include clear reasoning in 'Thought: [detailed reasoning with answer]'" +
            f"\nReceived output: {input_text}"
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
            
        if "Thought:" in output:
            thought, answer = extract_final_response(output)
            return ResponseReasoningStep(
                thought=thought, response=answer, is_streaming=is_streaming
            )

        raise ValueError(
            "INVALID_FORMAT: Output must either:" +
            "\n1. Include 'Thought: [reasoning]' and 'Action: [action]' and 'Action Input: [input]'" +
            "\n2. Include 'Thought: [reasoning]' and 'Answer: [answer]'" +
            "\n3. Include clear reasoning in 'Thought: [detailed reasoning with answer]'" +
            f"\nReceived output: {output}"
        )

    def format(self, output: str) -> str:
        """Format a query with structured output formatting instructions."""
        raise NotImplementedError
