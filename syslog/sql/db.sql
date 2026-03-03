DROP DATABASE IF EXISTS `Logs_fw`;
CREATE DATABASE IF NOT EXISTS `Logs_fw` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `Logs_fw`;

CREATE TABLE IF NOT EXISTS `FW` (
  `datetime` datetime NOT NULL,
  `ipsrc` text NOT NULL,
  `ipdst` text NOT NULL,
  `dstport` text NOT NULL,
  `proto` text NOT NULL,
  `action` text NOT NULL,
  `policyid` text NOT NULL,
  `interface_in` text NOT NULL,
  `interface_out` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
