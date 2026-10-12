# Worst test failures: scope-explicit

DEV-selected system or fixed DEV-derived combined arm. Showing 30 of 50 failures.
Ranking: all-quotes@10, Recall@10, nDCG@10, MRR ascending; then ID.

## draft-2f27ea088c1b07ce

What happens if json_object_agg_unique receives duplicate keys in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) json_object_agg_unique ( key "any", value "any" ) json jsonb_object_agg_unique ( key "any", value "any" ) jsonb Collects all the key/value pairs into a JSON object. Key arguments are coerced to text; value arguments are converted as per to_json or to_jsonb. Values can be null, but keys cannot. If there is a duplicate key an error is thrown.

### Top three retrieved
1. `chunk-38ef0f1957b75f4f1fb69fbc57358be1ea419b7711492183b41078360f4ddf84` — pg-16; score=1.413758, dense=0.759116, sparse=0.000000, rerank=1.4137579202651978

> Parameters UNIQUE Causes the system to check for duplicate values in the table when the index is created (if data already exist) and each time data is added. Attempts to insert or update data which would result in duplicate entries will generate an error. Additional restrictions apply when unique indexes are applied to partitioned tables; see CREATE TABLE . CONCURRENTLY When this option is used, PostgreSQL will build the index without taking any locks that prevent concurrent inserts, updates, or deletes on the table; whereas a standard index build locks out writes (but not reads) on the table until it's done. There are several caveats to be aware of when using this option — see Building Indexes Concurrently below. For temporary tables, CREATE INDEX is always non-concurrent, as no other session can access them, and non-concurrent index creation is cheaper. IF NOT EXISTS Do not throw an error if a relation with the same name already exists. A notice is issued in this case. Note that there is no guarantee that the existing index is anything like the one that would have been created. Index name is required when IF NOT EXISTS is specified. INCLUDE The optional INCLUDE clause specifies a list of columns which will be included in the index as non-key columns. A non-key column cannot be used

2. `chunk-b93a1022182b07cdb0235f89cc3f25dbf75f563acbe59c22e19a24a2cd55d18c` — pg-16; score=1.413758, dense=0.759116, sparse=0.000000, rerank=1.4137579202651978

> CREATE INDEX 7 SQL - Language Statements CREATE INDEX define a new index

3. `chunk-ecc3d9d8222bb76d2b65fc0a87cf875bb75d063824bea57052bf74fe8b4d57cc` — pg-16; score=1.269969, dense=0.000000, sparse=2.000000, rerank=1.2699694633483887

> a significant advantage. Because the json type stores an exact copy of the input text, it will preserve semantically-insignificant white space between tokens, as well as the order of keys within JSON objects. Also, if a JSON object within the value contains the same key more than once, all the key/value pairs are kept. (The processing functions consider the last value as the operative one.) By contrast, jsonb does not preserve white space, does not preserve the order of object keys, and does not keep duplicate object keys. If duplicate keys are specified in the input, only the last value is kept. In general, most applications should prefer to store JSON data as jsonb , unless there are quite specialized needs, such as legacy assumptions about ordering of object keys. RFC 7159 specifies that JSON strings should be encoded in UTF8. It is therefore not possible for the JSON types to conform rigidly to the JSON specification unless the database encoding is UTF8. Attempts to directly include characters that cannot be represented in the database encoding will fail; conversely, characters that can be represented in the database encoding but not in UTF8 will be allowed. RFC 7159 permits JSON strings to contain Unicode escape sequences denoted by \u XXXX . In the input function for the json type, Unicode escapes

## draft-33d8c19a2a6a932d

What is the maximum size of one pg_largeobject.data value?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) data bytea Actual data stored in the large object. This will never be more than LOBLKSIZE bytes and might be less.

### Top three retrieved
1. `chunk-006cbb7bc5add7256d761b85457c7544eeeafa8e73e18e97b992d80c2cba1080` — pg-15; score=3.412874, dense=0.809760, sparse=0.600000, rerank=3.412874221801758

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

2. `chunk-e30d9056d0a38876d1e9396379b37ac829e392467bead372d39ffe9f0aa36026` — pg-15; score=3.412874, dense=0.809760, sparse=0.600000, rerank=3.412874221801758

> System Catalogs The system catalogs are the place where a relational database management system stores schema metadata, such as information about tables and columns, and internal bookkeeping information. PostgreSQL 's system catalogs are regular tables. You can drop and recreate the tables, add columns, insert and update values, and severely mess up your system that way. Normally, one should not change the system catalogs by hand, there are normally SQL commands to do that. (For example, CREATE DATABASE inserts a row into the pg_database catalog — and actually creates the database on disk.) There are some exceptions for particularly esoteric operations, but many of those have been made available as SQL commands over time, and so the need for direct manipulation of the system catalogs is ever decreasing.

3. `chunk-c4f8414130493235ad3be27b13f774e78ee53c75fa60af89587bd5557fb290dc` — pg-15; score=2.920619, dense=0.735928, sparse=0.000000, rerank=2.920619487762451

> Introduction All large objects are stored in a single system table named pg_largeobject . Each large object also has an entry in the system table pg_largeobject_metadata . Large objects can be created, modified, and deleted using a read/write API that is similar to standard operations on files. PostgreSQL also supports a storage system called TOAST , which automatically stores values larger than a single database page into a secondary storage area per table. This makes the large object facility partially obsolete. One remaining advantage of the large object facility is that it allows values up to 4 TB in size, whereas TOAST ed fields can be at most 1 GB. Also, reading and updating portions of a large object can be done efficiently, while most operations on a TOAST ed field will read or write the whole value as a unit.

## draft-3abee3e4240c30d3

What is the default work_mem in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes. The default value is four megabytes ( 4MB ).
- (pg-16) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes. The default value is four megabytes ( 4MB ).

### Top three retrieved
1. `chunk-fdc50dcaf183bb0e851ed735ae8d77b5aa556f5eda191678e6665f20f7a5b7cc` — pg-15; score=3.210735, dense=0.796697, sparse=0.400000, rerank=3.2107348442077637

> -S work-mem Specifies the base amount of memory to be used by sorts and hash tables before resorting to temporary disk files. See the description of the work_mem configuration parameter in Memory . -V --version Print the postgres version and exit. -- name = value Sets a named run-time parameter; a shorter form of -c . --describe-config This option dumps out the server's internal configuration variables, descriptions, and defaults in tab-delimited COPY format. It is designed primarily for use by administration tools. -? --help Show help about postgres command line arguments, and exit.

2. `chunk-79b1260d4447fe168e82c36568083beeccd6da96f67c70eca3a9b502d7c0aec7` — pg-15; score=3.210735, dense=0.796697, sparse=0.400000, rerank=3.2107348442077637

> Options postgres accepts the following command-line arguments. For a detailed discussion of the options consult Server Configuration . You can save typing most of these options by setting up a configuration file. Some (safe) options can also be set from the connecting client in an application-dependent way to apply only for that session. For example, if the environment variable PGOPTIONS is set, then libpq -based clients will pass that string to the server, which will interpret it as postgres command-line options.

3. `chunk-0e88e248640413eaa378907aed8922a944d18385436df3a7a1eef856612a138f` — pg-15; score=3.048995, dense=0.741561, sparse=0.000000, rerank=3.048995018005371

> Examples To start postgres in the background using default values, type: To start postgres with a specific port, e.g., 1234: To connect to this server using psql , specify this port with the -p option: or set the environment variable PGPORT : Named run-time parameters can be set in either of these styles: Either form overrides whatever setting might exist for work_mem in postgresql.conf . Notice that underscores in parameter names can be written as either underscore or dash on the command line. Except for short-term experiments, it's probably better practice to edit the setting in postgresql.conf than to rely on a command-line switch to set a parameter.

## draft-3bbf02c4e418a086

Which bitwise aggregate can checksum an unordered set of values in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bit_xor ( smallint ) smallint bit_xor ( integer ) integer bit_xor ( bigint ) bigint bit_xor ( bit ) bit Computes the bitwise exclusive OR of all non-null input values. Can be useful as a checksum for an unordered set of values.
- (pg-16) bit_xor ( smallint ) smallint bit_xor ( integer ) integer bit_xor ( bigint ) bigint bit_xor ( bit ) bit Computes the bitwise exclusive OR of all non-null input values. Can be useful as a checksum for an unordered set of values.

### Top three retrieved
1. `chunk-dbebf0e79902d7d2b7ef8662c9576fc123c51adfd48a6155d28ae3567614339d` — pg-15; score=0.421528, dense=0.760520, sparse=0.000000, rerank=0.42152824997901917

> (Tom Lane) § § Parsing of these query structures did not check for overflow of 16-bit fields, so that construction of an invalid query tree was possible. This can crash the server when executing the query. The PostgreSQL Project thanks Xint Code for reporting this problem. (CVE-2026-6473) Guard against overly long values of contrib/ltree 's lquery type (Michael Paquier) § Values with more than 64K items caused internal overflows, potentially resulting in stack smashes or wrong answers. The PostgreSQL Project thanks Vergissmeinnicht, A1ex, and Jihe Wang for reporting this problem. (CVE-2026-6473) Prevent SQL injection and buffer overruns in contrib/spi (Nathan Bossart) § check_foreign_key() was insufficiently careful about quoting key values, and also used fixed-length buffers for constructing queries. While this module is only meant as example code, it still shouldn't contain such dangerous errors. The PostgreSQL Project thanks Nikolay Samokhvalov for reporting this problem. (CVE-2026-6637) Check for nondeterministic collations before assuming that an equality condition on a collatable type implies uniqueness (Richard Guo) § § Numerous planner optimizations assume that, for example, at most one table row can satisfy WHERE x = 'abc' if there is a unique index on x . However this conclusion is unsafe in general if the index and the WHERE clause have different collations attached. It is safe when both collations are deterministic, because that

