/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50719
Source Host           : localhost:3306
Source Database       : movie

Target Server Type    : MYSQL
Target Server Version : 50719
File Encoding         : 65001

Date: 2018-03-23 16:20:48
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for pro_actor
-- ----------------------------
DROP TABLE IF EXISTS `pro_actor`;
CREATE TABLE `pro_actor` (
  `id` char(37) NOT NULL COMMENT '演员id',
  `actor_name` varchar(200) DEFAULT NULL COMMENT '演员姓名',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='演员表';

-- ----------------------------
-- Table structure for pro_movie
-- ----------------------------
DROP TABLE IF EXISTS `pro_movie`;
CREATE TABLE `pro_movie` (
  `id` char(37) NOT NULL COMMENT '电影id',
  `movie_name` varchar(200) DEFAULT NULL COMMENT '电影名称',
  `movie_descr` varchar(1000) DEFAULT NULL COMMENT '电影简介',
  `movie_img_url` varchar(1000) DEFAULT NULL COMMENT '电影背景url',
  `movie_year` varchar(200) DEFAULT NULL COMMENT '电影年份',
  `movie_real_name` varchar(200) DEFAULT NULL COMMENT '电影真实名称',
  `create_time` bigint(20) DEFAULT NULL COMMENT '创建时间',
  `enable` char(1) DEFAULT 'Y' COMMENT '是否启用',
  `source` varchar(200) DEFAULT NULL COMMENT '来源',
  `source_page_url` varchar(200) DEFAULT NULL COMMENT '来源页面',
  `update_date` bigint(20) DEFAULT NULL,
  `score` char(50) DEFAULT NULL COMMENT '豆瓣评分',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='电影表';

-- ----------------------------
-- Table structure for pro_movie_actor
-- ----------------------------
DROP TABLE IF EXISTS `pro_movie_actor`;
CREATE TABLE `pro_movie_actor` (
  `id` char(37) NOT NULL COMMENT '记录id',
  `movie_id` char(37) DEFAULT NULL COMMENT '电影id',
  `actor_id` char(37) DEFAULT NULL COMMENT '演员id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for pro_movie_down_address
-- ----------------------------
DROP TABLE IF EXISTS `pro_movie_down_address`;
CREATE TABLE `pro_movie_down_address` (
  `id` char(37) NOT NULL COMMENT '记录id',
  `movie_id` char(37) DEFAULT NULL COMMENT '电影id',
  `down_address` varchar(1000) DEFAULT NULL COMMENT '下载地址',
  `down_type` varchar(200) DEFAULT NULL COMMENT '下载地址类型',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='电影下载地址表';

-- ----------------------------
-- Table structure for pro_user
-- ----------------------------
DROP TABLE IF EXISTS `pro_user`;
CREATE TABLE `pro_user` (
  `id` char(37) NOT NULL COMMENT '用户id',
  `user_account` char(16) DEFAULT NULL COMMENT '用户账号',
  `user_name` varchar(200) DEFAULT NULL COMMENT '用户名称',
  `user_xunlei_account` varchar(200) DEFAULT NULL COMMENT '用户迅雷账户',
  `user_xunlei_password` varchar(200) DEFAULT NULL COMMENT '用户迅雷密码',
  `user_password` varchar(200) DEFAULT NULL COMMENT '用户密码',
  `user_wx_id` char(50) DEFAULT NULL COMMENT '微信id',
  `user_wx_session_key` char(50) DEFAULT NULL COMMENT '微信sessionkey',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户表';

-- ----------------------------
-- Table structure for pro_user_movie
-- ----------------------------
DROP TABLE IF EXISTS `pro_user_movie`;
CREATE TABLE `pro_user_movie` (
  `id` char(37) DEFAULT NULL COMMENT '记录id',
  `user_id` char(37) DEFAULT NULL COMMENT '用户id',
  `movie_id` char(37) DEFAULT NULL COMMENT '电影id',
  UNIQUE KEY `movie_id` (`movie_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户已添加的电影关系表';
