ALTER TABLE debate.debate_participant_master ADD COLUMN virtual_id INT,ADD CONSTRAINT fk_virtual_id FOREIGN KEY (virtual_id) REFERENCES debate.debate_tracker_master(id) ON DELETE CASCADE;
