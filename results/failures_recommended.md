# Worst test failures: recommended

DEV-selected system or fixed DEV-derived combined arm. Showing 30 of 47 failures.
Ranking: all-quotes@10, Recall@10, nDCG@10, MRR ascending; then ID.

## draft-33d8c19a2a6a932d

What is the maximum size of one pg_largeobject.data value?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) data bytea Actual data stored in the large object. This will never be more than LOBLKSIZE bytes and might be less.

### Top three retrieved
1. `chunk-006cbb7bc5add7256d761b85457c7544eeeafa8e73e18e97b992d80c2cba1080` — pg-15; score=1.000000, dense=0.809760, sparse=23.997541, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

2. `chunk-61e357df06adaa29a4cf6da9f325363b17f4d2cc36c5fb14b547aebd4c27856a` — pg-16; score=1.000000, dense=0.809760, sparse=23.997541, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

3. `chunk-7030d3387276a19728f0806066578ef33be22c4946369d8afe8885e40c9fa50a` — pg-17; score=1.000000, dense=0.809760, sparse=23.997541, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

## draft-9b1f37bc7842b40e

Must the ECDH exchange curve match the curve of the server's elliptic-curve key?

**Category:** text gap. **Reason:** No authorized, version-valid chunk contains a whole evidence quote.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key.

### Top three retrieved
1. `chunk-1516438718b7513bfd977d04dd2afed0941fe3834c835381deba48e8a702508a` — pg-17; score=0.981968, dense=0.735613, sparse=49.835055, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

2. `chunk-5eb8f088a27537161214049d6e1af3cbf51e833d78773287d7864d13cae3def4` — pg-16; score=0.981968, dense=0.735613, sparse=49.835055, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

3. `chunk-7db320984913426c010575bf8fd4f79e99b38a5a603cdc29ae591524251088c6` — pg-15; score=0.981968, dense=0.735613, sparse=49.835055, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

## draft-a2cf6aa49912f6e7

When does bool_or return true in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bool_or ( boolean ) boolean Returns true if any non-null input value is true, otherwise false.
- (pg-16) bool_or ( boolean ) boolean Returns true if any non-null input value is true, otherwise false.

### Top three retrieved
1. `chunk-2361d4168e2d31e3ee1e448c83269bdb731d4b3a1263c8d1054f0852f5894ae9` — pg-15; score=0.943304, dense=0.756914, sparse=20.916121, rerank=None

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

2. `chunk-d36f151f4a60dbc8dc70ef0b26546747f657353b4e2bb40f420e2be9282008e8` — pg-17; score=0.943304, dense=0.756914, sparse=20.916121, rerank=None

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

3. `chunk-d9c5f9047dba883af7c556147a557304d8e7d9b21bca41af46a2d2caf4975e5b` — pg-16; score=0.943304, dense=0.756914, sparse=20.916121, rerank=None

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

## draft-d1b8f6b5aa7eddfa

When does bool_and return true in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bool_and ( boolean ) boolean Returns true if all non-null input values are true, otherwise false.
- (pg-16) bool_and ( boolean ) boolean Returns true if all non-null input values are true, otherwise false.

### Top three retrieved
1. `chunk-2361d4168e2d31e3ee1e448c83269bdb731d4b3a1263c8d1054f0852f5894ae9` — pg-15; score=0.987247, dense=0.757129, sparse=20.916121, rerank=None

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

2. `chunk-d36f151f4a60dbc8dc70ef0b26546747f657353b4e2bb40f420e2be9282008e8` — pg-17; score=0.987247, dense=0.757129, sparse=20.916121, rerank=None

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

3. `chunk-d9c5f9047dba883af7c556147a557304d8e7d9b21bca41af46a2d2caf4975e5b` — pg-16; score=0.987247, dense=0.757129, sparse=20.916121, rerank=None

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

## draft-dadefc52fd565605

What OpenSSL curve name is the default for ssl_ecdh_curve?

**Category:** text gap. **Reason:** No authorized, version-valid chunk contains a whole evidence quote.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 .

### Top three retrieved
1. `chunk-1516438718b7513bfd977d04dd2afed0941fe3834c835381deba48e8a702508a` — pg-17; score=0.973007, dense=0.768774, sparse=50.220235, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

2. `chunk-5eb8f088a27537161214049d6e1af3cbf51e833d78773287d7864d13cae3def4` — pg-16; score=0.973007, dense=0.768774, sparse=50.220235, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

3. `chunk-7db320984913426c010575bf8fd4f79e99b38a5a603cdc29ae591524251088c6` — pg-15; score=0.973007, dense=0.768774, sparse=50.220235, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

## draft-dee2728be3a4e6aa

What is the return type of count(*) in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) count ( * ) bigint Computes the number of input rows.
- (pg-16) count ( * ) bigint Computes the number of input rows.

### Top three retrieved
1. `chunk-19ce536d81f9f2e4a0840b38cc4575ce1259723c2933c6d0b72fc83b8b82c146` — pg-16; score=0.750000, dense=0.000000, sparse=22.470789, rerank=None

> 1, 2, 9, 11, and 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, 15, and 16 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2023. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2023. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2023 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if

2. `chunk-bdbed1a0703466d4547441f4e516b6d9c3d433275fee2c9c2469525489adba7d` — pg-17; score=0.750000, dense=0.000000, sparse=22.470789, rerank=None

> 1, 2, 9, 11, and 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, 15, and 16 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2023. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2023. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2023 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if

3. `chunk-23e0a51180b1e0761f149e3e1a396a11c6a85bf4c8edb7a6db8fc334bd44ddc7` — pg-16; score=0.699693, dense=0.000000, sparse=20.963544, rerank=None

> Return Value The function returns the row(s) produced by the query. Since dblink can be used with any query, it is declared to return record , rather than specifying any particular set of columns. This means that you must specify the expected set of columns in the calling query — otherwise PostgreSQL would not know what to expect. Here is an example: The alias part of the FROM clause must specify the column names and types that the function will return. (Specifying column names in an alias is actually standard SQL syntax, but specifying column types is a PostgreSQL extension.) This allows the system to understand what * should expand to, and what proname in the WHERE clause refers to, in advance of trying to execute the function. At run time, an error will be thrown if the actual query result from the remote database does not have the same number of columns shown in the FROM clause. The column names need not match, however, and dblink does not insist on exact type matches either. It will succeed so long as the returned data strings are valid input for the column type declared in the FROM clause.

## draft-df61a1a2e6822bb7

What does cardinality return for an empty array in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) cardinality ( anyarray ) integer Returns the total number of elements in the array, or 0 if the array is empty.
- (pg-16) cardinality ( anyarray ) integer Returns the total number of elements in the array, or 0 if the array is empty.

### Top three retrieved
1. `chunk-c60fe33dccc0af5bebc3a77e2495f1f63a4ad71ae63934fcc96d624891c10813` — pg-15; score=0.826397, dense=0.736751, sparse=19.275642, rerank=None

> transactional logical replication message (Tomas Vondra) § Avoid locale sensitivity when processing regular expression escapes (Jeff Davis) § A backslash followed by a non-ASCII character could sometimes cause an assertion failure, depending on the prevailing locale. Avoid trying to write an empty WAL record in log_newpage_range() when the last few pages in the specified range are empty (Matthias van de Meent) § It is not entirely clear whether this case is reachable in released branches, but if it is then an assertion failure could occur. Fix session-lifespan memory leakage in plpgsql DO blocks that use cast expressions (Ajit Awekar, Tom Lane) § Tighten array dimensionality checks when converting Perl list structures to multi-dimensional SQL arrays (Tom Lane) § plperl could misbehave when the nesting of sub-lists is inconsistent so that the data does not represent a rectangular array of values. Such cases now produce errors, but previously they could result in a crash or garbage output. Tighten array dimensionality checks when converting Python list structures to multi-dimensional SQL arrays (Tom Lane) § § plpython could misbehave when dealing with empty sub-lists, or when the nesting of sub-lists is inconsistent so that the data does not represent a rectangular array of values. The former should result in an empty output array, and the latter in an error. But some cases resulted

2. `chunk-19ce536d81f9f2e4a0840b38cc4575ce1259723c2933c6d0b72fc83b8b82c146` — pg-16; score=0.750000, dense=0.000000, sparse=24.714966, rerank=None

> 1, 2, 9, 11, and 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, 15, and 16 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2023. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2023. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2023 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if

3. `chunk-bdbed1a0703466d4547441f4e516b6d9c3d433275fee2c9c2469525489adba7d` — pg-17; score=0.750000, dense=0.000000, sparse=24.714966, rerank=None

> 1, 2, 9, 11, and 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, 15, and 16 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2023. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2023. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2023 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if

## draft-3abee3e4240c30d3

What is the default work_mem in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes. The default value is four megabytes ( 4MB ).
- (pg-16) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes. The default value is four megabytes ( 4MB ).

### Top three retrieved
1. `chunk-7bb0bbd093fbf56955c694cf4c38db5d8dd7ac3aaf606394f28f9ff5a2200ea9` — pg-17; score=0.874879, dense=0.742120, sparse=28.269560, rerank=None

