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
│  (Azure OpenAI) │     │ Grade Check │
└────────┬────────┘     └──────┬──────┘
         │                     │
         │                Yes  │  No
         │        (A/B/VALID)  │  (INVALID)
         │                     ↓
         │              ┌──────┴─────────┐
         │              │   Revise       │
         │              │ (Azure OpenAI) │
         │              └──────┬─────────┘
         │                     │
         └─────────────────────┘
                               │
                        Max 5 iterations
```

**Validation Configuration:**
- Configurable allowed grades in `config.yaml`
- Default: `["VALID", "VALID (A)", "VALID (B)"]`
- Each validation pass logged with grade and feedback
- Success/failure outcome logged for transparency

# Detailed Implementation Flow

```
main.py
  ↓
1. Parse CLI args (--input, --output, --template, --log-level)
  ↓
2. Set up logging with custom STANDARD level (25)
  ↓
3. Load environment (.env) and configuration (config.yaml)
  ↓
4. Environment validation:
   - check_env_vars() for Azure OpenAI credentials
   - check_pandoc_installed() for Word document conversion
   - get_client() to create Azure OpenAI client
  ↓
5. Determine paths from CLI args or config defaults:
   - input_dir (default: 'transcripts')
   - output_dir (default: 'reports') 
   - template_path (default: 'AnalysisTemplate.txt')
  ↓
6. Load analysis template and ensure reports directory exists
  ↓
7. For each transcript in input directory:
    process_all_transcripts()  # (processing/batch_processing.py)
      ↓
    A. File Management
       - Delete old report files for this transcript (if any):
         * {transcript}_analysis.md
         * {transcript}_analysis.docx 
         * {transcript}_llm_validation.md
       - Show progress bar: Step 0 & 1 (Preparing & Collection)
      ↓
    B. Automated LLM Analysis  # (processing/transcript_processing.py)
       - Show progress bar: Step 2 (Automated LLM Analysis)
       - process_transcript():
         * Load transcript file with error handling
         * Load prompt templates from prompts/:
           - initial_analysis.txt
           - validation.txt  
           - revision.txt
           - system.txt
         * Check token limits (128K context window)
         * Generate initial analysis using Azure OpenAI
         * Save actual prompt used to reports/ for auditability
      ↓
    C. LLM Self-Check & Validation Loop (Up to 5 iterations)
       - Show progress bar: Step 3 (LLM Self-Check & Validation)
       - Load validation configuration from config.yaml:
         * allowed_validation_grades: ["VALID", "VALID (A)", "VALID (B)"]
       - For each validation pass:
         * Call Azure OpenAI to validate the report
         * Save validation prompt and response to reports/
         * Check if LLM grade matches allowed grades
         * If valid: STOP (success)
         * If invalid: Generate revision using revision prompt
         * Save revision prompt to reports/
       - Log final outcome: SUCCESS or FAILURE
       - Save all validation feedback to {transcript}_llm_validation.md
      ↓
    D. Human Review Stage
       - Show progress bar: Step 4 (Human Review & Approval)
       - Save final analysis to {transcript}_analysis.md
       - Log guidance for human review
      ↓
    E. Output Generation
       - Show progress bar: Step 5 (Finalized Report)
       - convert_markdown_to_docx() using Pandoc
       - Save Word document to {transcript}_analysis.docx
  ↓
8. Final completion messages and guidance for human review
```

## Large Transcript Processing
When a transcript exceeds the token limit (128,000 tokens for GPT-4o), the system uses transcript_chunking.py:

**Note**: The current implementation includes chunking logic but the main processing flow checks token limits and aborts if exceeded rather than automatically chunking. The chunking functionality exists for future enhancement.

1. **Token Management**
    - Check combined token count (transcript + template + completion tokens)
    - MAX_CONTEXT_TOKENS = 128,000 (GPT-4o context window)
    - MAX_COMPLETION_TOKENS = 16,000
    - If total exceeds limits, currently aborts with user error

2. **Chunking Process** (process_large_transcript - available but not integrated)
    - Split transcript into manageable chunks (configurable chunk_size)
    - Preserve context and coherence at chunk boundaries
    - Track chunk sequence (1/N, 2/N, etc.)

3. **Per-Chunk Processing**
    - Process each chunk with segment markers
    - Include MCEM framework context in system prompts
    - Handle individual chunk failures gracefully

4. **Result Consolidation**
    - Combine individual chunk analyses
    - Run consolidation pass for coherence
    - Remove redundancies and smooth transitions
    - Return single coherent analysis

**Final outputs** (in reports/):
- `{transcript}_analysis.md` (LLM-generated structured analysis)
- `{transcript}_analysis.docx` (Word version via Pandoc conversion)
- `{transcript}_llm_validation.md` (validation feedback log with grades)
- `{transcript}_initial_prompt.txt` (actual initial analysis prompt used)
- `{transcript}_revision_prompt_passN.txt` (revision prompts for each failed validation)
- `{transcript}_validation_prompt_passN.txt` (validation prompts for each check)

**Key supporting modules:**
- `processing/batch_processing.py`: Orchestrates per-transcript workflow, progress tracking, file cleanup
- `processing/transcript_processing.py`: Handles LLM interactions, validation loop, prompt saving
- `processing/transcript_chunking.py`: Large transcript handling (available but not integrated)
- `conversion/output_conversion.py`: Markdown to Word conversion via Pandoc
- `utils/env_utils.py`: Logging, progress bar, environment validation, error handling
- `utils/file_utils.py`: File operations, token counting, template loading
- `utils/config_utils.py`: Configuration loading with environment variable expansion
- `prompts/`: LLM prompt templates (system.txt, initial_analysis.txt, revision.txt, validation.txt)

**Configuration & Environment:**
- `.env`: Azure OpenAI credentials and endpoints
- `config.yaml`: Processing settings, validation grades, paths
- CLI arguments: `--input`, `--output`, `--template`, `--log-level`

**Logging & Progress:**
- Custom STANDARD log level (25) for user-friendly progress
- Detailed logging at DEBUG/INFO levels for troubleshooting
- Progress bar showing steps 0-5 for each transcript
- Success/failure logging for validation outcomes

**Auditability & Privacy:**
- All actual LLM prompts saved with timestamp and iteration info
- Validation feedback preserved with grades and reasoning
- `.gitignore` covers transcripts/ and reports/ directories
- Configurable validation stopping criteria
