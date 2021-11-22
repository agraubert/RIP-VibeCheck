create database if not exists reddit;

use reddit;

create table if not exists comments (
  comment_id varchar(10) primary key not null,
  permalink text,
  created_time datetime,
  author_username varchar(255),
  author_id varchar(10),
  comment_text text,
  comment_score integer,
  comment_score_last_updated datetime,
  subreddit_name varchar(255),
  subreddit_id varchar(10),
  post_permalink text,
  -- maybe resize
  post_title varchar(255),
  post_id varchar(10),
  post_score integer,
  post_score_last_updated datetime,
  is_top_level boolean,
  parent_id varchar(15)
);
