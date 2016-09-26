DROP DATABASE IF EXISTS UpworkTasks;
CREATE DATABASE UpworkTasks;

USE UpworkTasks;

DROP TABLE IF EXISTS `tasks`;
CREATE TABLE `tasks` (

job_status BOOLEAN,
category2 varchar(255),
title varchar(255),
skills varchar(255),
job_type varchar(255),
budget int,
snippet text,
url varchar(255),
workload varchar(255),
subcategory2 varchar(255),
duration varchar(255),
date_created varchar(255),
id varchar(255) NOT NULL,

suitable_mark BOOLEAN,
relevance_week_1 float,
relevance_week_2 float,
relevance_week_3 float,
relevance_week_4 float,
relevance_week_5 float,
relevance_week_6 float,
relevance_week_7 float,
relevance_week_8 float,
times_recommended int,

INDEX `id`(`id`),
PRIMARY KEY (id)
) ENGINE=MyISAM;