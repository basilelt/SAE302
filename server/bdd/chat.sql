CREATE TABLE `utilisateurs` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `nom` VARCHAR(40) UNIQUE NOT NULL,
  `mdp` VARCHAR(60) NOT NULL,
  `statut` BOOL DEFAULT False,
  `date_creation` TIMESTAMP
);

CREATE TABLE `salons` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `nom` VARCHAR(60) NOT NULL,
  `type` VARCHAR(6) NOT NULL
);

CREATE TABLE `messages` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT,
  `salon_id` INT,
  `date_message` TIMESTAMP,
  `ip` VARCHAR(39),
  `body` TEXT(2000) COMMENT 'Contenu du message'
);

CREATE TABLE `appartenance` (
  `user_id` INT,
  `salon_id` INT,
  `test` BOOL DEFAULT False,
  PRIMARY KEY (`user_id`, `salon_id`)
);

ALTER TABLE `salons` ADD FOREIGN KEY (`id`) REFERENCES `appartenance` (`salon_id`);

ALTER TABLE `utilisateurs` ADD FOREIGN KEY (`id`) REFERENCES `appartenance` (`user_id`);

ALTER TABLE `utilisateurs` ADD FOREIGN KEY (`id`) REFERENCES `messages` (`user_id`);

ALTER TABLE `salons` ADD FOREIGN KEY (`id`) REFERENCES `messages` (`salon_id`);
