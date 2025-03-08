
CREATE TABLE IF NOT EXISTS general.subscription_type
	(
		id serial primary key not null,
		plan_name varchar(300),
		amount numeric(10,2) not null default 0.00,
		debate_type integer not null references debate.debate_type_master,
		allowed_debate integer,
		created_by integer not null references auth.user_master(id),
		is_active boolean not null default True,
		generated integer not null default extract(epoch from now())

	);


CREATE TABLE IF NOT EXISTS	general.payment_details
	(
		id serial primary key not null,
		transiction_id varchar(200),
		subscription_type_id integer not null references general.subscription_type,
		generated integer not null default extract(epoch from now())

	);

CREATE TABLE If NOT EXISTS users.user_subscription_details
	(
		id serial primary key not null,
		user_id integer not null references auth.user_master(id),
		subscription_type_id integer not null references general.subscription_type,
		payment_details_id integer not null references general.payment_details,
		used_debated integer,
		is_active boolean not null default True,
		generated integer not null default extract(epoch from now())

	);

