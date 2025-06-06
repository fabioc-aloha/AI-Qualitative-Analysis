# Learnings: Iterative Refinement of the Qualitative Interview Processor

## Context
To improve the completeness and accuracy of automated MCEM interview transcript analyses, we iteratively enhanced the analysis template (`AnalysisTemplate.txt`) and the processing workflow. The primary goal was to reduce the number of LLM validation/revision iterations required for each transcript, especially for complex cases such as "rosebank" and "Tara Anglican School".

## Key Refinement Steps

1. **Centralized Configuration**
   - All environment and template settings were moved to `config.yaml` for consistency and maintainability.
   - Template selection is now dynamic and centrally managed.

2. **Template Enhancements**
   - Added explicit instructions for verbatim inclusion, attribution, and context for all quotes, ratings, and recommendations.
   - Introduced comprehensive checklists, a transcript coverage table, and section completeness self-checks.
   - Added new sections for frequently missed areas: representative changes, communication, pricing/value, AI support, product targeting, and suitability.
   - Created a "Frequently Missed Quotes & Context" checklist and explicit prompts for nuanced/contradictory feedback, post-COVID changes, and vendor/partner interactions.
   - Added a dedicated section for contradictions, nuanced feedback, and mixed sentiments, with instructions for verbatim inclusion, attribution, and context.
   - Removed line number references for transcript quotes; now require a brief, descriptive context for each quote instead.
   - Added explicit formatting guidance: sections should be written in clear, descriptive paragraphs, with bullets reserved for lists of quotes, recommendations, or summary tables.
   - Emphasized narrative flow and context to improve readability and usability for non-technical stakeholders.
   - These changes address concerns about template complexity and LLM/human usability, aiming for a balance between completeness and clarity.

3. **Workflow Improvements**
   - The script (`main.py`) was refactored to use the improved template and configuration.
   - The workflow now enforces completion of all checklists and self-checks before a report is considered complete.

4. **Validation and Iteration**
   - After each template/configuration change, the script was run on all transcripts.
   - For straightforward transcripts, the number of validation iterations dropped to 1.
   - For complex transcripts, persistent omissions of nuanced or context-specific content required up to 5 iterations, even after multiple rounds of template refinement.

5. **Targeted Additions**
   - Based on validation logs, further explicit instructions and checklists were added for the most commonly missed content.
   - A special section for contradictions and nuanced feedback was introduced to ensure these are not overlooked.

## Outcomes
- The workflow is now highly optimized for LLM compliance, with most transcripts passing in 1-2 iterations.
- For the most challenging transcripts, the new contradictions/nuanced feedback section and explicit checklists help reduce omissions, but some LLM limitations remain.

## Next Steps
- Explore prompt chaining, quote extraction pre-passes, or more granular chunking to further reduce iterations for complex transcripts.
- Continue to monitor validation logs and refine the template and workflow as needed.

---

# Key Learnings from Refactor (May 2024)

## Process Flow & Logging
- Sectioned, stepwise logging for each transcript greatly improves transparency and user trust.
- Announcing each process step (collection, LLM analysis, self-check, human review, finalization) in logs helps users understand and audit the workflow.
- Summarizing human review and finalization at the end of batch processing reinforces the importance of human-in-the-loop validation.

## CLI & User Experience
- Adding CLI options for input/output/template increases flexibility and usability for diverse research workflows.
- Clear CLI help and documentation reduce onboarding friction for new users.

## Hallucination Mitigation
- Explicitly documenting and logging the LLM self-check step, followed by mandatory human review, is essential for mitigating hallucinations and ensuring trustworthy outputs.
- Aligning code, logs, and documentation around this process makes the tool more robust and defensible in research settings.

## Documentation
- Placing the process flow and validation steps at the top of the README helps set user expectations and supports best practices.
- Keeping README, code, and logs in sync prevents confusion and supports reproducibility.

## Dependency & Error Handling
- Ensuring all dependencies are listed in requirements.txt and fixing import/syntax errors in tests improves reliability and maintainability.

## May 2024: Progress Bar & Logging Enhancement
- Added an explicit initial step (0/5) to the progress bar for each transcript file, displaying the file name and the analysis template being used.
- This change clarifies per-file processing in logs and progress output, improving transparency and user guidance.
- All subsequent pipeline steps were shifted to accommodate the new step 0, ensuring accurate and granular progress tracking throughout the analysis workflow.

---

## Release 1.1.0 (June 2025): Practical, Not Perfect Validation
- LLM validation now requires reports to be very accurate and complete for business use, not flawless.
- Most transcripts pass validation in 1–2 turns, making the workflow efficient and realistic.
- Progress bar and per-file logging improved for transparency.
- Documentation and process flow updated to reflect the new approach.

## Release 1.1.1 (June 2025): Output Hygiene & Outcome Logging
- Old report files for each transcript are now deleted before processing to prevent confusion.
- Final log message after validation now clearly indicates SUCCESS or FAILURE.
- Minor improvements to log clarity and output separation.

---

*This document summarizes the learnings and rationale behind the iterative refinement of the Qualitative Interview Processor analysis template and workflow.*
