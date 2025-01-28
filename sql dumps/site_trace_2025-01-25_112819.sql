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
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trace`
--

/*!40000 ALTER TABLE `trace` DISABLE KEYS */;
INSERT INTO `trace` VALUES (1,'1',1,1,2,'[]',1),(2,'2',1,2,3,'[]',1),(3,'3',1,3,4,'[]',1),(4,'4',1,4,1,'[[46.54115202742685, 6.446485519409181, 516.0], [46.54353560265215, 6.447497313406165, 523.0]]',1),(5,'5',1,1,4,'[]',2),(6,'debut-Q - édition 2023 - Nyon ',6,6,7,'[[46.420996697253344, 6.262936592102052, 427.0], [46.42051225924294, 6.263532042503357, 422.0], [46.418910994582326, 6.260734498500825, 425.0]]',1),(7,'Nyon - rew ',6,7,8,'[]',1),(33,'debut-W - route chaniaz ',15,33,34,'[[46.54342860229261, 6.445874760813803, 523.0]]',1),(34,'route chaniaz - chaniaz cours ',15,34,35,'[[46.540432506603416, 6.445435747582394, 544.0]]',1),(35,'chaniaz cours - reverolle ',15,35,36,'[]',1),(52,'52',20,57,58,'[[46.54643929051163, 6.449612975120545, 532.0], [46.54532506016766, 6.449897289276124, 520.0]]',1),(59,'59',20,57,63,'[]',2),(60,'60',20,63,59,'[]',2),(62,'62',20,58,57,'[]',1);
/*!40000 ALTER TABLE `trace` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-25 11:28:25
