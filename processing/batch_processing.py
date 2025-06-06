import logging
from pathlib import Path

from conversion.output_conversion import convert_markdown_to_docx
from processing.transcript_processing import process_transcript
from utils.env_utils import show_progress_bar, STANDARD_LEVEL

# Define STANDARD log level between INFO (20) and WARNING (30)
if not hasattr(logging, 'STANDARD'):
    logging.addLevelName(STANDARD_LEVEL, 'STANDARD')
    def standard(self, message, *args, **kws):
        if self.isEnabledFor(STANDARD_LEVEL):
            self._log(STANDARD_LEVEL, message, args, **kws)
    logging.Logger.standard = standard


def process_all_transcripts(client, template: str, reports_dir: Path, input_dir: str = "./transcripts", template_path: str = None) -> None:
    """
    Process all transcript files in the specified transcripts directory.

    This function iterates over all .txt files in the transcripts directory, processes each
    transcript using the provided Azure OpenAI client and template, and saves the analysis
    in both Markdown and Word document formats in the reports directory.

    Args:
        client: The Azure OpenAI client.
        template (str): The analysis template content.
        reports_dir (Path): The directory to save output reports.
        input_dir (str): The directory containing input transcript files.
        template_path (str): The path to the template file being used (for display in progress bar).
    """
    from time import sleep
    transcript_files = list(Path(input_dir).glob("*.txt"))
    if not transcript_files:
        logging.warning("No .txt transcript files found in '%s'.", input_dir)
        return
    for transcript_file in transcript_files:
        logger = logging.getLogger()
        is_standard = logger.getEffectiveLevel() == STANDARD_LEVEL
        template_display = template_path if template_path else (template[:40] + '...')
        if is_standard:
            show_progress_bar(0, transcript_name=transcript_file.name, extra=f"Template: {template_display}")
        else:
            logger.standard("==============================")
            logger.standard("Processing transcript: %s", transcript_file.name)
            logger.standard("Step 0: Preparing Analysis - File: '%s', Template: '%s'", transcript_file.name, template_display)
        # Step 1: Transcript Collection
        md_output_file = reports_dir / f"{transcript_file.stem}_analysis.md"
        docx_output_file = reports_dir / f"{transcript_file.stem}_analysis.docx"
        # Step 2: Automated LLM Analysis
        if is_standard:
            show_progress_bar(2, transcript_name=transcript_file.name)
        else:
            logger.standard("Step 2: Automated LLM Analysis - Generating draft report...")
        # Save LLM validation/feedback if available
        feedback_file = reports_dir / f"{transcript_file.stem}_llm_validation.md"
        report, _ = process_transcript(transcript_file, template, client, feedback_file)
        if report:
            md_output_file.write_text(report, encoding="utf-8")
            logging.info("Draft report saved: %s", md_output_file)
            # Step 4: Human Review & Approval
            if is_standard:
                show_progress_bar(4, transcript_name=transcript_file.name)
            else:
                logger.standard("Step 4: Human Review & Approval - Please review the generated reports in '%s' for accuracy, context, and completeness before sharing.", reports_dir)
            # Step 5: Finalized, Shareable Report - Exporting to Word format...
            if is_standard:
                show_progress_bar(5, transcript_name=transcript_file.name)
            else:
                logger.standard("Step 5: Finalized, Shareable Report - Exporting to Word format...")
            convert_markdown_to_docx(md_output_file, docx_output_file)
            logging.info("Word report saved: %s", docx_output_file)
        else:
            logging.error("Failed to generate report for '%s'.", transcript_file.name)
    if is_standard:
        show_progress_bar(5, extra="All transcripts processed. Review reports for human approval and sharing.")
        logging.info("All transcripts processed. Review reports for human approval and sharing.")
    else:
        logger.standard("==============================")
        logger.standard("\nStep 4: Human Review & Approval - Please review the generated reports in '%s' for accuracy, context, and completeness before sharing.", reports_dir)
        logger.standard("Step 5: Finalized, Shareable Report - All reports are ready in Markdown and Word formats.")