> where work_mem has already been increased to 40MB or more. maintenance_work_mem ( integer ) Specifies the maximum amount of memory to be used by maintenance operations, such as VACUUM , CREATE INDEX , and ALTER TABLE ADD FOREIGN KEY . If this value is specified without units, it is taken as kilobytes. It defaults to 64 megabytes ( 64MB ). Since only one of these operations can be executed at a time by a database session, and an installation normally doesn't have many of them running concurrently, it's safe to set this value significantly larger than work_mem . Larger settings might improve performance for vacuuming and for restoring database dumps. Note that when autovacuum runs, up to autovacuum_max_workers times this memory may be allocated, so be careful not to set the default value too high. It may be useful to control for this by separately setting autovacuum_work_mem . autovacuum_work_mem ( integer ) Specifies the maximum amount of memory to be used by each autovacuum worker process. If this value is specified without units, it is taken as kilobytes. It defaults to -1, indicating that the value of maintenance_work_mem should be used instead. The setting has no effect on the behavior of VACUUM when run in other contexts. This parameter can only be set in the postgresql.conf file or on the

2. `chunk-5066d3bd1c7ab8a2f2d8cbc21b1103a34206a2a288f086058e72e274cda87abd` — pg-15; score=0.839664, dense=0.763596, sparse=26.422175, rerank=None

> $ postgres -c work_mem=1234 $ postgres --work-mem=1234

3. `chunk-836c3010843efb86dc749eb8cde386937d30a110febb508110a0021448c1f5d1` — pg-17; score=0.839664, dense=0.763596, sparse=26.422175, rerank=None

> $ postgres -c work_mem=1234 $ postgres --work-mem=1234

## draft-7aba123f3dd8b9f6

What does defaclnamespace = 0 indicate in pg_default_acl?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-16) defaclnamespace oid (references pg_namespace.oid) The OID of the namespace associated with this entry, or zero if none

### Top three retrieved
1. `chunk-497263c216e671ac118ca27f6da0d32df665113296215fb4de41e8142573ae60` — pg-15; score=1.000000, dense=0.768639, sparse=45.129827, rerank=None

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

2. `chunk-da6d3c3daae1d20227cac5402abe455ddc35b88b4b474f42af8724ea34dec1f5` — pg-16; score=1.000000, dense=0.768639, sparse=45.129827, rerank=None

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

3. `chunk-ecb07ce2d8f7a6ba484992fa9abb51168effa59591154263b56051dcd2828dc7` — pg-17; score=1.000000, dense=0.768639, sparse=45.129827, rerank=None

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

## draft-51a8ac7c7fbf24a6

What does amtype = i mean in pg_am?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) amtype char t = table (including materialized views), i = index.

### Top three retrieved
1. `chunk-28519f7eb362bcdbaa90205b0118b69183eb7361f4eacfdd2f2e733686e4fc46` — pg-17; score=0.954744, dense=0.715740, sparse=24.602397, rerank=None

> SELECT am.amname AS index_method, opc.opcname AS opclass_name, opc.opcintype::regtype AS indexed_type, opc.opcdefault AS is_default FROM pg_am am, pg_opclass opc WHERE opc.opcmethod = am.oid ORDER BY index_method, opclass_name;

2. `chunk-e146379eff239c4647bc09f7f2fb4d6f5a5451bf4e032a39a53f2658a3578540` — pg-15; score=0.954744, dense=0.715740, sparse=24.602397, rerank=None

> SELECT am.amname AS index_method, opc.opcname AS opclass_name, opc.opcintype::regtype AS indexed_type, opc.opcdefault AS is_default FROM pg_am am, pg_opclass opc WHERE opc.opcmethod = am.oid ORDER BY index_method, opclass_name;

3. `chunk-ed041b3ff31c812ceac3ac1ded17578f3d15d1dd83ce51b6224f1e0ac0e18f99` — pg-16; score=0.954744, dense=0.715740, sparse=24.602397, rerank=None

> SELECT am.amname AS index_method, opc.opcname AS opclass_name, opc.opcintype::regtype AS indexed_type, opc.opcdefault AS is_default FROM pg_am am, pg_opclass opc WHERE opc.opcmethod = am.oid ORDER BY index_method, opclass_name;

## draft-7f9ef8ca7db593fa

What is the customary filename selected by hba_file?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) hba_file ( string ) Specifies the configuration file for host-based authentication (customarily called pg_hba.conf ).

### Top three retrieved
1. `chunk-3d24696d8bf22df17c9d499baa02c736f092adc5f797dfb01435aef4d45d73c5` — pg-17; score=0.993327, dense=0.733305, sparse=23.997900, rerank=None

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The pg_hba.conf file is read on start-up and when the main server process receives a SIGHUP signal. If you edit the file on an active system, you will need to signal the postmaster (using pg_ctl reload , calling the SQL function pg_reload_conf() , or using kill -HUP ) to make it re-read the file. The preceding statement is not true on Microsoft Windows: there, any changes in the pg_hba.conf file are immediately applied by subsequent new connections. The system view pg_hba_file_rules can be helpful for pre-testing changes to the pg_hba.conf file, or for diagnosing problems if loading of the file did not have the desired effects. Rows in the view with non-null error fields indicate problems in the corresponding lines of the file. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the

2. `chunk-b8f76b4a73b8336b8d1f1b8849c85e4a8ab4c21a64f334f6319930eae60ad559` — pg-15; score=0.961061, dense=0.753416, sparse=22.751975, rerank=None

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the next line by ending the line with a backslash. (Backslashes are not special except at the end of a line.) A record is made up of a number of fields which are separated by spaces and/or tabs. Fields can contain white space if the field value is double-quoted. Quoting one of the keywords in a database, user, or address field (e.g., all or replication ) makes the word lose its special meaning, and just match a database, user, or host with that name. Backslash line continuation applies even within quoted text or comments. Each record specifies a connection type, a client IP address range (if relevant for the connection type), a database name, a user name, and the authentication method to be used

3. `chunk-67911986d3b2b9cc75a7cb444cd329061fd2defb1e88be726ccdaf3ef765a079` — pg-16; score=0.958574, dense=0.745920, sparse=22.751975, rerank=None

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the next line by ending the line with a backslash. (Backslashes are not special except at the end of a line.) A record is made up of a number of fields which are separated by spaces and/or tabs. Fields can contain white space if the field value is double-quoted. Quoting one of the keywords in a database, user, or address field (e.g., all or replication ) makes the word lose its special meaning, and just match a database, user, or host with that name. Backslash line continuation applies even within quoted text or comments. Each authentication record specifies a connection type, a client IP address range (if relevant for the connection type), a database name, a user name, and the authentication method to be

## draft-32068527036ef646

Which setting selects the configuration file for user-name mapping?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ident_file ( string ) Specifies the configuration file for user name mapping (customarily called pg_ident.conf ).

### Top three retrieved
1. `chunk-bd85516efd5b74b2d6611b3e65527f94d9dde3a0ca6ea87ff2ba6684e323f0ef` — pg-16; score=0.940612, dense=0.785943, sparse=26.056438, rerank=None

> An Example pg_ident.conf File When using an external authentication system such as Ident or GSSAPI, the name of the operating system user that initiated the connection might not be the same as the database user (role) that is to be used. In this case, a user name map can be applied to map the operating system user name to a database user. To use user name mapping, specify map = map-name in the options field in pg_hba.conf . This option is supported for all authentication methods that receive external user names. Since different mappings might be needed for different connections, the name of the map to be used is specified in the map-name parameter in pg_hba.conf to indicate which map to use for each individual connection. User name maps are defined in the ident map file, which by default is named pg_ident.conf and is stored in the cluster's data directory. (It is possible to place the map file elsewhere, however; see the ident_file configuration parameter.) The ident map file contains lines of the general forms: Comments, whitespace and line continuations are handled in the same way as in pg_hba.conf . The map-name is an arbitrary name that will be used to refer to this mapping in pg_hba.conf . The other two fields specify an operating system user name and a

2. `chunk-d68e87ab36622009ffec71330e6aaacc0ab3df3fd29c6f663182f8a6a65be0cf` — pg-17; score=0.940612, dense=0.785943, sparse=26.056438, rerank=None

> An Example pg_ident.conf File When using an external authentication system such as Ident or GSSAPI, the name of the operating system user that initiated the connection might not be the same as the database user (role) that is to be used. In this case, a user name map can be applied to map the operating system user name to a database user. To use user name mapping, specify map = map-name in the options field in pg_hba.conf . This option is supported for all authentication methods that receive external user names. Since different mappings might be needed for different connections, the name of the map to be used is specified in the map-name parameter in pg_hba.conf to indicate which map to use for each individual connection. User name maps are defined in the ident map file, which by default is named pg_ident.conf and is stored in the cluster's data directory. (It is possible to place the map file elsewhere, however; see the ident_file configuration parameter.) The ident map file contains lines of the general forms: Comments, whitespace and line continuations are handled in the same way as in pg_hba.conf . The map-name is an arbitrary name that will be used to refer to this mapping in pg_hba.conf . The other two fields specify an operating system user name and a

