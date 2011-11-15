SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- 数据库: `fanfou_ontime`
--

-- --------------------------------------------------------

--
-- 表的结构 `logs`
--

CREATE TABLE IF NOT EXISTS `logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(20) NOT NULL,
  `status` varchar(140) NOT NULL,
  `token` binary(16) NOT NULL,
  `plan_time` datetime NOT NULL,
  `exec_time` datetime NOT NULL,
  `result` enum('success','accepted','timeout','unauthorized','other') NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`,`token`,`result`,`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 ;

-- --------------------------------------------------------

--
-- 表的结构 `plans`
--

CREATE TABLE IF NOT EXISTS `plans` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(20) NOT NULL,
  `status` varchar(140) NOT NULL,
  `time` datetime NOT NULL,
  `timeoffset` smallint(6) NOT NULL,
  `period` mediumint(9) unsigned NOT NULL DEFAULT '0',
  `priority` tinyint(4) NOT NULL DEFAULT '0',
  `timeout` smallint(5) unsigned NOT NULL DEFAULT '10',
  `in_queue` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`,`time`,`priority`),
  KEY `time` (`in_queue`,`time`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 ;

-- --------------------------------------------------------

--
-- 表的结构 `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `user_id` varchar(20) NOT NULL,
  `token` varchar(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `secret` varchar(40) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  `limit` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
