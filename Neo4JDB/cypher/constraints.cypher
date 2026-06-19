CREATE CONSTRAINT distributor_id_unique IF NOT EXISTS
FOR (d:Distributor)
REQUIRE d.id IS UNIQUE;

CREATE CONSTRAINT technician_id_unique IF NOT EXISTS
FOR (t:Technician)
REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT installation_id_unique IF NOT EXISTS
FOR (i:Installation)
REQUIRE i.installation_id IS UNIQUE;

CREATE INDEX region_name_index IF NOT EXISTS
FOR (r:Region)
ON (r.name);

CREATE INDEX FOR (i:Installation) ON (i.region) IF NOT EXISTS;
CREATE INDEX FOR (i:Installation) ON (i.status) IF NOT EXISTS;