3. `chunk-ee8b2fbf8085c7c99a3b401d07dad33623993fdd81d9ac948c3b49c550820dcf` — pg-15; score=0.940468, dense=0.785489, sparse=26.056438, rerank=None

> An Example pg_ident.conf File When using an external authentication system such as Ident or GSSAPI, the name of the operating system user that initiated the connection might not be the same as the database user (role) that is to be used. In this case, a user name map can be applied to map the operating system user name to a database user. To use user name mapping, specify map = map-name in the options field in pg_hba.conf . This option is supported for all authentication methods that receive external user names. Since different mappings might be needed for different connections, the name of the map to be used is specified in the map-name parameter in pg_hba.conf to indicate which map to use for each individual connection. User name maps are defined in the ident map file, which by default is named pg_ident.conf and is stored in the cluster's data directory. (It is possible to place the map file elsewhere, however; see the ident_file configuration parameter.) The ident map file contains lines of the general form: Comments, whitespace and line continuations are handled in the same way as in pg_hba.conf . The map-name is an arbitrary name that will be used to refer to this mapping in pg_hba.conf . The other two fields specify an operating system user name and a

## draft-d6a79ce1778ec9b4

What does array_upper(ARRAY[1,8,3,7], 1) return in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) array_upper ( anyarray, integer ) integer Returns the upper bound of the requested array dimension. array_upper(ARRAY[1,8,3,7], 1) 4
- (pg-16) array_upper ( anyarray, integer ) integer Returns the upper bound of the requested array dimension. array_upper(ARRAY[1,8,3,7], 1) 4

### Top three retrieved
1. `chunk-410255fcbf9b92b62fe0564c658730bd86f4a4a9f7f96ebb3b740181017d4134` — pg-16; score=0.750000, dense=0.000000, sparse=35.212194, rerank=None

> postgres=# SELECT * FROM pg_freespace('foo'); blkno | avail -------+------- 0 | 0 1 | 0 2 | 0 3 | 32 4 | 704 5 | 704 6 | 704 7 | 1216 8 | 704 9 | 704 10 | 704 11 | 704 12 | 704 13 | 704 14 | 704 15 | 704 16 | 704 17 | 704 18 | 704 19 | 3648 (20 rows) postgres=# SELECT * FROM pg_freespace('foo', 7); pg_freespace -------------- 1216 (1 row)

2. `chunk-982e73cee55eb327c7618354722561f2a57581ec8380c284e7f40fa25b0b4819` — pg-17; score=0.750000, dense=0.000000, sparse=35.212194, rerank=None

> postgres=# SELECT * FROM pg_freespace('foo'); blkno | avail -------+------- 0 | 0 1 | 0 2 | 0 3 | 32 4 | 704 5 | 704 6 | 704 7 | 1216 8 | 704 9 | 704 10 | 704 11 | 704 12 | 704 13 | 704 14 | 704 15 | 704 16 | 704 17 | 704 18 | 704 19 | 3648 (20 rows) postgres=# SELECT * FROM pg_freespace('foo', 7); pg_freespace -------------- 1216 (1 row)

3. `chunk-dbd3c9f5171e3a4bb84afeb0c3678226c322e446d1961dac09ed8ff0eccb0cf5` — pg-15; score=0.750000, dense=0.000000, sparse=35.212194, rerank=None

> postgres=# SELECT * FROM pg_freespace('foo'); blkno | avail -------+------- 0 | 0 1 | 0 2 | 0 3 | 32 4 | 704 5 | 704 6 | 704 7 | 1216 8 | 704 9 | 704 10 | 704 11 | 704 12 | 704 13 | 704 14 | 704 15 | 704 16 | 704 17 | 704 18 | 704 19 | 3648 (20 rows) postgres=# SELECT * FROM pg_freespace('foo', 7); pg_freespace -------------- 1216 (1 row)

## draft-832a9b9cbacbceba

Which predefined role lets a user with database CREATE permission issue CREATE SUBSCRIPTION in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) pg_create_subscription | Allow users with CREATE permission on the database to issue CREATE SUBSCRIPTION.

### Top three retrieved
1. `chunk-70c178fe2cfd0ebb0602c6fabcb0ed0de35a7833edd44d6e0c69e8def0c75dbc` — pg-16; score=0.984801, dense=0.784970, sparse=37.936402, rerank=None

> Privileges Add predefined role pg_create_subscription with permission to create subscriptions (Robert Haas) § Allow subscriptions to not require passwords (Robert Haas) § § § This is accomplished with the option password_required=false . Simplify permissions for LOCK TABLE (Jeff Davis) § Previously a user's ability to perform LOCK TABLE at various lock levels was limited to the lock levels required by the commands they had permission to execute on the table. For example, someone with UPDATE permission could perform all lock levels except ACCESS SHARE , even though it was a lesser lock level. Now users can issue lesser lock levels if they already have permission for greater lock levels. Allow ALTER GROUP group_name ADD USER user_name to be performed with ADMIN OPTION (Robert Haas) § Previously CREATEROLE permission was required. Allow GRANT to use WITH ADMIN TRUE / FALSE syntax (Robert Haas) § Previously only the WITH ADMIN OPTION syntax was supported. Allow roles that create other roles to automatically inherit the new role's rights or the ability to SET ROLE to the new role (Robert Haas, Shi Yu) § § This is controlled by server variable createrole_self_grant . Prevent users from changing the default privileges of non-inherited roles (Robert Haas) § This is now only allowed for inherited roles. When granting role membership, require the granted-by role to be

2. `chunk-03e8644fe74ed7abe75751425d34b7eb18b03478e1d37cfd32c57b8ccdf6436e` — pg-16; score=0.801370, dense=0.768435, sparse=28.908280, rerank=None

> on the table. To add all tables in schema to a publication, the user must be a superuser. To create a publication that publishes all tables or all tables in schema automatically, the user must be a superuser. There are currently no privileges on publications. Any subscription (that is able to connect) can access any publication. Thus, if you intend to hide some information from particular subscribers, such as by using row filters or column lists, or by not adding the whole table to the publication, be aware that other publications in the same database could expose the same information. Publication privileges might be added to PostgreSQL in the future to allow for finer-grained access control. To create a subscription, the user must have the privileges of the the pg_create_subscription role, as well as CREATE privileges on the database. The subscription apply process will, at a session level, run with the privileges of the subscription owner. However, when performing an insert, update, delete, or truncate operation on a particular table, it will switch roles to the table owner and perform the operation with the table owner's privileges. This means that the subscription owner needs to be able to SET ROLE to each role that owns a replicated table. If the subscription has been configured with run_as_owner = true , then

3. `chunk-e7cbd567c7bd82c77b53407c18414c404b61d3cc0a26abc1ce52319e811ebcf7` — pg-16; score=0.782955, dense=0.815109, sparse=27.270641, rerank=None

> Description createuser creates a new PostgreSQL user (or more precisely, a role). Only superusers and users with CREATEROLE privilege can create new users, so createuser must be invoked by someone who can connect as a superuser or a user with CREATEROLE privilege. If you wish to create a role with the SUPERUSER , REPLICATION , or BYPASSRLS privilege, you must connect as a superuser, not merely with CREATEROLE privilege. Being a superuser implies the ability to bypass all access permission checks within the database, so superuser access should not be granted lightly. CREATEROLE also conveys very extensive privileges . createuser is a wrapper around the SQL command CREATE ROLE . There is no effective difference between creating users via this utility and via other methods for accessing the server.

## draft-63730cc51a247416

Which objects receive changed privileges after modifying a pg_default_acl entry with defaclobjtype = S?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) defaclobjtype char Type of object this entry is for: r = relation (table, view), S = sequence, f = function, T = type, n = schema
- (pg-17) pg_default_acl is only consulted during object creation.

### Top three retrieved
1. `chunk-497263c216e671ac118ca27f6da0d32df665113296215fb4de41e8142573ae60` — pg-15; score=1.000000, dense=0.813160, sparse=54.007953, rerank=None

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

2. `chunk-da6d3c3daae1d20227cac5402abe455ddc35b88b4b474f42af8724ea34dec1f5` — pg-16; score=1.000000, dense=0.813160, sparse=54.007953, rerank=None

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

3. `chunk-ecb07ce2d8f7a6ba484992fa9abb51168effa59591154263b56051dcd2828dc7` — pg-17; score=1.000000, dense=0.813160, sparse=54.007953, rerank=None

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

## draft-97bcb36324c56d2a

What number identifies the first page of a large object in pg_largeobject?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) pageno int4 Page number of this page within its large object (counting from zero)

### Top three retrieved
1. `chunk-006cbb7bc5add7256d761b85457c7544eeeafa8e73e18e97b992d80c2cba1080` — pg-15; score=1.000000, dense=0.843869, sparse=51.593954, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

2. `chunk-61e357df06adaa29a4cf6da9f325363b17f4d2cc36c5fb14b547aebd4c27856a` — pg-16; score=1.000000, dense=0.843869, sparse=51.593954, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

