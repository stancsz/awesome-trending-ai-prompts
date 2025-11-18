# chatgpt/text

Text-focused ChatGPT prompts — required CSV format.

All prompt files in this directory must be UTF-8 encoded CSV files with the exact header (first line):

prompt,contributor,comment

Rules:
- Header order must be exactly: prompt,contributor,comment
- Each row represents a single prompt.
- Fields that contain commas, double quotes, or newlines must be wrapped in double quotes.
- Escape double quotes by doubling them (e.g., "He said ""hello""").
- contributor should be a short handle (e.g., @alice or an email) or use @curated for curated entries.
- comment is a short tag or note (optional).
- Use UTF-8 encoding; preserve newlines inside quoted fields for multiline prompts.

Example row:
"Summarize the following article:\n[article text]",@alice,"summarization"

Please only add CSV files that follow these rules. Incorrectly formatted files may be rejected or reformatted.
