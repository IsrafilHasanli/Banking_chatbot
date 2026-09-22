import os

os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASS", "test")

from app.services.chat_cache import is_cacheable_prompt, make_cache_key, normalize_prompt


def test_cache_key_is_stable_for_equivalent_prompts() -> None:
    assert make_cache_key(42, "  What are the tariff fees? ") == make_cache_key(
        42,
        "what are the tariff fees?",
    )


def test_sensitive_account_prompts_are_not_cacheable() -> None:
    assert not is_cacheable_prompt("What is my account balance?")
    assert not is_cacheable_prompt("Please transfer 10 AZN")


def test_general_banking_prompts_are_cacheable() -> None:
    assert is_cacheable_prompt("What are the bank tariff fees?")
    assert normalize_prompt("  Bank   policy  ") == "bank policy"
