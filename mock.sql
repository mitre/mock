CREATE TABLE if not exists sim_response (id integer primary key AUTOINCREMENT, ability_id text, paw text, status integer, response text, UNIQUE (ability_id, paw) ON CONFLICT IGNORE);
CREATE TABLE if not exists sim_response_map (sim_response_id integer, property text, value text, UNIQUE (sim_response_id, property) ON CONFLICT IGNORE);
