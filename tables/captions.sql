CREATE TABLE captions (
    id serial PRIMARY KEY,
    caption_text text NOT NULL,
    tags text,
    length text,
    category text,
    tone text,
    likes integer DEFAULT 0,
    shares integer DEFAULT 0,
    comments integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT current_timestamp
);
