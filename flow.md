# Codebase Flow: AI Qualitative Analysis

## High-Level Flow Diagram
```
┌──────────────┐
│   main.py    │
└──────┬───────┘
       ↓
┌──────┴───────┐     ┌─────────────────┐
│ Environment  │ ←── │   config.yaml   │
│    Setup     │     │     .env        │
└──────┬───────┘     └─────────────────┘
       ↓
┌──────┴───────┐     ┌─────────────────┐
│Process Batch │ ←── │  transcripts/   │
│of Transcripts│     │    *.txt        │
└──────┬───────┘     └─────────────────┘
       ↓
┌──────┴───────┐     ┌─────────────────┐
│  Process     │ ←── │    prompts/     │
│ Individual   │     │  templates      │
│ Transcript   │     └─────────────────┘
└──────┬───────┘
       ↓
┌──────┴───────┐
│ LLM Analysis │
│ & Validation │
└──────┬───────┘
       ↓
┌──────┴───────┐     ┌─────────────────┐
│  Generate    │ ←── │    reports/     │
│   Reports    │ ──→ │ MD, DOCX, Logs  │
└──────────────┘     └─────────────────┘
```

## Detailed Processing Flow
```
                               Large Transcript Handling
                              ┌────────────────────────┐
                              │   Token Count Check    │
                              └──────────┬─────────────┘
                                        ↓
                              ┌──────────┴─────────────┐
                              │   Split into Chunks    │
                              └──────────┬─────────────┘
                                        ↓
┌──────────────┐              ┌──────────┴─────────────┐
│  Analysis    │ ─────────→   │Process Individual      │
│  Template    │              │Chunks with Context     │
└──────────────┘              └──────────┬─────────────┘
                                        ↓
                              ┌──────────┴─────────────┐
                              │ Consolidate Results    │
                              └──────────┬─────────────┘
                                        ↓
                              ┌──────────┴─────────────┐
                              │   Validation Loop      │
                              └────────────────────────┘
```

## Validation & Revision Loop
```
┌─────────────────┐
│ Initial Report  │
└────────┬────────┘
         ↓
┌────────┴────────┐     ┌─────────────┐
│  Validation     │ ──→ │   Valid?    │
└────────┬────────┘     └──────┬──────┘
         │                     │
         │                Yes  │  No
         │                     ↓
         │              ┌──────┴──────┐
         └───────────── │   Revise    │
                        └─────────────┘
```

# Detailed Implementation Flow

```
main.py
  ↓
Parse CLI args, set up logging, check environment (env_utils.py)
  ↓
For each transcript in transcripts/:
    process_all_transcripts()  # (processing/batch_processing.py)
      ↓
    1. Delete old report files for this transcript (if any)
        - Removes previous *_analysis.md, *_analysis.docx, *_llm_validation.md
      ↓
    2. Transcript Collection
        - Load .txt transcript from transcripts/ folder
        - Log step and progress bar (env_utils.py)
      ↓
    3. Automated LLM Analysis
        - process_transcript()  # (processing/transcript_processing.py)
            * Load analysis template (prompts/initial_analysis.txt)
            * Prepare prompt with transcript inserted
            * Call Azure OpenAI (GPT-4) to generate draft report
            * Save actual prompt to reports/ for auditability
            * Save draft report as *_analysis.md
      ↓
    4. LLM Self-Check & Validation (Practical, Not Perfect)
        - For up to 5 passes:
            * Prepare validation prompt (prompts/validation.txt)
            * Call Azure OpenAI to validate report
            * Save validation prompt and feedback to reports/
            * If LLM returns VALID, VALID (A), or VALID (B):
                - Stop validation loop (success)
            * Else:
                - Prepare revision prompt (prompts/revision.txt)
                - Call Azure OpenAI to revise report
                - Save revision prompt to reports/
        - Log each validation pass and result
        - Add blank line after last pass for separation
        - Final log: SUCCESS or FAILURE after validation attempts
      ↓
    5. Human Review & Approval
        - Log step and progress bar
        - User reviews *_analysis.md and *_llm_validation.md for accuracy, context, and completeness
        - Make manual edits if needed
      ↓
    6. Finalized, Shareable Report
        - convert_markdown_to_docx()  # (conversion/output_conversion.py)
            * Convert *_analysis.md to *_analysis.docx using Pandoc
        - Log step and progress bar
        - Save final outputs to reports/
```

## Large Transcript Processing
When a transcript exceeds the token limit (128,000 tokens for GPT-4), the system automatically handles it using transcript_chunking.py:

1. Token Management
    - Check combined token count (transcript + template)
    - Account for expected completion tokens
    - If exceeds limits, trigger chunking process

2. Chunking Process (process_large_transcript)
    - Split transcript into manageable chunks
    - Preserve context and coherence at chunk boundaries
    - Track chunk sequence (1/N, 2/N, etc.)

3. Per-Chunk Processing
    - Process each chunk with appropriate context
    - Include segment markers in prompts
    - Handle individual chunk failures gracefully

4. Result Consolidation
    - Combine individual chunk analyses
    - Run consolidation pass to ensure coherence
    - Remove redundancies and smooth transitions
    - Return single coherent analysis

5. Error Handling
    - Individual chunk failures don't stop processing
    - Fallback to partial results if some chunks succeed
    - Clear error logging and status tracking

Final outputs (in reports/):
    - {transcript}_analysis.md (LLM-generated structured analysis)
    - {transcript}_analysis.docx (Word version)
    - {transcript}_llm_validation.md (validation feedback log)
    - {transcript}_initial_prompt.txt, _revision_prompt_passN.txt, _validation_prompt_passN.txt (actual prompts used)
    - Diagnostic logs (console, progress bar, and info logs)

Key supporting modules:
- processing/batch_processing.py: Orchestrates per-transcript workflow, progress bar, and logging
- processing/transcript_processing.py: Handles LLM prompt construction, validation loop, and prompt/report saving
- conversion/output_conversion.py: Markdown to Word conversion
- utils/env_utils.py: Logging, progress bar, environment checks
- prompts/: All LLM prompt templates (system, initial_analysis, revision, validation)
- reports/: All outputs, logs, and prompt audit files
- transcripts/: Input .txt files

Auditability & Privacy:
- All actual LLM/user prompts and validation feedback are saved for each run
- .gitignore covers transcripts/ and reports/ to prevent accidental publishing of sensitive data
