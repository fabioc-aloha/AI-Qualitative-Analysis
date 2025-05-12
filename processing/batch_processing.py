from pathlib import Path
import logging
from processing.transcript_processing import process_transcript
from conversion.output_conversion import convert_markdown_to_docx

def process_all_transcripts(client, template: str, reports_dir: Path) -> None:
    """
    Process all transcript files in the transcripts directory.
    Args:
        client: The Azure OpenAI client.
        template (str): The analysis template content.
        reports_dir (Path): The directory to save output reports.
    """
    for transcript_file in Path("./transcripts").glob("*.txt"):
        logging.info(f"Processing {transcript_file.name}")
        md_output_file = reports_dir / f"{transcript_file.stem}_analysis.md"
        docx_output_file = reports_dir / f"{transcript_file.stem}_analysis.docx"
        result = process_transcript(transcript_file, template, client)
        if result:
            md_output_file.write_text(result, encoding="utf-8")
            logging.info(f"Analysis saved to {md_output_file}")
            convert_markdown_to_docx(md_output_file, docx_output_file)
