-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: site
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb3_bin NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `edition`
--

DROP TABLE IF EXISTS `edition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `edition` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creation_date` datetime NOT NULL,
  `name` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `event_id` int NOT NULL,
  `edition_date` datetime NOT NULL,
  `first_inscription` datetime NOT NULL,
  `last_inscription` datetime NOT NULL,
  `rdv_lat` float NOT NULL,
  `rdv_lng` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `event_id` (`event_id`),
  CONSTRAINT `edition_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `event` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `editions_parcours`
--

DROP TABLE IF EXISTS `editions_parcours`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `editions_parcours` (
  `edition_id` int DEFAULT NULL,
  `parcours_id` int DEFAULT NULL,
  KEY `edition_id` (`edition_id`),
  KEY `parcours_id` (`parcours_id`),
  CONSTRAINT `editions_parcours_ibfk_1` FOREIGN KEY (`edition_id`) REFERENCES `edition` (`id`),
  CONSTRAINT `editions_parcours_ibfk_2` FOREIGN KEY (`parcours_id`) REFERENCES `parcours` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creation_date` datetime NOT NULL,
  `name` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `createur_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `createur_id_user_id` (`createur_id`),
  CONSTRAINT `createur_id_user_id` FOREIGN KEY (`createur_id`) REFERENCES `user` (`id`),
  CONSTRAINT `event_ibfk_1` FOREIGN KEY (`createur_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inscription`
--

DROP TABLE IF EXISTS `inscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inscription` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creation_date` datetime NOT NULL,
  `user_id` int NOT NULL,
  `event_id` int NOT NULL,
  `edition_id` int NOT NULL,
  `parcours_id` int NOT NULL,
  `dossard` int DEFAULT NULL,
  `present` tinyint(1) NOT NULL,
  `end` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `event_id` (`event_id`),
  KEY `parcours_id_parcours_id` (`parcours_id`),
  KEY `edition_id_edition_id` (`edition_id`),
  KEY `user_id_user_id` (`user_id`),
  CONSTRAINT `edition_id_edition_id` FOREIGN KEY (`edition_id`) REFERENCES `edition` (`id`),
  CONSTRAINT `inscription_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `inscription_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `event` (`id`),
  CONSTRAINT `inscription_ibfk_3` FOREIGN KEY (`edition_id`) REFERENCES `edition` (`id`),
  CONSTRAINT `inscription_ibfk_4` FOREIGN KEY (`parcours_id`) REFERENCES `parcours` (`id`),
  CONSTRAINT `parcours_id_parcours_id` FOREIGN KEY (`parcours_id`) REFERENCES `parcours` (`id`),
  CONSTRAINT `user_id_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `parcours`
--

DROP TABLE IF EXISTS `parcours`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parcours` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creation_date` datetime NOT NULL,
  `name` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `event_id` int NOT NULL,
  `description` text NOT NULL,
  `archived` tinyint(1) NOT NULL,
  `chronos_list` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `event_id_event_id` (`event_id`),
  CONSTRAINT `event_id_event_id` FOREIGN KEY (`event_id`) REFERENCES `event` (`id`),
  CONSTRAINT `parcours_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `event` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `passage`
--

DROP TABLE IF EXISTS `passage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `passage` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time_stamp` datetime NOT NULL,
  `key_id` int DEFAULT NULL,
  `inscription_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `key_id_passage_key_id` (`key_id`),
  KEY `inscription_id_inscription_id` (`inscription_id`),
  CONSTRAINT `inscription_id_inscription_id` FOREIGN KEY (`inscription_id`) REFERENCES `inscription` (`id`),
  CONSTRAINT `key_id_passage_key_id` FOREIGN KEY (`key_id`) REFERENCES `passage_key` (`id`),
  CONSTRAINT `passage_ibfk_1` FOREIGN KEY (`key_id`) REFERENCES `passage_key` (`id`),
  CONSTRAINT `passage_ibfk_2` FOREIGN KEY (`inscription_id`) REFERENCES `inscription` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `passage_key`
--

DROP TABLE IF EXISTS `passage_key`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `passage_key` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creation_date` datetime NOT NULL,
  `event_id` int NOT NULL,
  `edition_id` int NOT NULL,
  `key` varchar(20) NOT NULL,
  `name` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`),
  KEY `event_id` (`event_id`),
  KEY `edition_id` (`edition_id`),
  CONSTRAINT `passage_key_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `event` (`id`),
  CONSTRAINT `passage_key_ibfk_2` FOREIGN KEY (`edition_id`) REFERENCES `edition` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `passagekey_stand`
