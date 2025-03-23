CREATE TABLE IF NOT EXISTS debate.debate_participant_teams_master
	(
		id serial primary key not null,
		debate_id integer not null references debate.debate_master(id),
		team_side varchar(10),
		generated integer not null default extract(epoch from now()),
		created_by integer not null references auth.user_master(id),
		is_active boolean not null default True

	);


ALTER TABLE debate.debate_participant_teams_details_master 
DROP COLUMN team_side;

ALTER TABLE debate.debate_participant_teams_details_master 
ADD COLUMN team_id INT,
ADD CONSTRAINT fk_team
FOREIGN KEY (team_id) REFERENCES debate.debate_participant_teams_master(id)
ON DELETE CASCADE;


ALTER TABLE debate.debate_participant_teams_details_master 
ADD COLUMN virtual_id INT,
ADD CONSTRAINT virtualId
FOREIGN KEY (virtual_id) REFERENCES debate.debate_tracker_master(id)
ON DELETE CASCADE;

ALTER TABLE debate.advance_debate_details_master
DROP COLUMN team_id;

ALTER TABLE debate.advance_debate_details_master
ADD COLUMN team_id INT,
ADD CONSTRAINT fk_team_id
FOREIGN KEY (team_id) REFERENCES debate.debate_participant_teams_master(id)
ON DELETE CASCADE;