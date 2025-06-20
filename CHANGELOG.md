# Changelog

## [1.1.3] - 2025-06-20
### Enhanced
- **Prompt Consistency**: Audited all prompt templates for correct placeholder usage and standardized context injection
- **Error Handling**: Improved user-friendly error messages with guidance for common failures (missing files, API errors, configuration issues)
- **Configurable Validation**: Validation stopping criteria now fully configurable via `config.yaml` with `allowed_validation_grades`
- **Logging Standards**: Standardized log levels and messaging across all modules for consistent user experience
- **Configuration Validation**: All config options validated at startup with clear error messages for missing/invalid settings

### Added
- **Comprehensive Testing**: Expanded test coverage for file management, error handling, utilities, and core functionality
- **Enhanced Documentation**: Added detailed prompt customization guide and configuration reference
- **Command Line Flexibility**: Full CLI argument support for input/output directories, templates, and log levels
- **Grade Transparency**: All LLM validation grades logged with detailed feedback for auditability

### Fixed
- Improved exception handling for file I/O, LLM API calls, and template loading
- Better user guidance for environment setup and common configuration issues

## [1.1.1] - 2025-06-06
### Added
- Automatically deletes old report files for each transcript before processing to avoid confusion with previous runs.
- Final log message now indicates SUCCESS or FAILURE after validation attempts.
- Minor log and output improvements for clarity.

## [1.1.0] - 2025-06
### Added
- Introduced 'practical, not perfect' validation: LLM validation now requires reports to be very accurate and complete for business use, not flawless.
- Most transcripts now pass in 1–2 turns, making the workflow efficient and realistic.
- Progress bar and logs improved for transparency and per-file clarity.
- Documentation updated to reflect the new validation approach.

## [1.0.0] - Initial Release
### Feature List
- LLM-powered qualitative analysis using Azure OpenAI (GPT-4)
- MCEM (Microsoft Customer Engagement Model) as the default analysis framework
- Externalized, customizable prompt templates for all LLM steps
- Human-in-the-loop validation step to mitigate LLM hallucinations
- Automated extraction of key insights, direct quotes, and metrics from transcripts
- Multi-format output: Markdown and Word reports
- Handles large transcripts with automatic chunking and consolidation
- CLI workflow with clear progress bar and logging
- Auditability: saves actual LLM/user prompts and validation feedback for each run
- Privacy: `.gitignore` covers sensitive folders by default
- Modular, maintainable codebase with clear folder structure
- Documentation for setup, configuration, and customization