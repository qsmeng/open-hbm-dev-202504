-- 服务器配置表
CREATE TABLE server_configs (
  id INT AUTO_INCREMENT PRIMARY KEY COMMENT '配置ID',
  config_key VARCHAR(50) NOT NULL COMMENT '配置键名',
  config_value VARCHAR(255) NOT NULL COMMENT '配置值',
  data_type ENUM('int','string','bool') NOT NULL COMMENT '数据类型',
  description VARCHAR(255) COMMENT '配置说明',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='服务器配置表';

-- 空间表
CREATE TABLE spaces (
  id VARCHAR(36) PRIMARY KEY COMMENT '空间ID',
  type ENUM('temp','stable','fixed') NOT NULL COMMENT '空间类型:临时/稳定/固化',
  author_id VARCHAR(36) NOT NULL COMMENT '作者ID',
  title VARCHAR(100) NOT NULL COMMENT '标题',
  content TEXT NOT NULL COMMENT '内容',
  heat INT DEFAULT 0 COMMENT '热度值',
  stability INT DEFAULT 100 COMMENT '稳定度(0-100)',
  turns_left INT DEFAULT 10 COMMENT '剩余轮次',
  creator_id VARCHAR(36) NOT NULL COMMENT '创建者ID',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_creator (creator_id),
  INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='空间表';

-- 回复表
CREATE TABLE replies (
  id VARCHAR(36) PRIMARY KEY COMMENT '回复ID',
  space_id VARCHAR(36) NOT NULL COMMENT '所属空间ID',
  parent_id VARCHAR(36) COMMENT '父回复ID',
  author_id VARCHAR(36) NOT NULL COMMENT '作者ID',
  content TEXT NOT NULL COMMENT '内容',
  floor_num INT NOT NULL COMMENT '楼层号',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_space (space_id),
  INDEX idx_parent (parent_id),
  UNIQUE INDEX idx_space_floor (space_id, floor_num)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回复表';

-- 卡牌表
CREATE TABLE treasures (
  id VARCHAR(36) PRIMARY KEY COMMENT '卡牌ID',
  name VARCHAR(100) NOT NULL COMMENT '名称',
  effect TEXT NOT NULL COMMENT '效果描述',
  strength INT NOT NULL COMMENT '强度值(0-256)',
  is_replica BOOLEAN DEFAULT FALSE COMMENT '是否为复制品',
  deviation INT DEFAULT 0 COMMENT '故事线偏离度减值',
  heat INT DEFAULT 0 COMMENT '热度加值',
  owner_id VARCHAR(36) NOT NULL COMMENT '拥有者ID',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_owner (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='卡牌表';

-- 体力变动日志表
CREATE TABLE energy_logs (
  id INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
  user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
  change_value INT NOT NULL COMMENT '变动值',
  current_value INT NOT NULL COMMENT '变动后值',
  action_type ENUM('explore','attack','recover','use') NOT NULL COMMENT '动作类型',
  related_id VARCHAR(36) COMMENT '关联ID',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_user (user_id),
  INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='体力变动日志表';

-- 用户表
CREATE TABLE users (
  id VARCHAR(36) PRIMARY KEY COMMENT '用户ID',
  username VARCHAR(32) NOT NULL COMMENT '用户名(登录用)',
  password_hash VARCHAR(64) NOT NULL COMMENT '密码哈希',
  email VARCHAR(32) UNIQUE COMMENT '电子邮箱(登录用)',
  phone_number VARCHAR(15) UNIQUE COMMENT '电话号码(登录用)',
  status TINYINT NOT NULL DEFAULT 0 COMMENT '状态: 1-激活, 0-未激活',
  gender ENUM('m','f','o') DEFAULT 'o' COMMENT '性别: m=男, f=女, o=其他',
  birthdate DATE COMMENT '出生日期',
  country VARCHAR(100) COMMENT '国家',
  city VARCHAR(100) COMMENT '城市',
  invite_code VARCHAR(16) COMMENT '邀请码(16位)',
  is_verified TINYINT(1) DEFAULT 0 COMMENT '是否实名验证',
  last_login_at TIMESTAMP COMMENT '最后登录时间',
  login_ip VARCHAR(45) COMMENT '最后登录IP',
  experience INT DEFAULT 0 COMMENT '总资历值',
  current_level INT DEFAULT 1 COMMENT '当前等级',
  energy INT DEFAULT 256 COMMENT '当前体力值',
  max_energy INT DEFAULT 256 COMMENT '最大体力值',
  energy_recovery_at TIMESTAMP COMMENT '体力恢复时间',
  score INT DEFAULT 0 COMMENT '游戏分数',
  game_count INT DEFAULT 0 COMMENT '游戏局数',
  avatar_url VARCHAR(255) COMMENT '头像URL',
  yesterday_rank INT COMMENT '昨日排名',
  last_game_uuid VARCHAR(36) COMMENT '最近游戏UUID',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE INDEX idx_username (username),
  UNIQUE INDEX idx_email (email),
  UNIQUE INDEX idx_phone (phone_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

-- 资历日志表
CREATE TABLE experience_logs (
  id VARCHAR(36) PRIMARY KEY COMMENT '日志ID',
  user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
  experience_change INT NOT NULL COMMENT '资历变动值',
  current_experience INT NOT NULL COMMENT '变动后资历值',
  source_type ENUM('achievement','game','system') NOT NULL COMMENT '来源类型',
  source_id VARCHAR(36) COMMENT '来源ID',
  description TEXT COMMENT '描述',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_user (user_id),
  INDEX idx_source (source_type, source_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资历变动日志表';

-- 初始化配置数据
INSERT INTO server_configs (config_key, config_value, data_type, description) VALUES
('space_stability_threshold', '80', 'int', '空间稳定转化线'),
('energy_recovery_rate', '10', 'int', '体力恢复时间(分钟)'),
('max_energy', '256', 'int', '最大体力值');

-- 用户测试数据
INSERT INTO users (id, username, password_hash, email, status, experience, energy) VALUES
('user001', 'player1', 'hash1', 'player1@test.com', 1, 100, 200),
('user002', 'player2', 'hash2', 'player2@test.com', 1, 50, 150),
('user003', 'player3', 'hash3', 'player3@test.com', 0, 0, 256);

-- 空间测试数据
INSERT INTO spaces (id, type, author_id, title, content, stability, creator_id) VALUES
('space001', 'temp', 'user001', '新手空间', '欢迎来到新手空间', 80, 'user001'),
('space002', 'stable', 'user002', '进阶空间', '这里是进阶玩家空间', 90, 'user002'),
('space003', 'fixed', 'user001', '高级空间', '高级玩家专属空间', 100, 'user001');

-- 回复测试数据
INSERT INTO replies (id, space_id, author_id, content, floor_num) VALUES
('reply001', 'space001', 'user002', '这个空间很棒', 1),
('reply002', 'space001', 'user003', '我也这么觉得', 2),
('reply003', 'space002', 'user001', '进阶内容很有帮助', 1);

-- 卡牌测试数据
INSERT INTO treasures (id, name, effect, strength, owner_id) VALUES
('card001', '火焰卡', '造成火焰伤害', 100, 'user001'),
('card002', '治疗卡', '恢复生命值', 80, 'user002'),
('card003', '防御卡', '提高防御力', 120, 'user001');

-- 体力变动日志测试数据
INSERT INTO energy_logs (user_id, change_value, current_value, action_type) VALUES
('user001', -50, 150, 'attack'),
('user002', 20, 170, 'recover'),
('user003', -100, 156, 'explore');

-- 资历日志测试数据
INSERT INTO experience_logs (id, user_id, experience_change, current_experience, source_type) VALUES
('exp001', 'user001', 20, 120, 'game'),
('exp002', 'user002', 10, 60, 'achievement'),
('exp003', 'user001', 5, 125, 'system');