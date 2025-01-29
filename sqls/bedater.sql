
DROP DATABASE IF EXISTS bedater_debates;
DROP USER IF EXISTS bedateruser;
CREATE USER bedateruser WITH SUPERUSER LOGIN PASSWORD 'password';
CREATE DATABASE bedater_debates owner bedateruser;

\c bedater_debates


CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS general;
CREATE SCHEMA IF NOT EXISTS debate;
CREATE SCHEMA IF NOT EXISTS vote;

BEGIN WORK;
CREATE TABLE IF NOT EXISTS auth.user_master
	(
		id serial primary key not null,
		username varchar(500) not null unique,
		email varchar(500),
		name varchar(100),
		gender varchar(20),
		phone_no varchar(100),
		profile_exist boolean not null default false,
		is_active boolean not null default true,
		generated integer not null default extract(epoch from now())

	);

CREATE TABLE IF NOT EXISTS auth.password_master
	(
		id serial primary key not null,
		user_id integer not null references auth.user_master(id),
		password varchar(500) not null,
		is_active boolean not null default true,
		generated integer not null default extract(epoch from now())

	);


CREATE TABLE IF NOT EXISTS users.profile_pictures_master
	(
		id serial primary key not null,
		user_id integer not null references auth.user_master(id),
		profile_path varchar(500),
		is_active boolean not null default true,
		generated integer not null default extract(epoch from now())


	);


CREATE TABLE IF NOT EXISTS general.image_type_master
	(
		id serial primary key not null,
		type varchar(100),
		is_active boolean not null default true,
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)

	);


CREATE TABLE IF NOT EXISTS general.image_master
	(
		id serial primary key not null,
		image_name varchar(200),
		image_path varchar(500),
		image_type integer not null references general.image_type_master(id),
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)

	);


CREATE TABLE IF NOT EXISTS users.avatar_master
	(
		id serial primary key not null,
		user_id integer not null references auth.user_master(id),
		gender varchar(20),
		skin integer not null references general.image_type_master(id),
		hair integer not null references general.image_type_master(id),
		dress integer not null references general.image_type_master(id),
		is_active boolean not null default true,
		generated integer not null default extract(epoch from now())


	);

CREATE TABLE IF NOT EXISTS debate.debate_type_master
	(
		id serial primary key not null,
		type varchar(200),
		is_active boolean not null default true,
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)
	);


CREATE TABLE IF NOT EXISTS debate.debate_master
	(
		id serial primary key not null,
		debate_type_id integer not null references debate.debate_type_master(id),
		title varchar(500),
		room_id varchar(1000),
		hour varchar(10),
		minute varchar(10),
		seconds varchar(10),
		member_on_each_side integer,
		participants_code varchar(100),
		audience_code varchar(100),
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)
	);

CREATE TABLE IF NOT EXISTS debate.topic_master
	(
		id serial primary key not null,
		debate_id integer not null references debate.debate_master(id),
		topic varchar(500),
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)

	);

CREATE TABLE IF NOT EXISTS debate.counter_statements_master
	(
		id serial primary key not null,
		debate_id integer not null references debate.debate_master(id),
		counters integer,
		seconds varchar(10),
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)
	);


CREATE TABLE IF NOT EXISTS debate.debate_cost_master
	(
		id serial primary key not null,
		price numeric(10,2) not null,
		debate_type_id integer not null references debate.debate_type_master(id),
		generated integer not null default extract(epoch from now()),
		is_active integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)

			
	);


CREATE TABLE IF NOT EXISTS debate.participants_type_master
	(
		id serial primary key not null,
		participant_type varchar(100),
		is_active integer not null default extract(epoch from now()),
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)

	);


CREATE TABLE IF	 NOT EXISTS debate.debate_participant_master
	(
		id serial primary key not null,
		debate_id integer not null references debate.debate_master(id),
		user_id integer not null references auth.user_master(id),
		participant_type_id integer not null references debate.participants_type_master(id),
		is_locked boolean not null default false,
		generated integer not null default extract(epoch from now())

	);


CREATE TABLE IF	NOT EXISTS debate.debate_participant_teams_details_master
	(
		id serial primary key not null,
		debate_id integer not null references debate.debate_master(id),
		team_name varchar(200),
		team_side varchar(10),
		image_path varchar(500),
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)

	);


CREATE TABLE IF	 NOT EXISTS debate.debate_participant_details
	(
		id serial primary key not null,
		participant_id integer not null references debate.debate_participant_master(id),
		joined_team integer not null references debate.debate_participant_teams_details_master(id),
		debate_id integer not null references debate.debate_master(id),
		generated integer not null default extract(epoch from now())
	);



CREATE TABLE IF NOT EXISTS vote.vote_type_master
	(
		id serial primary key not null,
		type varchar(100),
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)
	);


CREATE TABLE IF NOT EXISTS vote.vote_master
	(
		id serial primary key not null,
		debate_id integer not null references debate.debate_master(id),
		topic_id integer not null references debate.topic_master(id),
		team_id integer not null references debate.debate_participant_teams_details_master(id),
		vote_type integer not null references vote.vote_type_master(id),
		count integer,
		generated integer not null default extract(epoch from now()),
		updated integer not null default extract(epoch from now())

	);

CREATE TABLE IF NOT EXISTS debate.advance_debate_details_master
	(
		id serial primary key not null,
		debate_id integer not null references debate.debate_master(id),
		topic_id integer not null references debate.topic_master(id),
		-- action_side varchar(100),
		team_id integer not null references debate.debate_participant_teams_details_master(id),
		voting_type integer not null references vote.vote_type_master(id),
		voting_allowed boolean not null default true,
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)
	);


CREATE TABLE IF NOT EXISTS debate.advance_debate_topic_time_master
	(
		id serial primary key not null,
		debate_id integer not null references debate.debate_master(id),
		topic_id integer not null references debate.topic_master(id),
		hour varchar(10),
		minute varchar(10),
		seconds varchar(10),
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id)

	);
COMMIT WORK;