const dbName = process.env.MONGO_INITDB_DATABASE || "solarmboa";
const appUser = process.env.MONGO_APP_USER || "solarmboa_app";
const appPassword = process.env.MONGO_APP_PASSWORD;


if (!appPassword) {
  throw new Error("MONGO_APP_PASSWORD is required");
}

db = db.getSiblingDB(dbName);

db.createUser({
  user: appUser,
  pwd: appPassword,
  roles: [
    { role: "readWrite", db: dbName }
  ]
});


print(`Utilisateur applicatif '${appUser}' créé avec succès dans ${dbName}`);
