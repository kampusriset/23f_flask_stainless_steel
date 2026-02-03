-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               8.0.30 - MySQL Community Server - GPL
-- Server OS:                    Win64
-- HeidiSQL Version:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for bimantara_db
CREATE DATABASE IF NOT EXISTS `bimantara_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `bimantara_db`;

-- Dumping structure for table bimantara_db.orders
CREATE TABLE IF NOT EXISTS `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `kd_order` varchar(255) NOT NULL,
  `product_name` varchar(255) NOT NULL,
  `quantity` int NOT NULL,
  `customer_name` varchar(255) NOT NULL,
  `address` text NOT NULL,
  `contact` varchar(255) NOT NULL,
  `user_id` int DEFAULT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `total_price` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table bimantara_db.orders: ~12 rows (approximately)
INSERT INTO `orders` (`id`, `kd_order`, `product_name`, `quantity`, `customer_name`, `address`, `contact`, `user_id`, `status`, `total_price`, `created_at`) VALUES
	(20, '43690', 'Dandang 10kg', 1, 'Fandy Dwi Putra', 'Jl. Kenanga Raya Blok B No. 8, Kel. Harapan Jaya, Kec. Sentosa, Kota Mandiri, Jawa Barat 40123', '12345678', 4, 'cancelled', 500000.00, '2026-02-03 03:37:01'),
	(21, '98634', 'Dandang 8kg', 1, 'Fandy Dwi Putra', 'Jl. Kenanga Raya Blok B No. 8, Kel. Harapan Jaya, Kec. Sentosa, Kota Mandiri, Jawa Barat 40123', '12345678', 4, 'pending', 300000.00, '2026-02-03 03:38:34'),
	(22, '32533', 'Dandang 10kg (x1), Dandang 6kg (x1), Dandang 8kg (x1)', 3, 'Fandy Dwi Putra', 'Jl. Kenanga Raya Blok B No. 8, Kel. Harapan Jaya, Kec. Sentosa, Kota Mandiri, Jawa Barat 40123', '12345678', 4, 'completed', 1000000.00, '2026-02-03 03:38:58');

-- Dumping structure for table bimantara_db.products
CREATE TABLE IF NOT EXISTS `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table bimantara_db.products: ~3 rows (approximately)
INSERT INTO `products` (`id`, `name`, `slug`, `price`) VALUES
	(1, 'Dandang 6kg', 'dandang-6kg', 200000.00),
	(2, 'Dandang 8kg', 'dandang-8kg', 300000.00),
	(3, 'Dandang 10kg', 'dandang-10kg', 500000.00);

-- Dumping structure for table bimantara_db.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `address` text NOT NULL,
  `role` enum('admin','pembeli') DEFAULT 'pembeli',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Dumping data for table bimantara_db.users: ~4 rows (approximately)
INSERT INTO `users` (`id`, `name`, `email`, `password`, `phone`, `address`, `role`, `created_at`) VALUES
	(1, 'Administrator', 'admin@bimantara.com', '$2b$12$qyJerSazY3AWsllu4A71auLpfxa.Gh1HepWQUhXvw0uCHMo0jBy1W', '081234567890', 'Jl. Industri No. 123, Jakarta', 'admin', '2026-01-14 09:47:22'),
	(2, 'ilyas', 'yasa@gmail.com', '$2b$12$GQRtvJ6jbyOTw9ccMJhJaupqUb06R8e1iix6yhdZdNHXHQRftXaSC', '12345678', 'Jl. Melati Indah No. 123, RT 04/RW 07, Kel. Sukamaju, Kec. Cendana, Kota Nusantara, Jawa Tengah 54321', 'pembeli', '2026-01-14 10:06:38'),
	(3, 'maw', 'maw@gmail.com', '$2b$12$zo00eV2R571zZkwPqn1sMeqeqNzw0Qjhd5rl33CjAeFZMIPC5IBL.', '12345678', 'Perumahan Taman Anggrek Asri, Jl. Flamboyan No. 5, Kel. Mekar Sari, Kec. Sejahtera, Kota Pusaka, DI Yogyakarta 55234', 'pembeli', '2026-01-14 10:07:07'),
	(4, 'Fandy Dwi Putra', 'fann@gmail.com', '$2b$12$DSZtC4pvNcwSai9.WOSjBezBdtGLThJf4dTg2Sdp.K8pbwPzqtI6.', '12345678', 'Jl. Kenanga Raya Blok B No. 8, Kel. Harapan Jaya, Kec. Sentosa, Kota Mandiri, Jawa Barat 40123', 'pembeli', '2026-01-14 10:09:09');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
