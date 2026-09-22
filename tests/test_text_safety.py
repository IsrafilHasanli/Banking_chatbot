from app.core.text_safety import remove_user_name


def test_remove_user_name_strips_personal_names() -> None:
    response = "For Aysel, Aysel's card is active. Regards, Mammad."

    cleaned = remove_user_name(response, "Aysel", "Mammad")

    assert "Aysel" not in cleaned
    assert "Mammad" not in cleaned
    assert "your card is active" in cleaned


def test_remove_user_name_normalizes_whitespace() -> None:
    response = "Leyla,   your account is active.\n\n\nStatus: ACTIVE"

    cleaned = remove_user_name(response, "Leyla", None)

    assert cleaned == "your account is active.\n\nStatus: ACTIVE"