3. `chunk-7030d3387276a19728f0806066578ef33be22c4946369d8afe8885e40c9fa50a` — pg-17; score=1.000000, dense=0.843869, sparse=51.593954, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

## draft-e5b5f0b94a5943be

Which setting names the server's certificate-authority file?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ca_file ( string ) Specifies the name of the file containing the SSL server certificate authority (CA).

### Top three retrieved
1. `chunk-7385e8cf22bf0af12a1a47b5d70b5a43df5cbc135d0548af564d37bcfc16b19b` — pg-17; score=0.984975, dense=0.740366, sparse=33.583707, rerank=None

> | File | Contents | Effect | | --- | --- | --- | | ssl_cert_file ($PGDATA/server.crt) | server certificate | sent to client to indicate server's identity | | ssl_key_file ($PGDATA/server.key) | server private key | proves server certificate was sent by the owner; does not indicate certificate owner is trustworthy | | ssl_ca_file | trusted certificate authorities | checks that client certificate is signed by a trusted certificate authority | | ssl_crl_file | certificates revoked by certificate authorities | client certificate must not be on this list |

2. `chunk-b67a28ea116696e7710fe1f28bb6c6d4d384d4b6eb0b1c5ee6722df1a7164b64` — pg-16; score=0.984975, dense=0.740366, sparse=33.583707, rerank=None

> | File | Contents | Effect | | --- | --- | --- | | ssl_cert_file ($PGDATA/server.crt) | server certificate | sent to client to indicate server's identity | | ssl_key_file ($PGDATA/server.key) | server private key | proves server certificate was sent by the owner; does not indicate certificate owner is trustworthy | | ssl_ca_file | trusted certificate authorities | checks that client certificate is signed by a trusted certificate authority | | ssl_crl_file | certificates revoked by certificate authorities | client certificate must not be on this list |

3. `chunk-ed02b66fcb953ea322b20775bf33298bca5247972a2257c0b1b48a93eb0cf60f` — pg-15; score=0.984975, dense=0.740366, sparse=33.583707, rerank=None

> | File | Contents | Effect | | --- | --- | --- | | ssl_cert_file ($PGDATA/server.crt) | server certificate | sent to client to indicate server's identity | | ssl_key_file ($PGDATA/server.key) | server private key | proves server certificate was sent by the owner; does not indicate certificate owner is trustworthy | | ssl_ca_file | trusted certificate authorities | checks that client certificate is signed by a trusted certificate authority | | ssl_crl_file | certificates revoked by certificate authorities | client certificate must not be on this list |

## draft-529a81ca28099b25

Is Partial Mode supported by string_agg in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) string_agg ( value text, delimiter text ) text string_agg ( value bytea, delimiter bytea ) bytea Concatenates the non-null input values into a string. Each value after the first is preceded by the corresponding delimiter (if it's not null). | Yes

### Top three retrieved
1. `chunk-557d8850f5bad9e6709ba512b164f320b2a43f45f44442e64530ba7f20a3d484` — pg-16; score=0.979976, dense=0.771070, sparse=26.887071, rerank=None

> SELECT string_agg(a, ',' ORDER BY a) FROM table;

2. `chunk-9deb90a5fa2ac2c8a5aa0b4d07645861829f3da95f52836dac8563ab3c7bef8e` — pg-16; score=0.976057, dense=0.772750, sparse=26.722811, rerank=None

> SELECT string_agg(a ORDER BY a, ',') FROM table; -- incorrect

3. `chunk-8908fa26e794467b20d3f73e1de7a855254a1873b19a1936a59b028a09daaf9e` — pg-16; score=0.873751, dense=0.761202, sparse=23.094927, rerank=None

> , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given to these aggregates. Users accustomed to working with other SQL database management systems might be disappointed by the performance of the count aggregate when it is applied to the entire

## draft-00f9bb9ebb902fbc

Which dimension does trim_array shorten in a multidimensional array in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) trim_array ( array anyarray, n integer ) anyarray Trims an array by removing the last n elements. If the array is multidimensional, only the first dimension is trimmed.
- (pg-16) trim_array ( array anyarray, n integer ) anyarray Trims an array by removing the last n elements. If the array is multidimensional, only the first dimension is trimmed.

### Top three retrieved
1. `chunk-694386ae933c4ccbd7df98547a55077dc2bb48f5edadaf19dd5feb4cf3979e3d` — pg-17; score=0.761151, dense=0.743631, sparse=20.903856, rerank=None

> Arrays, Lists SQL array values are passed into PL/Python as a Python list. To return an SQL array value out of a PL/Python function, return a Python list: Multidimensional arrays are passed into PL/Python as nested Python lists. A 2-dimensional array is a list of lists, for example. When returning a multi-dimensional SQL array out of a PL/Python function, the inner lists at each level must all be of the same size. For example: Other Python sequences, like tuples, are also accepted for backwards-compatibility with PostgreSQL versions 9.6 and below, when multi-dimensional arrays were not supported. However, they are always treated as one-dimensional arrays, because they are ambiguous with composite types. For the same reason, when a composite type is used in a multi-dimensional array, it must be represented by a tuple, rather than a list. Note that in Python, strings are sequences, which can have undesirable effects that might be familiar to Python programmers:

2. `chunk-697d381610187065d96f107de60c639f4b24670ae7e70e7765e173014d67fdc3` — pg-15; score=0.761151, dense=0.743631, sparse=20.903856, rerank=None

> Arrays, Lists SQL array values are passed into PL/Python as a Python list. To return an SQL array value out of a PL/Python function, return a Python list: Multidimensional arrays are passed into PL/Python as nested Python lists. A 2-dimensional array is a list of lists, for example. When returning a multi-dimensional SQL array out of a PL/Python function, the inner lists at each level must all be of the same size. For example: Other Python sequences, like tuples, are also accepted for backwards-compatibility with PostgreSQL versions 9.6 and below, when multi-dimensional arrays were not supported. However, they are always treated as one-dimensional arrays, because they are ambiguous with composite types. For the same reason, when a composite type is used in a multi-dimensional array, it must be represented by a tuple, rather than a list. Note that in Python, strings are sequences, which can have undesirable effects that might be familiar to Python programmers:

3. `chunk-9f9080e0d6cf841feda3646d0428b7c90007b4ad62c978a63eca904dbd46d252` — pg-16; score=0.761151, dense=0.743631, sparse=20.903856, rerank=None

> Arrays, Lists SQL array values are passed into PL/Python as a Python list. To return an SQL array value out of a PL/Python function, return a Python list: Multidimensional arrays are passed into PL/Python as nested Python lists. A 2-dimensional array is a list of lists, for example. When returning a multi-dimensional SQL array out of a PL/Python function, the inner lists at each level must all be of the same size. For example: Other Python sequences, like tuples, are also accepted for backwards-compatibility with PostgreSQL versions 9.6 and below, when multi-dimensional arrays were not supported. However, they are always treated as one-dimensional arrays, because they are ambiguous with composite types. For the same reason, when a composite type is used in a multi-dimensional array, it must be represented by a tuple, rather than a list. Note that in Python, strings are sequences, which can have undesirable effects that might be familiar to Python programmers:

## draft-3b18c553103442c0

Which setting selects the configuration file for host-based authentication?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) hba_file ( string ) Specifies the configuration file for host-based authentication (customarily called pg_hba.conf ).

### Top three retrieved
1. `chunk-3d24696d8bf22df17c9d499baa02c736f092adc5f797dfb01435aef4d45d73c5` — pg-17; score=0.922769, dense=0.716873, sparse=30.662895, rerank=None

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The pg_hba.conf file is read on start-up and when the main server process receives a SIGHUP signal. If you edit the file on an active system, you will need to signal the postmaster (using pg_ctl reload , calling the SQL function pg_reload_conf() , or using kill -HUP ) to make it re-read the file. The preceding statement is not true on Microsoft Windows: there, any changes in the pg_hba.conf file are immediately applied by subsequent new connections. The system view pg_hba_file_rules can be helpful for pre-testing changes to the pg_hba.conf file, or for diagnosing problems if loading of the file did not have the desired effects. Rows in the view with non-null error fields indicate problems in the corresponding lines of the file. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the

2. `chunk-bcd56fe484c4fa60608a00b01f9e694128e82f273c22fc61badc8e1eb8925c34` — pg-17; score=0.859903, dense=0.720168, sparse=27.789615, rerank=None

> Options -A authmethod --auth= authmethod This option specifies the default authentication method for local users used in pg_hba.conf ( host and local lines). See The pg_hba.conf File for an overview of valid values. initdb will prepopulate pg_hba.conf entries using the specified authentication method for non-replication as well as replication connections. Do not use trust unless you trust all local users on your system. trust is the default for ease of installation. --auth-host= authmethod This option specifies the authentication method for local users via TCP/IP connections used in pg_hba.conf ( host lines). --auth-local= authmethod This option specifies the authentication method for local users via Unix-domain socket connections used in pg_hba.conf ( local lines). -D directory --pgdata= directory This option specifies the directory where the database cluster should be stored. This is the only information required by initdb , but you can avoid writing it by setting the PGDATA environment variable, which can be convenient since the database server ( postgres ) can find the data directory later by the same variable. -E encoding --encoding= encoding Selects the encoding of the template databases. This will also be the default encoding of any database you create later, unless you override it then. The character sets supported by the PostgreSQL server are described in Supported Character Sets . By default, the template database encoding

