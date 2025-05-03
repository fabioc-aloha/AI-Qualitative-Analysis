"""
MCEM Interview Processing Script

This script processes customer interview transcripts using Azure OpenAI's GPT-4 model to generate
structured analysis reports based on Microsoft's Customer Engagement Model (MCEM) framework.
It handles both small and large transcripts through intelligent chunking and generates output
in both Markdown and Word document formats.

Requirements:
    - Python 3.x
    - Azure OpenAI API access
    - Environment variables set in .env file:
        - AZURE_OPENAI_API_KEY
        - AZURE_OPENAI_API_VERSION
        - AZURE_OPENAI_ENDPOINT
        - AZURE_OPENAI_DEPLOYMENT
    - Pandoc installed for Word document conversion
    - Required packages: openai, python-dotenv, tiktoken

Usage:
    1. Place interview transcripts in the 'transcripts/' directory as .txt files
    2. Ensure AnalysisTemplate.txt exists with the desired template
    3. Run the script: python process_transcripts.py
    4. Generated analyses will be in the 'reports/' directory
"""

from typing import List
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from pathlib import Path
import tiktoken

def count_tokens(text: str) -> int:
    """Count tokens using tiktoken for GPT-4"""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def get_client():
    """Create and return an Azure OpenAI client"""
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

def process_transcript(transcript_path: Path, template: str, client: AzureOpenAI) -> str:
    """
    Process a single transcript file and generate an analysis using Azure OpenAI.
    
    If the transcript exceeds the safe token limit, it will be processed in chunks
    using process_large_transcript().
    
    Args:
        transcript_path (Path): Path to the transcript file
        template (str): Analysis template to use
        client (AzureOpenAI): Initialized Azure OpenAI client
    
    Returns:
        str: Generated analysis text, or None if processing fails
        
    Raises:
        Exception: If there's an error during API communication or text processing
    """
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()
        company_name = transcript_path.stem.replace(" Transcription", "")

    SAFE_TOKEN_LIMIT = 100000
    MAX_COMPLETION_TOKENS = 16000

    total_tokens = count_tokens(transcript + template)
    print(f"Total tokens in transcript + template: {total_tokens}")

    if total_tokens > SAFE_TOKEN_LIMIT:
        print("Warning: Transcript exceeds safe token limit, will process in chunks")
        return process_large_transcript(transcript, template, client)
    
    prompt = (
        f"{template}\n\n"
        "TRANSCRIPT ANALYSIS INSTRUCTIONS:\n"
        "1. Write in a professional, narrative style with clear section headings.\n"
        "2. Analysis Requirements:\n"
        "   - Identify all participants (names and roles) and the interviewer\n"
        "   - Support all findings with direct quotes from the transcript\n"
        "   - Format quotes using proper markdown blockquotes (>)\n"
        "   - Apply Microsoft Customer Engagement Methodology (MCEM) framework:\n"
        "     * Customer Focus: Industry context, specific needs, and desired outcomes\n"
        "     * One Microsoft Approach: Cross-functional collaboration opportunities\n"
        "     * Short-term & Long-term Balance: Immediate priorities vs strategic goals\n"
        "     * Value Differentiation: Microsoft's unique value proposition\n"
        "   - Preserve specific metrics and ratings mentioned\n"
        "   - Identify key themes and patterns\n"
        "   - Note technical requirements and challenges\n"
        "   - Highlight regulatory and compliance needs\n"
        "   - Document support and operational issues\n"
        "   - Analyze partnership dynamics\n"
        "\nTRANSCRIPT:\n"
        f"{transcript}"
    )

    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": (
                    "You are an expert business analyst creating detailed, evidence-based analyses. "
                    "Begin by identifying all participants and their roles. "
                    "Apply the Microsoft Customer Engagement Methodology (MCEM) framework to structure the analysis: "
                    "1) Focus on customer industry context and desired outcomes, "
                    "2) Identify cross-functional collaboration opportunities, "
                    "3) Balance immediate needs with strategic goals, and "
                    "4) Highlight Microsoft's unique value proposition. "
                    "Support key findings with direct quotes and specific examples from "
                    "the transcript. Pay special attention to ratings, metrics, and technical details."
                )},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=MAX_COMPLETION_TOKENS
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error processing transcript: {str(e)}")
        return None

def process_large_transcript(transcript: str, template: str, client: AzureOpenAI) -> str:
    """
    Handle large transcripts by breaking them into chunks for processing.
    
    This function:
    1. Splits the transcript into chunks based on token count
    2. Processes each chunk separately
    3. Consolidates the results into a single coherent analysis
    
    Args:
        transcript (str): The full transcript text
        template (str): Analysis template to use
        client (AzureOpenAI): Initialized Azure OpenAI client
    
    Returns:
        str: Consolidated analysis text, or None if processing fails
        
    Notes:
        - Uses a chunk size of 80,000 tokens
        - Each chunk is processed independently with the MCEM framework
        - Results are consolidated with a final API call if multiple chunks exist
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
        print(f"Processing chunk {i} of {len(chunks)}")
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
            print(f"Error processing chunk {i}: {str(e)}")
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
            print(f"Error consolidating results: {str(e)}")
            return combined
    
    return results[0] if results else None

def main():
    """
    Main execution function that:
    1. Loads environment variables
    2. Initializes Azure OpenAI client
    3. Creates output directory if needed
    4. Processes all .txt files in the transcripts directory
    5. Generates both markdown and Word document outputs
    
    Environment Requirements:
        - .env file with Azure OpenAI credentials
        - 'transcripts' directory with .txt files
        - 'AnalysisTemplate.txt' file
        - Pandoc installed for Word conversion
    """
    load_dotenv()
    client = get_client()
    
    # Create reports directory
    reports_dir = Path("./reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Load template
    template = Path("AnalysisTemplate.txt").read_text(encoding="utf-8")
    
    # Process transcripts
    for transcript_file in Path("./transcripts").glob("*.txt"):
        print(f"\nProcessing {transcript_file.name}")
        md_output_file = reports_dir / f"{transcript_file.stem}_analysis.md"
        docx_output_file = reports_dir / f"{transcript_file.stem}_analysis.docx"
        
        result = process_transcript(transcript_file, template, client)
        if result:
            # Save markdown file
            md_output_file.write_text(result, encoding="utf-8")
            print(f"Analysis saved to {md_output_file}")
            
            # Convert to Word document using pandoc
            try:
                import subprocess
                cmd = f'pandoc "{md_output_file}" -f markdown -t docx -o "{docx_output_file}"'
                subprocess.run(cmd, shell=True, check=True)
                print(f"Word document saved to {docx_output_file}")
            except subprocess.CalledProcessError as e:
                print(f"Error converting to Word document: {str(e)}")
            except Exception as e:
                print(f"Unexpected error during conversion: {str(e)}")

if __name__ == "__main__":
    main()