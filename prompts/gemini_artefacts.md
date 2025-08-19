# Regex for removing Gemini citations
Gemini adds citations to the pdfs in the summaries which clutter the text. You can remove them using the following regex.

\[(?:cite:\s*(?:\d+(?:,\s*\d+)*)?|cite_start)\]

Gemini can not reliabe provide side hooks. Replace the part below with #
https://www.google.com/search?q=%23