CREATE TABLE if not exists sim_response (id integer primary key AUTOINCREMENT, ability_id text, paw text, status integer, response text, UNIQUE (ability_id, paw) ON CONFLICT IGNORE);
