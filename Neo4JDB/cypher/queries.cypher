// 1. Compter les types de nœuds
MATCH (n)
RETURN labels(n) AS labels, count(n) AS total;

// 2. Compter les types de relations
MATCH ()-[r]->()
RETURN type(r) AS relation, count(r) AS total;

// 3. Top 10 distributeurs par nombre d’installations vendues
MATCH (d:Distributor)-[:SOLD]->(i:Installation)
RETURN d.id AS distributor_id, d.name AS distributor_name, count(i) AS installations_sold
ORDER BY installations_sold DESC
LIMIT 10;

// 4. Top 10 techniciens par installations maintenues
MATCH (t:Technician)-[:MAINTAINS]->(i:Installation)
RETURN t.id AS technician_id, t.name AS technician_name, count(i) AS installations_maintained
ORDER BY installations_maintained DESC
LIMIT 10;

// 5. Installations sans technicien
MATCH (i:Installation)
WHERE NOT EXISTS {
  MATCH (:Technician)-[:MAINTAINS]->(i)
}
RETURN i.installation_id AS installation_id, i.region AS region, i.status AS status
LIMIT 20;

// 6. Chemin complet distributeur → technicien → installation
MATCH path = (d:Distributor)-[:EMPLOYS]->(t:Technician)-[:MAINTAINS]->(i:Installation)
RETURN path
LIMIT 25;

// 7. Distributeurs et techniciens opérant dans la même région
MATCH (d:Distributor)-[:OPERATES_IN]->(r:Region)<-[:OPERATES_IN]-(t:Technician)
RETURN r.name AS region, d.name AS distributor, t.name AS technician
LIMIT 50;

// 8. Installations vendues par des distributeurs d’une autre région
MATCH (d:Distributor)-[:SOLD]->(i:Installation)
WHERE d.region <> i.region
RETURN d.name AS distributor, d.region AS distributor_region,
       i.installation_id AS installation_id, i.region AS installation_region
LIMIT 50;

// 9. Distributeurs qui vendent le plus hors de leur région
MATCH (d:Distributor)-[:SOLD]->(i:Installation)
WHERE d.region <> i.region
RETURN d.id AS distributor_id,
       d.name AS distributor_name,
       d.region AS distributor_region,
       count(i) AS cross_region_sales
ORDER BY cross_region_sales DESC
LIMIT 10;

// 10. Techniciens non certifiés qui maintiennent des installations
MATCH (t:Technician)-[:MAINTAINS]->(i:Installation)
WHERE t.certified = false
RETURN t.id AS technician_id,
       t.name AS technician_name,
       t.region AS technician_region,
       count(i) AS maintained_installations
ORDER BY maintained_installations DESC
LIMIT 20;

// 11. Installations vendues mais jamais maintenues
MATCH (d:Distributor)-[:SOLD]->(i:Installation)
WHERE NOT EXISTS {
  MATCH (:Technician)-[:MAINTAINS]->(i)
}
RETURN i.installation_id AS installation_id,
       i.region AS region,
       i.status AS status,
       d.name AS seller
LIMIT 50;

// 12. Installations maintenues par un technicien d’une autre région
MATCH (t:Technician)-[:MAINTAINS]->(i:Installation)
WHERE t.region <> i.region
RETURN t.id AS technician_id,
       t.name AS technician_name,
       t.region AS technician_region,
       i.installation_id AS installation_id,
       i.region AS installation_region
LIMIT 50;

// 13. Charge moyenne de maintenance par technicien certifié / non certifié
MATCH (t:Technician)-[:MAINTAINS]->(i:Installation)
WITH t.certified AS certified,
     t.id AS technician_id,
     count(i) AS load
RETURN certified,
       count(technician_id) AS technicians,
       avg(load) AS avg_maintenance_load,
       max(load) AS max_maintenance_load
ORDER BY avg_maintenance_load DESC;

// 14. Distributeurs sans technicien rattaché
MATCH (d:Distributor)
WHERE NOT EXISTS {
  MATCH (d)-[:EMPLOYS]->(:Technician)
}
RETURN d.id AS distributor_id,
       d.name AS distributor_name,
       d.region AS region
LIMIT 50;

// 15. Chemin complet d’une installation
MATCH path = (d:Distributor)-[:SOLD]->(i:Installation)<-[:MAINTAINS]-(t:Technician)
WHERE i.installation_id = 1
RETURN path;

// 16. Installations actives avec vendeur et technicien
MATCH (d:Distributor)-[:SOLD]->(i:Installation)<-[:MAINTAINS]-(t:Technician)
WHERE i.status = "active"
RETURN i.installation_id AS installation_id,
       i.region AS region,
       d.name AS distributor,
       t.name AS technician,
       t.certified AS technician_certified
LIMIT 50;