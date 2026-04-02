BEGIN TRANSACTION;
CREATE TABLE "books" (
	"isbn13"	INTEGER,
	"title"	TEXT NOT NULL,
	"subtitle"	TEXT,
	"authors"	TEXT,
	"year"	INTEGER NOT NULL,
	"is_hardcover"	BOOLEAN,
	"notes"	TEXT,
	PRIMARY KEY("isbn13")
);
INSERT INTO "books" VALUES(9780008356224,'The Gate to China','A New History of the People''s Republic & Hong Kong','Michael Sheridan',2021,1,NULL);
INSERT INTO "books" VALUES(9780131103627,'The C Programming Language',NULL,'Brian W. Kernighan; Dennis M. Ritchie',1988,0,NULL);
INSERT INTO "books" VALUES(9780140148756,'The Penguin book of curious and interesting puzzles',NULL,'David G. Wells',1992,0,NULL);
INSERT INTO "books" VALUES(9780140432077,'On Liberty',NULL,'John Stuart Mill',1974,0,NULL);
INSERT INTO "books" VALUES(9780141036137,'Animal Farm',NULL,'George Orwell',1945,0,NULL);
INSERT INTO "books" VALUES(9780141036144,'Nineteen Eighty-Four',NULL,'George Orwell',1949,0,NULL);
INSERT INTO "books" VALUES(9780226151311,'Major Political Writings of Jean-Jacques Rousseau',NULL,'Jean-Jacques Rousseau; John T. Scott',2014,0,NULL);
INSERT INTO "books" VALUES(9780241560495,'The Hong Kong Diaries',NULL,'Chris Patten',2022,1,NULL);
INSERT INTO "books" VALUES(9780300084559,'On Democracy',NULL,'Robert Alan Dahl',2000,0,NULL);
INSERT INTO "books" VALUES(9780306924248,'COVID-19','The Pandemic that Never Should Have Happened and How to Stop the Next One','Debora MacKenzie',2020,1,NULL);
INSERT INTO "books" VALUES(9780452288522,'This Is Your Brain on Music','The Science of a Human Obsession','Daniel J. Levitin',2006,0,NULL);
INSERT INTO "books" VALUES(9780486284248,'Concepts of Modern Mathematics',NULL,'Ian Stewart',1995,0,NULL);
INSERT INTO "books" VALUES(9780500289822,'The Crown Jewels','The Official Illustrated History','Anna Keay',2011,0,NULL);
INSERT INTO "books" VALUES(9780734310859,'Borrowed Spaces','Life Between the Cracks of Modern Hong Kong','Christopher DeWolf',2017,0,NULL);
INSERT INTO "books" VALUES(9780734398505,'Generation HK','Seeking Identity in China''s Shadow','Ben Bland',2017,0,NULL);
INSERT INTO "books" VALUES(9780734399380,'Dear Hong Kong','An Elegy for a City','Xu Xi',2017,0,NULL);
INSERT INTO "books" VALUES(9780734399410,'Cantonese Love Stories',NULL,'Kai-cheung Dung',2017,0,NULL);
INSERT INTO "books" VALUES(9780734399465,'A System Apart','Hong Kong''s Political Economy from 1997 Until Now','Simon Cartledge',2017,0,NULL);
INSERT INTO "books" VALUES(9780734399625,'City of Protest','A Recent History of Dissent in Hong Kong','Antony Dapiran',2017,0,NULL);
INSERT INTO "books" VALUES(9780735211513,'We Have No Idea','A Guide to the Unknown Universe','Jorge Cham; Daniel Whiteson',2017,1,NULL);
INSERT INTO "books" VALUES(9780802713315,'Fermat''s Enigma','The Epic Quest to Solve the World''s Greatest Mathematical Problem','Simon Singh',1997,1,NULL);
INSERT INTO "books" VALUES(9780804190114,'On Tyranny',NULL,'Timothy Snyder',2017,0,NULL);
INSERT INTO "books" VALUES(9780810980594,'The Infinite World of M.C. Escher',NULL,'M. C. Escher; J. L. Locher',1984,1,NULL);
INSERT INTO "books" VALUES(9781402757969,'The Math Book',NULL,'Clifford A. Pickover',2009,1,NULL);
INSERT INTO "books" VALUES(9781467332507,'A Brief History of Communications',NULL,'IEEE Communications Society',2012,0,NULL);
INSERT INTO "books" VALUES(9781526626998,'Dictators','The Cult of Personality in the Twentieth Century','Frank Dikötter',2019,0,NULL);
INSERT INTO "books" VALUES(9781527283909,'An Introduction to Digital Healthcare in the NHS',NULL,'Gary McAllister',2021,0,NULL);
INSERT INTO "books" VALUES(9781546310259,'Deliver on Your Promise','How Simulation-Based Scheduling Will Change Your Business','C. Dennis Pegden',2017,0,NULL);
INSERT INTO "books" VALUES(9781586033491,'100 Years of Telephone Switching','Vol 1: Manual and Electo-mechanical Switching (1878-1960''s)','Robert J. Chapuis; Amos E. Joel',2003,1,NULL);
INSERT INTO "books" VALUES(9781616551681,'Legend of Korra : the Art of the Animated Series--Book One',NULL,'Michael Dante DiMartino; Bryan Konietzko',2013,1,NULL);
INSERT INTO "books" VALUES(9781616554620,'Legend of Korra : the Art of the Animated Series--Book Two',NULL,'Michael Dante DiMartino; Bryan Konietzko',2014,1,NULL);
INSERT INTO "books" VALUES(9781616555658,'Legend of Korra : the Art of the Animated Series--Book Three','','Michael Dante DiMartino; Bryan Konietzko',2015,1,NULL);
INSERT INTO "books" VALUES(9781733623742,'Vigil','Hong Kong on the Brink','Jeffery Wasserstrom',2020,0,NULL);
INSERT INTO "books" VALUES(9781787301405,'Orwell on Freedom',NULL,'George Orwell',2018,1,NULL);
INSERT INTO "books" VALUES(9781787635432,'Freedom','How We Lose It and How We Fight Back','Nathan Law; Evan Fowler',2021,0,NULL);
INSERT INTO "books" VALUES(9781789546040,'Democracy for Sale','Dark Money and Dirty Politics','Peter Geoghegan',2021,0,NULL);
INSERT INTO "books" VALUES(9781846685323,'17 Equations That Changed the World',NULL,'Ian Stewart',2012,0,NULL);
INSERT INTO "books" VALUES(9781851243631,'Magna Carta','The Foundation of Freedom 1215-2015','Nicholas Vincent',2014,0,NULL);
INSERT INTO "books" VALUES(9789881556233,'A Stroll Through Colonial Hong Kong',NULL,'Trea Wiltshire',2013,0,NULL);
COMMIT;