3. `chunk-c792920e9f29d855a6f84314dbf9c0e7f5697b27e6ec1c1f78e66b5cdb8ca535` — pg-16; score=0.859903, dense=0.720168, sparse=27.789615, rerank=None

> Options -A authmethod --auth= authmethod This option specifies the default authentication method for local users used in pg_hba.conf ( host and local lines). See The pg_hba.conf File for an overview of valid values. initdb will prepopulate pg_hba.conf entries using the specified authentication method for non-replication as well as replication connections. Do not use trust unless you trust all local users on your system. trust is the default for ease of installation. --auth-host= authmethod This option specifies the authentication method for local users via TCP/IP connections used in pg_hba.conf ( host lines). --auth-local= authmethod This option specifies the authentication method for local users via Unix-domain socket connections used in pg_hba.conf ( local lines). -D directory --pgdata= directory This option specifies the directory where the database cluster should be stored. This is the only information required by initdb , but you can avoid writing it by setting the PGDATA environment variable, which can be convenient since the database server ( postgres ) can find the data directory later by the same variable. -E encoding --encoding= encoding Selects the encoding of the template databases. This will also be the default encoding of any database you create later, unless you override it then. The character sets supported by the PostgreSQL server are described in Supported Character Sets . By default, the template database encoding

## draft-3bbf02c4e418a086

Which bitwise aggregate can checksum an unordered set of values in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bit_xor ( smallint ) smallint bit_xor ( integer ) integer bit_xor ( bigint ) bigint bit_xor ( bit ) bit Computes the bitwise exclusive OR of all non-null input values. Can be useful as a checksum for an unordered set of values.
- (pg-16) bit_xor ( smallint ) smallint bit_xor ( integer ) integer bit_xor ( bigint ) bigint bit_xor ( bit ) bit Computes the bitwise exclusive OR of all non-null input values. Can be useful as a checksum for an unordered set of values.

### Top three retrieved
1. `chunk-3ef50586b55c247e5bbfee8cec73464f2cce545aa0cb39e58fdec9187b27a178` — pg-15; score=0.810555, dense=0.738964, sparse=21.235449, rerank=None

> the record match the stored images. In certain cases (such as hint bits), minor variations are acceptable, and will be ignored. Any unexpected differences will result in a fatal error, terminating recovery. The default value of this setting is the empty string, which disables the feature. It can be set to all to check all records, or to a comma-separated list of resource managers to check only records originating from those resource managers. Currently, the supported resource managers are heap , heap2 , btree , hash , gin , gist , sequence , spgist , brin , and generic . Extensions may define additional resource managers. Only superusers and users with the appropriate SET privilege can change this setting. wal_debug ( boolean ) If on, emit WAL-related debugging output. This parameter is only available if the WAL_DEBUG macro was defined when PostgreSQL was compiled. ignore_checksum_failure ( boolean ) Only has effect if data checksums are enabled. Detection of a checksum failure during a read normally causes PostgreSQL to report an error, aborting the current transaction. Setting ignore_checksum_failure to on causes the system to ignore the failure (but still report a warning), and continue processing. This behavior may cause crashes, propagate or hide corruption, or other serious problems . However, it may allow you to get past the error and retrieve

2. `chunk-a97bf6ba8f281884b10222fca5a6878837f53f3285554788ef693ce4c4806d34` — pg-17; score=0.810266, dense=0.738058, sparse=21.235449, rerank=None

> stored images. In certain cases (such as hint bits), minor variations are acceptable, and will be ignored. Any unexpected differences will result in a fatal error, terminating recovery. The default value of this setting is the empty string, which disables the feature. It can be set to all to check all records, or to a comma-separated list of resource managers to check only records originating from those resource managers. Currently, the supported resource managers are heap , heap2 , btree , hash , gin , gist , sequence , spgist , brin , and generic . Extensions may define additional resource managers. Only superusers and users with the appropriate SET privilege can change this setting. wal_debug ( boolean ) If on, emit WAL-related debugging output. This parameter is only available if the WAL_DEBUG macro was defined when PostgreSQL was compiled. ignore_checksum_failure ( boolean ) Only has effect if data checksums are enabled. Detection of a checksum failure during a read normally causes PostgreSQL to report an error, aborting the current transaction. Setting ignore_checksum_failure to on causes the system to ignore the failure (but still report a warning), and continue processing. This behavior may cause crashes, propagate or hide corruption, or other serious problems . However, it may allow you to get past the error and retrieve undamaged tuples that might

3. `chunk-4eb6f59acb8256025818a9295ab2cca5683081199c2885ad8a430fd21fdf711a` — pg-15; score=0.799198, dense=0.740320, sparse=20.799725, rerank=None

> Aggregate Functions Like most other relational database products, PostgreSQL supports aggregate functions . An aggregate function computes a single result from multiple input rows. For example, there are aggregates to compute the count , sum , avg (average), max (maximum) and min (minimum) over a set of rows. As an example, we can find the highest low-temperature reading anywhere with: If we wanted to know what city (or cities) that reading occurred in, we might try: but this will not work since the aggregate max cannot be used in the WHERE clause. (This restriction exists because the WHERE clause determines which rows will be included in the aggregate calculation; so obviously it has to be evaluated before aggregate functions are computed.) However, as is often the case the query can be restated to accomplish the desired result, here by using a subquery : This is OK because the subquery is an independent computation that computes its own aggregate separately from what is happening in the outer query. Aggregates are also very useful in combination with GROUP BY clauses. For example, we can get the number of readings and the maximum low temperature observed in each city with: which gives us one output row per city. Each aggregate result is computed over the table rows matching that city. We can filter

## draft-826bd7733c5466a3

What happens when auto_explain.log_min_duration is zero?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15']

### Expected evidence
- (pg-15) auto_explain.log_min_duration is the minimum statement execution time, in milliseconds, that will cause the statement's plan to be logged. Setting this to 0 logs all plans.

### Top three retrieved
1. `chunk-564ed25d723855db471b50fe4f7b6dc2e6929428175365d624f82d179936201f` — pg-17; score=0.995607, dense=0.831771, sparse=51.034589, rerank=None

> Configuration Parameters There are several configuration parameters that control the behavior of auto_explain . Note that the default behavior is to do nothing, so you must set at least auto_explain.log_min_duration if you want any results. auto_explain.log_min_duration ( integer ) auto_explain.log_min_duration is the minimum statement execution time, in milliseconds, that will cause the statement's plan to be logged. Setting this to 0 logs all plans. -1 (the default) disables logging of plans. For example, if you set it to 250ms then all statements that run 250ms or longer will be logged. Only superusers can change this setting. auto_explain.log_parameter_max_length ( integer ) auto_explain.log_parameter_max_length controls the logging of query parameter values. A value of -1 (the default) logs the parameter values in full. 0 disables logging of parameter values. A value greater than zero truncates each parameter value to that many bytes. Only superusers can change this setting. auto_explain.log_analyze ( boolean ) auto_explain.log_analyze causes EXPLAIN ANALYZE output, rather than just EXPLAIN output, to be printed when an execution plan is logged. This parameter is off by default. Only superusers can change this setting. When this parameter is on, per-plan-node timing occurs for all statements executed, whether or not they run long enough to actually get logged. This can have an extremely negative impact on performance. Turning off auto_explain.log_timing ameliorates the performance cost, at

2. `chunk-5908f0b8765b4563e6888fb1568dce267692909cded74a45bca8f0bb0250713d` — pg-16; score=0.995607, dense=0.831771, sparse=51.034589, rerank=None

> Configuration Parameters There are several configuration parameters that control the behavior of auto_explain . Note that the default behavior is to do nothing, so you must set at least auto_explain.log_min_duration if you want any results. auto_explain.log_min_duration ( integer ) auto_explain.log_min_duration is the minimum statement execution time, in milliseconds, that will cause the statement's plan to be logged. Setting this to 0 logs all plans. -1 (the default) disables logging of plans. For example, if you set it to 250ms then all statements that run 250ms or longer will be logged. Only superusers can change this setting. auto_explain.log_parameter_max_length ( integer ) auto_explain.log_parameter_max_length controls the logging of query parameter values. A value of -1 (the default) logs the parameter values in full. 0 disables logging of parameter values. A value greater than zero truncates each parameter value to that many bytes. Only superusers can change this setting. auto_explain.log_analyze ( boolean ) auto_explain.log_analyze causes EXPLAIN ANALYZE output, rather than just EXPLAIN output, to be printed when an execution plan is logged. This parameter is off by default. Only superusers can change this setting. When this parameter is on, per-plan-node timing occurs for all statements executed, whether or not they run long enough to actually get logged. This can have an extremely negative impact on performance. Turning off auto_explain.log_timing ameliorates the performance cost, at

3. `chunk-06e0ee74cb7a506fd20611eee95b48f482132e9b44e56ec03981cda446be8851` — pg-15; score=0.970265, dense=0.741342, sparse=51.138704, rerank=None

