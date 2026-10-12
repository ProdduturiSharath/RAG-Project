# Worst test failures: parent-off

System selected on dev. Showing 30 of 64 failures.
Ranking: all-quotes@10, Recall@10, nDCG@10, MRR ascending; then ID.

## draft-00d4ad3e896413a3

Is Partial Mode supported by string_agg in PostgreSQL 15?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) string_agg ( value text, delimiter text ) text string_agg ( value bytea, delimiter bytea ) bytea Concatenates the non-null input values into a string. Each value after the first is preceded by the corresponding delimiter (if it's not null). | No

### Top three retrieved
1. `chunk-0a2bc8bc20369b3ac4b40204c954bb758e0c94bb79066a8aec365a860ac60780` — pg-15; score=0.167372, dense=0.749565, sparse=0.000000, rerank=0.16737216711044312

> , json_object_agg , jsonb_object_agg , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given to these aggregates. Users accustomed to working with other SQL database management systems might be disappointed by the performance of the count aggregate when it is applied to the entire table. A query like: will require effort proportional to the size of the table: PostgreSQL will

2. `chunk-679daae5d0d418760b28931d366d44e55adf66c77381fee6f30803c4cdd5e7de` — pg-17; score=0.124478, dense=0.750289, sparse=0.000000, rerank=0.1244780644774437

> there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given

3. `chunk-5a286b4b48cce9100872ba42f6f5c660e372387ad407c0522a210af2909049db` — pg-15; score=-0.824310, dense=0.742189, sparse=0.000000, rerank=-0.8243102431297302

> | Column Type Description | | --- | | feature_id character_data An identifier string containing the number of the part | | feature_name character_data Descriptive name of the part | | is_supported yes_or_no YES if the part is fully supported by the current version of PostgreSQL, NO if not | | is_verified_by character_data Always null, since the PostgreSQL development group does not perform formal testing of feature conformance | | comments character_data Possibly a comment about the supported status of the part |

## draft-00f9bb9ebb902fbc

Which dimension does trim_array shorten in a multidimensional array in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) trim_array ( array anyarray, n integer ) anyarray Trims an array by removing the last n elements. If the array is multidimensional, only the first dimension is trimmed.
- (pg-16) trim_array ( array anyarray, n integer ) anyarray Trims an array by removing the last n elements. If the array is multidimensional, only the first dimension is trimmed.

### Top three retrieved
1. `chunk-a5dba9a289c4fc973548117510da3416f41e101a259955b9bfb0cb5902284993` — pg-15; score=0.711170, dense=0.766024, sparse=0.000000, rerank=0.7111700773239136

> Arrays PostgreSQL allows columns of a table to be defined as variable-length multidimensional arrays. Arrays of any built-in or user-defined base type, enum type, composite type, range type, or domain can be created.

2. `chunk-cfc78c62397612eb877d0a6567c91cb7f544798b75177add0f29e607084c749e` — pg-17; score=0.711170, dense=0.766024, sparse=0.000000, rerank=0.7111700773239136

> Arrays PostgreSQL allows columns of a table to be defined as variable-length multidimensional arrays. Arrays of any built-in or user-defined base type, enum type, composite type, range type, or domain can be created.

3. `chunk-f0d18a2b666b31ccd937d65f9ff9229dd15bc0af1c6faf527853cec44adce24f` — pg-16; score=0.711170, dense=0.766024, sparse=0.000000, rerank=0.7111700773239136

> Arrays PostgreSQL allows columns of a table to be defined as variable-length multidimensional arrays. Arrays of any built-in or user-defined base type, enum type, composite type, range type, or domain can be created.

## draft-05e120c03871ce0e

When can notify_buffers be set in PostgreSQL 17?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: []

### Expected evidence
- (pg-17) notify_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_notify (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 16 . This parameter can only be set at server start.

### Top three retrieved
1. `chunk-2b606adb8fcb2bfb730ee2e2f0d3b9d7832c1b7c32865c1dab98f19826684307` — pg-16; score=0.150160, dense=0.757609, sparse=0.000000, rerank=0.15016025304794312

> thereby producing nonsensical results, and even causing out-of-bounds writes in some cases. The PostgreSQL Project thanks Ben Morris (in collaboration with Claude and Anthropic Research) for reporting this problem. (CVE-2026-15742) Fix buffer overrun in contrib/pg_stat_statements (Álvaro Herrera) Query normalization didn't accurately account for the amount of space the normalized string would require. The PostgreSQL Project thanks Sajeeb Lohani (with TrendAI Zero Day Initiative) and Yuelin Wang for reporting this problem. (CVE-2026-14676) Fix datatype error in contrib/pg_trgm 's GiST picksplit function (Heikki Linnakangas) § This mistake resulted in reading past the end of the buffer, typically causing bad split decisions; but a crash could ensue if you're very unlucky. The PostgreSQL Project thanks Mehmet D. Ince for reporting this problem. (CVE-2026-14678) Remove the plan cache in contrib/refint (Ayush Tiwari) § This caching behavior has several serious bugs, notably that check_foreign_key() embeds the new key values in its cascade-UPDATE queries, so a cached plan reuses the originally-needed values rather than the key values that should be used. The simplest solution is to remove it. The PostgreSQL Project thanks Hcamael for reporting this problem. (CVE-2026-14671) Fix self-deadlock when replaying WAL generated by an older minor version (Andrey Borodin) § This error was introduced in the previous set of minor releases. It caused standby servers that were following a primary of an older minor

2. `chunk-63af3cf7e027a4f1a08ac36c23c0b90ee8c4c0c2d4b2b8c73c9d217b2606e332` — pg-15; score=0.117989, dense=0.757157, sparse=0.000000, rerank=0.11798946559429169

> producing nonsensical results, and even causing out-of-bounds writes in some cases. The PostgreSQL Project thanks Ben Morris (in collaboration with Claude and Anthropic Research) for reporting this problem. (CVE-2026-15742) Fix buffer overrun in contrib/pg_stat_statements (Álvaro Herrera) Query normalization didn't accurately account for the amount of space the normalized string would require. The PostgreSQL Project thanks Sajeeb Lohani (with TrendAI Zero Day Initiative) and Yuelin Wang for reporting this problem. (CVE-2026-14676) Fix datatype error in contrib/pg_trgm 's GiST picksplit function (Heikki Linnakangas) § This mistake resulted in reading past the end of the buffer, typically causing bad split decisions; but a crash could ensue if you're very unlucky. The PostgreSQL Project thanks Mehmet D. Ince for reporting this problem. (CVE-2026-14678) Remove the plan cache in contrib/refint (Ayush Tiwari) § This caching behavior has several serious bugs, notably that check_foreign_key() embeds the new key values in its cascade-UPDATE queries, so a cached plan reuses the originally-needed values rather than the key values that should be used. The simplest solution is to remove it. The PostgreSQL Project thanks Hcamael for reporting this problem. (CVE-2026-14671) Fix self-deadlock when replaying WAL generated by an older minor version (Andrey Borodin) § This error was introduced in the previous set of minor releases. It caused standby servers that were following a primary of an older minor release

3. `chunk-4ced3b308ae1589ed905c906cb3856eedfa596a4c479703d1b2a826ef64d3c23` — pg-17; score=-0.335761, dense=0.751289, sparse=0.000000, rerank=-0.3357612192630768

> Asynchronous Notification PostgreSQL offers asynchronous notification via the LISTEN and NOTIFY commands. A client session registers its interest in a particular notification channel with the LISTEN command (and can stop listening with the UNLISTEN command). All sessions listening on a particular channel will be notified asynchronously when a NOTIFY command with that channel name is executed by any session. A payload string can be passed to communicate additional data to the listeners. libpq applications submit LISTEN , UNLISTEN , and NOTIFY commands as ordinary SQL commands. The arrival of NOTIFY messages can subsequently be detected by calling PQnotifies . The function PQnotifies returns the next notification from a list of unhandled notification messages received from the server. It returns a null pointer if there are no pending notifications. Once a notification is returned from PQnotifies , it is considered handled and will be removed from the list of notifications. After processing a PGnotify object returned by PQnotifies , be sure to free it with . It is sufficient to free the PGnotify pointer; the relname and extra fields do not represent separate allocations. (The names of these fields are historical; in particular, channel names need not have anything to do with relation names.) libpq Example Program 2 gives a sample program that illustrates the use of asynchronous notification. PQnotifies does

## draft-0bd01d40748321be

Which role grants access to the slots reserved by reserved_connections in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) reserved_connections ( integer ) Determines the number of connection slots that are reserved for connections by roles with privileges of the pg_use_reserved_connections role.

### Top three retrieved
1. `chunk-49edd73b121ff2b2d390c9ed189ff0307b6ea96c49c2d2b92d4f1e5eef8f4494` — pg-16; score=2.891462, dense=0.763951, sparse=0.000000, rerank=2.8914623260498047

