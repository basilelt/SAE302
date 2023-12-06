CREATE DATABASE IF NOT EXISTS `chat` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER IF NOT EXISTS 'chat'@'%' IDENTIFIED BY 'chat';
GRANT ALL PRIVILEGES ON `chat`.* TO 'chat'@'%';

USE `chat`;

CREATE TABLE `users` (
  `name` VARCHAR(40) UNIQUE PRIMARY KEY NOT NULL,
  `password` VARCHAR(60) NOT NULL,
  `pending_room` VARCHAR(2000),
  `state` VARCHAR(5) NOT NULL DEFAULT "valid",
  `reason` VARCHAR(2000),
  `timeout` TIMESTAMP,
  `date_creation` TIMESTAMP NOT NULL
);

CREATE TABLE `rooms` (
  `name` VARCHAR(60) PRIMARY KEY NOT NULL,
  `type` VARCHAR(6) NOT NULL
);

CREATE TABLE `messages` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user` VARCHAR(40),
  `room` VARCHAR(60),
  `date_message` TIMESTAMP,
  `ip` VARCHAR(39),
  `body` TEXT(2000) COMMENT 'Contentenu du message',
  FOREIGN KEY (`user`) REFERENCES `users` (`name`),
  FOREIGN KEY (`room`) REFERENCES `rooms` (`name`)
);

CREATE TABLE `belong` (
  `user` VARCHAR(40),
  `room` VARCHAR(60),
  `test` BOOL DEFAULT False,
  PRIMARY KEY (`user`, `room`),
  FOREIGN KEY (`user`) REFERENCES `users` (`name`),
  FOREIGN KEY (`room`) REFERENCES `rooms` (`name`)
);
