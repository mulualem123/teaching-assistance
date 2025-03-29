-- Active: 1682668039818@@127.0.0.1@3306
-- schema.sql (safe for existing data)
CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS mezmur_org1 (
  m_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  titleen TEXT,
  azmach TEXT NOT NULL,
  azmachen TEXT,
  dir TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP  
);

CREATE TABLE IF NOT EXISTS mezmur (
  m_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  titleen TEXT,
  azmach TEXT NOT NULL,        -- Original Ge'ez lyrics
  azmachen TEXT,               -- Original transliterated lyrics
  engTrans TEXT,               -- Original English translation
  timed_geez TEXT,             -- New: Ge'ez lyrics with timestamps
  timed_latin TEXT,            -- New: Transliterated lyrics with timestamps
  timed_english TEXT,          -- New: English lyrics with timestamps
  dir TEXT NOT NULL,
  audio_file TEXT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  cat1 TEXT NOT NULL,
  cat2 TEXT NOT NULL,
  cat3 TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tagList (
  t_id INTEGER PRIMARY KEY,
  tag TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS mezTags (
  tag_id INTEGER,
  m_id INTEGER,
  tag TEXT NOT NULL,
  FOREIGN KEY (m_id) REFERENCES mezmur(m_id),
  FOREIGN KEY (tag_id) REFERENCES tagList(t_id),
  PRIMARY KEY (m_id, tag_id)
);
