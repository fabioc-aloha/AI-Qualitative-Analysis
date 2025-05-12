import os
import logging
from pathlib import Path
from openai import AzureOpenAI
from typing import Optional
from utils.file_utils import count_tokens, get_client, load_analysis_template, ensure_reports_dir
from utils.env_utils import setup_logging, check_env_vars, check_pandoc_installed

def process_transcript(transcript_path: Path, template: str, client: AzureOpenAI) -> Optional[str]:
    """
    Process a single transcript file and generate an analysis using Azure OpenAI.
    Args:
        transcript_path (Path): Path to the transcript file.
        template (str): The analysis template content.
        client (AzureOpenAI): The Azure OpenAI client.
    Returns:
        Optional[str]: The generated analysis text, or None if processing fails.
    """
    logging.info(f"Starting analysis for transcript: {transcript_path.name}")
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()
    logging.info("Transcript loaded from file.")
    MAX_CONTEXT_TOKENS = 128000  # GPT-4o context window (adjust if needed)
    MAX_COMPLETION_TOKENS = 16000
    total_tokens = count_tokens(transcript + template)
    logging.info(f"Total tokens in transcript + template: {total_tokens}")
    if total_tokens + MAX_COMPLETION_TOKENS > MAX_CONTEXT_TOKENS:
        logging.error(f"Transcript + template + completion tokens ({total_tokens + MAX_COMPLETION_TOKENS}) exceed model context window ({MAX_CONTEXT_TOKENS}). Aborting analysis.")
        return None
    logging.info("Preparing prompt for Azure OpenAI analysis.")
    try:
        logging.info("Sending prompt to Azure OpenAI for initial report generation.")
        def generate_report(transcript, template, issues=None, prev_report=None):
            if not issues:
                prompt = (
                    f"{template}\n\n"
                    "TRANSCRIPT ANALYSIS INSTRUCTIONS (Enhanced Output Formatting):\n"
                    "1. Start with a concise **Summary Section** at the top, using bullet points for key findings.\n"
                    "2. Always include and fill out the **Summary Table** (see template) with relevant data for each role.\n"
                    "3. If any metrics or ratings are mentioned, add a **Key Metrics Table** in Markdown format.\n"
                    "4. Use clear section headings (##, ###) and bold for important points.\n"
                    "5. Use bullet lists for recommendations and key insights.\n"
                    "6. Format all direct quotes using Markdown blockquotes (>).\n"
                    "7. Use tables, lists, and visual structure to improve readability.\n"
                    "8. Follow the MCEM structure and ensure each stage is clearly separated.\n"
                    "9. At the end, add a short **Summary of Insights** section that aggregates the most important findings.\n"
                    "10. Ensure all sections in the template are present and well-formatted, even if some data is missing.\n"
                    "\nTRANSCRIPT:\n"
                    f"{transcript}"
                )
            else:
                prompt = (
                    f"{template}\n\n"
                    "The previous report was incomplete or inaccurate. Please revise and improve the report to address ALL the listed issues below, ensuring every customer statement and key point is included and accurately represented. Use the same formatting and structure as before.\n\n"
                    "TRANSCRIPT:\n" + transcript + "\n\nPREVIOUS REPORT:\n" + (prev_report or "") + "\n\nISSUES TO FIX:\n" + issues
                )
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
                        "the transcript. Pay special attention to ratings, metrics, and technical details. "
                        "Enhance output formatting by using Markdown tables, bullet points, bold text, and clear section headings. "
                        "Always include a summary section and summary table as described in the template. "
                    )},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=MAX_COMPLETION_TOKENS
            )
            return response.choices[0].message.content

        report = generate_report(transcript, template)
        logging.info("Initial report generated by Azure OpenAI.")
        for iteration in range(5):
            logging.info(f"Validation pass {iteration+1}: Checking report completeness against transcript.")
            validation_prompt = (
                "Compare the following transcript and the generated report. "
                "Check that every statement, quote, and key point from the customer in the transcript is accurately captured in the report. "
                "List any customer statements, quotes, or important points that are missing or misrepresented in the report. "
                "If the report is missing anything, provide a list of omissions or inaccuracies and suggest corrections. "
                "If the report is complete and accurate, reply with 'VALID'.\n\n"
                "TRANSCRIPT:\n" + transcript + "\n\nREPORT:\n" + report
            )
            validation_response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=[
                    {"role": "system", "content": "You are a meticulous analyst validating report completeness and accuracy."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0.0,
                max_tokens=2000
            )
            validation_result = validation_response.choices[0].message.content.strip()
            if validation_result == "VALID":
                logging.info(f"Report validation passed on iteration {iteration+1}: all customer statements are captured.")
                break
            else:
                logging.warning(f"Report validation found issues on iteration {iteration+1}:\n" + validation_result)
                report = generate_report(transcript, template, issues=validation_result, prev_report=report)
                logging.info(f"Report revised on iteration {iteration+1}.")
        logging.info(f"Analysis complete for transcript: {transcript_path.name}")
        return report
    except Exception as e:
        logging.error(f"Error processing transcript: {str(e)}")
        return None

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
    # ...existing code...
