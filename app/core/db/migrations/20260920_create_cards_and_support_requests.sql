CREATE TABLE IF NOT EXISTS cards (
    card_id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    card_number VARCHAR(19) NOT NULL UNIQUE,
    card_type VARCHAR(50) NOT NULL DEFAULT 'DEBIT',
    linked_account_number VARCHAR(16),
    expiry_date DATE,
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    blocked_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_cards_owner_id ON cards (owner_id);
CREATE INDEX IF NOT EXISTS ix_cards_card_number ON cards (card_number);

CREATE TABLE IF NOT EXISTS support_requests (
    request_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'GENERAL',
    subject VARCHAR(120) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'OPEN',
    priority VARCHAR(30) NOT NULL DEFAULT 'NORMAL',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_support_requests_user_id ON support_requests (user_id);
CREATE INDEX IF NOT EXISTS ix_support_requests_status ON support_requests (status);
