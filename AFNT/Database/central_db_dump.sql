CREATE DATABASE  IF NOT EXISTS `centraldb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `centraldb`;
-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    Database: centraldb
-- ------------------------------------------------------
-- Server version	8.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `advices`
--

DROP TABLE IF EXISTS `advices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `advices` (
  `advice_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `type_of_advice` enum('Health','Fitness','Nutrition') NOT NULL,
  `description` text,
  `solution` text,
  `reference_link` varchar(255) DEFAULT NULL,
  `image_link` varchar(255) DEFAULT NULL,
  `date_added` date DEFAULT NULL,
  `time_added` time DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`advice_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `advices`
--

LOCK TABLES `advices` WRITE;
/*!40000 ALTER TABLE `advices` DISABLE KEYS */;
/*!40000 ALTER TABLE `advices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exercise_logs`
--

DROP TABLE IF EXISTS `exercise_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exercise_logs` (
  `exercise_log_id` int NOT NULL AUTO_INCREMENT,
  `exercise_id` int NOT NULL,
  `workout_log_id` int NOT NULL,
  `sets` int DEFAULT NULL,
  `reps` int DEFAULT NULL,
  `weight_kg` double DEFAULT NULL,
  `rest_per_set_s` int DEFAULT NULL,
  `duration` time DEFAULT NULL,
  `distance_m` int DEFAULT NULL,
  `rpe` int DEFAULT NULL,
  `is_complete` tinyint(1) NOT NULL,
  `date_complete` date DEFAULT NULL,
  `time_complete` time DEFAULT NULL,
  `details` varchar(300) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`exercise_log_id`),
  UNIQUE KEY `exercise_log_id` (`exercise_log_id`),
  KEY `exercise_id` (`exercise_id`),
  KEY `workout_log_id` (`workout_log_id`),
  CONSTRAINT `exercise_logs_ibfk_1` FOREIGN KEY (`exercise_id`) REFERENCES `exercises` (`exercise_id`),
  CONSTRAINT `exercise_logs_ibfk_2` FOREIGN KEY (`workout_log_id`) REFERENCES `workout_logs` (`workout_log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exercise_logs`
--

LOCK TABLES `exercise_logs` WRITE;
/*!40000 ALTER TABLE `exercise_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `exercise_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exercises`
--

DROP TABLE IF EXISTS `exercises`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exercises` (
  `exercise_id` int NOT NULL AUTO_INCREMENT,
  `exercise_name` varchar(150) NOT NULL,
  `description` varchar(300) DEFAULT NULL,
  `type` enum('Strength','Cardio','Olympic Weightlifting','Plyometrics','Powerlifting','Stretching','Strongman') NOT NULL,
  `body_part` enum('Abdominals','Adductors','Chest','Hamstrings','Quadriceps','Lats','Shoulders','Triceps') NOT NULL,
  `equiptment` enum('Body Only','Dumbbell','Exercise Ball','Kettlebells','Medicine Bell','None','Other') NOT NULL,
  `level` enum('Beginner','Intermediate','Advanced') NOT NULL,
  `rating` double DEFAULT NULL,
  `rating_description` varchar(45) DEFAULT NULL,
  `is_active` tinyint NOT NULL,
  PRIMARY KEY (`exercise_id`),
  UNIQUE KEY `exercise_id_UNIQUE` (`exercise_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exercises`
--

LOCK TABLES `exercises` WRITE;
/*!40000 ALTER TABLE `exercises` DISABLE KEYS */;
/*!40000 ALTER TABLE `exercises` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `food_item_logs`
--

DROP TABLE IF EXISTS `food_item_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `food_item_logs` (
  `food_item_log_id` int NOT NULL AUTO_INCREMENT,
  `meal_log_id` int NOT NULL,
  `food_item_id` int NOT NULL,
  `serving` double NOT NULL,
  `weight_g` double DEFAULT NULL,
  `ate` tinyint(1) NOT NULL,
  `date_ate` date DEFAULT NULL,
  `time_ate` time DEFAULT NULL,
  `description` varchar(300) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`food_item_log_id`),
  UNIQUE KEY `food_item_log_id` (`food_item_log_id`),
  KEY `meal_log_id` (`meal_log_id`),
  KEY `food_item_id` (`food_item_id`),
  CONSTRAINT `food_item_logs_ibfk_1` FOREIGN KEY (`meal_log_id`) REFERENCES `meal_logs` (`meal_log_id`),
  CONSTRAINT `food_item_logs_ibfk_2` FOREIGN KEY (`food_item_id`) REFERENCES `food_items` (`food_item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `food_item_logs`
--

LOCK TABLES `food_item_logs` WRITE;
/*!40000 ALTER TABLE `food_item_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `food_item_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `food_items`
--

DROP TABLE IF EXISTS `food_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `food_items` (
  `food_item_id` int NOT NULL,
  `food_item_name` varchar(255) NOT NULL,
  `water_g` decimal(5,2) DEFAULT NULL,
  `energy_kcal` int NOT NULL,
  `protein_g` decimal(5,2) DEFAULT NULL,
  `lipid_g` decimal(5,2) DEFAULT NULL,
  `carbs_g` decimal(5,2) DEFAULT NULL,
  `fiber_td_g` decimal(5,2) DEFAULT NULL,
  `sugar_g` decimal(5,2) DEFAULT NULL,
  `calcium_mg` decimal(5,2) DEFAULT NULL,
  `iron_mg` decimal(5,2) DEFAULT NULL,
  `cholestrl_mg` decimal(5,2) DEFAULT NULL,
  `gmwt_1` decimal(5,2) DEFAULT NULL,
  `gmwt_desc1` varchar(255) DEFAULT NULL,
  `gmwt_2` decimal(5,2) DEFAULT NULL,
  `gmwt_desc2` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`food_item_id`),
  UNIQUE KEY `food_item_id` (`food_item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `food_items`
--

LOCK TABLES `food_items` WRITE;
/*!40000 ALTER TABLE `food_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `food_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meal_logs`
--

DROP TABLE IF EXISTS `meal_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meal_logs` (
  `meal_log_id` int NOT NULL AUTO_INCREMENT,
  `meal_id` int NOT NULL,
  `ate` tinyint(1) NOT NULL,
  `date_ate` date NOT NULL,
  `time_ate` time NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`meal_log_id`),
  UNIQUE KEY `meal_log_id` (`meal_log_id`),
  KEY `meal_id` (`meal_id`),
  CONSTRAINT `meal_logs_ibfk_1` FOREIGN KEY (`meal_id`) REFERENCES `meals` (`meal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meal_logs`
--

LOCK TABLES `meal_logs` WRITE;
/*!40000 ALTER TABLE `meal_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `meal_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meals`
--

DROP TABLE IF EXISTS `meals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meals` (
  `meal_id` int NOT NULL AUTO_INCREMENT,
  `type` enum('Breakfast','Morning Snack','Lunch','Afternoon Snack','Brunch','Dinner','Evening Snack') NOT NULL,
  `description` varchar(300) DEFAULT NULL,
  `water_tot_g` int DEFAULT NULL,
  `energy_tot_kcal` int DEFAULT NULL,
  `protein_tot_g` double DEFAULT NULL,
  `lipid_tot_g` double DEFAULT NULL,
  `carbs_tot_g` double DEFAULT NULL,
  `fiber_tot_g` double DEFAULT NULL,
  `sugar_tot_g` double DEFAULT NULL,
  `calcium_tot_mg` double DEFAULT NULL,
  `iron_tot_mg` double DEFAULT NULL,
  `cholestrl_tot_mg` double DEFAULT NULL,
  `serving` double NOT NULL,
  `date_created` date NOT NULL,
  `time_created` time NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`meal_id`),
  UNIQUE KEY `meal_id` (`meal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meals`
--

LOCK TABLES `meals` WRITE;
/*!40000 ALTER TABLE `meals` DISABLE KEYS */;
/*!40000 ALTER TABLE `meals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `type` enum('Admin','User') NOT NULL,
  `email` varchar(150) NOT NULL,
  `country_code` int DEFAULT NULL,
  `phone` varchar(20) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `postcode_zipcode` varchar(20) DEFAULT NULL,
  `gender` enum('Male','Female') NOT NULL,
  `dob` date NOT NULL,
  `date_enrolled` date NOT NULL,
  `time_enrolled` time NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `workout_logs`
--

DROP TABLE IF EXISTS `workout_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workout_logs` (
  `workout_log_id` int NOT NULL AUTO_INCREMENT,
  `workout_id` int NOT NULL,
  `date_assigned` date NOT NULL,
  `time_assigned` time NOT NULL,
  `is_complete` tinyint(1) NOT NULL,
  `date_completed` date DEFAULT NULL,
  `time_completed` time DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`workout_log_id`),
  KEY `workout_id` (`workout_id`),
  CONSTRAINT `workout_logs_ibfk_1` FOREIGN KEY (`workout_id`) REFERENCES `workouts` (`workout_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `workout_logs`
--

LOCK TABLES `workout_logs` WRITE;
/*!40000 ALTER TABLE `workout_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `workout_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `workouts`
--

DROP TABLE IF EXISTS `workouts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workouts` (
  `workout_id` int NOT NULL,
  `workout_name` varchar(150) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `type` enum('Abdominals','Adductors','Chest','Hamstrings','Quadriceps','Lats','Shoulders','Triceps') NOT NULL,
  `date_created` date NOT NULL,
  `level` enum('Beginner','Intermediate','Advanced') NOT NULL,
  `rating` int DEFAULT NULL,
  `rating_description` varchar(100) DEFAULT NULL,
  `time_created` time NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`workout_id`),
  UNIQUE KEY `workout_id` (`workout_id`),
  UNIQUE KEY `workout_name` (`workout_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `workouts`
--

LOCK TABLES `workouts` WRITE;
/*!40000 ALTER TABLE `workouts` DISABLE KEYS */;
/*!40000 ALTER TABLE `workouts` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-05-07  1:27:15