> connection slots are available, new connections will be accepted only for superusers. The default value is zero connections. The value must be less than max_connections minus superuser_reserved_connections . This parameter can only be set at server start. superuser_reserved_connections ( integer ) Determines the number of connection slots that are reserved for connections by PostgreSQL superusers. At most max_connections connections can ever be active simultaneously. Whenever the number of active concurrent connections is at least max_connections minus superuser_reserved_connections , new connections will be accepted only for superusers. The connection slots reserved by this parameter are intended as final reserve for emergency use after the slots reserved by reserved_connections have been exhausted. The default value is three connections. The value must be less than max_connections minus reserved_connections . This parameter can only be set at server start. unix_socket_directories ( string ) Specifies the directory of the Unix-domain socket(s) on which the server is to listen for connections from client applications. Multiple sockets can be created by listing multiple directories separated by commas. Whitespace between entries is ignored; surround a directory name with double quotes if you need to include whitespace or commas in the name. An empty value specifies not listening on any Unix-domain sockets, in which case only TCP/IP sockets can be used to connect to the server. A value that

2. `chunk-05092af7916b7eaea23cdfcfef52054aea8f6cf92aa7923df6915366eb018f6d` — pg-17; score=1.314646, dense=0.782987, sparse=0.000000, rerank=1.3146462440490723

> Predefined Roles PostgreSQL provides a set of predefined roles that provide access to certain, commonly needed, privileged capabilities and information. Administrators (including roles that have the CREATEROLE privilege) can GRANT these roles to users and/or other roles in their environment, providing those users with access to the specified capabilities and information. The predefined roles are described in Predefined Roles . Note that the specific permissions for each of the roles may change in the future as additional capabilities are added. Administrators should monitor the release notes for changes. The pg_monitor , pg_read_all_settings , pg_read_all_stats and pg_stat_scan_tables roles are intended to allow administrators to easily configure a role for the purpose of monitoring the database server. They grant a set of common privileges allowing the role to read various useful configuration settings, statistics and other system information normally restricted to superusers. The pg_database_owner role has one implicit, situation-dependent member, namely the owner of the current database. Like any role, it can own objects or receive grants of access privileges. Consequently, once pg_database_owner has rights within a template database, each owner of a database instantiated from that template will exercise those rights. pg_database_owner cannot be a member of any role, and it cannot have non-implicit members. Initially, this role owns the public schema, so each database owner governs local use of the

3. `chunk-a7aa45f40fd71eb1e9f356317180d4c0efd6b0b8df4f5155736ab8c09e2c9acd` — pg-16; score=1.314646, dense=0.782987, sparse=0.000000, rerank=1.3146462440490723

> Predefined Roles PostgreSQL provides a set of predefined roles that provide access to certain, commonly needed, privileged capabilities and information. Administrators (including roles that have the CREATEROLE privilege) can GRANT these roles to users and/or other roles in their environment, providing those users with access to the specified capabilities and information. The predefined roles are described in Predefined Roles . Note that the specific permissions for each of the roles may change in the future as additional capabilities are added. Administrators should monitor the release notes for changes. The pg_monitor , pg_read_all_settings , pg_read_all_stats and pg_stat_scan_tables roles are intended to allow administrators to easily configure a role for the purpose of monitoring the database server. They grant a set of common privileges allowing the role to read various useful configuration settings, statistics and other system information normally restricted to superusers. The pg_database_owner role has one implicit, situation-dependent member, namely the owner of the current database. Like any role, it can own objects or receive grants of access privileges. Consequently, once pg_database_owner has rights within a template database, each owner of a database instantiated from that template will exercise those rights. pg_database_owner cannot be a member of any role, and it cannot have non-implicit members. Initially, this role owns the public schema, so each database owner governs local use of the

## draft-24083cabffc26972

Does bit_and ignore null inputs in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) Computes the bitwise AND of all non-null input values.
- (pg-16) Computes the bitwise AND of all non-null input values.

### Top three retrieved
1. `chunk-6560e13f63abd4e6e3a5451dfa771daf888b2a1912c309a93b2cd975764a7fdf` — pg-15; score=2.456904, dense=0.789368, sparse=0.000000, rerank=2.456904411315918

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

2. `chunk-75d6f7845f32cf5b2105aaa47c1bcfbe416391ba5f4f973d1e0ba3d0e6d6e6ae` — pg-17; score=2.456904, dense=0.789368, sparse=0.000000, rerank=2.456904411315918

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

3. `chunk-e96bdd39a5eea04e1d94cad496fb7a45adc7440d5c0425607a7e9fdaf887060f` — pg-16; score=2.456904, dense=0.789368, sparse=0.000000, rerank=2.456904411315918

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

## draft-2f27ea088c1b07ce

What happens if json_object_agg_unique receives duplicate keys in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) json_object_agg_unique ( key "any", value "any" ) json jsonb_object_agg_unique ( key "any", value "any" ) jsonb Collects all the key/value pairs into a JSON object. Key arguments are coerced to text; value arguments are converted as per to_json or to_jsonb. Values can be null, but keys cannot. If there is a duplicate key an error is thrown.

### Top three retrieved
1. `chunk-e67df7d5e94b884efef1364b2c05bb86057341739c3a3f8afbad1097d052a674` — pg-15; score=2.497820, dense=0.757001, sparse=0.000000, rerank=2.4978203773498535

> contrib/hstore 's binary input function (Michael Paquier) § hstore 's receive function crashed on input containing duplicate keys. hstore values generated by Postgres would never contain duplicate keys, so this mistake has gone unnoticed. The crash could be provoked by malicious or corrupted data.

2. `chunk-38ef0f1957b75f4f1fb69fbc57358be1ea419b7711492183b41078360f4ddf84` — pg-16; score=1.413758, dense=0.759116, sparse=0.000000, rerank=1.4137579202651978

> Parameters UNIQUE Causes the system to check for duplicate values in the table when the index is created (if data already exist) and each time data is added. Attempts to insert or update data which would result in duplicate entries will generate an error. Additional restrictions apply when unique indexes are applied to partitioned tables; see CREATE TABLE . CONCURRENTLY When this option is used, PostgreSQL will build the index without taking any locks that prevent concurrent inserts, updates, or deletes on the table; whereas a standard index build locks out writes (but not reads) on the table until it's done. There are several caveats to be aware of when using this option — see Building Indexes Concurrently below. For temporary tables, CREATE INDEX is always non-concurrent, as no other session can access them, and non-concurrent index creation is cheaper. IF NOT EXISTS Do not throw an error if a relation with the same name already exists. A notice is issued in this case. Note that there is no guarantee that the existing index is anything like the one that would have been created. Index name is required when IF NOT EXISTS is specified. INCLUDE The optional INCLUDE clause specifies a list of columns which will be included in the index as non-key columns. A non-key column cannot be used

3. `chunk-a0d61208c107dffd45292ef359b144df51534049f981a80b0ccde88b86c5ef23` — pg-17; score=1.413758, dense=0.759116, sparse=0.000000, rerank=1.4137579202651978

> Parameters UNIQUE Causes the system to check for duplicate values in the table when the index is created (if data already exist) and each time data is added. Attempts to insert or update data which would result in duplicate entries will generate an error. Additional restrictions apply when unique indexes are applied to partitioned tables; see CREATE TABLE . CONCURRENTLY When this option is used, PostgreSQL will build the index without taking any locks that prevent concurrent inserts, updates, or deletes on the table; whereas a standard index build locks out writes (but not reads) on the table until it's done. There are several caveats to be aware of when using this option — see Building Indexes Concurrently below. For temporary tables, CREATE INDEX is always non-concurrent, as no other session can access them, and non-concurrent index creation is cheaper. IF NOT EXISTS Do not throw an error if a relation with the same name already exists. A notice is issued in this case. Note that there is no guarantee that the existing index is anything like the one that would have been created. Index name is required when IF NOT EXISTS is specified. INCLUDE The optional INCLUDE clause specifies a list of columns which will be included in the index as non-key columns. A non-key column cannot be used

## draft-32068527036ef646

Which setting selects the configuration file for user-name mapping?

**Category:** identifier not matched. **Reason:** The expected identifier is absent from the top three.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ident_file ( string ) Specifies the configuration file for user name mapping (customarily called pg_ident.conf ).

### Top three retrieved
1. `chunk-5069d9d685ab1b2478c29cb8a2557eb5ed4ee2df6412104ae53c450240b8762a` — pg-16; score=4.435529, dense=0.784789, sparse=0.000000, rerank=4.435528755187988

> Parameters user_name User name of the mapping. CURRENT_ROLE , CURRENT_USER , and USER match the name of the current user. PUBLIC is used to match all present and future user names in the system. server_name Server name of the user mapping. OPTIONS ( [ ADD | SET | DROP ] option [' value '] [, ... ] ) Change options for the user mapping. The new options override any previously specified options. ADD , SET , and DROP specify the action to be performed. ADD is assumed if no operation is explicitly specified. Option names must be unique; options are also validated by the server's foreign-data wrapper.

2. `chunk-6588ed9eb9ede4e386bc459ca36799b5cd8508e10227752dc6da2303929f6802` — pg-15; score=4.435529, dense=0.784789, sparse=0.000000, rerank=4.435528755187988

