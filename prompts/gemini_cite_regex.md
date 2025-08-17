# Regex for removing Gemini citations
Gemini adds citations to the pdfs in the summaries whihc clutter the text. You can remove them using the following regex.

\[(?:cite:\s*(?:\d+(?:,\s*\d+)*)?|cite_start)\]