2. `chunk-0a2bc8bc20369b3ac4b40204c954bb758e0c94bb79066a8aec365a860ac60780` — pg-15; score=-0.723435, dense=0.773352, sparse=0.000000, rerank=-0.723434567451477

> , json_object_agg , jsonb_object_agg , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given to these aggregates. Users accustomed to working with other SQL database management systems might be disappointed by the performance of the count aggregate when it is applied to the entire table. A query like: will require effort proportional to the size of the table: PostgreSQL will

3. `chunk-0788edefc26326a08ecb7ca41245f22bf06fca4c8fd9ea0bce85a6ff81b703e6` — pg-15; score=-0.723435, dense=0.773352, sparse=0.000000, rerank=-0.723434567451477

> Functions and Operators PostgreSQL provides a large number of functions and operators for the built-in data types. This chapter describes most of them, although additional special-purpose functions appear in relevant sections of the manual. Users can also define their own functions and operators, as described in Server Programming . The psql commands \df and \do can be used to list all available functions and operators, respectively. The notation used throughout this chapter to describe the argument and result data types of a function or operator is like this: which says that the function repeat takes one text and one integer argument and returns a result of type text. The right arrow is also used to indicate the result of an example, thus: If you are concerned about portability then note that most of the functions and operators described in this chapter, with the exception of the most trivial arithmetic and comparison operators and some explicitly marked functions, are not specified by the SQL standard. Some of this extended functionality is present in other SQL database management systems, and in many cases this functionality is compatible and consistent between the various implementations.

## draft-51a8ac7c7fbf24a6

What does amtype = i mean in pg_am?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) amtype char t = table (including materialized views), i = index.

### Top three retrieved
1. `chunk-e146379eff239c4647bc09f7f2fb4d6f5a5451bf4e032a39a53f2658a3578540` — pg-15; score=3.652203, dense=0.715740, sparse=0.000000, rerank=3.65220308303833

> SELECT am.amname AS index_method, opc.opcname AS opclass_name, opc.opcintype::regtype AS indexed_type, opc.opcdefault AS is_default FROM pg_am am, pg_opclass opc WHERE opc.opcmethod = am.oid ORDER BY index_method, opclass_name;

2. `chunk-aff1fe360742d2293515bf0cce22b7d9d90201670ddaea45a49b7faf6d1c564c` — pg-15; score=3.652203, dense=0.715740, sparse=0.000000, rerank=3.65220308303833

> Indexes Indexes are a common way to enhance database performance. An index allows the database server to find and retrieve specific rows much faster than it could do without an index. But indexes also add overhead to the database system as a whole, so they should be used sensibly.

3. `chunk-c8440fc9175b26c5420ba3724818356cb4a32b4e57f4dd6ade22149b5d62c066` — pg-15; score=1.114808, dense=0.000000, sparse=1.100000, rerank=1.1148078441619873

> test=# SELECT bt_index_check(index => c.oid, heapallindexed => i.indisunique), c.relname, c.relpages FROM pg_index i JOIN pg_opclass op ON i.indclass[0] = op.oid JOIN pg_am am ON op.opcmethod = am.oid JOIN pg_class c ON i.indexrelid = c.oid JOIN pg_namespace n ON c.relnamespace = n.oid WHERE am.amname = 'btree' AND n.nspname = 'pg_catalog' -- Don't check temp tables, which may be from another session: AND c.relpersistence != 't' -- Function may throw an error when this is omitted: AND c.relkind = 'i' AND i.indisready AND i.indisvalid ORDER BY c.relpages DESC LIMIT 10; bt_index_check | relname | relpages ----------------+---------------------------------+---------- | pg_depend_reference_index | 43 | pg_depend_depender_index | 40 | pg_proc_proname_args_nsp_index | 31 | pg_description_o_c_o_index | 21 | pg_attribute_relid_attnam_index | 14 | pg_proc_oid_index | 10 | pg_attribute_relid_attnum_index | 9 | pg_amproc_fam_proc_index | 5 | pg_amop_opr_fam_index | 5 | pg_amop_fam_strat_index | 5 (10 rows)

## draft-7aba123f3dd8b9f6

What does defaclnamespace = 0 indicate in pg_default_acl?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-16) defaclnamespace oid (references pg_namespace.oid) The OID of the namespace associated with this entry, or zero if none

### Top three retrieved
1. `chunk-da6d3c3daae1d20227cac5402abe455ddc35b88b4b474f42af8724ea34dec1f5` — pg-16; score=6.917902, dense=0.768639, sparse=0.700000, rerank=6.917901515960693

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

2. `chunk-40fe6e17a06ad7075818645abfb72a36d073f1bc4153e419a185c3ff93554203` — pg-16; score=6.917902, dense=0.768639, sparse=0.700000, rerank=6.917901515960693

> System Catalogs The system catalogs are the place where a relational database management system stores schema metadata, such as information about tables and columns, and internal bookkeeping information. PostgreSQL 's system catalogs are regular tables. You can drop and recreate the tables, add columns, insert and update values, and severely mess up your system that way. Normally, one should not change the system catalogs by hand, there are normally SQL commands to do that. (For example, CREATE DATABASE inserts a row into the pg_database catalog — and actually creates the database on disk.) There are some exceptions for particularly esoteric operations, but many of those have been made available as SQL commands over time, and so the need for direct manipulation of the system catalogs is ever decreasing.

3. `chunk-76f20191133b9227d3e88323f80973b7e5472592be797003712485a8b4f93cb2` — pg-16; score=-0.914256, dense=0.737697, sparse=0.000000, rerank=-0.9142557382583618

> Values: 0, 1 Default: 0 Applies to: pgp_sym_decrypt, pgp_pub_decrypt

## draft-7f9ef8ca7db593fa

What is the customary filename selected by hba_file?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) hba_file ( string ) Specifies the configuration file for host-based authentication (customarily called pg_hba.conf ).

### Top three retrieved
1. `chunk-3d24696d8bf22df17c9d499baa02c736f092adc5f797dfb01435aef4d45d73c5` — pg-17; score=-0.774003, dense=0.733305, sparse=1.000000, rerank=-0.7740029692649841

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The pg_hba.conf file is read on start-up and when the main server process receives a SIGHUP signal. If you edit the file on an active system, you will need to signal the postmaster (using pg_ctl reload , calling the SQL function pg_reload_conf() , or using kill -HUP ) to make it re-read the file. The preceding statement is not true on Microsoft Windows: there, any changes in the pg_hba.conf file are immediately applied by subsequent new connections. The system view pg_hba_file_rules can be helpful for pre-testing changes to the pg_hba.conf file, or for diagnosing problems if loading of the file did not have the desired effects. Rows in the view with non-null error fields indicate problems in the corresponding lines of the file. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the

2. `chunk-6d11dcabd85b4859c1ef2831d85f0ebf206ddb5c541f06bb2998682c2d61d75c` — pg-17; score=-0.774003, dense=0.733305, sparse=1.000000, rerank=-0.7740029692649841

> Client Authentication When a client application connects to the database server, it specifies which PostgreSQL database user name it wants to connect as, much the same way one logs into a Unix computer as a particular user. Within the SQL environment the active database user name determines access privileges to database objects — see Database Roles for more information. Therefore, it is essential to restrict which database users can connect. As explained in Database Roles , PostgreSQL actually does privilege management in terms of roles . In this chapter, we consistently use database user to mean role with the LOGIN privilege . Authentication is the process by which the database server establishes the identity of the client, and by extension determines whether the client application (or the user who runs the client application) is permitted to connect with the database user name that was requested. PostgreSQL offers a number of different client authentication methods. The method used to authenticate a particular client connection can be selected on the basis of (client) host address, database, and user. PostgreSQL database user names are logically separate from user names of the operating system in which the server runs. If all the users of a particular server also have accounts on the server's machine, it makes sense to assign database user names that match

3. `chunk-9a10a63e6660c41d9aa74fc4c62bb575f3ea15edf0d0b797872b8b5fd939c3aa` — pg-17; score=-0.926634, dense=0.701140, sparse=0.400000, rerank=-0.9266339540481567

> pg_hba_file_rules The view pg_hba_file_rules provides a summary of the contents of the client authentication configuration file, pg_hba.conf . A row appears in this view for each non-empty, non-comment line in the file, with annotations indicating whether the rule could be applied successfully. This view can be helpful for checking whether planned changes in the authentication configuration file will work, or for diagnosing a previous failure. Note that this view reports on the current contents of the file, not on what was last loaded by the server. By default, the pg_hba_file_rules view can be read only by superusers. Usually, a row reflecting an incorrect entry will have values for only the line_number and error fields. See Client Authentication for more information about client authentication configuration.

## draft-832a9b9cbacbceba

Which predefined role lets a user with database CREATE permission issue CREATE SUBSCRIPTION in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) pg_create_subscription | Allow users with CREATE permission on the database to issue CREATE SUBSCRIPTION.

### Top three retrieved
1. `chunk-70c178fe2cfd0ebb0602c6fabcb0ed0de35a7833edd44d6e0c69e8def0c75dbc` — pg-16; score=4.252891, dense=0.784970, sparse=1.400000, rerank=4.252890586853027