> Parameters user_name User name of the mapping. CURRENT_ROLE , CURRENT_USER , and USER match the name of the current user. PUBLIC is used to match all present and future user names in the system. server_name Server name of the user mapping. OPTIONS ( [ ADD | SET | DROP ] option [' value '] [, ... ] ) Change options for the user mapping. The new options override any previously specified options. ADD , SET , and DROP specify the action to be performed. ADD is assumed if no operation is explicitly specified. Option names must be unique; options are also validated by the server's foreign-data wrapper.

3. `chunk-d8bc5d3a281e143715f850ae9232ed6c8326d082e258f2413b2d4f110101d298` — pg-17; score=4.435529, dense=0.784789, sparse=0.000000, rerank=4.435528755187988

> Parameters user_name User name of the mapping. CURRENT_ROLE , CURRENT_USER , and USER match the name of the current user. PUBLIC is used to match all present and future user names in the system. server_name Server name of the user mapping. OPTIONS ( [ ADD | SET | DROP ] option [' value '] [, ... ] ) Change options for the user mapping. The new options override any previously specified options. ADD , SET , and DROP specify the action to be performed. ADD is assumed if no operation is explicitly specified. Option names must be unique; options are also validated by the server's foreign-data wrapper.

## draft-33d8c19a2a6a932d

What is the maximum size of one pg_largeobject.data value?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) data bytea Actual data stored in the large object. This will never be more than LOBLKSIZE bytes and might be less.

### Top three retrieved
1. `chunk-006cbb7bc5add7256d761b85457c7544eeeafa8e73e18e97b992d80c2cba1080` — pg-15; score=3.412874, dense=0.809760, sparse=0.000000, rerank=3.412874221801758

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

2. `chunk-61e357df06adaa29a4cf6da9f325363b17f4d2cc36c5fb14b547aebd4c27856a` — pg-16; score=3.412874, dense=0.809760, sparse=0.000000, rerank=3.412874221801758

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

3. `chunk-7030d3387276a19728f0806066578ef33be22c4946369d8afe8885e40c9fa50a` — pg-17; score=3.412874, dense=0.809760, sparse=0.000000, rerank=3.412874221801758

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

## draft-39a8f35fc5f9cb13

What happens to null array entries in array_to_string when null_string is omitted in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) array_to_string ( array anyarray, delimiter text , null_string text ) text Converts each array element to its text representation, and concatenates those separated by the delimiter string. If null_string is given and is not NULL, then NULL array entries are represented by that string; otherwise, they are omitted.
- (pg-16) array_to_string ( array anyarray, delimiter text , null_string text ) text Converts each array element to its text representation, and concatenates those separated by the delimiter string. If null_string is given and is not NULL, then NULL array entries are represented by that string; otherwise, they are omitted.

### Top three retrieved
1. `chunk-6560e13f63abd4e6e3a5451dfa771daf888b2a1912c309a93b2cd975764a7fdf` — pg-15; score=4.931211, dense=0.838063, sparse=0.000000, rerank=4.931211471557617

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

2. `chunk-75d6f7845f32cf5b2105aaa47c1bcfbe416391ba5f4f973d1e0ba3d0e6d6e6ae` — pg-17; score=4.931211, dense=0.838063, sparse=0.000000, rerank=4.931211471557617

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

3. `chunk-e96bdd39a5eea04e1d94cad496fb7a45adc7440d5c0425607a7e9fdaf887060f` — pg-16; score=4.931211, dense=0.838063, sparse=0.000000, rerank=4.931211471557617

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

## draft-3abee3e4240c30d3

What is the default work_mem in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes. The default value is four megabytes ( 4MB ).
- (pg-16) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes. The default value is four megabytes ( 4MB ).

### Top three retrieved
1. `chunk-7fd14a36387fc84e861c402fd973fcfbfd2b6be66b06d29e18b86db8fe479883` — pg-17; score=3.210735, dense=0.796697, sparse=0.000000, rerank=3.2107348442077637

> -S work-mem Specifies the base amount of memory to be used by sorts and hash tables before resorting to temporary disk files. See the description of the work_mem configuration parameter in Memory . -V --version Print the postgres version and exit. -- name = value Sets a named run-time parameter; a shorter form of -c . --describe-config This option dumps out the server's internal configuration variables, descriptions, and defaults in tab-delimited COPY format. It is designed primarily for use by administration tools. -? --help Show help about postgres command line arguments, and exit.

2. `chunk-88c8272c1ad2d399b7072d8d7d8886a83425e75b9045962e0047733fc2a80532` — pg-16; score=3.210735, dense=0.796697, sparse=0.000000, rerank=3.2107348442077637

> -S work-mem Specifies the base amount of memory to be used by sorts and hash tables before resorting to temporary disk files. See the description of the work_mem configuration parameter in Memory . -V --version Print the postgres version and exit. -- name = value Sets a named run-time parameter; a shorter form of -c . --describe-config This option dumps out the server's internal configuration variables, descriptions, and defaults in tab-delimited COPY format. It is designed primarily for use by administration tools. -? --help Show help about postgres command line arguments, and exit.

3. `chunk-fdc50dcaf183bb0e851ed735ae8d77b5aa556f5eda191678e6665f20f7a5b7cc` — pg-15; score=3.210735, dense=0.796697, sparse=0.000000, rerank=3.2107348442077637

> -S work-mem Specifies the base amount of memory to be used by sorts and hash tables before resorting to temporary disk files. See the description of the work_mem configuration parameter in Memory . -V --version Print the postgres version and exit. -- name = value Sets a named run-time parameter; a shorter form of -c . --describe-config This option dumps out the server's internal configuration variables, descriptions, and defaults in tab-delimited COPY format. It is designed primarily for use by administration tools. -? --help Show help about postgres command line arguments, and exit.

## draft-3b18c553103442c0

Which setting selects the configuration file for host-based authentication?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) hba_file ( string ) Specifies the configuration file for host-based authentication (customarily called pg_hba.conf ).

### Top three retrieved
1. `chunk-3d24696d8bf22df17c9d499baa02c736f092adc5f797dfb01435aef4d45d73c5` — pg-17; score=3.357517, dense=0.716873, sparse=0.000000, rerank=3.3575174808502197

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The pg_hba.conf file is read on start-up and when the main server process receives a SIGHUP signal. If you edit the file on an active system, you will need to signal the postmaster (using pg_ctl reload , calling the SQL function pg_reload_conf() , or using kill -HUP ) to make it re-read the file. The preceding statement is not true on Microsoft Windows: there, any changes in the pg_hba.conf file are immediately applied by subsequent new connections. The system view pg_hba_file_rules can be helpful for pre-testing changes to the pg_hba.conf file, or for diagnosing problems if loading of the file did not have the desired effects. Rows in the view with non-null error fields indicate problems in the corresponding lines of the file. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the

2. `chunk-bcd56fe484c4fa60608a00b01f9e694128e82f273c22fc61badc8e1eb8925c34` — pg-17; score=0.816975, dense=0.720168, sparse=0.000000, rerank=0.8169747591018677

> Options -A authmethod --auth= authmethod This option specifies the default authentication method for local users used in pg_hba.conf ( host and local lines). See The pg_hba.conf File for an overview of valid values. initdb will prepopulate pg_hba.conf entries using the specified authentication method for non-replication as well as replication connections. Do not use trust unless you trust all local users on your system. trust is the default for ease of installation. --auth-host= authmethod This option specifies the authentication method for local users via TCP/IP connections used in pg_hba.conf ( host lines). --auth-local= authmethod This option specifies the authentication method for local users via Unix-domain socket connections used in pg_hba.conf ( local lines). -D directory --pgdata= directory This option specifies the directory where the database cluster should be stored. This is the only information required by initdb , but you can avoid writing it by setting the PGDATA environment variable, which can be convenient since the database server ( postgres ) can find the data directory later by the same variable. -E encoding --encoding= encoding Selects the encoding of the template databases. This will also be the default encoding of any database you create later, unless you override it then. The character sets supported by the PostgreSQL server are described in Supported Character Sets . By default, the template database encoding

3. `chunk-c792920e9f29d855a6f84314dbf9c0e7f5697b27e6ec1c1f78e66b5cdb8ca535` — pg-16; score=0.816975, dense=0.720168, sparse=0.000000, rerank=0.8169747591018677

> Options -A authmethod --auth= authmethod This option specifies the default authentication method for local users used in pg_hba.conf ( host and local lines). See The pg_hba.conf File for an overview of valid values. initdb will prepopulate pg_hba.conf entries using the specified authentication method for non-replication as well as replication connections. Do not use trust unless you trust all local users on your system. trust is the default for ease of installation. --auth-host= authmethod This option specifies the authentication method for local users via TCP/IP connections used in pg_hba.conf ( host lines). --auth-local= authmethod This option specifies the authentication method for local users via Unix-domain socket connections used in pg_hba.conf ( local lines). -D directory --pgdata= directory This option specifies the directory where the database cluster should be stored. This is the only information required by initdb , but you can avoid writing it by setting the PGDATA environment variable, which can be convenient since the database server ( postgres ) can find the data directory later by the same variable. -E encoding --encoding= encoding Selects the encoding of the template databases. This will also be the default encoding of any database you create later, unless you override it then. The character sets supported by the PostgreSQL server are described in Supported Character Sets . By default, the template database encoding

