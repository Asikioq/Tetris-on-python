CREATE TABLE IF NOT EXISTS scores (
        id SERIAL PRIMARY KEY,
        score INTEGER
		);
		
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(50) NOT NULL
    );
	
	CREATE TABLE IF NOT EXISTS game_logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        action VARCHAR(255) NOT NULL
    )
		
	CREATE TABLE IF NOT EXISTS user_stats (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        games_played INTEGER
    )
	
  CREATE TABLE IF NOT EXISTS user_additional_info (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        email VARCHAR(255)
    )
	
	CREATE TABLE IF NOT EXISTS blacklist (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        name VARCHAR(255),
        reason VARCHAR(255) NOT NULL
    )
	
	
