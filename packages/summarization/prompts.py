"""Three distinct tier prompts (build guide 6.3). The tiers differ in *what they may do*,
not just in compression ratio: L1 extracts verbatim, L2 describes intent/decisions from L1 facts,
L3 is the only tier allowed to generalize."""

L1_SYSTEM = """You extract memory records from a conversation excerpt. EXTRACT VERBATIM. Do not interpret,
paraphrase, merge or infer. Copy exact wording, names, numbers and code signatures.

Return ONLY a JSON object:
{
  "facts": [{"key": str, "value": str, "kind": one of
              ["code_signature","rename","attribute","decision","constraint","request","statement"],
             "source_turn_id": str}],
  "entities": [str],
  "constraints": [str]
}
Key conventions (these keys are used to detect contradictions, so be consistent):
- code: "func:<name>" / "class:<name>" with value = the exact signature line, e.g. "def get_user_tasks(uid)"
- renames: "rename:<old_name>" with value = "<new_name>"
- user attributes: "user.<attribute>" (user.location, user.job, ...)
- settings/choices: "setting:<name>" / "choice:<purpose>"
- anything else: "stmt:<turn_id>:<n>" """

L1_USER = """Conversation excerpt (turn ids in brackets):
{turns}

Extract the L1 record now."""

L2_SYSTEM = """You write the L2 (intent) tier of a hierarchical memory from L1 fact records.
Describe what the user is trying to do and what was decided. DROP individual facts: do not copy
facts, values or code signatures unless they are themselves a decision. Do not generalize about
the user as a person (that is the L3 tier's job).

Return ONLY a JSON object:
{"intent": str, "decisions": [str], "open_goals": [str]}"""

L2_USER = """L1 records:
{l1_json}

Write the L2 record now."""

L3_SYSTEM = """You write the L3 (profile) tier of a hierarchical memory from L2 intent records.
This is the ONLY tier allowed to generalize: describe who the user is, what they ultimately want,
and the current state of the work. Be brief.

Return ONLY a JSON object:
{"persona": str, "main_objective": str, "final_state": str}"""

L3_USER = """L2 records:
{l2_json}

Write the L3 record now."""

NAIVE_SYSTEM = """Summarize the conversation so far in a short paragraph."""
