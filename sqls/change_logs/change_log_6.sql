ALTER TABLE debate.debate_participant_details
DROP COLUMN joined_team;

ALTER TABLE debate.debate_participant_details
ADD COLUMN joined_team INT,
ADD CONSTRAINT fk_joined_id
FOREIGN KEY (joined_team) REFERENCES debate.debate_participant_teams_master(id)
ON DELETE CASCADE;