> Privileges Add predefined role pg_create_subscription with permission to create subscriptions (Robert Haas) § Allow subscriptions to not require passwords (Robert Haas) § § § This is accomplished with the option password_required=false . Simplify permissions for LOCK TABLE (Jeff Davis) § Previously a user's ability to perform LOCK TABLE at various lock levels was limited to the lock levels required by the commands they had permission to execute on the table. For example, someone with UPDATE permission could perform all lock levels except ACCESS SHARE , even though it was a lesser lock level. Now users can issue lesser lock levels if they already have permission for greater lock levels. Allow ALTER GROUP group_name ADD USER user_name to be performed with ADMIN OPTION (Robert Haas) § Previously CREATEROLE permission was required. Allow GRANT to use WITH ADMIN TRUE / FALSE syntax (Robert Haas) § Previously only the WITH ADMIN OPTION syntax was supported. Allow roles that create other roles to automatically inherit the new role's rights or the ability to SET ROLE to the new role (Robert Haas, Shi Yu) § § This is controlled by server variable createrole_self_grant . Prevent users from changing the default privileges of non-inherited roles (Robert Haas) § This is now only allowed for inherited roles. When granting role membership, require the granted-by role to be

2. `chunk-56275052bea1307b23381f915788da6584049f9177f8ee27faf000885e4c3105` — pg-16; score=4.252891, dense=0.784970, sparse=1.400000, rerank=4.252890586853027

> Changes Below you will find a detailed account of the changes between PostgreSQL 16 and the previous major release.

3. `chunk-a7aa45f40fd71eb1e9f356317180d4c0efd6b0b8df4f5155736ab8c09e2c9acd` — pg-16; score=3.962882, dense=0.796061, sparse=0.000000, rerank=3.9628818035125732

> Predefined Roles PostgreSQL provides a set of predefined roles that provide access to certain, commonly needed, privileged capabilities and information. Administrators (including roles that have the CREATEROLE privilege) can GRANT these roles to users and/or other roles in their environment, providing those users with access to the specified capabilities and information. The predefined roles are described in Predefined Roles . Note that the specific permissions for each of the roles may change in the future as additional capabilities are added. Administrators should monitor the release notes for changes. The pg_monitor , pg_read_all_settings , pg_read_all_stats and pg_stat_scan_tables roles are intended to allow administrators to easily configure a role for the purpose of monitoring the database server. They grant a set of common privileges allowing the role to read various useful configuration settings, statistics and other system information normally restricted to superusers. The pg_database_owner role has one implicit, situation-dependent member, namely the owner of the current database. Like any role, it can own objects or receive grants of access privileges. Consequently, once pg_database_owner has rights within a template database, each owner of a database instantiated from that template will exercise those rights. pg_database_owner cannot be a member of any role, and it cannot have non-implicit members. Initially, this role owns the public schema, so each database owner governs local use of the

## draft-9b1f37bc7842b40e

Must the ECDH exchange curve match the curve of the server's elliptic-curve key?

**Category:** text gap. **Reason:** No authorized, version-valid chunk contains a whole evidence quote.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key.

### Top three retrieved
1. `chunk-d368baa59607597c650cea379d867c65561088b6e137e5cd4280087f49373d7e` — pg-17; score=5.879607, dense=0.792794, sparse=0.600000, rerank=5.879607200622559

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

2. `chunk-59bd804ec9a678648324bd35b29a321ce557bd5e3460d627d8d9f8848eb19a4c` — pg-17; score=5.879607, dense=0.792794, sparse=0.600000, rerank=5.879607200622559

> Server Configuration There are many configuration parameters that affect the behavior of the database system. In the first section of this chapter we describe how to interact with configuration parameters. The subsequent sections discuss each parameter in detail.

3. `chunk-1516438718b7513bfd977d04dd2afed0941fe3834c835381deba48e8a702508a` — pg-17; score=1.917000, dense=0.735613, sparse=0.700000, rerank=1.9169995784759521

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

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

2. `chunk-478634341373bb10d8018586815c99956a1caea0f825a6b173898968428577b5` — pg-15; score=4.512215, dense=0.756914, sparse=0.000000, rerank=4.512214660644531

> Data Values Generally speaking, the aim of PL/Python is to provide a natural mapping between the PostgreSQL and the Python worlds. This informs the data mapping rules described below.

3. `chunk-8aaf18ea80f7b44e494c23b1741cf6c1f79a84dfdd32288dc5e1795159050947` — pg-15; score=4.021094, dense=0.756446, sparse=0.000000, rerank=4.021093845367432

> be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be converted to Python bytes using the respective Python built-ins, with the result being converted to bytea . For all other PostgreSQL return types, the return value is converted to a string using the Python built-in str , and the result is passed to the input function of the PostgreSQL data type. (If the Python value is a float , it is converted using the repr built-in instead of str , to avoid loss of precision.) Strings are automatically converted to the PostgreSQL server encoding when they are passed to PostgreSQL. For nonscalar data types, see below. Note that logical mismatches between the declared PostgreSQL return type and the Python data type of the actual return object are not flagged; the value will be converted in any case.

## draft-d1b8f6b5aa7eddfa

When does bool_and return true in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bool_and ( boolean ) boolean Returns true if all non-null input values are true, otherwise false.
- (pg-16) bool_and ( boolean ) boolean Returns true if all non-null input values are true, otherwise false.

### Top three retrieved
1. `chunk-2361d4168e2d31e3ee1e448c83269bdb731d4b3a1263c8d1054f0852f5894ae9` — pg-15; score=4.434857, dense=0.757129, sparse=0.000000, rerank=4.434857368469238

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

2. `chunk-478634341373bb10d8018586815c99956a1caea0f825a6b173898968428577b5` — pg-15; score=4.434857, dense=0.757129, sparse=0.000000, rerank=4.434857368469238

> Data Values Generally speaking, the aim of PL/Python is to provide a natural mapping between the PostgreSQL and the Python worlds. This informs the data mapping rules described below.

3. `chunk-8aaf18ea80f7b44e494c23b1741cf6c1f79a84dfdd32288dc5e1795159050947` — pg-15; score=3.869199, dense=0.748768, sparse=0.000000, rerank=3.869198799133301

> be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be converted to Python bytes using the respective Python built-ins, with the result being converted to bytea . For all other PostgreSQL return types, the return value is converted to a string using the Python built-in str , and the result is passed to the input function of the PostgreSQL data type. (If the Python value is a float , it is converted using the repr built-in instead of str , to avoid loss of precision.) Strings are automatically converted to the PostgreSQL server encoding when they are passed to PostgreSQL. For nonscalar data types, see below. Note that logical mismatches between the declared PostgreSQL return type and the Python data type of the actual return object are not flagged; the value will be converted in any case.

## draft-dadefc52fd565605

What OpenSSL curve name is the default for ssl_ecdh_curve?

**Category:** text gap. **Reason:** No authorized, version-valid chunk contains a whole evidence quote.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 .

### Top three retrieved
1. `chunk-d368baa59607597c650cea379d867c65561088b6e137e5cd4280087f49373d7e` — pg-17; score=7.971632, dense=0.861828, sparse=1.300000, rerank=7.971632480621338

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

2. `chunk-59bd804ec9a678648324bd35b29a321ce557bd5e3460d627d8d9f8848eb19a4c` — pg-17; score=7.971632, dense=0.861828, sparse=1.300000, rerank=7.971632480621338

> Server Configuration There are many configuration parameters that affect the behavior of the database system. In the first section of this chapter we describe how to interact with configuration parameters. The subsequent sections discuss each parameter in detail.

3. `chunk-1516438718b7513bfd977d04dd2afed0941fe3834c835381deba48e8a702508a` — pg-17; score=3.267294, dense=0.768774, sparse=1.100000, rerank=3.267294406890869

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

## draft-dee2728be3a4e6aa

What is the return type of count(*) in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) count ( * ) bigint Computes the number of input rows.
- (pg-16) count ( * ) bigint Computes the number of input rows.

### Top three retrieved
1. `chunk-8aaf18ea80f7b44e494c23b1741cf6c1f79a84dfdd32288dc5e1795159050947` — pg-15; score=3.371118, dense=0.747265, sparse=0.000000, rerank=3.3711180686950684

> be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be converted to Python bytes using the respective Python built-ins, with the result being converted to bytea . For all other PostgreSQL return types, the return value is converted to a string using the Python built-in str , and the result is passed to the input function of the PostgreSQL data type. (If the Python value is a float , it is converted using the repr built-in instead of str , to avoid loss of precision.) Strings are automatically converted to the PostgreSQL server encoding when they are passed to PostgreSQL. For nonscalar data types, see below. Note that logical mismatches between the declared PostgreSQL return type and the Python data type of the actual return object are not flagged; the value will be converted in any case.

2. `chunk-478634341373bb10d8018586815c99956a1caea0f825a6b173898968428577b5` — pg-15; score=3.371118, dense=0.747265, sparse=0.000000, rerank=3.3711180686950684

> Data Values Generally speaking, the aim of PL/Python is to provide a natural mapping between the PostgreSQL and the Python worlds. This informs the data mapping rules described below.

3. `chunk-0d7c683bc660a140e94b2775305df3ece1d6ae7a6498b2d0c1999e3eb62a7a0b` — pg-15; score=1.211858, dense=0.745057, sparse=0.600000, rerank=1.2118580341339111