## draft-3bbf02c4e418a086

Which bitwise aggregate can checksum an unordered set of values in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bit_xor ( smallint ) smallint bit_xor ( integer ) integer bit_xor ( bigint ) bigint bit_xor ( bit ) bit Computes the bitwise exclusive OR of all non-null input values. Can be useful as a checksum for an unordered set of values.
- (pg-16) bit_xor ( smallint ) smallint bit_xor ( integer ) integer bit_xor ( bigint ) bigint bit_xor ( bit ) bit Computes the bitwise exclusive OR of all non-null input values. Can be useful as a checksum for an unordered set of values.

### Top three retrieved
1. `chunk-dbebf0e79902d7d2b7ef8662c9576fc123c51adfd48a6155d28ae3567614339d` — pg-15; score=0.421528, dense=0.760520, sparse=0.000000, rerank=0.42152807116508484

> (Tom Lane) § § Parsing of these query structures did not check for overflow of 16-bit fields, so that construction of an invalid query tree was possible. This can crash the server when executing the query. The PostgreSQL Project thanks Xint Code for reporting this problem. (CVE-2026-6473) Guard against overly long values of contrib/ltree 's lquery type (Michael Paquier) § Values with more than 64K items caused internal overflows, potentially resulting in stack smashes or wrong answers. The PostgreSQL Project thanks Vergissmeinnicht, A1ex, and Jihe Wang for reporting this problem. (CVE-2026-6473) Prevent SQL injection and buffer overruns in contrib/spi (Nathan Bossart) § check_foreign_key() was insufficiently careful about quoting key values, and also used fixed-length buffers for constructing queries. While this module is only meant as example code, it still shouldn't contain such dangerous errors. The PostgreSQL Project thanks Nikolay Samokhvalov for reporting this problem. (CVE-2026-6637) Check for nondeterministic collations before assuming that an equality condition on a collatable type implies uniqueness (Richard Guo) § § Numerous planner optimizations assume that, for example, at most one table row can satisfy WHERE x = 'abc' if there is a unique index on x . However this conclusion is unsafe in general if the index and the WHERE clause have different collations attached. It is safe when both collations are deterministic, because that

2. `chunk-0a2bc8bc20369b3ac4b40204c954bb758e0c94bb79066a8aec365a860ac60780` — pg-15; score=-0.723434, dense=0.773352, sparse=0.000000, rerank=-0.7234342694282532

> , json_object_agg , jsonb_object_agg , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given to these aggregates. Users accustomed to working with other SQL database management systems might be disappointed by the performance of the count aggregate when it is applied to the entire table. A query like: will require effort proportional to the size of the table: PostgreSQL will

3. `chunk-151009069415cf30ea2471b894c8e75b70d2af6021ae04232a18e0fc4a6ee5e8` — pg-16; score=-1.161884, dense=0.737331, sparse=0.000000, rerank=-1.161884069442749

> case, write just () not (*) . ( PostgreSQL will actually accept either spelling, but only the first way conforms to the SQL standard.) An example of an ordered-set aggregate call is: which obtains the 50th percentile, or median, value of the income column from table households . Here, 0.5 is a direct argument; it would make no sense for the percentile fraction to be a value varying across rows. If FILTER is specified, then only the input rows for which the filter_clause evaluates to true are fed to the aggregate function; other rows are discarded. For example: The predefined aggregate functions are described in Aggregate Functions . Other aggregate functions can be added by the user. An aggregate expression can only appear in the result list or HAVING clause of a SELECT command. It is forbidden in other clauses, such as WHERE , because those clauses are logically evaluated before the results of aggregates are formed. When an aggregate expression appears in a subquery (see Scalar Subqueries and Subquery Expressions ), the aggregate is normally evaluated over the rows of the subquery. But an exception occurs if the aggregate's arguments (and filter_clause if any) contain only outer-level variables: the aggregate then belongs to the nearest such outer level, and is evaluated over the rows of that query. The aggregate

## draft-4a08f22879a56114

Which dimension of a multidimensional array does array_shuffle randomize in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) array_shuffle ( anyarray ) anyarray Randomly shuffles the first dimension of the array.

### Top three retrieved
1. `chunk-a5dba9a289c4fc973548117510da3416f41e101a259955b9bfb0cb5902284993` — pg-15; score=1.235363, dense=0.706140, sparse=0.000000, rerank=1.235363483428955

> Arrays PostgreSQL allows columns of a table to be defined as variable-length multidimensional arrays. Arrays of any built-in or user-defined base type, enum type, composite type, range type, or domain can be created.

2. `chunk-cfc78c62397612eb877d0a6567c91cb7f544798b75177add0f29e607084c749e` — pg-17; score=1.235363, dense=0.706140, sparse=0.000000, rerank=1.235363483428955

> Arrays PostgreSQL allows columns of a table to be defined as variable-length multidimensional arrays. Arrays of any built-in or user-defined base type, enum type, composite type, range type, or domain can be created.

3. `chunk-f0d18a2b666b31ccd937d65f9ff9229dd15bc0af1c6faf527853cec44adce24f` — pg-16; score=1.235363, dense=0.706140, sparse=0.000000, rerank=1.235363483428955

> Arrays PostgreSQL allows columns of a table to be defined as variable-length multidimensional arrays. Arrays of any built-in or user-defined base type, enum type, composite type, range type, or domain can be created.

## draft-51a8ac7c7fbf24a6

What does amtype = i mean in pg_am?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) amtype char t = table (including materialized views), i = index.

### Top three retrieved
1. `chunk-28519f7eb362bcdbaa90205b0118b69183eb7361f4eacfdd2f2e733686e4fc46` — pg-17; score=3.652203, dense=0.715740, sparse=0.000000, rerank=3.652202606201172

> SELECT am.amname AS index_method, opc.opcname AS opclass_name, opc.opcintype::regtype AS indexed_type, opc.opcdefault AS is_default FROM pg_am am, pg_opclass opc WHERE opc.opcmethod = am.oid ORDER BY index_method, opclass_name;

2. `chunk-e146379eff239c4647bc09f7f2fb4d6f5a5451bf4e032a39a53f2658a3578540` — pg-15; score=3.652203, dense=0.715740, sparse=0.000000, rerank=3.652202606201172

> SELECT am.amname AS index_method, opc.opcname AS opclass_name, opc.opcintype::regtype AS indexed_type, opc.opcdefault AS is_default FROM pg_am am, pg_opclass opc WHERE opc.opcmethod = am.oid ORDER BY index_method, opclass_name;

3. `chunk-ed041b3ff31c812ceac3ac1ded17578f3d15d1dd83ce51b6224f1e0ac0e18f99` — pg-16; score=3.652203, dense=0.715740, sparse=0.000000, rerank=3.652202606201172

> SELECT am.amname AS index_method, opc.opcname AS opclass_name, opc.opcintype::regtype AS indexed_type, opc.opcdefault AS is_default FROM pg_am am, pg_opclass opc WHERE opc.opcmethod = am.oid ORDER BY index_method, opclass_name;

## draft-529a81ca28099b25

Is Partial Mode supported by string_agg in PostgreSQL 16?

