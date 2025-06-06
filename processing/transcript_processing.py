import os
import logging
from pathlib import Path
from typing import Optional
from openai import AzureOpenAI
from utils.file_utils import count_tokens, get_client, load_analysis_template, ensure_reports_dir
from utils.env_utils import setup_logging, check_env_vars, check_pandoc_installed, STANDARD_LEVEL


def process_transcript(transcript_path: Path, template: str, client: AzureOpenAI, feedback_file_path: Path = None, prompts_dir: Path = None) -> Optional[str]:
    """
    Process a single transcript file and generate an analysis using Azure OpenAI.

    This function loads a transcript, checks token limits, and generates a structured
    analysis report using the provided template and Azure OpenAI client. It iteratively
    validates the report for completeness and accuracy, revising as needed.

    Args:
        transcript_path (Path): Path to the transcript file.
        template (str): The analysis template content.
        client (AzureOpenAI): The Azure OpenAI client.
    Returns:
        Optional[str]: The generated analysis text, or None if processing fails.
    """
    logging.info(f"Starting analysis for transcript: {transcript_path.name}")
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = f.read()
    except FileNotFoundError:
        logging.error(f"Transcript file not found: {transcript_path}")
        return None
    logging.info("Transcript loaded from file.")
    # Ensure prompts directory exists
    # Always use root-level prompts/ directory
    if prompts_dir is None:
        root_dir = Path(__file__).resolve().parent.parent  # project root
        prompts_dir = root_dir / 'prompts'
    prompts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = root_dir / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    with open(prompts_dir / 'initial_analysis.txt', 'r', encoding='utf-8') as f:
        initial_prompt_template = f.read()
    with open(prompts_dir / 'validation.txt', 'r', encoding='utf-8') as f:
        validation_prompt_template = f.read()
    with open(prompts_dir / 'revision.txt', 'r', encoding='utf-8') as f:
        revision_prompt_template = f.read()
    with open(prompts_dir / 'system.txt', 'r', encoding='utf-8') as f:
        system_prompt_template = f.read()
    transcript_stem = transcript_path.stem.replace(' ', '_')
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
        def save_prompt(prompt_content, prompt_type, iteration=None):
            """
            Save a prompt to the prompts/ directory with a unique name.
            """
            if iteration is not None:
                prompt_filename = f"{transcript_stem}_{prompt_type}_pass{iteration}.txt"
            else:
                prompt_filename = f"{transcript_stem}_{prompt_type}_prompt.txt"
            prompt_path = prompts_dir / prompt_filename
            with open(prompt_path, "w", encoding="utf-8") as pf:
                pf.write(prompt_content)

        def save_actual_prompt(prompt_content, prompt_type, iteration=None):
            """
            Save the actual prompt (with variables filled in) to the reports/ directory for troubleshooting.
            """
            if iteration is not None:
                prompt_filename = f"{transcript_stem}_{prompt_type}_prompt_pass{iteration}.txt"
            else:
                prompt_filename = f"{transcript_stem}_{prompt_type}_prompt.txt"
            prompt_path = reports_dir / prompt_filename
            with open(prompt_path, "w", encoding="utf-8") as pf:
                pf.write(prompt_content)

        def generate_report(transcript, template, issues=None, prev_report=None, iteration=None):
            """
            Helper function to generate or revise a report using Azure OpenAI.
            Loads prompt template from file, fills in variables, and saves the actual prompt used.
            """
            if not issues:
                prompt = initial_prompt_template.format(transcript=transcript)
                save_actual_prompt(prompt, "initial")
            else:
                prompt = revision_prompt_template.format(transcript=transcript, prev_report=prev_report or "", issues=issues)
                save_actual_prompt(prompt, "revision", iteration)
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=[
                    {"role": "system", "content": system_prompt_template},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=MAX_COMPLETION_TOKENS
            )
            return response.choices[0].message.content

        report = generate_report(transcript, template)
        logging.info("Initial report generated by Azure OpenAI.")
        validation_feedback = []
        feedback_md_header = f"# LLM Validation Feedback\n\n"
        feedback_file = None
        if feedback_file_path:
            feedback_file = open(feedback_file_path, "w", encoding="utf-8")
            feedback_file.write(feedback_md_header)
        from utils.env_utils import show_progress_bar
        show_progress_bar(3, transcript_name=transcript_path.name)
        success = False
        for iteration in range(5):
            show_progress_bar(3, transcript_name=transcript_path.name, extra=f"LLM Validation/Revision Pass {iteration+1}")
            logging.info(f"Validation pass {iteration+1}: Checking report completeness against transcript.")
            validation_prompt = validation_prompt_template.format(transcript=transcript, report=report)
            save_actual_prompt(validation_prompt, "validation", iteration+1)
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
            is_final = validation_result.strip().upper() in ["VALID", "VALID (A)", "VALID (B)"]
            feedback_entry = f"### Validation Pass {iteration+1}\n{validation_result}\n"
            validation_feedback.append(feedback_entry)
            if feedback_file:
                feedback_file.write(feedback_entry)
                feedback_file.flush()
            if is_final:
                logging.info(f"Report validation passed on iteration {iteration+1}: {validation_result}")
                # Add an extra blank line after the last (successful) pass
                if feedback_file:
                    feedback_file.write("\n")
                    feedback_file.flush()
                success = True
                break
            else:
                logging.info(f"Report validation found issues on iteration {iteration+1}:\n" + validation_result)
                report = generate_report(transcript, template, issues=validation_result, prev_report=report, iteration=iteration+1)
                logging.info(f"Report revised on iteration {iteration+1}.")
        # Final outcome log
        logger = logging.getLogger()
        if logger.getEffectiveLevel() == STANDARD_LEVEL:
            if success:
                logger.log(STANDARD_LEVEL, f"SUCCESS: Analysis for '{transcript_path.name}' passed validation.")
            else:
                logger.log(STANDARD_LEVEL, f"FAILURE: Analysis for '{transcript_path.name}' did NOT pass validation after 5 attempts.")
        else:
            if success:
                logging.info(f"SUCCESS: Analysis for '{transcript_path.name}' passed validation.")
            else:
                logging.error(f"FAILURE: Analysis for '{transcript_path.name}' did NOT pass validation after 5 attempts.")
        if feedback_file:
            feedback_file.close()
        logging.info(f"Analysis complete for transcript: {transcript_path.name}")
        feedback_md = feedback_md_header + "".join(validation_feedback)
        return report, feedback_md
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