> LIMIT Clause The LIMIT clause consists of two independent sub-clauses: The parameter count specifies the maximum number of rows to return, while start specifies the number of rows to skip before starting to return rows. When both are specified, start rows are skipped before starting to count the count rows to be returned. If the count expression evaluates to NULL, it is treated as LIMIT ALL , i.e., no limit. If start evaluates to NULL, it is treated the same as OFFSET 0 . SQL:2008 introduced a different syntax to achieve the same result, which PostgreSQL also supports. It is: In this syntax, the start or count value is required by the standard to be a literal constant, a parameter, or a variable name; as a PostgreSQL extension, other expressions are allowed, but will generally need to be enclosed in parentheses to avoid ambiguity. If count is omitted in a FETCH clause, it defaults to 1. The WITH TIES option is used to return any additional rows that tie for the last place in the result set according to the ORDER BY clause; ORDER BY is mandatory in this case, and SKIP LOCKED is not allowed. ROW and ROWS as well as FIRST and NEXT are noise words that don't influence the effects of these clauses. According to the standard,

## draft-e62aee50eb83cb03

What does pg_inherits.inhdetachpending = true mean?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) inhdetachpending bool true for a partition that is in the process of being detached; false otherwise.

### Top three retrieved
1. `chunk-a29517a4a4c481c0d0e5aa3199049f2306fe0205ba20d06425ac217a13575f75` — pg-17; score=1.738606, dense=0.709355, sparse=0.000000, rerank=1.7386062145233154

> pg_inherits The catalog pg_inherits records information about table and index inheritance hierarchies. There is one entry for each direct parent-child table or index relationship in the database. (Indirect inheritance can be determined by following chains of entries.)

2. `chunk-f8d711506ea39112552fc5f8ad3775af2785221902115c8367b2caf63d7271ac` — pg-17; score=1.738606, dense=0.709355, sparse=0.000000, rerank=1.7386062145233154

> System Catalogs The system catalogs are the place where a relational database management system stores schema metadata, such as information about tables and columns, and internal bookkeeping information. PostgreSQL 's system catalogs are regular tables. You can drop and recreate the tables, add columns, insert and update values, and severely mess up your system that way. Normally, one should not change the system catalogs by hand, there are normally SQL commands to do that. (For example, CREATE DATABASE inserts a row into the pg_database catalog — and actually creates the database on disk.) There are some exceptions for particularly esoteric operations, but many of those have been made available as SQL commands over time, and so the need for direct manipulation of the system catalogs is ever decreasing.

3. `chunk-ca87fdb18481a35c0c77f68ad06f6477aa111c52b0fce82359dffcd0c89708d7` — pg-17; score=-1.174207, dense=0.000000, sparse=1.500000, rerank=-1.1742067337036133

> | Column Type Description | | --- | | indexrelid oid (references pg_class.oid) The OID of the pg_class entry for this index | | indrelid oid (references pg_class.oid) The OID of the pg_class entry for the table this index is for | | indnatts int2 The total number of columns in the index (duplicates pg_class.relnatts); this number includes both key and included attributes | | indnkeyatts int2 The number of key columns in the index, not counting any included columns, which are merely stored and do not participate in the index semantics | | indisunique bool If true, this is a unique index | | indnullsnotdistinct bool This value is only used for unique indexes. If false, this unique index will consider null values distinct (so the index can contain multiple null values in a column, the default PostgreSQL behavior). If it is true, it will consider null values to be equal (so the index can only contain one null value in a column). | | indisprimary bool If true, this index represents the primary key of the table (indisunique should always be true when this is true) | | indisexclusion bool If true, this index supports an exclusion constraint | | indimmediate bool If true, the uniqueness check is enforced immediately on insertion (irrelevant if indisunique is not true) | | indisclustered bool If true, the table was last clustered on this index | | indisvalid bool If true, the index is currently valid for queries. False means the index is possibly incomplete: it must still be modified by INSERT/UPDATE operations, but it cannot safely be used for queries. If it is unique, the uniqueness property is not guaranteed true either. | | indcheckxmin bool If true, queries must not use the index until the xmin of this pg_index row is below their TransactionXmin event horizon, because the table may contain broken HOT chains with incompatible rows that they can see | | indisready bool If true, the index is currently ready for inserts. False means the index must be ignored by INSERT/UPDATE operations. | | indislive bool If false, the index is in process of being dropped, and should be ignored for all purposes (including HOT-safety decisions) | | indisreplident bool If true this index has been chosen as replica identity using ALTER TABLE ... REPLICA IDENTITY USING INDEX ... | | indkey int2vector (references pg_attribute.attnum) This is an array of indnatts values that indicate which table columns this index indexes. For example, a value of 1 3 would mean that the first and the third table columns make up the index entries. Key columns come before non-key (included) columns. A zero in this array indicates that the corresponding index attribute is an expression over the table columns, rather than a simple column reference. | | indcollation oidvector (references pg_collation.oid) For each column in the index key (indnkeyatts values), this contains the OID of the collation to use for the index, or zero if the column is not of a collatable data type. | | indclass oidvector (references pg_opclass.oid) For each column in the index key (indnkeyatts values), this contains the OID of the operator class to use. See pg_opclass for details. | | indoption int2vector This is an array of indnkeyatts values that store per-column flag bits. The meaning of the bits is defined by the index's access method. | | indexprs pg_node_tree Expression trees (in nodeToString() representation) for index attributes that are not simple column references. This is a list with one element for each zero entry in indkey. Null if all index attributes are simple references. | | indpred pg_node_tree Expression tree (in nodeToString() representation) for partial index predicate. Null if not a partial index. |

## draft-24083cabffc26972

Does bit_and ignore null inputs in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) Computes the bitwise AND of all non-null input values.
- (pg-16) Computes the bitwise AND of all non-null input values.

### Top three retrieved
1. `chunk-89665eb32aaa682cf2887821ff32b951cf56ce25a98b119a7f3f45a6bc895769` — pg-15; score=2.946849, dense=0.755430, sparse=0.600000, rerank=2.9468488693237305

> — the SQL standard expects sum to behave that way. We can do this simply by omitting the initcond phrase, so that the initial state value is null. Ordinarily this would mean that the sfunc would need to check for a null state-value input. But for sum and some other simple aggregates like max and min , it is sufficient to insert the first nonnull input value into the state variable and then start applying the transition function at the second nonnull input value. PostgreSQL will do that automatically if the initial state value is null and the transition function is marked strict (i.e., not to be called for null inputs). Another bit of default behavior for a strict transition function is that the previous state value is retained unchanged whenever a null input value is encountered. Thus, null values are ignored. If you need some other behavior for null inputs, do not declare your transition function as strict; instead code it to test for null inputs and do whatever is needed. avg (average) is a more complex example of an aggregate. It requires two pieces of running state: the sum of the inputs and the count of the number of inputs. The final result is obtained by dividing these quantities. Average is typically implemented by using an array as

2. `chunk-6560e13f63abd4e6e3a5451dfa771daf888b2a1912c309a93b2cd975764a7fdf` — pg-15; score=2.456903, dense=0.789368, sparse=0.000000, rerank=2.4569029808044434

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

3. `chunk-43f6d34b718a6f3bdcedc3af97bd6db623ea7fdd16f6e617d6cec1031b96cdf4` — pg-15; score=2.456903, dense=0.789368, sparse=0.000000, rerank=2.4569029808044434

> Server Configuration There are many configuration parameters that affect the behavior of the database system. In the first section of this chapter we describe how to interact with configuration parameters. The subsequent sections discuss each parameter in detail.

## draft-39a8f35fc5f9cb13

What happens to null array entries in array_to_string when null_string is omitted in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) array_to_string ( array anyarray, delimiter text , null_string text ) text Converts each array element to its text representation, and concatenates those separated by the delimiter string. If null_string is given and is not NULL, then NULL array entries are represented by that string; otherwise, they are omitted.
- (pg-16) array_to_string ( array anyarray, delimiter text , null_string text ) text Converts each array element to its text representation, and concatenates those separated by the delimiter string. If null_string is given and is not NULL, then NULL array entries are represented by that string; otherwise, they are omitted.

### Top three retrieved
1. `chunk-6560e13f63abd4e6e3a5451dfa771daf888b2a1912c309a93b2cd975764a7fdf` — pg-15; score=4.931211, dense=0.838063, sparse=0.000000, rerank=4.931210994720459

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

2. `chunk-43f6d34b718a6f3bdcedc3af97bd6db623ea7fdd16f6e617d6cec1031b96cdf4` — pg-15; score=4.931211, dense=0.838063, sparse=0.000000, rerank=4.931210994720459

> Server Configuration There are many configuration parameters that affect the behavior of the database system. In the first section of this chapter we describe how to interact with configuration parameters. The subsequent sections discuss each parameter in detail.

3. `chunk-6f543e7df63755ce424965f9dee8a73f8ca986ae0c05349a8c1e459ff719db86` — pg-15; score=0.661809, dense=0.758140, sparse=0.000000, rerank=0.6618088483810425

> it will be true or false according to whether Perl would evaluate the returned value as true. Similar transformations are also performed for boolean query arguments and results of SPI queries performed inside the function ( Database Access from PL/Perl ). Perl can return PostgreSQL arrays as references to Perl arrays. Here is an example: Perl passes PostgreSQL arrays as a blessed PostgreSQL::InServer::ARRAY object. This object may be treated as an array reference or a string, allowing for backward compatibility with Perl code written for PostgreSQL versions below 9.1 to run. For example: Multidimensional arrays are represented as references to lower-dimensional arrays of references in a way common to every Perl programmer. Composite-type arguments are passed to the function as references to hashes. The keys of the hash are the attribute names of the composite type. Here is an example: A PL/Perl function can return a composite-type result using the same approach: return a reference to a hash that has the required attributes. For example: Any columns in the declared result data type that are not present in the hash will be returned as null values. Similarly, output arguments of procedures can be returned as a hash reference: PL/Perl functions can also return sets of either scalar or composite types. Usually you'll want to return rows one at a time,

