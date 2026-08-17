CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS username_history (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    username TEXT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chats (
    id BIGSERIAL PRIMARY KEY,
    telegram_chat_id BIGINT UNIQUE NOT NULL,
    title TEXT,
    username TEXT,
    chat_type TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memberships (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    telegram_chat_id BIGINT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(telegram_id, telegram_chat_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    telegram_message_id BIGINT NOT NULL,
    telegram_chat_id BIGINT NOT NULL,
    author_id BIGINT,
    username TEXT,
    text TEXT,
    message_date TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(telegram_message_id, telegram_chat_id)
);

CREATE TABLE IF NOT EXISTS searches (
    id BIGSERIAL PRIMARY KEY,
    searcher_id BIGINT,
    query TEXT NOT NULL,
    result_type TEXT,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username
ON users(username);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id
ON users(telegram_id);

CREATE INDEX IF NOT EXISTS idx_username_history_username
ON username_history(username);

CREATE INDEX IF NOT EXISTS idx_messages_author
ON messages(author_id);

CREATE INDEX IF NOT EXISTS idx_messages_chat
ON messages(telegram_chat_id);

CREATE INDEX IF NOT EXISTS idx_messages_username
ON messages(username);
CREATE TABLE IF NOT EXISTS vip_requests (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount INTEGER NOT NULL,
    duration_days INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    processed_by BIGINT
);

CREATE TABLE IF NOT EXISTS vip_users (
    user_id BIGINT PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_vip_requests_user
ON vip_requests(user_id);

CREATE INDEX IF NOT EXISTS idx_vip_requests_status
ON vip_requests(status);

CREATE INDEX IF NOT EXISTS idx_vip_users_expires
ON vip_users(expires_at);