> # postgresql.conf session_preload_libraries = 'auto_explain' auto_explain.log_min_duration = '3s'

## draft-24083cabffc26972

Does bit_and ignore null inputs in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) Computes the bitwise AND of all non-null input values.
- (pg-16) Computes the bitwise AND of all non-null input values.

### Top three retrieved
1. `chunk-97eec8cb65436e01e1e9468cec070e1fa54a40260344c3eed6ccb5b671a339ba` — pg-15; score=0.750000, dense=0.000000, sparse=29.765900, rerank=None

> File Header The file header consists of 15 bytes of fixed fields, followed by a variable-length header extension area. The fixed fields are: Signature 11-byte sequence PGCOPY\n\377\r\n\0 — note that the zero byte is a required part of the signature. (The signature is designed to allow easy identification of files that have been munged by a non-8-bit-clean transfer. This signature will be changed by end-of-line-translation filters, dropped zero bytes, dropped high bits, or parity changes.) Flags field 32-bit integer bit mask to denote important aspects of the file format. Bits are numbered from 0 ( LSB ) to 31 ( MSB ). Note that this field is stored in network byte order (most significant byte first), as are all the integer fields used in the file format. Bits 16–31 are reserved to denote critical file format issues; a reader should abort if it finds an unexpected bit set in this range. Bits 0–15 are reserved to signal backwards-compatible format issues; a reader should simply ignore any unexpected bits set in this range. Currently only one flag bit is defined, and the rest must be zero: Bit 16 If 1, OIDs are included in the data; if 0, not. Oid system columns are not supported in PostgreSQL anymore, but the format still contains the indicator. Header extension area length 32-bit integer,

2. `chunk-abd596e46d3dfd2903b110c5f7f53bebbfa1a8718e1b232e410e9f6393941bf4` — pg-17; score=0.750000, dense=0.000000, sparse=29.765900, rerank=None

> File Header The file header consists of 15 bytes of fixed fields, followed by a variable-length header extension area. The fixed fields are: Signature 11-byte sequence PGCOPY\n\377\r\n\0 — note that the zero byte is a required part of the signature. (The signature is designed to allow easy identification of files that have been munged by a non-8-bit-clean transfer. This signature will be changed by end-of-line-translation filters, dropped zero bytes, dropped high bits, or parity changes.) Flags field 32-bit integer bit mask to denote important aspects of the file format. Bits are numbered from 0 ( LSB ) to 31 ( MSB ). Note that this field is stored in network byte order (most significant byte first), as are all the integer fields used in the file format. Bits 16–31 are reserved to denote critical file format issues; a reader should abort if it finds an unexpected bit set in this range. Bits 0–15 are reserved to signal backwards-compatible format issues; a reader should simply ignore any unexpected bits set in this range. Currently only one flag bit is defined, and the rest must be zero: Bit 16 If 1, OIDs are included in the data; if 0, not. Oid system columns are not supported in PostgreSQL anymore, but the format still contains the indicator. Header extension area length 32-bit integer,

3. `chunk-f1c55a1888f2a5840cc043d3e95113cfa0d02686ff9dd8cc8717c820e7542a9a` — pg-16; score=0.750000, dense=0.000000, sparse=29.765900, rerank=None

> File Header The file header consists of 15 bytes of fixed fields, followed by a variable-length header extension area. The fixed fields are: Signature 11-byte sequence PGCOPY\n\377\r\n\0 — note that the zero byte is a required part of the signature. (The signature is designed to allow easy identification of files that have been munged by a non-8-bit-clean transfer. This signature will be changed by end-of-line-translation filters, dropped zero bytes, dropped high bits, or parity changes.) Flags field 32-bit integer bit mask to denote important aspects of the file format. Bits are numbered from 0 ( LSB ) to 31 ( MSB ). Note that this field is stored in network byte order (most significant byte first), as are all the integer fields used in the file format. Bits 16–31 are reserved to denote critical file format issues; a reader should abort if it finds an unexpected bit set in this range. Bits 0–15 are reserved to signal backwards-compatible format issues; a reader should simply ignore any unexpected bits set in this range. Currently only one flag bit is defined, and the rest must be zero: Bit 16 If 1, OIDs are included in the data; if 0, not. Oid system columns are not supported in PostgreSQL anymore, but the format still contains the indicator. Header extension area length 32-bit integer,

## draft-519d2a3d29e1d233

Does array_agg retain null scalar inputs in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) array_agg ( anynonarray ) anyarray Collects all the input values, including nulls, into an array.
- (pg-16) array_agg ( anynonarray ) anyarray Collects all the input values, including nulls, into an array.

### Top three retrieved
1. `chunk-aae4c030d027aae9699e88db37910f7cdd407fe1b66a26bd44ee2ec255408fcd` — pg-17; score=0.938387, dense=0.771032, sparse=28.521049, rerank=None

> test_sub=# SELECT array_agg(quote_literal(s.subslotname)) AS slots FROM pg_subscription s WHERE s.subfailover AND s.subslotname IS NOT NULL; slots ------- {'sub1','sub2','sub3'} (1 row)

2. `chunk-5f519f9195c89a59d21c5893518bdf090079ba3852430a9fd05ae490ef42765b` — pg-17; score=0.936128, dense=0.752980, sparse=28.650288, rerank=None

> below. Most aggregate functions ignore null inputs, so that rows in which one or more of the expression(s) yield null are discarded. This can be assumed to be true, unless otherwise specified, for all built-in aggregates. For example, count(*) yields the total number of input rows; count(f1) yields the number of input rows in which f1 is non-null, since count ignores nulls; and count(distinct f1) yields the number of distinct non-null values of f1 . Ordinarily, the input rows are fed to the aggregate function in an unspecified order. In many cases this does not matter; for example, min produces the same result no matter what order it receives the inputs in. However, some aggregate functions (such as array_agg and string_agg ) produce results that depend on the ordering of the input rows. When using such an aggregate, the optional order_by_clause can be used to specify the desired ordering. The order_by_clause has the same syntax as for a query-level ORDER BY clause, as described in Sorting Rows (ORDER BY) , except that its expressions are always just expressions and cannot be output-column names or numbers. For example: Since jsonb only keeps the last matching key, ordering of its keys can be significant: When dealing with multiple-argument aggregate functions, note that the ORDER BY clause goes after all the aggregate arguments.

3. `chunk-2759f0822a788033d79c3140f537e1c3fc78d00f0d4b2a2ae38f7b1d3f05e262` — pg-17; score=0.928874, dense=0.756590, sparse=28.312866, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. While all aggregates below accept an optional ORDER BY clause (as outlined in Aggregate Expressions ), the clause has only been added to aggregates whose output is affected by ordering. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict ,

## draft-05e120c03871ce0e

When can notify_buffers be set in PostgreSQL 17?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: []

### Expected evidence
- (pg-17) notify_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_notify (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 16 . This parameter can only be set at server start.

### Top three retrieved
1. `chunk-f98fa9a1b35aee4676c55f1d07ee3619a7b07c1523f115b0fea59bc6a08128f4` — pg-17; score=0.756624, dense=0.736035, sparse=17.808658, rerank=None

> during recent rounds. The average recent need is multiplied by bgwriter_lru_multiplier to arrive at an estimate of the number of buffers that will be needed during the next round. Dirty buffers are written until there are that many clean, reusable buffers available. (However, no more than bgwriter_lru_maxpages buffers will be written per round.) Thus, a setting of 1.0 represents a just in time policy of writing exactly the number of buffers predicted to be needed. Larger values provide some cushion against spikes in demand, while smaller values intentionally leave writes to be done by server processes. The default is 2.0. This parameter can only be set in the postgresql.conf file or on the server command line. bgwriter_flush_after ( integer ) Whenever more than this amount of data has been written by the background writer, attempt to force the OS to issue these writes to the underlying storage. Doing so will limit the amount of dirty data in the kernel's page cache, reducing the likelihood of stalls when an fsync is issued at the end of a checkpoint, or when the OS writes data back in larger batches in the background. Often that will result in greatly reduced transaction latency, but there also are some cases, especially with workloads that are bigger than shared_buffers , but smaller than the OS's page

2. `chunk-fbd642988423cfc897bfaf06cd0d56f729a7e6a729509498cef8a8bcc28b0353` — pg-17; score=0.750000, dense=0.000000, sparse=25.478822, rerank=None

> Server Configuration Add system variable allow_alter_system to disallow ALTER SYSTEM (Jelte Fennema-Nio, Gabriele Bartolini) § Allow ALTER SYSTEM to set unrecognized custom server variables (Tom Lane) § This is also possible with GRANT ON PARAMETER . Add server variable transaction_timeout to restrict the duration of transactions (Andrey Borodin, Japin Li, Junwang Zhao, Alexander Korotkov) § § § Add a builtin platform-independent collation provider (Jeff Davis) § § § § This supports C and C.UTF-8 collations. Add server variable huge_pages_status to report the use of huge pages by Postgres (Justin Pryzby) § This is useful when huge_pages is set to try . Add server variable to disable event triggers (Daniel Gustafsson) § The setting, event_triggers , allows for the temporary disabling of event triggers for debugging. Allow the SLRU cache sizes to be configured (Andrey Borodin, Dilip Kumar, Alvaro Herrera) § The new server variables are commit_timestamp_buffers , multixact_member_buffers , multixact_offset_buffers , notify_buffers , serializable_buffers , subtransaction_buffers , and transaction_buffers . commit_timestamp_buffers , transaction_buffers , and subtransaction_buffers scale up automatically with shared_buffers .

3. `chunk-4ced3b308ae1589ed905c906cb3856eedfa596a4c479703d1b2a826ef64d3c23` — pg-17; score=0.722600, dense=0.751289, sparse=16.489176, rerank=None

> Asynchronous Notification PostgreSQL offers asynchronous notification via the LISTEN and NOTIFY commands. A client session registers its interest in a particular notification channel with the LISTEN command (and can stop listening with the UNLISTEN command). All sessions listening on a particular channel will be notified asynchronously when a NOTIFY command with that channel name is executed by any session. A payload string can be passed to communicate additional data to the listeners. libpq applications submit LISTEN , UNLISTEN , and NOTIFY commands as ordinary SQL commands. The arrival of NOTIFY messages can subsequently be detected by calling PQnotifies . The function PQnotifies returns the next notification from a list of unhandled notification messages received from the server. It returns a null pointer if there are no pending notifications. Once a notification is returned from PQnotifies , it is considered handled and will be removed from the list of notifications. After processing a PGnotify object returned by PQnotifies , be sure to free it with . It is sufficient to free the PGnotify pointer; the relname and extra fields do not represent separate allocations. (The names of these fields are historical; in particular, channel names need not have anything to do with relation names.) libpq Example Program 2 gives a sample program that illustrates the use of asynchronous notification. PQnotifies does

## draft-1a061285c851d1c0

Does array_agg support Partial Mode in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) | Function Description | Partial Mode | | --- | --- | | any_value ( anyelement ) same as input type Returns an arbitrary value from the non-null input values. | Yes | | array_agg ( anynonarray ) anyarray Collects all the input values, including nulls, into an array. | Yes |

