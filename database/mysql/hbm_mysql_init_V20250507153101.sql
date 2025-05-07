-- 创建数据库用户(与docker-compose环境变量一致)
CREATE USER IF NOT EXISTS 'hbm_user'@'%' IDENTIFIED BY 'hbm_password';
GRANT ALL PRIVILEGES ON hbm_db.* TO 'hbm_user'@'%';
FLUSH PRIVILEGES;


CREATE TABLE replies (
	id VARCHAR(36) NOT NULL, 
	space_id VARCHAR(36) NOT NULL, 
	parent_id VARCHAR(36), 
	author_id VARCHAR(36) NOT NULL, 
	content TEXT NOT NULL, 
	floor_num INTEGER NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_space_floor UNIQUE (space_id, floor_num)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_parent ON replies (parent_id);

CREATE INDEX idx_space ON replies (space_id);


CREATE TABLE server_configs (
	id INTEGER NOT NULL, 
	config_key VARCHAR(50) NOT NULL, 
	config_value VARCHAR(255) NOT NULL, 
	data_type ENUM('temp','stable','fixed') NOT NULL, 
	description VARCHAR(255), 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_config_key UNIQUE (config_key)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE spaces (
	id VARCHAR(36) NOT NULL, 
	type ENUM('temp','stable','fixed') NOT NULL, 
	author_id VARCHAR(36) NOT NULL, 
	title VARCHAR(100) NOT NULL, 
	content TEXT NOT NULL, 
	heat INTEGER, 
	stability INTEGER, 
	turns_left INTEGER, 
	creator_id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_type ON spaces (type);

CREATE INDEX idx_creator ON spaces (creator_id);


CREATE TABLE treasures (
	id VARCHAR(36) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	effect TEXT NOT NULL, 
	strength INTEGER NOT NULL, 
	is_replica BOOLEAN, 
	deviation INTEGER, 
	heat INTEGER, 
	owner_id VARCHAR(36) NOT NULL, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_owner ON treasures (owner_id);


CREATE TABLE users (
	id VARCHAR(36) NOT NULL, 
	username VARCHAR(32) NOT NULL, 
	password_hash VARCHAR(64) NOT NULL, 
	email VARCHAR(32), 
	phone_number VARCHAR(15), 
	status INTEGER, 
	gender VARCHAR(1), 
	birthdate DATE, 
	country VARCHAR(100), 
	city VARCHAR(100), 
	invite_code VARCHAR(16), 
	is_verified BOOLEAN, 
	last_login_at DATETIME, 
	login_ip VARCHAR(45), 
	experience INTEGER, 
	current_level INTEGER, 
	energy INTEGER, 
	max_energy INTEGER, 
	energy_recovery_at DATETIME, 
	score INTEGER, 
	game_count INTEGER, 
	avatar_url VARCHAR(255), 
	yesterday_rank INTEGER, 
	last_game_uuid VARCHAR(36), 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email), 
	UNIQUE (phone_number)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE energy_logs (
	id INTEGER NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	change_value INTEGER NOT NULL, 
	current_value INTEGER NOT NULL, 
	action_type ENUM('explore','attack','recover','use') NOT NULL, 
	related_id VARCHAR(36), 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_user ON energy_logs (user_id);

CREATE INDEX idx_created ON energy_logs (created_at);


CREATE TABLE experience_logs (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	experience_change INTEGER NOT NULL, 
	current_experience INTEGER NOT NULL, 
	source_type ENUM('achievement','game','system') NOT NULL, 
	source_id VARCHAR(36), 
	description TEXT, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
)

 ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE experience_logs ADD FOREIGN KEY (user_id) REFERENCES users(id);

CREATE INDEX idx_user ON experience_logs (user_id);

CREATE INDEX idx_source ON experience_logs (source_type, source_id);

ALTER TABLE experience_logs ADD FOREIGN KEY (user_id) REFERENCES users(id);


-- 示例数据
INSERT INTO users (id, username, password_hash, email, status, experience, energy) VALUES
('user001', 'player1', 'hash1', 'player1@test.com', 1, 100, 200),
('user002', 'player2', 'hash2', 'player2@test.com', 1, 50, 150),
('user003', 'player3', 'hash3', 'player3@test.com', 0, 0, 256);

INSERT INTO spaces (id, type, author_id, title, content, stability, creator_id) VALUES
('space001', 'temp', 'user001', '新手空间', '欢迎来到新手空间', 80, 'user001'),
('space002', 'stable', 'user002', '进阶空间', '这里是进阶玩家空间', 90, 'user002'),
('space003', 'fixed', 'user001', '高级空间', '高级玩家专属空间', 100, 'user001');

INSERT INTO replies (id, space_id, author_id, content, floor_num) VALUES
('reply001', 'space001', 'user002', '这个空间很棒', 1),
('reply002', 'space001', 'user003', '我也这么觉得', 2),
('reply003', 'space002', 'user001', '进阶内容很有帮助', 1);

INSERT INTO treasures (id, name, effect, strength, owner_id) VALUES
('card001', '火焰卡', '造成火焰伤害', 100, 'user001'),
('card002', '治疗卡', '恢复生命值', 80, 'user002'),
('card003', '防御卡', '提高防御力', 120, 'user001');

INSERT INTO energy_logs (user_id, change_amount, remaining, change_reason) VALUES
('user001', -50, 150, 'attack'),
('user002', 20, 170, 'recover'),
('user003', -100, 156, 'explore');

INSERT INTO experience_logs (user_id, change_amount, remaining, change_reason) VALUES
('user001', 20, 120, 'game'),
('user002', 10, 60, 'achievement'),
('user001', 5, 125, 'system');

INSERT INTO server_configs (config_key, config_value, data_type, description) VALUES
('space_stability_threshold', '80', 'int', '空间稳定转化线'),
('energy_recovery_rate', '10', 'int', '体力恢复时间(分钟)'),
('max_energy', '256', 'int', '最大体力值');

