CREATE DATABASE IF NOT EXISTS toilet_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE toilet_tracker;

CREATE TABLE admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE problems (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  room_id VARCHAR(255) NOT NULL,
  category VARCHAR(100),
  user_name VARCHAR(255),
  user_status VARCHAR(100),
  user_phone VARCHAR(50),
  user_email VARCHAR(255),
  problem_desc TEXT,
  img_path VARCHAR(512),
  status ENUM('pending','in-progress','completed','pending_sync','online') DEFAULT 'pending',
  reporter_token VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