### Top three retrieved
1. `chunk-2f36aa1f580396a671b0332b7dcf3a5e1930c71bd5a2c398b08c006081eb50ae` — pg-16; score=0.809698, dense=0.726781, sparse=27.644917, rerank=None

> CREATE FUNCTION array_agg_transfn(internal, anynonarray) RETURNS internal ...; CREATE FUNCTION array_agg_finalfn(internal, anynonarray) RETURNS anyarray ...; CREATE AGGREGATE array_agg (anynonarray) ( sfunc = array_agg_transfn, stype = internal, finalfunc = array_agg_finalfn, finalfunc_extra );

2. `chunk-9453a072e55cd82e2a8a39e8cea7751ae5e81bbf8f1a28069af6c232b45341ad` — pg-16; score=0.771181, dense=0.757256, sparse=25.301886, rerank=None

> SELECT array_agg(a ORDER BY b DESC) FROM table;

3. `chunk-8b016650fef8bd099dbcd9cfd1de8beb5d2bbf2fad2c975133bc5c32d6b548c8` — pg-16; score=0.750000, dense=0.000000, sparse=36.245541, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully

## draft-39a8f35fc5f9cb13

What happens to null array entries in array_to_string when null_string is omitted in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) array_to_string ( array anyarray, delimiter text , null_string text ) text Converts each array element to its text representation, and concatenates those separated by the delimiter string. If null_string is given and is not NULL, then NULL array entries are represented by that string; otherwise, they are omitted.
- (pg-16) array_to_string ( array anyarray, delimiter text , null_string text ) text Converts each array element to its text representation, and concatenates those separated by the delimiter string. If null_string is given and is not NULL, then NULL array entries are represented by that string; otherwise, they are omitted.

### Top three retrieved
1. `chunk-6560e13f63abd4e6e3a5451dfa771daf888b2a1912c309a93b2cd975764a7fdf` — pg-15; score=0.844003, dense=0.838063, sparse=23.094645, rerank=None

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

2. `chunk-75d6f7845f32cf5b2105aaa47c1bcfbe416391ba5f4f973d1e0ba3d0e6d6e6ae` — pg-17; score=0.844003, dense=0.838063, sparse=23.094645, rerank=None

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

3. `chunk-e96bdd39a5eea04e1d94cad496fb7a45adc7440d5c0425607a7e9fdaf887060f` — pg-16; score=0.844003, dense=0.838063, sparse=23.094645, rerank=None

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

## draft-4b2f4b62ab512fa7

When automatic plan logging samples nested statements, can it select just some nested statements from a call?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15']

### Expected evidence
- (pg-15) auto_explain.sample_rate causes auto_explain to only explain a fraction of the statements in each session. The default is 1, meaning explain all the queries. In case of nested statements, either all will be explained or none.

### Top three retrieved
1. `chunk-6ddaee7cbf778ca607792f50ab7c3f1a9422f805050989f45eeadecbc44f1d5a` — pg-15; score=0.987686, dense=0.754392, sparse=30.549664, rerank=None

> included when an execution plan is logged. This parameter has no effect unless auto_explain.log_analyze is enabled. This parameter is off by default. Only superusers can change this setting. auto_explain.log_verbose ( boolean ) auto_explain.log_verbose controls whether verbose details are printed when an execution plan is logged; it's equivalent to the VERBOSE option of EXPLAIN . This parameter is off by default. Only superusers can change this setting. auto_explain.log_settings ( boolean ) auto_explain.log_settings controls whether information about modified configuration options is printed when an execution plan is logged. Only options affecting query planning with value different from the built-in default value are included in the output. This parameter is off by default. Only superusers can change this setting. auto_explain.log_format ( enum ) auto_explain.log_format selects the EXPLAIN output format to be used. The allowed values are text , xml , json , and yaml . The default is text. Only superusers can change this setting. auto_explain.log_level ( enum ) auto_explain.log_level selects the log level at which auto_explain will log the query plan. Valid values are DEBUG5 , DEBUG4 , DEBUG3 , DEBUG2 , DEBUG1 , INFO , NOTICE , WARNING , and LOG . The default is LOG . Only superusers can change this setting. auto_explain.log_nested_statements ( boolean ) auto_explain.log_nested_statements causes nested statements (statements executed inside a function) to be considered for logging.

2. `chunk-28b75402e8c5c35be236aa87c9b3138827ab26f6aad28447de81224c0558dc7e` — pg-17; score=0.975187, dense=0.766648, sparse=29.883238, rerank=None

> , json , and yaml . The default is text. Only superusers can change this setting. auto_explain.log_level ( enum ) auto_explain.log_level selects the log level at which auto_explain will log the query plan. Valid values are DEBUG5 , DEBUG4 , DEBUG3 , DEBUG2 , DEBUG1 , INFO , NOTICE , WARNING , and LOG . The default is LOG . Only superusers can change this setting. auto_explain.log_nested_statements ( boolean ) auto_explain.log_nested_statements causes nested statements (statements executed inside a function) to be considered for logging. When it is off, only top-level query plans are logged. This parameter is off by default. Only superusers can change this setting. auto_explain.sample_rate ( real ) auto_explain.sample_rate causes auto_explain to only explain a fraction of the statements in each session. The default is 1, meaning explain all the queries. In case of nested statements, either all will be explained or none. Only superusers can change this setting. In ordinary usage, these parameters are set in postgresql.conf , although superusers can alter them on-the-fly within their own sessions. Typical usage might be:

3. `chunk-e98db9981bf201f66c728351ed56559136fb8ddc0a542444ccd50a528a53e57b` — pg-16; score=0.975187, dense=0.766648, sparse=29.883238, rerank=None

> , json , and yaml . The default is text. Only superusers can change this setting. auto_explain.log_level ( enum ) auto_explain.log_level selects the log level at which auto_explain will log the query plan. Valid values are DEBUG5 , DEBUG4 , DEBUG3 , DEBUG2 , DEBUG1 , INFO , NOTICE , WARNING , and LOG . The default is LOG . Only superusers can change this setting. auto_explain.log_nested_statements ( boolean ) auto_explain.log_nested_statements causes nested statements (statements executed inside a function) to be considered for logging. When it is off, only top-level query plans are logged. This parameter is off by default. Only superusers can change this setting. auto_explain.sample_rate ( real ) auto_explain.sample_rate causes auto_explain to only explain a fraction of the statements in each session. The default is 1, meaning explain all the queries. In case of nested statements, either all will be explained or none. Only superusers can change this setting. In ordinary usage, these parameters are set in postgresql.conf , although superusers can alter them on-the-fly within their own sessions. Typical usage might be:

## draft-5ca5682d5aa33579

Does json_object_agg_unique_strict keep entries whose values are null in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) json_object_agg_unique_strict ( key "any", value "any" ) json jsonb_object_agg_unique_strict ( key "any", value "any" ) jsonb Collects all the key/value pairs into a JSON object. Key arguments are coerced to text; value arguments are converted as per to_json or to_jsonb. The key can not be null. If the value is null then the entry is skipped. If there is a duplicate key an error is thrown.