--

DROP TABLE IF EXISTS `passagekey_stand`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `passagekey_stand` (
  `passage_key_id` int DEFAULT NULL,
  `stand_id` int DEFAULT NULL,
  KEY `stand_id_stand_id` (`stand_id`),
  KEY `passage_key_id_passage_key_id` (`passage_key_id`),
  CONSTRAINT `passage_key_id_passage_key_id` FOREIGN KEY (`passage_key_id`) REFERENCES `passage_key` (`id`),
  CONSTRAINT `passagekey_stand_ibfk_1` FOREIGN KEY (`passage_key_id`) REFERENCES `passage_key` (`id`),
  CONSTRAINT `passagekey_stand_ibfk_2` FOREIGN KEY (`stand_id`) REFERENCES `stand` (`id`),
  CONSTRAINT `stand_id_stand_id` FOREIGN KEY (`stand_id`) REFERENCES `stand` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stand`
--

DROP TABLE IF EXISTS `stand`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stand` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `lat` float NOT NULL,
  `lng` float NOT NULL,
  `elevation` float DEFAULT NULL,
  `parcours_id` int DEFAULT NULL,
  `start_stand` int DEFAULT NULL,
  `end_stand` int DEFAULT NULL,
  `color` varchar(20) NOT NULL,
  `chrono` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `parcours_id` (`parcours_id`),
  KEY `end_stand_parcours_id` (`end_stand`),
  KEY `start_stand_parcours_id` (`start_stand`),
  CONSTRAINT `end_stand_parcours_id` FOREIGN KEY (`end_stand`) REFERENCES `parcours` (`id`),
  CONSTRAINT `stand_ibfk_1` FOREIGN KEY (`parcours_id`) REFERENCES `parcours` (`id`),
  CONSTRAINT `stand_ibfk_2` FOREIGN KEY (`start_stand`) REFERENCES `parcours` (`id`),
  CONSTRAINT `stand_ibfk_3` FOREIGN KEY (`end_stand`) REFERENCES `parcours` (`id`),
  CONSTRAINT `start_stand_parcours_id` FOREIGN KEY (`start_stand`) REFERENCES `parcours` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trace`
--

DROP TABLE IF EXISTS `trace`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trace` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `parcours_id` int DEFAULT NULL,
  `start_id` int NOT NULL,
  `end_id` int NOT NULL,
  `trace` text NOT NULL,
  `turn_nb` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `parcours_id` (`parcours_id`),
  KEY `end_id_stand_id` (`end_id`),
  KEY `start_id_stand_id` (`start_id`),
  CONSTRAINT `end_id_stand_id` FOREIGN KEY (`end_id`) REFERENCES `stand` (`id`),
  CONSTRAINT `start_id_stand_id` FOREIGN KEY (`start_id`) REFERENCES `stand` (`id`),
  CONSTRAINT `trace_ibfk_1` FOREIGN KEY (`parcours_id`) REFERENCES `parcours` (`id`),
  CONSTRAINT `trace_ibfk_2` FOREIGN KEY (`start_id`) REFERENCES `stand` (`id`),
  CONSTRAINT `trace_ibfk_3` FOREIGN KEY (`end_id`) REFERENCES `stand` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creation_date` datetime NOT NULL,
  `avatar` varchar(80) NOT NULL,
  `name` varchar(40) NOT NULL,
  `lastname` varchar(20) NOT NULL,
  `password` varchar(80) NOT NULL,
  `username` varchar(20) NOT NULL,
  `email` varchar(80) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `datenaiss` datetime NOT NULL,
  `admin` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-02 15:23:18
