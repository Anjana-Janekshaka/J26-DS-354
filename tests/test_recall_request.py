"""Recall-request cue (conversation manager) and the controller rule that uses it (v5_recall)."""

import pytest

from controller import RuleBasedController, RuleConfig
from conversation_manager import ConversationManager, SignalBus
from conversation_manager.classifier import is_recall_request

from conftest import make_signal


@pytest.mark.parametrize("text", [
    "Remind me which database we settled on.",
    "Do you remember the name of my sister's dog?",
    "Could you tell me what I mentioned about my training schedule?",
    "Can you show the steps we discussed for the deployment?",
    "List the books I talked about earlier in our conversation.",
    "What did you suggest for the logging setup?",
    "Which hotel had I picked in our previous chat?",
])
def test_recall_requests_are_flagged(text):
    assert is_recall_request(text)


@pytest.mark.parametrize("text", [
    "I told my boss I need Fridays off.",  # a statement, not a request
    "We decided to move to Lisbon next spring.",
    "Can you explain how a hash map works?",  # a request, but no back-reference
    "Tell me a joke about cats.",
    "Summarize what we discussed so far.",  # a summary request stays with summarization
    "What's the weather like in Paris in May?",
])
def test_other_messages_are_not_flagged(text):
    assert not is_recall_request(text)


def test_signal_carries_the_cue_for_user_turns_only():
    cm = ConversationManager("c1", token_budget=200, bus=SignalBus())
    assert cm.observe("user", "Remind me what we planned for Saturday.").signal.recall_request
    assert not cm.observe("assistant", "Remind me what we planned for Saturday.").signal.recall_request
    assert not cm.observe("user", "Let's plan Sunday too.").signal.recall_request


def recall_signal(task_type="chat", used=100, budget=100):
    return make_signal(used=used, budget=budget, task_type=task_type).model_copy(update={"recall_request": True})


def test_rule_is_off_by_default():
    _, d = RuleBasedController(RuleConfig(long_chat_strategy="summarization")).decide(recall_signal())
    assert d.selected_strategy == "summarization"


@pytest.mark.parametrize("task_type", ["chat", "exploration"])
def test_recall_request_over_budget_is_routed_like_qa(task_type):
    cfg = RuleConfig(long_chat_strategy="summarization", recall_requests_as_qa=True)
    _, d = RuleBasedController(cfg).decide(recall_signal(task_type))
    assert d.selected_strategy == "rag"
    assert "[recall_request]" in d.rationale
    cfg = cfg.model_copy(update={"qa_strategy": "hybrid"})
    assert RuleBasedController(cfg).decide(recall_signal(task_type))[1].selected_strategy == "hybrid"


def test_recall_rule_leaves_other_cases_alone():
    cfg = RuleConfig(long_chat_strategy="summarization", recall_requests_as_qa=True)
    # History still fits: the window is lossless, so it stays.
    assert RuleBasedController(cfg).decide(recall_signal(used=10))[1].selected_strategy == "sliding_window"
    # Code task types keep their own rules.
    assert RuleBasedController(cfg).decide(recall_signal("code_refactor"))[1].selected_strategy == "summarization"
    assert RuleBasedController(cfg).decide(recall_signal("debugging"))[1].selected_strategy == "sliding_window"
    # No cue: long chat keeps its strategy.
    plain = make_signal(used=100, budget=100, task_type="chat")
    assert RuleBasedController(cfg).decide(plain)[1].selected_strategy == "summarization"
