-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: site
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
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stand`
--

/*!40000 ALTER TABLE `stand` DISABLE KEYS */;
INSERT INTO `stand` VALUES (1,'start',46.5454,6.44768,534,1,1,NULL,'#ff0000',1),(2,'vignes',46.5454,6.44651,534,1,NULL,NULL,'#ff0000',0),(3,'reverolle',46.5407,6.44405,544,1,NULL,NULL,'#ff0000',0),(4,'end',46.5402,6.44487,544,1,NULL,1,'#ff0000',1),(5,'debut',46.5454,6.44768,534,2,2,NULL,'#ff0000',1),(6,'debut-Q - édition 2023',46.4212,6.26346,427,6,6,NULL,'#00ff28',1),(7,'Nyon',46.3839,6.23979,399,6,NULL,NULL,'#ff0000',1),(8,'rew',46.3835,6.23937,405,6,NULL,6,'#ff0000',1),(33,'start',46.5455,6.4477,534,15,15,NULL,'#ff0000',0),(34,'route chaniaz',46.5402,6.44483,544,15,NULL,NULL,'#ff0000',1),(35,'chaniaz cours',46.5374,6.44304,535,15,NULL,NULL,'#ff0000',1),(36,'reverolle',46.5449,6.44478,567,15,NULL,15,'#ff0000',0),(57,'57',46.5467,6.44979,532,20,20,NULL,'#ff0000',1),(58,'58',46.5455,6.44834,520,20,NULL,NULL,'#ff0000',0),(59,'59',46.5467,6.44852,532,20,NULL,20,'#ff0000',1),(63,'63',46.5459,6.44799,552,20,NULL,NULL,'#ff0000',1);
/*!40000 ALTER TABLE `stand` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-25 11:29:05