**Category:** wrong version. **Reason:** A same-lineage wrong version outranks the first correct evidence.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) string_agg ( value text, delimiter text ) text string_agg ( value bytea, delimiter bytea ) bytea Concatenates the non-null input values into a string. Each value after the first is preceded by the corresponding delimiter (if it's not null). | Yes

### Top three retrieved
1. `chunk-0a2bc8bc20369b3ac4b40204c954bb758e0c94bb79066a8aec365a860ac60780` — pg-15; score=0.188569, dense=0.749215, sparse=0.000000, rerank=0.18856921792030334

> , json_object_agg , jsonb_object_agg , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given to these aggregates. Users accustomed to working with other SQL database management systems might be disappointed by the performance of the count aggregate when it is applied to the entire table. A query like: will require effort proportional to the size of the table: PostgreSQL will

2. `chunk-679daae5d0d418760b28931d366d44e55adf66c77381fee6f30803c4cdd5e7de` — pg-17; score=0.093307, dense=0.747043, sparse=0.000000, rerank=0.0933070108294487

> there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given

3. `chunk-8f74eeab6521302bfbb9ab191ab4a062e67a8ae3e439c2de407b8214cf5efc5f` — pg-15; score=-0.385813, dense=0.739559, sparse=0.000000, rerank=-0.38581252098083496

> | Function Description | Partial Mode | | --- | --- | | array_agg ( anynonarray ) anyarray Collects all the input values, including nulls, into an array. | No | | array_agg ( anyarray ) anyarray Concatenates all the input arrays into an array of one higher dimension. (The inputs must all have the same dimensionality, and cannot be empty or null.) | No | | avg ( smallint ) numeric avg ( integer ) numeric avg ( bigint ) numeric avg ( numeric ) numeric avg ( real ) double precision avg ( double precision ) double precision avg ( interval ) interval Computes the average (arithmetic mean) of all the non-null input values. | Yes | | bit_and ( smallint ) smallint bit_and ( integer ) integer bit_and ( bigint ) bigint bit_and ( bit ) bit Computes the bitwise AND of all non-null input values. | Yes | | bit_or ( smallint ) smallint bit_or ( integer ) integer bit_or ( bigint ) bigint bit_or ( bit ) bit Computes the bitwise OR of all non-null input values. | Yes | | bit_xor ( smallint ) smallint bit_xor ( integer ) integer bit_xor ( bigint ) bigint bit_xor ( bit ) bit Computes the bitwise exclusive OR of all non-null input values. Can be useful as a checksum for an unordered set of values. | Yes | | bool_and ( boolean ) boolean Returns true if all non-null input values are true, otherwise false. | Yes | | bool_or ( boolean ) boolean Returns true if any non-null input value is true, otherwise false. | Yes | | count ( * ) bigint Computes the number of input rows. | Yes | | count ( "any" ) bigint Computes the number of input rows in which the input value is not null. | Yes | | every ( boolean ) boolean This is the SQL standard's equivalent to bool_and. | Yes | | json_agg ( anyelement ) json jsonb_agg ( anyelement ) jsonb Collects all the input values, including nulls, into a JSON array. Values are converted to JSON as per to_json or to_jsonb. | No | | json_object_agg ( key "any", value "any" ) json jsonb_object_agg ( key "any", value "any" ) jsonb Collects all the key/value pairs into a JSON object. Key arguments are coerced to text; value arguments are converted as per to_json or to_jsonb. Values can be null, but not keys. | No | | max ( see text ) same as input type Computes the maximum of the non-null input values. Available for any numeric, string, date/time, or enum type, as well as inet, interval, money, oid, pg_lsn, tid, xid8, and arrays of any of these types. | Yes | | min ( see text ) same as input type Computes the minimum of the non-null input values. Available for any numeric, string, date/time, or enum type, as well as inet, interval, money, oid, pg_lsn, tid, xid8, and arrays of any of these types. | Yes | | range_agg ( value anyrange ) anymultirange range_agg ( value anymultirange ) anymultirange Computes the union of the non-null input values. | No | | range_intersect_agg ( value anyrange ) anyrange range_intersect_agg ( value anymultirange ) anymultirange Computes the intersection of the non-null input values. | No | | string_agg ( value text, delimiter text ) text string_agg ( value bytea, delimiter bytea ) bytea Concatenates the non-null input values into a string. Each value after the first is preceded by the corresponding delimiter (if it's not null). | No | | sum ( smallint ) bigint sum ( integer ) bigint sum ( bigint ) numeric sum ( numeric ) numeric sum ( real ) real sum ( double precision ) double precision sum ( interval ) interval sum ( money ) money Computes the sum of the non-null input values. | Yes | | xmlagg ( xml ) xml Concatenates the non-null XML input values (see xmlagg). | No |

## draft-5ca5682d5aa33579

Does json_object_agg_unique_strict keep entries whose values are null in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) json_object_agg_unique_strict ( key "any", value "any" ) json jsonb_object_agg_unique_strict ( key "any", value "any" ) jsonb Collects all the key/value pairs into a JSON object. Key arguments are coerced to text; value arguments are converted as per to_json or to_jsonb. The key can not be null. If the value is null then the entry is skipped. If there is a duplicate key an error is thrown.

### Top three retrieved
1. `chunk-679daae5d0d418760b28931d366d44e55adf66c77381fee6f30803c4cdd5e7de` — pg-17; score=5.837944, dense=0.831338, sparse=0.000000, rerank=5.8379435539245605

> there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given

2. `chunk-8908fa26e794467b20d3f73e1de7a855254a1873b19a1936a59b028a09daaf9e` — pg-16; score=4.602391, dense=0.842301, sparse=0.000000, rerank=4.602390766143799

> , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given to these aggregates. Users accustomed to working with other SQL database management systems might be disappointed by the performance of the count aggregate when it is applied to the entire

3. `chunk-8fa7ce08a635422ae49fafa3adcb8a0a8547c2e5871ca1b469c1d67a3d336994` — pg-16; score=0.625259, dense=0.770568, sparse=0.000000, rerank=0.6252586841583252

> when no variables are supplied (Andrey Rachitskiy) § The jsonb @? and @@ operators cannot supply any variables to be used in their jsonpath expressions. This code path erroneously treated an unknown jsonpath variable as a JSON null, rather than raising an error as expected. Aside from not being the expected behavior, this mistake could result in unbounded memory consumption. Fix NULL-pointer crash when IS JSON or similar constructs have an argument that is of string category but lacks a cast to type text (Ayush Tiwari) § There are no such data types in core PostgreSQL , but the problem is reachable with some extension types. Avoid machine-dependent behavior when dividing the smallest possible money value by -1 (Andrey Rachitskiy) § Fix crash after out-of-memory failure partway through creation of a cache entry for a text search dictionary (Tom Lane) § Fix memory-safety bugs in processing of incorrect ispell/hunspell dictionary files (Andrey Rachitskiy) § Prevent access to other sessions' temporary tables (Jim Jones, Daniil Davydov, Alexander Korotkov) § Some code paths failed to prevent this, leading to silently wrong (inconsistent) results. Honor query cancel and vacuum delay during GIN index posting-tree cleanup (Paul Kim, Alexander Korotkov) § The posting tree for a common value can be large, so that this missed check could allow vacuum to run for a long

## draft-5fea284725ed24a7

Which pg_stat_gssapi field confirms that a connection delegated GSSAPI credentials in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) credentials_delegated boolean True if GSSAPI credentials were delegated on this connection.

### Top three retrieved
1. `chunk-1c0beae2c3af9d3f5281066825714c69678ad2816bf54b49426db8d2a79dce58` — pg-17; score=2.195230, dense=0.764616, sparse=0.000000, rerank=2.195230007171631

> parameter can only be set in the postgresql.conf file or on the server command line. See GSSAPI Authentication for more information. krb_caseins_users ( boolean ) Sets whether GSSAPI user names should be treated case-insensitively. The default is off (case sensitive). This parameter can only be set in the postgresql.conf file or on the server command line. gss_accept_delegation ( boolean ) Sets whether GSSAPI delegation should be accepted from the client. The default is off meaning credentials from the client will not be accepted. Changing this to on will make the server accept credentials delegated to it from the client. This parameter can only be set in the postgresql.conf file or on the server command line.

2. `chunk-7507f835516d00fb89182b3035967383136e82f267252c8096119cdbf89bd9ba` — pg-16; score=1.818443, dense=0.746419, sparse=0.000000, rerank=1.8184431791305542

> parameter can only be set in the postgresql.conf file or on the server command line. See GSSAPI Authentication for more information. krb_caseins_users ( boolean ) Sets whether GSSAPI user names should be treated case-insensitively. The default is off (case sensitive). This parameter can only be set in the postgresql.conf file or on the server command line. gss_accept_delegation ( boolean ) Sets whether GSSAPI delegation should be accepted from the client. The default is off meaning credentials from the client will not be accepted. Changing this to on will make the server accept credentials delegated to it from the client. This parameter can only be set in the postgresql.conf file or on the server command line. db_user_namespace ( boolean ) This parameter enables per-database user names. It is off by default. This parameter can only be set in the postgresql.conf file or on the server command line. If this is on, you should create users as username@dbname . When username is passed by a connecting client, @ and the database name are appended to the user name and that database-specific user name is looked up by the server. Note that when you create users with names containing @ within the SQL environment, you will need to quote the user name. With this parameter enabled, you can still create ordinary global users.

3. `chunk-b616f7f5508d5de5b7ad9709eb890b20780fa6e975d6cebb21036d3f93aac4b3` — pg-17; score=1.759724, dense=0.817616, sparse=0.000000, rerank=1.7597236633300781

> Basic Setup The PostgreSQL server will listen for both normal and GSSAPI -encrypted connections on the same TCP port, and will negotiate with any connecting client whether to use GSSAPI for encryption (and for authentication). By default, this decision is up to the client (which means it can be downgraded by an attacker); see The pg_hba.conf File about setting up the server to require the use of GSSAPI for some or all connections. When using GSSAPI for encryption, it is common to use GSSAPI for authentication as well, since the underlying mechanism will determine both client and server identities (according to the GSSAPI implementation) in any case. But this is not required; another PostgreSQL authentication method can be chosen to perform additional verification. Other than configuration of the negotiation behavior, GSSAPI encryption requires no setup beyond that which is necessary for GSSAPI authentication. (For more information on configuring that, see GSSAPI Authentication .)

## draft-7aba123f3dd8b9f6

What does defaclnamespace = 0 indicate in pg_default_acl?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-16) defaclnamespace oid (references pg_namespace.oid) The OID of the namespace associated with this entry, or zero if none

### Top three retrieved
1. `chunk-497263c216e671ac118ca27f6da0d32df665113296215fb4de41e8142573ae60` — pg-15; score=6.917902, dense=0.768639, sparse=0.000000, rerank=6.917901515960693

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

2. `chunk-da6d3c3daae1d20227cac5402abe455ddc35b88b4b474f42af8724ea34dec1f5` — pg-16; score=6.917902, dense=0.768639, sparse=0.000000, rerank=6.917901515960693

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

