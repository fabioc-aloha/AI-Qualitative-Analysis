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
    """Process a transcript file, chunking only if exceeds safe token limit"""
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
    """Handle extremely large transcripts that exceed token limits"""
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