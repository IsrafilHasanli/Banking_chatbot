CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    cognito_id VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    firstname VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    signup_date DATE NOT NULL,
    phone_number VARCHAR(20) NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_cognito_id ON users (cognito_id);

CREATE TABLE IF NOT EXISTS accounts (
    account_id SERIAL PRIMARY KEY,
    account_number VARCHAR(16) NOT NULL UNIQUE,
    owner_id INTEGER NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    currency VARCHAR(50) NOT NULL,
    balance DOUBLE PRECISION NOT NULL DEFAULT 0,
    creation_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'
);

CREATE INDEX IF NOT EXISTS ix_accounts_owner_id ON accounts (owner_id);
CREATE INDEX IF NOT EXISTS ix_accounts_account_number ON accounts (account_number);
