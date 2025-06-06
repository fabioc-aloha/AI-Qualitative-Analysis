# prompts/

This folder contains all prompt templates used by the analysis pipeline. Each template defines the instructions and structure for a specific step in the LLM-driven process. By editing these files, you can fully customize how the LLM analyzes, validates, and revises your transcripts.

**Prompt Templates:**
- `system.txt`: The system prompt, setting the LLM's role, tone, and the MCEM-based analysis structure. Used in every LLM call.
- `initial_analysis.txt`: The user prompt for the initial analysis of a transcript. Defines formatting, content requirements, and where the transcript is inserted.
- `revision.txt`: Used when the initial or revised report is found to be incomplete or inaccurate. Instructs the LLM to revise the previous report, addressing specific issues.
- `validation.txt`: Used to validate the completeness and accuracy of the generated report. The LLM is asked to compare the transcript and report, list any omissions or inaccuracies, and suggest corrections.

**Guidelines:**
- This folder is user-maintained. You are encouraged to edit these prompt templates to match your business framework, reporting standards, or analysis needs.
- Changes to these files immediately affect all future analyses.
- Use version control to track changes to prompt templates for auditability and reproducibility.

**Prompt Engineering Resources:**
- [OpenAI GPT-4.1 Prompting Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [OpenAI Cookbook: Prompt Engineering](https://github.com/openai/openai-cookbook/blob/main/techniques_to_improve_reliability.md)

> For best results, experiment with prompt changes on a single transcript before applying them to a batch.
