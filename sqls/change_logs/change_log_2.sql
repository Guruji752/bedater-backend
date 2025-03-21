ALTER TABLE general.subscription_type DROP CONSTRAINT IF EXISTS subscription_type_debate_type_fkey;
ALTER TABLE general.subscription_type ALTER COLUMN debate_type TYPE INTEGER[] USING ARRAY[debate_type];