## draft-8212c39cab5f00aa

Does bit_or include null inputs in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) Computes the bitwise OR of all non-null input values.
- (pg-16) Computes the bitwise OR of all non-null input values.

### Top three retrieved
1. `chunk-6560e13f63abd4e6e3a5451dfa771daf888b2a1912c309a93b2cd975764a7fdf` — pg-15; score=2.952332, dense=0.784275, sparse=0.000000, rerank=2.952332019805908

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

2. `chunk-43f6d34b718a6f3bdcedc3af97bd6db623ea7fdd16f6e617d6cec1031b96cdf4` — pg-15; score=2.952332, dense=0.784275, sparse=0.000000, rerank=2.952332019805908

> Server Configuration There are many configuration parameters that affect the behavior of the database system. In the first section of this chapter we describe how to interact with configuration parameters. The subsequent sections discuss each parameter in detail.

3. `chunk-a87e27504595d23722e9835b62a989edd7d53da76744135d9a615dcac2822341` — pg-15; score=1.789621, dense=0.769836, sparse=0.000000, rerank=1.7896208763122559

> in Perl. The above function definition will not behave very nicely with null inputs (in fact, it will act as though they are zeroes). We could add STRICT to the function definition to make PostgreSQL do something more reasonable: if a null value is passed, the function will not be called at all, but will just return a null result automatically. Alternatively, we could check for undefined inputs in the function body. For example, suppose that we wanted perl_max with one null and one nonnull argument to return the nonnull argument, rather than a null value: As shown above, to return an SQL null value from a PL/Perl function, return an undefined value. This can be done whether the function is strict or not. Anything in a function argument that is not a reference is a string, which is in the standard PostgreSQL external text representation for the relevant data type. In the case of ordinary numeric or text types, Perl will just do the right thing and the programmer will normally not have to worry about it. However, in other cases the argument will need to be converted into a form that is more usable in Perl. For example, the decode_bytea function can be used to convert an argument of type bytea into unescaped binary. Similarly, values passed back

## draft-5ca5682d5aa33579

Does json_object_agg_unique_strict keep entries whose values are null in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) json_object_agg_unique_strict ( key "any", value "any" ) json jsonb_object_agg_unique_strict ( key "any", value "any" ) jsonb Collects all the key/value pairs into a JSON object. Key arguments are coerced to text; value arguments are converted as per to_json or to_jsonb. The key can not be null. If the value is null then the entry is skipped. If there is a duplicate key an error is thrown.

### Top three retrieved
1. `chunk-8908fa26e794467b20d3f73e1de7a855254a1873b19a1936a59b028a09daaf9e` — pg-16; score=4.602391, dense=0.842301, sparse=3.400000, rerank=4.602390766143799

> , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given to these aggregates. Users accustomed to working with other SQL database management systems might be disappointed by the performance of the count aggregate when it is applied to the entire

2. `chunk-9204da04d5eb965ba2af9a6db5346a4af9cdb78dc3e8f3cd78f5f2c443902655` — pg-16; score=4.602391, dense=0.842301, sparse=3.400000, rerank=4.602390766143799

> Functions and Operators PostgreSQL provides a large number of functions and operators for the built-in data types. This chapter describes most of them, although additional special-purpose functions appear in relevant sections of the manual. Users can also define their own functions and operators, as described in Server Programming . The psql commands \df and \do can be used to list all available functions and operators, respectively. The notation used throughout this chapter to describe the argument and result data types of a function or operator is like this: which says that the function repeat takes one text and one integer argument and returns a result of type text. The right arrow is also used to indicate the result of an example, thus: If you are concerned about portability then note that most of the functions and operators described in this chapter, with the exception of the most trivial arithmetic and comparison operators and some explicitly marked functions, are not specified by the SQL standard. Some of this extended functionality is present in other SQL database management systems, and in many cases this functionality is compatible and consistent between the various implementations.

3. `chunk-8b016650fef8bd099dbcd9cfd1de8beb5d2bbf2fad2c975133bc5c32d6b548c8` — pg-16; score=2.978392, dense=0.000000, sparse=3.900000, rerank=2.978391647338867

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully

## draft-de8d404798f688a2

What limits the number of items requested by array_sample in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) array_sample ( array anyarray, n integer ) anyarray Returns an array of n items randomly selected from array. n may not exceed the length of array's first dimension.

### Top three retrieved
1. `chunk-189f79cd43bf3b9200a68762f0f093df1889cc3a10666ff2fde9798ada2cc723` — pg-16; score=1.347900, dense=0.730296, sparse=0.000000, rerank=1.347900152206421

> Limitations The current limitations of PostgreSQL 's text search features are: The length of each lexeme must be less than 2 kilobytes The length of a tsvector (lexemes + positions) must be less than 1 megabyte The number of lexemes must be less than 2 64 Position values in tsvector must be greater than 0 and no more than 16,383 The match distance in a < N > (FOLLOWED BY) tsquery operator cannot be more than 16,384 No more than 256 positions per lexeme The number of nodes (lexemes + operators) in a tsquery must be less than 32,768 For comparison, the PostgreSQL 8.1 documentation contained 10,441 unique words, a total of 335,420 words, and the most frequent word postgresql was mentioned 6,127 times in 655 documents. Another example — the PostgreSQL mailing list archives contained 910,989 unique words with 57,491,343 lexemes in 461,020 messages.

2. `chunk-eac002acaefcc063634a948602a34a4c435a0feee01567eed60d8bae006b4871` — pg-16; score=1.240303, dense=0.751028, sparse=0.000000, rerank=1.2403026819229126

> than a few processes do so then the system-wide limit can easily be exceeded. If you find this happening, and you do not want to alter the system-wide limit, you can set PostgreSQL 's max_files_per_process configuration parameter to limit the consumption of open files. Another kernel limit that may be of concern when supporting large numbers of client connections is the maximum socket connection queue length. If more than that many connection requests arrive within a very short period, some may get rejected before the PostgreSQL server can service the requests, with those clients receiving unhelpful connection failure errors such as Resource temporarily unavailable or Connection refused . The default queue length limit is 128 on many platforms. To raise it, adjust the appropriate kernel parameter via sysctl , then restart the PostgreSQL server. The parameter is variously named net.core.somaxconn on Linux, kern.ipc.soacceptqueue on newer FreeBSD, and kern.ipc.somaxconn on macOS and other BSD variants.

3. `chunk-56805de582000cfa3a162442a4a5bbc9f74a1d87ea1cff808725fca5ae26d30d` — pg-16; score=1.240303, dense=0.751028, sparse=0.000000, rerank=1.2403026819229126

> Managing Kernel Resources PostgreSQL can sometimes exhaust various operating system resource limits, especially when multiple copies of the server are running on the same system, or in very large installations. This section explains the kernel resources used by PostgreSQL and the steps you can take to resolve problems related to kernel resource consumption.

## draft-df61a1a2e6822bb7

What does cardinality return for an empty array in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) cardinality ( anyarray ) integer Returns the total number of elements in the array, or 0 if the array is empty.
- (pg-16) cardinality ( anyarray ) integer Returns the total number of elements in the array, or 0 if the array is empty.

### Top three retrieved
1. `chunk-6f543e7df63755ce424965f9dee8a73f8ca986ae0c05349a8c1e459ff719db86` — pg-15; score=0.580477, dense=0.744907, sparse=0.000000, rerank=0.5804767608642578

> it will be true or false according to whether Perl would evaluate the returned value as true. Similar transformations are also performed for boolean query arguments and results of SPI queries performed inside the function ( Database Access from PL/Perl ). Perl can return PostgreSQL arrays as references to Perl arrays. Here is an example: Perl passes PostgreSQL arrays as a blessed PostgreSQL::InServer::ARRAY object. This object may be treated as an array reference or a string, allowing for backward compatibility with Perl code written for PostgreSQL versions below 9.1 to run. For example: Multidimensional arrays are represented as references to lower-dimensional arrays of references in a way common to every Perl programmer. Composite-type arguments are passed to the function as references to hashes. The keys of the hash are the attribute names of the composite type. Here is an example: A PL/Perl function can return a composite-type result using the same approach: return a reference to a hash that has the required attributes. For example: Any columns in the declared result data type that are not present in the hash will be returned as null values. Similarly, output arguments of procedures can be returned as a hash reference: PL/Perl functions can also return sets of either scalar or composite types. Usually you'll want to return rows one at a time,

2. `chunk-3fb0b13d87986fb4b6844b85f225e4bfe29f33d05cf8838db98ed359760b6b3d` — pg-15; score=0.580477, dense=0.744907, sparse=0.000000, rerank=0.5804767608642578

> PL/Perl — Perl Procedural Language PL/Perl is a loadable procedural language that enables you to write PostgreSQL functions and procedures in the Perl programming language . The main advantage to using PL/Perl is that this allows use, within stored functions and procedures, of the manyfold string munging operators and functions available for Perl. Parsing complex strings might be easier using Perl than it is with the string functions and control structures provided in PL/pgSQL. To install PL/Perl in a particular database, use CREATE EXTENSION plperl . If a language is installed into template1 , all subsequently created databases will have the language installed automatically. Users of source packages must specially enable the build of PL/Perl during the installation process. (Refer to Installation from Source Code for more information.) Users of binary packages might find PL/Perl in a separate subpackage.

3. `chunk-c2c860b65cb490897af726032852b53858306c55f66d2b95107afe7ea565c6e5` — pg-15; score=-1.071214, dense=0.000000, sparse=2.000000, rerank=-1.0712144374847412