3. `chunk-ecb07ce2d8f7a6ba484992fa9abb51168effa59591154263b56051dcd2828dc7` — pg-17; score=6.917902, dense=0.768639, sparse=0.000000, rerank=6.917901515960693

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

## draft-7f9ef8ca7db593fa

What is the customary filename selected by hba_file?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) hba_file ( string ) Specifies the configuration file for host-based authentication (customarily called pg_hba.conf ).

### Top three retrieved
1. `chunk-67911986d3b2b9cc75a7cb444cd329061fd2defb1e88be726ccdaf3ef765a079` — pg-16; score=0.019379, dense=0.745920, sparse=0.000000, rerank=0.019378721714019775

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the next line by ending the line with a backslash. (Backslashes are not special except at the end of a line.) A record is made up of a number of fields which are separated by spaces and/or tabs. Fields can contain white space if the field value is double-quoted. Quoting one of the keywords in a database, user, or address field (e.g., all or replication ) makes the word lose its special meaning, and just match a database, user, or host with that name. Backslash line continuation applies even within quoted text or comments. Each authentication record specifies a connection type, a client IP address range (if relevant for the connection type), a database name, a user name, and the authentication method to be

2. `chunk-b8f76b4a73b8336b8d1f1b8849c85e4a8ab4c21a64f334f6319930eae60ad559` — pg-15; score=-0.079415, dense=0.753416, sparse=0.000000, rerank=-0.07941485941410065

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the next line by ending the line with a backslash. (Backslashes are not special except at the end of a line.) A record is made up of a number of fields which are separated by spaces and/or tabs. Fields can contain white space if the field value is double-quoted. Quoting one of the keywords in a database, user, or address field (e.g., all or replication ) makes the word lose its special meaning, and just match a database, user, or host with that name. Backslash line continuation applies even within quoted text or comments. Each record specifies a connection type, a client IP address range (if relevant for the connection type), a database name, a user name, and the authentication method to be used

3. `chunk-9bd3d326f2289bc6f598c4e5ee294f1306c635bfffc646636081e15072205b73` — pg-16; score=-0.463612, dense=0.724118, sparse=0.000000, rerank=-0.46361154317855835

> with .conf , processed in file name order (according to C locale rules, i.e., numbers before letters, and uppercase letters before lowercase ones). Files included by @ constructs are read as lists of names, which can be separated by either whitespace or commas. Comments are introduced by # , just as in pg_hba.conf , and nested @ constructs are allowed. Unless the file name following @ is an absolute path, it is taken to be relative to the directory containing the referencing file. Since the pg_hba.conf records are examined sequentially for each connection attempt, the order of the records is significant. Typically, earlier records will have tight connection match parameters and weaker authentication methods, while later records will have looser match parameters and stronger authentication methods. For example, one might wish to use trust authentication for local TCP/IP connections but require a password for remote TCP/IP connections. In this case a record specifying trust authentication for connections from 127.0.0.1 would appear before a record specifying password authentication for a wider range of allowed client IP addresses. The pg_hba.conf file is read on start-up and when the main server process receives a SIGHUP signal. If you edit the file on an active system, you will need to signal the postmaster (using pg_ctl reload , calling the SQL function pg_reload_conf() , or

## draft-8212c39cab5f00aa

Does bit_or include null inputs in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) Computes the bitwise OR of all non-null input values.
- (pg-16) Computes the bitwise OR of all non-null input values.

### Top three retrieved
1. `chunk-6560e13f63abd4e6e3a5451dfa771daf888b2a1912c309a93b2cd975764a7fdf` — pg-15; score=2.952335, dense=0.784275, sparse=0.000000, rerank=2.9523346424102783

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

2. `chunk-75d6f7845f32cf5b2105aaa47c1bcfbe416391ba5f4f973d1e0ba3d0e6d6e6ae` — pg-17; score=2.952335, dense=0.784275, sparse=0.000000, rerank=2.9523346424102783

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

3. `chunk-e96bdd39a5eea04e1d94cad496fb7a45adc7440d5c0425607a7e9fdaf887060f` — pg-16; score=2.952335, dense=0.784275, sparse=0.000000, rerank=2.9523346424102783

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

## draft-832a9b9cbacbceba

Which predefined role lets a user with database CREATE permission issue CREATE SUBSCRIPTION in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) pg_create_subscription | Allow users with CREATE permission on the database to issue CREATE SUBSCRIPTION.

### Top three retrieved
1. `chunk-70c178fe2cfd0ebb0602c6fabcb0ed0de35a7833edd44d6e0c69e8def0c75dbc` — pg-16; score=4.252891, dense=0.784970, sparse=0.000000, rerank=4.252890586853027

> Privileges Add predefined role pg_create_subscription with permission to create subscriptions (Robert Haas) § Allow subscriptions to not require passwords (Robert Haas) § § § This is accomplished with the option password_required=false . Simplify permissions for LOCK TABLE (Jeff Davis) § Previously a user's ability to perform LOCK TABLE at various lock levels was limited to the lock levels required by the commands they had permission to execute on the table. For example, someone with UPDATE permission could perform all lock levels except ACCESS SHARE , even though it was a lesser lock level. Now users can issue lesser lock levels if they already have permission for greater lock levels. Allow ALTER GROUP group_name ADD USER user_name to be performed with ADMIN OPTION (Robert Haas) § Previously CREATEROLE permission was required. Allow GRANT to use WITH ADMIN TRUE / FALSE syntax (Robert Haas) § Previously only the WITH ADMIN OPTION syntax was supported. Allow roles that create other roles to automatically inherit the new role's rights or the ability to SET ROLE to the new role (Robert Haas, Shi Yu) § § This is controlled by server variable createrole_self_grant . Prevent users from changing the default privileges of non-inherited roles (Robert Haas) § This is now only allowed for inherited roles. When granting role membership, require the granted-by role to be

2. `chunk-05092af7916b7eaea23cdfcfef52054aea8f6cf92aa7923df6915366eb018f6d` — pg-17; score=3.962882, dense=0.796061, sparse=0.000000, rerank=3.9628818035125732

> Predefined Roles PostgreSQL provides a set of predefined roles that provide access to certain, commonly needed, privileged capabilities and information. Administrators (including roles that have the CREATEROLE privilege) can GRANT these roles to users and/or other roles in their environment, providing those users with access to the specified capabilities and information. The predefined roles are described in Predefined Roles . Note that the specific permissions for each of the roles may change in the future as additional capabilities are added. Administrators should monitor the release notes for changes. The pg_monitor , pg_read_all_settings , pg_read_all_stats and pg_stat_scan_tables roles are intended to allow administrators to easily configure a role for the purpose of monitoring the database server. They grant a set of common privileges allowing the role to read various useful configuration settings, statistics and other system information normally restricted to superusers. The pg_database_owner role has one implicit, situation-dependent member, namely the owner of the current database. Like any role, it can own objects or receive grants of access privileges. Consequently, once pg_database_owner has rights within a template database, each owner of a database instantiated from that template will exercise those rights. pg_database_owner cannot be a member of any role, and it cannot have non-implicit members. Initially, this role owns the public schema, so each database owner governs local use of the

3. `chunk-a7aa45f40fd71eb1e9f356317180d4c0efd6b0b8df4f5155736ab8c09e2c9acd` — pg-16; score=3.962882, dense=0.796061, sparse=0.000000, rerank=3.9628818035125732

> Predefined Roles PostgreSQL provides a set of predefined roles that provide access to certain, commonly needed, privileged capabilities and information. Administrators (including roles that have the CREATEROLE privilege) can GRANT these roles to users and/or other roles in their environment, providing those users with access to the specified capabilities and information. The predefined roles are described in Predefined Roles . Note that the specific permissions for each of the roles may change in the future as additional capabilities are added. Administrators should monitor the release notes for changes. The pg_monitor , pg_read_all_settings , pg_read_all_stats and pg_stat_scan_tables roles are intended to allow administrators to easily configure a role for the purpose of monitoring the database server. They grant a set of common privileges allowing the role to read various useful configuration settings, statistics and other system information normally restricted to superusers. The pg_database_owner role has one implicit, situation-dependent member, namely the owner of the current database. Like any role, it can own objects or receive grants of access privileges. Consequently, once pg_database_owner has rights within a template database, each owner of a database instantiated from that template will exercise those rights. pg_database_owner cannot be a member of any role, and it cannot have non-implicit members. Initially, this role owns the public schema, so each database owner governs local use of the

## draft-8958779a0216b9a7

Are null inputs included in the array produced by json_agg_strict in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) json_agg_strict ( anyelement ) json jsonb_agg_strict ( anyelement ) jsonb Collects all the input values, skipping nulls, into a JSON array. Values are converted to JSON as per to_json or to_jsonb.

### Top three retrieved
1. `chunk-679daae5d0d418760b28931d366d44e55adf66c77381fee6f30803c4cdd5e7de` — pg-17; score=4.876092, dense=0.866582, sparse=0.000000, rerank=4.876091957092285

> there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given

2. `chunk-6560e13f63abd4e6e3a5451dfa771daf888b2a1912c309a93b2cd975764a7fdf` — pg-15; score=1.446535, dense=0.809231, sparse=0.000000, rerank=1.4465348720550537

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

