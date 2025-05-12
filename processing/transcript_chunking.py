import os
import logging
from openai import AzureOpenAI
from typing import Optional
import tiktoken
from utils.file_utils import count_tokens

def process_large_transcript(transcript: str, template: str, client: AzureOpenAI) -> Optional[str]:
    """
    Handle large transcripts by breaking them into chunks for processing.
    Args:
        transcript (str): The full transcript text.
        template (str): The analysis template content.
        client (AzureOpenAI): The Azure OpenAI client.
    Returns:
        Optional[str]: The consolidated analysis text, or None if processing fails.
    """
    chunk_size = 80000
    MAX_COMPLETION_TOKENS = 16000
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(transcript)
    chunks = []
    for i in range(0, len(tokens), chunk_size):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    results = []
    for i, chunk in enumerate(chunks, 1):
        logging.info(f"Processing chunk {i} of {len(chunks)}")
        prompt = f"{template}\n\nTRANSCRIPT SEGMENT {i}/{len(chunks)}:\n{chunk}"
        try:
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=[
                    {"role": "system", "content": (
                        "You are an expert business analyst skilled at creating detailed, narrative-driven analyses. "
                        "For each segment, identify any mentioned participants and their roles. "
                        "Apply the Microsoft Customer Engagement Methodology (MCEM) framework: "
                        "1) Customer industry context and desired outcomes, "
                        "2) Cross-functional collaboration opportunities, "
                        "3) Balance of immediate needs vs strategic goals, "
                        "4) Microsoft's unique value proposition. "
                        "Focus on technology partnerships and strategic recommendations."
                    )},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=MAX_COMPLETION_TOKENS
            )
            results.append(response.choices[0].message.content)
        except Exception as e:
            logging.error(f"Error processing chunk {i}: {str(e)}")
            continue
    if len(results) > 1:
        combined = "\n\n---\n\n".join(results)
        consolidation_prompt = "Please consolidate these analysis segments into a single coherent analysis, removing any redundancies and ensuring a smooth flow:"
        try:
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=[
                    {"role": "system", "content": "You are an expert at consolidating and summarizing analyses while maintaining a professional, narrative-driven style."},
                    {"role": "user", "content": f"{consolidation_prompt}\n\n{combined}"}
                ],
                temperature=0.3,
                max_tokens=MAX_COMPLETION_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error consolidating results: {str(e)}")
            return combined
    return results[0] if results else None