> | Column Type Description | | --- | | object_catalog sql_identifier Name of the database that contains the object that uses the array being described (always the current database) | | object_schema sql_identifier Name of the schema that contains the object that uses the array being described | | object_name sql_identifier Name of the object that uses the array being described | | object_type character_data The type of the object that uses the array being described: one of TABLE (the array is used by a column of that table), USER-DEFINED TYPE (the array is used by an attribute of that composite type), DOMAIN (the array is used by that domain), ROUTINE (the array is used by a parameter or the return data type of that function). | | collection_type_identifier sql_identifier The identifier of the data type descriptor of the array being described. Use this to join with the dtd_identifier columns of other information schema views. | | data_type character_data Data type of the array elements, if it is a built-in type, else USER-DEFINED (in that case, the type is identified in udt_name and associated columns). | | character_maximum_length cardinal_number Always null, since this information is not applied to array element data types in PostgreSQL | | character_octet_length cardinal_number Always null, since this information is not applied to array element data types in PostgreSQL | | character_set_catalog sql_identifier Applies to a feature not available in PostgreSQL | | character_set_schema sql_identifier Applies to a feature not available in PostgreSQL | | character_set_name sql_identifier Applies to a feature not available in PostgreSQL | | collation_catalog sql_identifier Name of the database containing the collation of the element type (always the current database), null if default or the data type of the element is not collatable | | collation_schema sql_identifier Name of the schema containing the collation of the element type, null if default or the data type of the element is not collatable | | collation_name sql_identifier Name of the collation of the element type, null if default or the data type of the element is not collatable | | numeric_precision cardinal_number Always null, since this information is not applied to array element data types in PostgreSQL | | numeric_precision_radix cardinal_number Always null, since this information is not applied to array element data types in PostgreSQL | | numeric_scale cardinal_number Always null, since this information is not applied to array element data types in PostgreSQL | | datetime_precision cardinal_number Always null, since this information is not applied to array element data types in PostgreSQL | | interval_type character_data Always null, since this information is not applied to array element data types in PostgreSQL | | interval_precision cardinal_number Always null, since this information is not applied to array element data types in PostgreSQL | | domain_default character_data Not yet implemented | | udt_catalog sql_identifier Name of the database that the data type of the elements is defined in (always the current database) | | udt_schema sql_identifier Name of the schema that the data type of the elements is defined in | | udt_name sql_identifier Name of the data type of the elements | | scope_catalog sql_identifier Applies to a feature not available in PostgreSQL | | scope_schema sql_identifier Applies to a feature not available in PostgreSQL | | scope_name sql_identifier Applies to a feature not available in PostgreSQL | | maximum_cardinality cardinal_number Always null, because arrays always have unlimited maximum cardinality in PostgreSQL | | dtd_identifier sql_identifier An identifier of the data type descriptor of the element. This is currently not useful. |

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

2. `chunk-3ae06156e4fb4ef9fa5e3e489fe17e32f5e46013c14e0b110aa55335a3e4a123` — pg-15; score=0.189657, dense=0.734255, sparse=0.000000, rerank=0.1896568089723587

> conforms to the SQL standard by using the keyword ARRAY , can be used for one-dimensional arrays. pay_by_quarter could have been defined as: Or, if no array size is to be specified: As before, however, PostgreSQL does not enforce the size restriction in any case.

3. `chunk-697d381610187065d96f107de60c639f4b24670ae7e70e7765e173014d67fdc3` — pg-15; score=-0.732748, dense=0.743631, sparse=0.000000, rerank=-0.7327476143836975

> Arrays, Lists SQL array values are passed into PL/Python as a Python list. To return an SQL array value out of a PL/Python function, return a Python list: Multidimensional arrays are passed into PL/Python as nested Python lists. A 2-dimensional array is a list of lists, for example. When returning a multi-dimensional SQL array out of a PL/Python function, the inner lists at each level must all be of the same size. For example: Other Python sequences, like tuples, are also accepted for backwards-compatibility with PostgreSQL versions 9.6 and below, when multi-dimensional arrays were not supported. However, they are always treated as one-dimensional arrays, because they are ambiguous with composite types. For the same reason, when a composite type is used in a multi-dimensional array, it must be represented by a tuple, rather than a list. Note that in Python, strings are sequences, which can have undesirable effects that might be familiar to Python programmers:

## draft-0bd01d40748321be

Which role grants access to the slots reserved by reserved_connections in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) reserved_connections ( integer ) Determines the number of connection slots that are reserved for connections by roles with privileges of the pg_use_reserved_connections role.

### Top three retrieved
1. `chunk-49edd73b121ff2b2d390c9ed189ff0307b6ea96c49c2d2b92d4f1e5eef8f4494` — pg-16; score=2.891462, dense=0.763951, sparse=2.900000, rerank=2.8914623260498047

> connection slots are available, new connections will be accepted only for superusers. The default value is zero connections. The value must be less than max_connections minus superuser_reserved_connections . This parameter can only be set at server start. superuser_reserved_connections ( integer ) Determines the number of connection slots that are reserved for connections by PostgreSQL superusers. At most max_connections connections can ever be active simultaneously. Whenever the number of active concurrent connections is at least max_connections minus superuser_reserved_connections , new connections will be accepted only for superusers. The connection slots reserved by this parameter are intended as final reserve for emergency use after the slots reserved by reserved_connections have been exhausted. The default value is three connections. The value must be less than max_connections minus reserved_connections . This parameter can only be set at server start. unix_socket_directories ( string ) Specifies the directory of the Unix-domain socket(s) on which the server is to listen for connections from client applications. Multiple sockets can be created by listing multiple directories separated by commas. Whitespace between entries is ignored; surround a directory name with double quotes if you need to include whitespace or commas in the name. An empty value specifies not listening on any Unix-domain sockets, in which case only TCP/IP sockets can be used to connect to the server. A value that

2. `chunk-9eb2b722825257854302d585cf8f1e101ec990767dcd3688eda05225ba8d609b` — pg-16; score=2.891462, dense=0.763951, sparse=2.900000, rerank=2.8914623260498047

> Server Configuration There are many configuration parameters that affect the behavior of the database system. In the first section of this chapter we describe how to interact with configuration parameters. The subsequent sections discuss each parameter in detail.

3. `chunk-2d785059557ba8e60cde58c2d81822dd99c4227288d7f455214cacb480f93b05` — pg-16; score=1.545969, dense=0.000000, sparse=1.500000, rerank=1.545968770980835

> it controls the inheritance status of memberships added with this command using the IN ROLE clause, and in later commands using the ROLE clause. It is also used as the default inheritance status when adding this role as a member using the GRANT command. If not specified, INHERIT is the default. In PostgreSQL versions before 16, inheritance was a role-level attribute that controlled all runtime membership checks for that role. LOGIN NOLOGIN These clauses determine whether a role is allowed to log in; that is, whether the role can be given as the initial session authorization name during client connection. A role having the LOGIN attribute can be thought of as a user. Roles without this attribute are useful for managing database privileges, but are not users in the usual sense of the word. If not specified, NOLOGIN is the default, except when CREATE ROLE is invoked through its alternative spelling CREATE USER . REPLICATION NOREPLICATION These clauses determine whether a role is a replication role. A role must have this attribute (or be a superuser) in order to be able to connect to the server in replication mode (physical or logical replication) and in order to be able to create or drop replication slots. A role having the REPLICATION attribute is a very highly privileged role, and should only

## draft-59e8d98dc1e8267d

How many blocks does serializable_buffers allocate by default in PostgreSQL 17?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: []