3. `chunk-75d6f7845f32cf5b2105aaa47c1bcfbe416391ba5f4f973d1e0ba3d0e6d6e6ae` — pg-17; score=1.446535, dense=0.809231, sparse=0.000000, rerank=1.4465348720550537

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

## draft-9b1f37bc7842b40e

Must the ECDH exchange curve match the curve of the server's elliptic-curve key?

**Category:** text gap. **Reason:** No authorized, version-valid chunk contains a whole evidence quote.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key.

### Top three retrieved
1. `chunk-44ae8642eeb739124b0e979a05fa3720b46decde1b8dc94b7569fc7afd82a620` — pg-15; score=5.879607, dense=0.792794, sparse=0.000000, rerank=5.8796067237854

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

2. `chunk-7a0f69735558b64a65e491b53e5fec6add8b0f7386beb4e360def027cc853198` — pg-16; score=5.879607, dense=0.792794, sparse=0.000000, rerank=5.8796067237854

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

3. `chunk-d368baa59607597c650cea379d867c65561088b6e137e5cd4280087f49373d7e` — pg-17; score=5.879607, dense=0.792794, sparse=0.000000, rerank=5.8796067237854

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

## draft-a2cf6aa49912f6e7

When does bool_or return true in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bool_or ( boolean ) boolean Returns true if any non-null input value is true, otherwise false.
- (pg-16) bool_or ( boolean ) boolean Returns true if any non-null input value is true, otherwise false.

### Top three retrieved
1. `chunk-2361d4168e2d31e3ee1e448c83269bdb731d4b3a1263c8d1054f0852f5894ae9` — pg-15; score=4.512215, dense=0.756914, sparse=0.000000, rerank=4.512214660644531

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

2. `chunk-d36f151f4a60dbc8dc70ef0b26546747f657353b4e2bb40f420e2be9282008e8` — pg-17; score=4.512215, dense=0.756914, sparse=0.000000, rerank=4.512214660644531

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

3. `chunk-d9c5f9047dba883af7c556147a557304d8e7d9b21bca41af46a2d2caf4975e5b` — pg-16; score=4.512215, dense=0.756914, sparse=0.000000, rerank=4.512214660644531

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

## draft-d1b8f6b5aa7eddfa

When does bool_and return true in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bool_and ( boolean ) boolean Returns true if all non-null input values are true, otherwise false.
- (pg-16) bool_and ( boolean ) boolean Returns true if all non-null input values are true, otherwise false.

### Top three retrieved
1. `chunk-2361d4168e2d31e3ee1e448c83269bdb731d4b3a1263c8d1054f0852f5894ae9` — pg-15; score=4.434858, dense=0.757129, sparse=0.000000, rerank=4.434858322143555

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

2. `chunk-d36f151f4a60dbc8dc70ef0b26546747f657353b4e2bb40f420e2be9282008e8` — pg-17; score=4.434858, dense=0.757129, sparse=0.000000, rerank=4.434858322143555

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

3. `chunk-d9c5f9047dba883af7c556147a557304d8e7d9b21bca41af46a2d2caf4975e5b` — pg-16; score=4.434858, dense=0.757129, sparse=0.000000, rerank=4.434858322143555

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

## draft-d6a79ce1778ec9b4

What does array_upper(ARRAY[1,8,3,7], 1) return in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) array_upper ( anyarray, integer ) integer Returns the upper bound of the requested array dimension. array_upper(ARRAY[1,8,3,7], 1) 4
- (pg-16) array_upper ( anyarray, integer ) integer Returns the upper bound of the requested array dimension. array_upper(ARRAY[1,8,3,7], 1) 4

### Top three retrieved
1. `chunk-104d426a1193e7db222460ed4d92c9fe741ade6a56c17c04a0b3818af200a987` — pg-16; score=0.334718, dense=0.762730, sparse=0.000000, rerank=0.33471769094467163

> it will be true or false according to whether Perl would evaluate the returned value as true. Similar transformations are also performed for boolean query arguments and results of SPI queries performed inside the function ( Database Access from PL/Perl ). Perl can return PostgreSQL arrays as references to Perl arrays. Here is an example: Perl passes PostgreSQL arrays as a blessed PostgreSQL::InServer::ARRAY object. This object may be treated as an array reference or a string, allowing for backward compatibility with Perl code written for PostgreSQL versions below 9.1 to run. For example: Multidimensional arrays are represented as references to lower-dimensional arrays of references in a way common to every Perl programmer. Composite-type arguments are passed to the function as references to hashes. The keys of the hash are the attribute names of the composite type. Here is an example: A PL/Perl function can return a composite-type result using the same approach: return a reference to a hash that has the required attributes. For example: Any columns in the declared result data type that are not present in the hash will be returned as null values. Similarly, output arguments of procedures can be returned as a hash reference: PL/Perl functions can also return sets of either scalar or composite types. Usually you'll want to return rows one at a time,

2. `chunk-6f543e7df63755ce424965f9dee8a73f8ca986ae0c05349a8c1e459ff719db86` — pg-15; score=0.334718, dense=0.762730, sparse=0.000000, rerank=0.33471769094467163

> it will be true or false according to whether Perl would evaluate the returned value as true. Similar transformations are also performed for boolean query arguments and results of SPI queries performed inside the function ( Database Access from PL/Perl ). Perl can return PostgreSQL arrays as references to Perl arrays. Here is an example: Perl passes PostgreSQL arrays as a blessed PostgreSQL::InServer::ARRAY object. This object may be treated as an array reference or a string, allowing for backward compatibility with Perl code written for PostgreSQL versions below 9.1 to run. For example: Multidimensional arrays are represented as references to lower-dimensional arrays of references in a way common to every Perl programmer. Composite-type arguments are passed to the function as references to hashes. The keys of the hash are the attribute names of the composite type. Here is an example: A PL/Perl function can return a composite-type result using the same approach: return a reference to a hash that has the required attributes. For example: Any columns in the declared result data type that are not present in the hash will be returned as null values. Similarly, output arguments of procedures can be returned as a hash reference: PL/Perl functions can also return sets of either scalar or composite types. Usually you'll want to return rows one at a time,

3. `chunk-c123e43146f69b158b8091a4bc2ac2dda74e1cedbd49e71b11b24487aeb17008` — pg-17; score=0.334718, dense=0.762730, sparse=0.000000, rerank=0.33471769094467163

> it will be true or false according to whether Perl would evaluate the returned value as true. Similar transformations are also performed for boolean query arguments and results of SPI queries performed inside the function ( Database Access from PL/Perl ). Perl can return PostgreSQL arrays as references to Perl arrays. Here is an example: Perl passes PostgreSQL arrays as a blessed PostgreSQL::InServer::ARRAY object. This object may be treated as an array reference or a string, allowing for backward compatibility with Perl code written for PostgreSQL versions below 9.1 to run. For example: Multidimensional arrays are represented as references to lower-dimensional arrays of references in a way common to every Perl programmer. Composite-type arguments are passed to the function as references to hashes. The keys of the hash are the attribute names of the composite type. Here is an example: A PL/Perl function can return a composite-type result using the same approach: return a reference to a hash that has the required attributes. For example: Any columns in the declared result data type that are not present in the hash will be returned as null values. Similarly, output arguments of procedures can be returned as a hash reference: PL/Perl functions can also return sets of either scalar or composite types. Usually you'll want to return rows one at a time,

## draft-dadefc52fd565605

What OpenSSL curve name is the default for ssl_ecdh_curve?

**Category:** text gap. **Reason:** No authorized, version-valid chunk contains a whole evidence quote.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 .

### Top three retrieved
1. `chunk-44ae8642eeb739124b0e979a05fa3720b46decde1b8dc94b7569fc7afd82a620` — pg-15; score=7.971632, dense=0.861828, sparse=0.000000, rerank=7.971632480621338

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

2. `chunk-7a0f69735558b64a65e491b53e5fec6add8b0f7386beb4e360def027cc853198` — pg-16; score=7.971632, dense=0.861828, sparse=0.000000, rerank=7.971632480621338

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

3. `chunk-d368baa59607597c650cea379d867c65561088b6e137e5cd4280087f49373d7e` — pg-17; score=7.971632, dense=0.861828, sparse=0.000000, rerank=7.971632480621338

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

## draft-de8d404798f688a2

What limits the number of items requested by array_sample in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) array_sample ( array anyarray, n integer ) anyarray Returns an array of n items randomly selected from array. n may not exceed the length of array's first dimension.

### Top three retrieved
1. `chunk-189f79cd43bf3b9200a68762f0f093df1889cc3a10666ff2fde9798ada2cc723` — pg-16; score=1.347900, dense=0.730296, sparse=0.000000, rerank=1.3478996753692627

