CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,  -- Assuming there is a user ID to link preferences to users
    notifications_enabled BOOLEAN DEFAULT TRUE,
    response_style VARCHAR(20) DEFAULT 'friendly',
    content_tone VARCHAR(20) DEFAULT 'neutral',
    content_frequency VARCHAR(20) DEFAULT 'daily',
    notification_method VARCHAR(20) DEFAULT 'email',
    interaction_type VARCHAR(20) DEFAULT 'reactive',
    comment_response_style VARCHAR(20) DEFAULT 'friendly',
    comment_content_tone VARCHAR(20) DEFAULT 'positive',
    comment_interaction_type VARCHAR(20) DEFAULT 'proactive',
    reply_response_style VARCHAR(20) DEFAULT 'formal',
    reply_content_tone VARCHAR(20) DEFAULT 'neutral',
    reply_interaction_type VARCHAR(20) DEFAULT 'reactive',
    tags TEXT[],  -- Assuming tags are stored as an array of strings
    category VARCHAR(50) DEFAULT 'general',
    tone VARCHAR(20) DEFAULT 'reserved',
    audience VARCHAR(50) DEFAULT 'general',
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
