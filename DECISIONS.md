# DECISIONS.md

## Architecture Overview

### High-Level Design
- The solution is a Python script (`process_transcripts.py`) that automates the analysis of customer interview transcripts using Azure OpenAI GPT-4.
- The script is designed for batch processing: it reads all `.txt` files from a `transcripts/` directory and outputs structured analysis reports to a `reports/` directory.
- Analyses are generated in Markdown format and then converted to Word (`.docx`) format using Pandoc for business-friendly consumption.
- The analysis is guided by a reusable template (`AnalysisTemplate.txt`) that enforces the MCEM (Microsoft Customer Engagement Model) structure.
- The script supports both small and large transcripts by chunking large files to stay within GPT-4 token limits, then consolidating results.
- Environment variables (API keys, endpoints, deployment names) are loaded from a `.env` file for security and flexibility.

### Key Components
- **process_transcripts.py**: Main script orchestrating the workflow (loading environment, processing files, calling Azure OpenAI, handling output).
- **AnalysisTemplate.txt**: Template file that defines the structure and requirements for the analysis output.
- **transcripts/**: Directory containing input transcript files.
- **reports/**: Directory for output reports (Markdown and Word formats).
- **requirements.txt**: Lists required Python packages (`openai`, `python-dotenv`, `tiktoken`).
- **DECISIONS.md**: Documents design decisions, architecture, and improvement recommendations.

### External Dependencies
- **Azure OpenAI**: Used for natural language analysis and report generation.
- **Pandoc**: Required for converting Markdown reports to Word documents.
- **tiktoken**: Used for accurate token counting to manage GPT-4 prompt limits.
- **python-dotenv**: Loads environment variables from `.env`.

---

## Project Structure (as of 2025-05-11)

- `process_transcripts.py`: Main entry point for the application.
- `utils/`
  - `env_utils.py`: Logging setup, environment variable and Pandoc checks.
  - `file_utils.py`: Token counting, OpenAI client creation, template loading, and reports directory management.
- `processing/`
  - `transcript_processing.py`: Transcript processing logic for single transcripts.
  - `transcript_chunking.py`: Logic for chunking and processing large transcripts.
  - `batch_processing.py`: Batch processing of all transcripts.
- `conversion/`
  - `output_conversion.py`: Markdown to Word document conversion.
- `transcripts/`: Input transcript files.
- `reports/`: Output analysis files (Markdown and Word).
- `AnalysisTemplate.txt`: Analysis template for MCEM structure.
- `requirements.txt`: Python dependencies.
- `DECISIONS.md`: Architecture, decisions, and improvement log.

### Notes
- All modules are now organized in folders by responsibility (utils, processing, conversion).
- Imports in all scripts have been updated to reflect the new structure.
- This modular structure improves maintainability, clarity, and testability.

---

## Recent Decisions & Updates (2025-05-12)

- The analysis template is now continuously optimized using the generated output to improve future analyses.
- The main docstring and documentation have been updated to reflect this optimization process.

## 2025-05-12: Template Refinement – Contradictions Section
- Added a dedicated section to the analysis template for "Contradictions, Nuanced Feedback & Mixed Sentiments (Verbatim)".
- This section requires explicit listing of all contradictions, nuanced feedback, or mixed sentiments from the transcript, with direct quotes, attribution, and context.
- The change was made to address persistent omissions of nuanced or contradictory content in complex transcripts, as identified in validation logs.
- The goal is to further reduce the number of LLM validation/revision iterations required for challenging transcripts by making these requirements explicit and auditable.

## 2025-05-12: Template Simplification and Narrative Guidance
- Removed line number references for transcript quotes; now require a brief, descriptive context for each quote instead.
- Added explicit formatting guidance: sections should be written in clear, descriptive paragraphs, with bullets reserved for lists of quotes, recommendations, or summary tables.
- Emphasized narrative flow and context to improve readability and usability for non-technical stakeholders.
- These changes address concerns about template complexity and LLM/human usability, aiming for a balance between completeness and clarity.

---

## To Do: Recommendations for Improvement

- [x] Replace print statements with the `logging` module for better diagnostics and log levels.
- [x] Validate required environment variables at startup and exit gracefully if missing.
- [x] Check for Pandoc installation before attempting Word conversion; provide a clear error if not found.
- [x] Refactor the `main()` function into smaller, testable functions (e.g., for environment checks, file processing, and conversion).
- [x] Use a list (not a string) for the Pandoc subprocess call to avoid shell injection risks.
- [x] Improve error handling and user feedback throughout the script.
- [x] Document all functions with clear docstrings and type hints.
- [x] Implement configuration file support (YAML/JSON) for advanced settings.
- [x] The analysis template is optimized using the output (continuous improvement loop).
- [ ] Enhance output formatting (e.g., add tables, summary sections, or visualizations).
- [ ] Allow selection of different analysis templates via config.
- [ ] Add language detection and support for multilingual transcripts.
- [ ] Integrate output quality checks (e.g., grammar, completeness, MCEM compliance).
- [ ] Provide a summary report aggregating insights across all processed transcripts.
- [ ] Add logging to file (not just console) for auditability.
- [ ] Support additional output formats (e.g., PDF, HTML).
- [ ] Add a CLI flag for dry-run/preview mode.
- [ ] Improve error messages with actionable suggestions.
- [ ] Add versioning and changelog for the codebase.

---

Add further recommendations as the project evolves.

### Configuration File Support
- Added `config.yaml` for advanced settings (Azure credentials, processing options, template selection, etc.).
- Created `utils/config_utils.py` to load and expand environment variables in YAML config.
- The main script now loads settings from `config.yaml` and uses them for environment validation and template selection.
- This enables flexible, maintainable, and environment-agnostic configuration management for the project.