> Limitations The current limitations of PostgreSQL 's text search features are: The length of each lexeme must be less than 2 kilobytes The length of a tsvector (lexemes + positions) must be less than 1 megabyte The number of lexemes must be less than 2 64 Position values in tsvector must be greater than 0 and no more than 16,383 The match distance in a < N > (FOLLOWED BY) tsquery operator cannot be more than 16,384 No more than 256 positions per lexeme The number of nodes (lexemes + operators) in a tsquery must be less than 32,768 For comparison, the PostgreSQL 8.1 documentation contained 10,441 unique words, a total of 335,420 words, and the most frequent word postgresql was mentioned 6,127 times in 655 documents. Another example — the PostgreSQL mailing list archives contained 910,989 unique words with 57,491,343 lexemes in 461,020 messages.

2. `chunk-216aabf26cca528dd8cdfb634a5cef115b98d1d286ef17451aae9b87678988df` — pg-17; score=1.347900, dense=0.730296, sparse=0.000000, rerank=1.3478996753692627

> Limitations The current limitations of PostgreSQL 's text search features are: The length of each lexeme must be less than 2 kilobytes The length of a tsvector (lexemes + positions) must be less than 1 megabyte The number of lexemes must be less than 2 64 Position values in tsvector must be greater than 0 and no more than 16,383 The match distance in a < N > (FOLLOWED BY) tsquery operator cannot be more than 16,384 No more than 256 positions per lexeme The number of nodes (lexemes + operators) in a tsquery must be less than 32,768 For comparison, the PostgreSQL 8.1 documentation contained 10,441 unique words, a total of 335,420 words, and the most frequent word postgresql was mentioned 6,127 times in 655 documents. Another example — the PostgreSQL mailing list archives contained 910,989 unique words with 57,491,343 lexemes in 461,020 messages.

3. `chunk-b238d02663c6788fa1921a73b3ba7fb4f64b8edeabf96d80ad8f70aee3060df1` — pg-17; score=1.240303, dense=0.751028, sparse=0.000000, rerank=1.2403030395507812

> than a few processes do so then the system-wide limit can easily be exceeded. If you find this happening, and you do not want to alter the system-wide limit, you can set PostgreSQL 's max_files_per_process configuration parameter to limit the consumption of open files. Another kernel limit that may be of concern when supporting large numbers of client connections is the maximum socket connection queue length. If more than that many connection requests arrive within a very short period, some may get rejected before the PostgreSQL server can service the requests, with those clients receiving unhelpful connection failure errors such as Resource temporarily unavailable or Connection refused . The default queue length limit is 128 on many platforms. To raise it, adjust the appropriate kernel parameter via sysctl , then restart the PostgreSQL server. The parameter is variously named net.core.somaxconn on Linux, kern.ipc.soacceptqueue on newer FreeBSD, and kern.ipc.somaxconn on macOS and other BSD variants.

## draft-dee2728be3a4e6aa

What is the return type of count(*) in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) count ( * ) bigint Computes the number of input rows.
- (pg-16) count ( * ) bigint Computes the number of input rows.

### Top three retrieved
1. `chunk-52b35e2ee42522f90eb8018e157f91b6de9f3d9d53f53c5fc5a7c1f29cdc8e60` — pg-17; score=3.371120, dense=0.747265, sparse=0.000000, rerank=3.3711202144622803

> be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be converted to Python bytes using the respective Python built-ins, with the result being converted to bytea . For all other PostgreSQL return types, the return value is converted to a string using the Python built-in str , and the result is passed to the input function of the PostgreSQL data type. (If the Python value is a float , it is converted using the repr built-in instead of str , to avoid loss of precision.) Strings are automatically converted to the PostgreSQL server encoding when they are passed to PostgreSQL. For nonscalar data types, see below. Note that logical mismatches between the declared PostgreSQL return type and the Python data type of the actual return object are not flagged; the value will be converted in any case.

2. `chunk-6e11871f7bb170be80db72946a2d88a43b5961a0042df07e284884c4ec61ffb2` — pg-16; score=3.371120, dense=0.747265, sparse=0.000000, rerank=3.3711202144622803

> be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be converted to Python bytes using the respective Python built-ins, with the result being converted to bytea . For all other PostgreSQL return types, the return value is converted to a string using the Python built-in str , and the result is passed to the input function of the PostgreSQL data type. (If the Python value is a float , it is converted using the repr built-in instead of str , to avoid loss of precision.) Strings are automatically converted to the PostgreSQL server encoding when they are passed to PostgreSQL. For nonscalar data types, see below. Note that logical mismatches between the declared PostgreSQL return type and the Python data type of the actual return object are not flagged; the value will be converted in any case.

3. `chunk-8aaf18ea80f7b44e494c23b1741cf6c1f79a84dfdd32288dc5e1795159050947` — pg-15; score=3.371120, dense=0.747265, sparse=0.000000, rerank=3.3711202144622803

> be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be converted to Python bytes using the respective Python built-ins, with the result being converted to bytea . For all other PostgreSQL return types, the return value is converted to a string using the Python built-in str , and the result is passed to the input function of the PostgreSQL data type. (If the Python value is a float , it is converted using the repr built-in instead of str , to avoid loss of precision.) Strings are automatically converted to the PostgreSQL server encoding when they are passed to PostgreSQL. For nonscalar data types, see below. Note that logical mismatches between the declared PostgreSQL return type and the Python data type of the actual return object are not flagged; the value will be converted in any case.

## draft-df61a1a2e6822bb7

What does cardinality return for an empty array in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) cardinality ( anyarray ) integer Returns the total number of elements in the array, or 0 if the array is empty.
- (pg-16) cardinality ( anyarray ) integer Returns the total number of elements in the array, or 0 if the array is empty.

### Top three retrieved
1. `chunk-104d426a1193e7db222460ed4d92c9fe741ade6a56c17c04a0b3818af200a987` — pg-16; score=0.580477, dense=0.744907, sparse=0.000000, rerank=0.5804771184921265

> it will be true or false according to whether Perl would evaluate the returned value as true. Similar transformations are also performed for boolean query arguments and results of SPI queries performed inside the function ( Database Access from PL/Perl ). Perl can return PostgreSQL arrays as references to Perl arrays. Here is an example: Perl passes PostgreSQL arrays as a blessed PostgreSQL::InServer::ARRAY object. This object may be treated as an array reference or a string, allowing for backward compatibility with Perl code written for PostgreSQL versions below 9.1 to run. For example: Multidimensional arrays are represented as references to lower-dimensional arrays of references in a way common to every Perl programmer. Composite-type arguments are passed to the function as references to hashes. The keys of the hash are the attribute names of the composite type. Here is an example: A PL/Perl function can return a composite-type result using the same approach: return a reference to a hash that has the required attributes. For example: Any columns in the declared result data type that are not present in the hash will be returned as null values. Similarly, output arguments of procedures can be returned as a hash reference: PL/Perl functions can also return sets of either scalar or composite types. Usually you'll want to return rows one at a time,

2. `chunk-6f543e7df63755ce424965f9dee8a73f8ca986ae0c05349a8c1e459ff719db86` — pg-15; score=0.580477, dense=0.744907, sparse=0.000000, rerank=0.5804771184921265

> it will be true or false according to whether Perl would evaluate the returned value as true. Similar transformations are also performed for boolean query arguments and results of SPI queries performed inside the function ( Database Access from PL/Perl ). Perl can return PostgreSQL arrays as references to Perl arrays. Here is an example: Perl passes PostgreSQL arrays as a blessed PostgreSQL::InServer::ARRAY object. This object may be treated as an array reference or a string, allowing for backward compatibility with Perl code written for PostgreSQL versions below 9.1 to run. For example: Multidimensional arrays are represented as references to lower-dimensional arrays of references in a way common to every Perl programmer. Composite-type arguments are passed to the function as references to hashes. The keys of the hash are the attribute names of the composite type. Here is an example: A PL/Perl function can return a composite-type result using the same approach: return a reference to a hash that has the required attributes. For example: Any columns in the declared result data type that are not present in the hash will be returned as null values. Similarly, output arguments of procedures can be returned as a hash reference: PL/Perl functions can also return sets of either scalar or composite types. Usually you'll want to return rows one at a time,

3. `chunk-c123e43146f69b158b8091a4bc2ac2dda74e1cedbd49e71b11b24487aeb17008` — pg-17; score=0.580477, dense=0.744907, sparse=0.000000, rerank=0.5804771184921265

> it will be true or false according to whether Perl would evaluate the returned value as true. Similar transformations are also performed for boolean query arguments and results of SPI queries performed inside the function ( Database Access from PL/Perl ). Perl can return PostgreSQL arrays as references to Perl arrays. Here is an example: Perl passes PostgreSQL arrays as a blessed PostgreSQL::InServer::ARRAY object. This object may be treated as an array reference or a string, allowing for backward compatibility with Perl code written for PostgreSQL versions below 9.1 to run. For example: Multidimensional arrays are represented as references to lower-dimensional arrays of references in a way common to every Perl programmer. Composite-type arguments are passed to the function as references to hashes. The keys of the hash are the attribute names of the composite type. Here is an example: A PL/Perl function can return a composite-type result using the same approach: return a reference to a hash that has the required attributes. For example: Any columns in the declared result data type that are not present in the hash will be returned as null values. Similarly, output arguments of procedures can be returned as a hash reference: PL/Perl functions can also return sets of either scalar or composite types. Usually you'll want to return rows one at a time,
