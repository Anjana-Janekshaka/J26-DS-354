# Labelling guide: grading answers (about 20 minutes)

You'll receive one spreadsheet (`annotator_N.csv`). Each row has a **question** about a long
conversation, the **gold answer** from the dataset, and a **response** written by a language model.
Fill in the `label` column for every row with **one** of:

| label | use it when |
|---|---|
| `CORRECT` | The response states the same fact as the gold answer. Different wording, a different date format ("7 May 2023" vs "May 7, 2023") or extra harmless detail is still correct. |
| `PARTIAL` | The response contains only part of the gold answer (e.g. one of two items), or is right but vaguer ("in May" when the gold answer is "7 May 2023"). |
| `WRONG` | The response contradicts the gold answer, misses it entirely, or says it doesn't know. |

`C`, `P` and `W` are accepted as shorthand.

Rules:

- **Grade only against the gold answer.** Don't use your own knowledge of the conversation, and don't
  guess which system produced the response (you aren't told, on purpose).
- **Work alone.** Don't discuss rows with other annotators until everyone has submitted. Some rows
  appear in everyone's sheet; that's how we measure agreement between people.
- If a row is genuinely ambiguous, pick the closest label and write a short reason in `notes`.
- Save as CSV with the same filename and return it. Don't add, remove or reorder columns.