### Top three retrieved
1. `chunk-8908fa26e794467b20d3f73e1de7a855254a1873b19a1936a59b028a09daaf9e` — pg-16; score=0.930999, dense=0.842301, sparse=47.474701, rerank=None

> , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given to these aggregates. Users accustomed to working with other SQL database management systems might be disappointed by the performance of the count aggregate when it is applied to the entire

2. `chunk-8b016650fef8bd099dbcd9cfd1de8beb5d2bbf2fad2c975133bc5c32d6b548c8` — pg-16; score=0.750000, dense=0.000000, sparse=52.284985, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully

3. `chunk-3dbafd71a2ab0c1a54fa4d9b0dc490702aa7856c5f044a8e85baad5a6ab3cffe` — pg-16; score=0.624068, dense=0.746580, sparse=28.058143, rerank=None

> | Function Description Example(s) | | --- | | to_json ( anyelement ) json to_jsonb ( anyelement ) jsonb Converts any SQL value to json or jsonb. Arrays and composites are converted recursively to arrays and objects (multidimensional arrays become arrays of arrays in JSON). Otherwise, if there is a cast from the SQL data type to json, the cast function will be used to perform the conversion; For example, the hstore extension has a cast from hstore to json, so that hstore values converted via the JSON creation functions will be represented as JSON objects, not as primitive string values. otherwise, a scalar JSON value is produced. For any scalar other than a number, a Boolean, or a null value, the text representation will be used, with escaping as necessary to make it a valid JSON string value. to_json('Fred said "Hi."'::text) "Fred said \"Hi.\"" to_jsonb(row(42, 'Fred said "Hi."'::text)) {"f1": 42, "f2": "Fred said \"Hi.\""} | | array_to_json ( anyarray , boolean ) json Converts an SQL array to a JSON array. The behavior is the same as to_json except that line feeds will be added between top-level array elements if the optional boolean parameter is true. array_to_json('{{1,5},{99,100}}'::int[]) [[1,5],[99,100]] | | json_array ( { value_expression FORMAT JSON } , ... { NULL | ABSENT } ON NULL RETURNING data_type FORMAT JSON ENCODING UTF8 ) json_array ( query_expression RETURNING data_type FORMAT JSON ENCODING UTF8 ) Constructs a JSON array from either a series of value_expression parameters or from the results of query_expression, which must be a SELECT query returning a single column. If ABSENT ON NULL is specified, NULL values are ignored. This is always the case if a query_expression is used. json_array(1,true,json '{"a":null}') [1, true, {"a":null}] json_array(SELECT * FROM (VALUES(1),(2)) t) [1, 2] | | row_to_json ( record , boolean ) json Converts an SQL composite value to a JSON object. The behavior is the same as to_json except that line feeds will be added between top-level elements if the optional boolean parameter is true. row_to_json(row(1,'foo')) {"f1":1,"f2":"foo"} | | json_build_array ( VARIADIC "any" ) json jsonb_build_array ( VARIADIC "any" ) jsonb Builds a possibly-heterogeneously-typed JSON array out of a variadic argument list. Each argument is converted as per to_json or to_jsonb. json_build_array(1, 2, 'foo', 4, 5) [1, 2, "foo", 4, 5] | | json_build_object ( VARIADIC "any" ) json jsonb_build_object ( VARIADIC "any" ) jsonb Builds a JSON object out of a variadic argument list. By convention, the argument list consists of alternating keys and values. Key arguments are coerced to text; value arguments are converted as per to_json or to_jsonb. json_build_object('foo', 1, 2, row(3,'bar')) {"foo" : 1, "2" : {"f1":3,"f2":"bar"}} | | json_object ( { key_expression { VALUE | ':' } value_expression FORMAT JSON ENCODING UTF8 }, ... { NULL | ABSENT } ON NULL { WITH | WITHOUT } UNIQUE KEYS RETURNING data_type FORMAT JSON ENCODING UTF8 ) Constructs a JSON object of all the key/value pairs given, or an empty object if none are given. key_expression is a scalar expression defining the JSON key, which is converted to the text type. It cannot be NULL nor can it belong to a type that has a cast to the json type. If WITH UNIQUE KEYS is specified, there must not be any duplicate key_expression. Any pair for which the value_expression evaluates to NULL is omitted from the output if ABSENT ON NULL is specified; if NULL ON NULL is specified or the clause omitted, the key is included with value NULL. json_object('code' VALUE 'P123', 'title': 'Jaws') {"code" : "P123", "title" : "Jaws"} | | json_object ( text[] ) json jsonb_object ( text[] ) jsonb Builds a JSON object out of a text array. The array must have either exactly one dimension with an even number of members, in which case they are taken as alternating key/value pairs, or two dimensions such that each inner array has exactly two elements, which are taken as a key/value pair. All values are converted to JSON strings. json_object('{a, 1, b, "def", c, 3.5}') {"a" : "1", "b" : "def", "c" : "3.5"} json_object('{{a, 1}, {b, "def"}, {c, 3.5}}') {"a" : "1", "b" : "def", "c" : "3.5"} | | json_object ( keys text[], values text[] ) json jsonb_object ( keys text[], values text[] ) jsonb This form of json_object takes keys and values pairwise from separate text arrays. Otherwise it is identical to the one-argument form. json_object('{a,b}', '{1,2}') {"a": "1", "b": "2"} |

## draft-7da3017f4660421c

Where can the config_file parameter be set?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) config_file ( string ) Specifies the main server configuration file (customarily called postgresql.conf ). This parameter can only be set on the postgres command line.

### Top three retrieved
1. `chunk-71e82184ee40d0de98c1dbe24020c3b3b5a9afd68e7629c784eb017c6696ce4a` — pg-16; score=0.989078, dense=0.766823, sparse=31.127745, rerank=None

> string ) Specifies the name of an additional process-ID (PID) file that the server should create for use by server administration programs. This parameter can only be set at server start. In a default installation, none of the above parameters are set explicitly. Instead, the data directory is specified by the -D command-line option or the PGDATA environment variable, and the configuration files are all found within the data directory. If you wish to keep the configuration files elsewhere than the data directory, the postgres -D command-line option or PGDATA environment variable must point to the directory containing the configuration files, and the data_directory parameter must be set in postgresql.conf (or on the command line) to show where the data directory is actually located. Notice that data_directory overrides -D and PGDATA for the location of the data directory, but not for the location of the configuration files. If you wish, you can specify the configuration file names and locations individually using the parameters config_file , hba_file and/or ident_file . config_file can only be specified on the postgres command line, but the others can be set within the main configuration file. If all three parameters plus data_directory are explicitly set, then it is not necessary to specify -D or PGDATA . When setting any of these parameters, a relative path will

2. `chunk-a42269e6b66a40f4cc912963cc63fac38fdf94ae12a6c413cf3ffe4077d3edd5` — pg-15; score=0.989078, dense=0.766823, sparse=31.127745, rerank=None

> string ) Specifies the name of an additional process-ID (PID) file that the server should create for use by server administration programs. This parameter can only be set at server start. In a default installation, none of the above parameters are set explicitly. Instead, the data directory is specified by the -D command-line option or the PGDATA environment variable, and the configuration files are all found within the data directory. If you wish to keep the configuration files elsewhere than the data directory, the postgres -D command-line option or PGDATA environment variable must point to the directory containing the configuration files, and the data_directory parameter must be set in postgresql.conf (or on the command line) to show where the data directory is actually located. Notice that data_directory overrides -D and PGDATA for the location of the data directory, but not for the location of the configuration files. If you wish, you can specify the configuration file names and locations individually using the parameters config_file , hba_file and/or ident_file . config_file can only be specified on the postgres command line, but the others can be set within the main configuration file. If all three parameters plus data_directory are explicitly set, then it is not necessary to specify -D or PGDATA . When setting any of these parameters, a relative path will

3. `chunk-c76a3d317833d41c2268cbedacf61b6ce075e56ef9b17a23562286c884b269fb` — pg-17; score=0.989078, dense=0.766823, sparse=31.127745, rerank=None

> string ) Specifies the name of an additional process-ID (PID) file that the server should create for use by server administration programs. This parameter can only be set at server start. In a default installation, none of the above parameters are set explicitly. Instead, the data directory is specified by the -D command-line option or the PGDATA environment variable, and the configuration files are all found within the data directory. If you wish to keep the configuration files elsewhere than the data directory, the postgres -D command-line option or PGDATA environment variable must point to the directory containing the configuration files, and the data_directory parameter must be set in postgresql.conf (or on the command line) to show where the data directory is actually located. Notice that data_directory overrides -D and PGDATA for the location of the data directory, but not for the location of the configuration files. If you wish, you can specify the configuration file names and locations individually using the parameters config_file , hba_file and/or ident_file . config_file can only be specified on the postgres command line, but the others can be set within the main configuration file. If all three parameters plus data_directory are explicitly set, then it is not necessary to specify -D or PGDATA . When setting any of these parameters, a relative path will
