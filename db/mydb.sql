DROP TABLE IF EXISTS public."user"
DROP TABLE IF EXISTS public."board"
DROP TABLE IF EXISTS public."link"

CREATE TABLE IF NOT EXISTS "users" (
    "user_id"   SERIAL NOT NULL,
	"name"  varchar(40) NOT NULL UNIQUE,
	"password"	varchar(40) NOT NULL,
	"email"	varchar(40) NOT NULL UNIQUE,
	"photo"	varchar(40),
	PRIMARY KEY("user_id")
);

CREATE TABLE IF NOT EXISTS "boards" (
	"board_id"	SERIAL NOT NULL,
	"name"	varchar(40) NOT NULL,
	"address"	varchar(10) NOT NULL UNIQUE,
	"about"	TEXT,
	"contents" jsonb,
	PRIMARY KEY("board_id")
);

CREATE TABLE IF NOT EXISTS "link" (
	"user_id"	INTEGER NOT NULL,
	"board_id"	INTEGER NOT NULL,
	PRIMARY KEY("user_id","board_id"),
	CONSTRAINT "K2" FOREIGN KEY("board_id") REFERENCES "boards"("board_id"),
	CONSTRAINT "K1" FOREIGN KEY("user_id") REFERENCES "users"("user_id")
);
