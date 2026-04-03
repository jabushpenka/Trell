DROP TABLE IF EXISTS "links";
DROP TABLE IF EXISTS "link";
DROP TABLE IF EXISTS "users";
DROP TABLE IF EXISTS "boards";
DROP TABLE IF EXISTS "roles";

CREATE TABLE IF NOT EXISTS "users" (
    "user_id"   SERIAL NOT NULL,
	"user_name"  varchar(40) NOT NULL UNIQUE,
	"pword"	VARCHAR(100) NOT NULL,
	"email"	varchar(40) NOT NULL UNIQUE,
	"photo"	varchar(40),
	PRIMARY KEY("user_id")
);

CREATE TABLE IF NOT EXISTS "boards" (
	"board_id"	SERIAL NOT NULL,
	"board_name"	varchar(40) NOT NULL,
	"address"	varchar(40) NOT NULL UNIQUE,
	"about"	TEXT,
	"contents" jsonb,
	PRIMARY KEY("board_id")
);

CREATE TABLE IF NOT EXISTS "roles" (
	"role_id"	SERIAL NOT NULL,
	"role_name"	VARCHAR(40) NOT NULL,
	"description"	TEXT,
	PRIMARY KEY("role_id")
);

CREATE TABLE IF NOT EXISTS "links" (
	"user_id"	INTEGER NOT NULL,
	"board_id"	INTEGER NOT NULL,
	"role_id"   INTEGER NOT NULL DEFAULT 4,
	PRIMARY KEY("user_id","board_id"),
	CONSTRAINT "K1" FOREIGN KEY("user_id") REFERENCES "users"("user_id") ON DELETE CASCADE,
	CONSTRAINT "K2" FOREIGN KEY("board_id") REFERENCES "boards"("board_id") ON DELETE CASCADE,
	CONSTRAINT "K3" FOREIGN KEY("role_id") REFERENCES "roles"("role_id") ON DELETE SET DEFAULT
);

INSERT INTO roles ("role_name","description") VALUES
    ('Owner','can manage the entire board'),
    ('Administrator','can manage columns'),
	('Manager','can manage cards'),
	('Worker','can manage tasks');