### Expected evidence
- (pg-17) serializable_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_serial (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 32 .

### Top three retrieved
1. `chunk-8a2237587bc1a83e94feb138913e39b20c6d2431d92dfd000b7fba113993ad13` — pg-17; score=1.233624, dense=0.761585, sparse=1.000000, rerank=1.233623743057251

> set at server start. subtransaction_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_subtrans (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 0 , which requests shared_buffers /512 up to 1024 blocks, but not fewer than 16 blocks. This parameter can only be set at server start. transaction_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_xact (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 0 , which requests shared_buffers /512 up to 1024 blocks, but not fewer than 16 blocks. This parameter can only be set at server start. max_stack_depth ( integer ) Specifies the maximum safe depth of the server's execution stack. The ideal setting for this parameter is the actual stack size limit enforced by the kernel (as set by ulimit -s or local equivalent), less a safety margin of a megabyte or so. The safety margin is needed because the stack depth is not checked in every routine in the server, but only in key potentially-recursive routines. If this value is specified

2. `chunk-59bd804ec9a678648324bd35b29a321ce557bd5e3460d627d8d9f8848eb19a4c` — pg-17; score=1.233624, dense=0.761585, sparse=1.000000, rerank=1.233623743057251

> Server Configuration There are many configuration parameters that affect the behavior of the database system. In the first section of this chapter we describe how to interact with configuration parameters. The subsequent sections discuss each parameter in detail.

3. `chunk-bfce0a27f238085aa3fcd21ffe8dda8b9adb0a8b4a5ad302c1120045f267239a` — pg-17; score=0.300014, dense=0.775476, sparse=0.000000, rerank=0.3000137507915497

> larger batches in the background. Often that will result in greatly reduced transaction latency, but there also are some cases, especially with workloads that are bigger than shared_buffers , but smaller than the OS's page cache, where performance might degrade. This setting may have no effect on some platforms. If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The valid range is between 0 , which disables forced writeback, and 2MB . The default is 512kB on Linux, 0 elsewhere. (If BLCKSZ is not 8kB, the default and maximum values scale proportionally to it.) This parameter can only be set in the postgresql.conf file or on the server command line. Smaller values of bgwriter_lru_maxpages and bgwriter_lru_multiplier reduce the extra I/O load caused by the background writer, but make it more likely that server processes will have to issue writes for themselves, delaying interactive queries.

## draft-63730cc51a247416

Which objects receive changed privileges after modifying a pg_default_acl entry with defaclobjtype = S?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) defaclobjtype char Type of object this entry is for: r = relation (table, view), S = sequence, f = function, T = type, n = schema
- (pg-17) pg_default_acl is only consulted during object creation.

### Top three retrieved
1. `chunk-ecb07ce2d8f7a6ba484992fa9abb51168effa59591154263b56051dcd2828dc7` — pg-17; score=5.306449, dense=0.813160, sparse=1.800000, rerank=5.306448936462402

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

2. `chunk-f8d711506ea39112552fc5f8ad3775af2785221902115c8367b2caf63d7271ac` — pg-17; score=5.306449, dense=0.813160, sparse=1.800000, rerank=5.306448936462402

> System Catalogs The system catalogs are the place where a relational database management system stores schema metadata, such as information about tables and columns, and internal bookkeeping information. PostgreSQL 's system catalogs are regular tables. You can drop and recreate the tables, add columns, insert and update values, and severely mess up your system that way. Normally, one should not change the system catalogs by hand, there are normally SQL commands to do that. (For example, CREATE DATABASE inserts a row into the pg_database catalog — and actually creates the database on disk.) There are some exceptions for particularly esoteric operations, but many of those have been made available as SQL commands over time, and so the need for direct manipulation of the system catalogs is ever decreasing.

3. `chunk-12ab8acbfe517288df0acd725aaee2159feb6a6897bd876fd624a177359466a2` — pg-17; score=2.121230, dense=0.700831, sparse=0.900000, rerank=2.121229648590088

> Parameters target_role Change default privileges for objects created by the target_role , or the current role if unspecified. schema_name The name of an existing schema. If specified, the default privileges are altered for objects later created in that schema. If IN SCHEMA is omitted, the global default privileges are altered. IN SCHEMA is not allowed when setting privileges for schemas, since schemas can't be nested. role_name The name of an existing role to grant or revoke privileges for. This parameter, and all the other parameters in abbreviated_grant_or_revoke , act as described under GRANT or REVOKE , except that one is setting permissions for a whole class of objects rather than specific named objects.

## draft-6ea99930a2f5381a

Which units does work_mem assume when none are specified in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes.
- (pg-16) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes.

### Top three retrieved
1. `chunk-ba92f9c34177a3fa7b2ed1fc6d9b6107ec597cf5d553415798bd6b2350a5a21d` — pg-15; score=0.750058, dense=0.694279, sparse=1.000000, rerank=0.750057578086853

> Specifies the maximum amount of memory to be used by maintenance operations, such as VACUUM , CREATE INDEX , and ALTER TABLE ADD FOREIGN KEY . If this value is specified without units, it is taken as kilobytes. It defaults to 64 megabytes ( 64MB ). Since only one of these operations can be executed at a time by a database session, and an installation normally doesn't have many of them running concurrently, it's safe to set this value significantly larger than work_mem . Larger settings might improve performance for vacuuming and for restoring database dumps. Note that when autovacuum runs, up to autovacuum_max_workers times this memory may be allocated, so be careful not to set the default value too high. It may be useful to control for this by separately setting autovacuum_work_mem . Note that for the collection of dead tuple identifiers, VACUUM is only able to utilize up to a maximum of 1GB of memory. autovacuum_work_mem ( integer ) Specifies the maximum amount of memory to be used by each autovacuum worker process. If this value is specified without units, it is taken as kilobytes. It defaults to -1, indicating that the value of maintenance_work_mem should be used instead. The setting has no effect on the behavior of VACUUM when run in other contexts. This parameter can only

2. `chunk-43f6d34b718a6f3bdcedc3af97bd6db623ea7fdd16f6e617d6cec1031b96cdf4` — pg-15; score=0.750058, dense=0.694279, sparse=1.000000, rerank=0.750057578086853

> Server Configuration There are many configuration parameters that affect the behavior of the database system. In the first section of this chapter we describe how to interact with configuration parameters. The subsequent sections discuss each parameter in detail.

3. `chunk-5066d3bd1c7ab8a2f2d8cbc21b1103a34206a2a288f086058e72e274cda87abd` — pg-15; score=0.725210, dense=0.778909, sparse=0.400000, rerank=0.7252101898193359

> $ postgres -c work_mem=1234 $ postgres --work-mem=1234

## draft-e5b5f0b94a5943be

Which setting names the server's certificate-authority file?

**Category:** identifier not matched. **Reason:** The expected identifier is absent from the top three.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ca_file ( string ) Specifies the name of the file containing the SSL server certificate authority (CA).

### Top three retrieved
1. `chunk-061bf406debb26d0a691c41347bf86ab0162105d2828024b22ed367fbf6f48aa` — pg-17; score=3.490977, dense=0.756542, sparse=0.600000, rerank=3.4909768104553223

> and any weaker setting will result in an error. In most cases it is trivial for anyone to obtain a certificate trusted by the system for a hostname they control, rendering verify-ca and all weaker modes useless. The magic system value will take precedence over a local certificate file with the same name. If for some reason you find yourself in this situation, use an alternative path like sslrootcert=./system instead. sslcrl This parameter specifies the file name of the SSL server certificate revocation list (CRL). Certificates listed in this file, if it exists, will be rejected while attempting to authenticate the server's certificate. If neither sslcrl nor sslcrldir is set, this setting is taken as ~/.postgresql/root.crl . sslcrldir This parameter specifies the directory name of the SSL server certificate revocation list (CRL). Certificates listed in the files in this directory, if it exists, will be rejected while attempting to authenticate the server's certificate. The directory needs to be prepared with the OpenSSL command openssl rehash or c_rehash . See its documentation for details. Both sslcrl and sslcrldir can be specified together. sslsni If set to 1 (default), libpq sets the TLS extension Server Name Indication ( SNI ) on SSL-enabled connections. By setting this parameter to 0, this is turned off. The Server Name Indication can be used by SSL-aware

2. `chunk-0a87e50e87ef7dc2cb59cd6077cb3c2df8ba3d2409ef1673412e5b61293ee9ec` — pg-17; score=3.490977, dense=0.756542, sparse=0.600000, rerank=3.4909768104553223

> Database Connection Control Functions The following functions deal with making a connection to a PostgreSQL backend server. An application program can have several backend connections open at one time. (One reason to do that is to access more than one database.) Each connection is represented by a PGconn object, which is obtained from the function , , or . Note that these functions will always return a non-null object pointer, unless perhaps there is too little memory even to allocate the PGconn object. The function should be called to check the return value for a successful connection before queries are sent via the connection object. If untrusted users have access to a database that has not adopted a secure schema usage pattern , begin each session by removing publicly-writable schemas from search_path . One can set parameter key word options to value -csearch_path= . Alternately, one can issue PQexec( conn , "SELECT pg_catalog.set_config('search_path', '', false)") after connecting. This consideration is not specific to libpq ; it applies to every interface for executing arbitrary SQL commands. On Unix, forking a process with open libpq connections can lead to unpredictable results because the parent and child processes share the same sockets and operating system resources. For this reason, such usage is not recommended, though doing an exec from the child process to

3. `chunk-843b3d4e73d70c55857d31399b2ba53a42780b048416743aacc1b0ff6c3e0cc5` — pg-17; score=2.731021, dense=0.734708, sparse=0.800000, rerank=2.7310211658477783

> server requests one and the client has one to send. require The server must request a certificate. The connection will fail if the client does not send a certificate and the server successfully authenticates the client anyway. sslcertmode=require doesn't add any additional security, since there is no guarantee that the server is validating the certificate correctly; PostgreSQL servers generally request TLS certificates from clients whether they validate them or not. The option may be useful when troubleshooting more complicated TLS setups. sslrootcert This parameter specifies the name of a file containing SSL certificate authority ( CA ) certificate(s). If the file exists, the server's certificate will be verified to be signed by one of these authorities. The default is ~/.postgresql/root.crt . The special value system may be specified instead, in which case the trusted CA roots from the SSL implementation will be loaded. The exact locations of these root certificates differ by SSL implementation and platform. For OpenSSL in particular, the locations may be further modified by the SSL_CERT_DIR and SSL_CERT_FILE environment variables. When using sslrootcert=system , the default sslmode is changed to verify-full , and any weaker setting will result in an error. In most cases it is trivial for anyone to obtain a certificate trusted by the system for a hostname they control, rendering verify-ca and all weaker

## draft-00d4ad3e896413a3

Is Partial Mode supported by string_agg in PostgreSQL 15?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) string_agg ( value text, delimiter text ) text string_agg ( value bytea, delimiter bytea ) bytea Concatenates the non-null input values into a string. Each value after the first is preceded by the corresponding delimiter (if it's not null). | No

### Top three retrieved
1. `chunk-3e7596d096f6d72115a5bc69777f909456547468ffede91368ab27c4cc28b03b` — pg-15; score=0.577905, dense=0.737895, sparse=0.000000, rerank=0.5779049396514893

> 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, and 15 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2016. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2016. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2016 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if some other subfeatures are supported.

2. `chunk-b195d7264ab5ee227724af4979d10955a88dbe442fa3f67a2df89cbfd5799508` — pg-15; score=0.252251, dense=0.736947, sparse=0.000000, rerank=0.252250999212265

> Note that this query cannot use this index: The order 3501 might be among the billed or unbilled orders. Setting up a Partial Index to Exclude Uninteresting Values also illustrates that the indexed column and the column used in the predicate do not need to match. PostgreSQL supports partial indexes with arbitrary predicates, so long as only columns of the table being indexed are involved. However, keep in mind that the predicate must match the conditions used in the queries that are supposed to benefit from the index. To be precise, a partial index can be used in a query only if the system can recognize that the WHERE condition of the query mathematically implies the predicate of the index. PostgreSQL does not have a sophisticated theorem prover that can recognize mathematically equivalent expressions that are written in different forms. (Not only is such a general theorem prover extremely difficult to create, it would probably be too slow to be of any real use.) The system can recognize simple inequality implications, for example x < 1 implies x < 2 ; otherwise the predicate condition must exactly match part of the query's WHERE condition or the index will not be recognized as usable. Matching takes place at query planning time, not at run time. As a result, parameterized query clauses

3. `chunk-aff1fe360742d2293515bf0cce22b7d9d90201670ddaea45a49b7faf6d1c564c` — pg-15; score=0.252251, dense=0.736947, sparse=0.000000, rerank=0.252250999212265

> Indexes Indexes are a common way to enhance database performance. An index allows the database server to find and retrieve specific rows much faster than it could do without an index. But indexes also add overhead to the database system as a whole, so they should be used sensibly.

## draft-05e120c03871ce0e

When can notify_buffers be set in PostgreSQL 17?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: []

### Expected evidence
- (pg-17) notify_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_notify (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 16 . This parameter can only be set at server start.

### Top three retrieved
1. `chunk-f98fa9a1b35aee4676c55f1d07ee3619a7b07c1523f115b0fea59bc6a08128f4` — pg-17; score=1.660201, dense=0.736035, sparse=0.600000, rerank=1.6602013111114502

> during recent rounds. The average recent need is multiplied by bgwriter_lru_multiplier to arrive at an estimate of the number of buffers that will be needed during the next round. Dirty buffers are written until there are that many clean, reusable buffers available. (However, no more than bgwriter_lru_maxpages buffers will be written per round.) Thus, a setting of 1.0 represents a just in time policy of writing exactly the number of buffers predicted to be needed. Larger values provide some cushion against spikes in demand, while smaller values intentionally leave writes to be done by server processes. The default is 2.0. This parameter can only be set in the postgresql.conf file or on the server command line. bgwriter_flush_after ( integer ) Whenever more than this amount of data has been written by the background writer, attempt to force the OS to issue these writes to the underlying storage. Doing so will limit the amount of dirty data in the kernel's page cache, reducing the likelihood of stalls when an fsync is issued at the end of a checkpoint, or when the OS writes data back in larger batches in the background. Often that will result in greatly reduced transaction latency, but there also are some cases, especially with workloads that are bigger than shared_buffers , but smaller than the OS's page

2. `chunk-59bd804ec9a678648324bd35b29a321ce557bd5e3460d627d8d9f8848eb19a4c` — pg-17; score=1.660201, dense=0.736035, sparse=0.600000, rerank=1.6602013111114502

> Server Configuration There are many configuration parameters that affect the behavior of the database system. In the first section of this chapter we describe how to interact with configuration parameters. The subsequent sections discuss each parameter in detail.

3. `chunk-be19a2575eae2e55120e2ce097e5d5e7c02792f0cd16a1738e8ff5ffc9423234` — pg-17; score=0.549776, dense=0.000000, sparse=0.600000, rerank=0.5497760772705078

> in the buffer pool, though, it goes into a longer sleep regardless of bgwriter_delay . If this value is specified without units, it is taken as milliseconds. The default value is 200 milliseconds ( 200ms ). Note that on some systems, the effective resolution of sleep delays is 10 milliseconds; setting bgwriter_delay to a value that is not a multiple of 10 might have the same results as setting it to the next higher multiple of 10. This parameter can only be set in the postgresql.conf file or on the server command line. bgwriter_lru_maxpages ( integer ) In each round, no more than this many buffers will be written by the background writer. Setting this to zero disables background writing. (Note that checkpoints, which are managed by a separate, dedicated auxiliary process, are unaffected.) The default value is 100 buffers. This parameter can only be set in the postgresql.conf file or on the server command line. bgwriter_lru_multiplier ( floating point ) The number of dirty buffers written in each round is based on the number of new buffers that have been needed by server processes during recent rounds. The average recent need is multiplied by bgwriter_lru_multiplier to arrive at an estimate of the number of buffers that will be needed during the next round. Dirty buffers are written until there

## draft-32068527036ef646

Which setting selects the configuration file for user-name mapping?

**Category:** identifier not matched. **Reason:** The expected identifier is absent from the top three.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ident_file ( string ) Specifies the configuration file for user name mapping (customarily called pg_ident.conf ).

### Top three retrieved
1. `chunk-d8bc5d3a281e143715f850ae9232ed6c8326d082e258f2413b2d4f110101d298` — pg-17; score=4.435529, dense=0.784789, sparse=0.000000, rerank=4.435528755187988

> Parameters user_name User name of the mapping. CURRENT_ROLE , CURRENT_USER , and USER match the name of the current user. PUBLIC is used to match all present and future user names in the system. server_name Server name of the user mapping. OPTIONS ( [ ADD | SET | DROP ] option [' value '] [, ... ] ) Change options for the user mapping. The new options override any previously specified options. ADD , SET , and DROP specify the action to be performed. ADD is assumed if no operation is explicitly specified. Option names must be unique; options are also validated by the server's foreign-data wrapper.

2. `chunk-27e586b4d2770b15b744232b425d92665adc844999956e02769d9a7874f6cca6` — pg-17; score=4.435529, dense=0.784789, sparse=0.000000, rerank=4.435528755187988

> ALTER USER MAPPING 7 SQL - Language Statements ALTER USER MAPPING change the definition of a user mapping

3. `chunk-5334c1c6bc6749661532b81e2a8a55961dbb18e0f3b5f06185c959af47e96da8` — pg-17; score=2.929708, dense=0.738061, sparse=0.600000, rerank=2.929708480834961

> Name Maps ). This is discouraged and is primarily available for backwards compatibility, as it is not secure in multi-realm environments unless krb_realm is also used. It is recommended to leave include_realm set to the default (1) and to provide an explicit mapping in pg_ident.conf to convert principal names to PostgreSQL user names. map Allows mapping from client principals to database user names. See User Name Maps for details. For a GSSAPI/Kerberos principal, such as username@EXAMPLE.COM (or, less commonly, username/hostbased@EXAMPLE.COM ), the user name used for mapping is username@EXAMPLE.COM (or username/hostbased@EXAMPLE.COM , respectively), unless include_realm has been set to 0, in which case username (or username/hostbased ) is what is seen as the system user name when mapping. krb_realm Sets the realm to match user principal names against. If this parameter is set, only users of that realm will be accepted. If it is not set, users of any realm can connect, subject to whatever user name mapping is done. In addition to these settings, which can be different for different pg_hba.conf entries, there is the server-wide krb_caseins_users configuration parameter. If that is set to true, client principals are matched to user map entries case-insensitively. krb_realm , if set, is also matched case-insensitively.

## draft-4a08f22879a56114

Which dimension of a multidimensional array does array_shuffle randomize in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) array_shuffle ( anyarray ) anyarray Randomly shuffles the first dimension of the array.

### Top three retrieved
1. `chunk-f0d18a2b666b31ccd937d65f9ff9229dd15bc0af1c6faf527853cec44adce24f` — pg-16; score=1.235363, dense=0.706140, sparse=0.000000, rerank=1.235363483428955

> Arrays PostgreSQL allows columns of a table to be defined as variable-length multidimensional arrays. Arrays of any built-in or user-defined base type, enum type, composite type, range type, or domain can be created.

2. `chunk-9a90e98bfaacc5e2130106701597ee9ad8be7b6919c112e765ad3eade321d050` — pg-16; score=0.750074, dense=0.684381, sparse=0.000000, rerank=0.750074028968811

> conforms to the SQL standard by using the keyword ARRAY , can be used for one-dimensional arrays. pay_by_quarter could have been defined as: Or, if no array size is to be specified: As before, however, PostgreSQL does not enforce the size restriction in any case.

3. `chunk-ce24d3f9f82a0a70ac799d013f9a94e600e4ed219b906c36705a4d9689a7ded6` — pg-16; score=0.065708, dense=0.714194, sparse=0.000000, rerank=0.06570780277252197

> Changes Guard against unexpected dimensions of oidvector / int2vector (Tom Lane) § These data types are expected to be 1-dimensional arrays containing no nulls, but there are cast pathways that permit violating those expectations. Add checks to some functions that were depending on those expectations without verifying them, and could misbehave in consequence. The PostgreSQL Project thanks Altan Birler for reporting this problem. (CVE-2026-2003) Harden selectivity estimators against being attached to operators that accept unexpected data types (Tom Lane) § § § contrib/intarray contained a selectivity estimation function that could be abused for arbitrary code execution, because it did not check that its input was of the expected data type. Third-party extensions should check for similar hazards and add defenses using the technique intarray now uses. Since such extension fixes will take time, we now require superuser privilege to attach a non-built-in selectivity estimator to an operator. The PostgreSQL Project thanks Daniel Firer, as part of zeroday.cloud, for reporting this problem. (CVE-2026-2004) Fix buffer overrun in contrib/pgcrypto 's PGP decryption functions (Michael Paquier) § Decrypting a crafted message with an overlength session key caused a buffer overrun, with consequences as bad as arbitrary code execution. The PostgreSQL Project thanks Team Xint Code, as part of zeroday.cloud, for reporting this problem. (CVE-2026-2005) Fix inadequate validation of multibyte character lengths (Thomas Munro,
