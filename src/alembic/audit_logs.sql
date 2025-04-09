-- Create the audit_logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    token_id INTEGER NOT NULL REFERENCES tokens(id),
    collection_name VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    filter_data JSONB,
    result_count INTEGER NOT NULL DEFAULT 0,
    response_data JSONB,
    execution_time_ms INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX ix_audit_logs_token_id ON audit_logs(token_id);
CREATE INDEX ix_audit_logs_created_at ON audit_logs(created_at);

