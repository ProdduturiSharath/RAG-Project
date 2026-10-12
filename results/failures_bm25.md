# Worst test failures: bm25

System selected on dev. Showing 30 of 55 failures.
Ranking: all-quotes@10, Recall@10, nDCG@10, MRR ascending; then ID.

## draft-33d8c19a2a6a932d

What is the maximum size of one pg_largeobject.data value?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) data bytea Actual data stored in the large object. This will never be more than LOBLKSIZE bytes and might be less.

### Top three retrieved
1. `chunk-006cbb7bc5add7256d761b85457c7544eeeafa8e73e18e97b992d80c2cba1080` — pg-15; score=23.997541, dense=0.000000, sparse=23.997541, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

2. `chunk-61e357df06adaa29a4cf6da9f325363b17f4d2cc36c5fb14b547aebd4c27856a` — pg-16; score=23.997541, dense=0.000000, sparse=23.997541, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

3. `chunk-7030d3387276a19728f0806066578ef33be22c4946369d8afe8885e40c9fa50a` — pg-17; score=23.997541, dense=0.000000, sparse=23.997541, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

## draft-9b1f37bc7842b40e

Must the ECDH exchange curve match the curve of the server's elliptic-curve key?

**Category:** text gap. **Reason:** No authorized, version-valid chunk contains a whole evidence quote.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key.

### Top three retrieved
1. `chunk-1516438718b7513bfd977d04dd2afed0941fe3834c835381deba48e8a702508a` — pg-17; score=49.835055, dense=0.000000, sparse=49.835055, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

2. `chunk-5eb8f088a27537161214049d6e1af3cbf51e833d78773287d7864d13cae3def4` — pg-16; score=49.835055, dense=0.000000, sparse=49.835055, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

3. `chunk-7db320984913426c010575bf8fd4f79e99b38a5a603cdc29ae591524251088c6` — pg-15; score=49.835055, dense=0.000000, sparse=49.835055, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

## draft-a2cf6aa49912f6e7

When does bool_or return true in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bool_or ( boolean ) boolean Returns true if any non-null input value is true, otherwise false.
- (pg-16) bool_or ( boolean ) boolean Returns true if any non-null input value is true, otherwise false.

### Top three retrieved
1. `chunk-21922f71b59fcc01b283df8cd279ec8a254f46a9b98300887f6489cf5e3fb2ab` — pg-17; score=22.414722, dense=0.000000, sparse=22.414722, rerank=None

> case the consistent method needs to consult it, and so are the queryKeys[] and nullFlags[] arrays previously returned by extractQuery . extra_data is the extra-data array returned by extractQuery , or NULL if none. When extractQuery returns a null key in queryKeys[] , the corresponding check[] element is true if the indexed item contains a null key; that is, the semantics of check[] are like IS NOT DISTINCT FROM . The consistent function can examine the corresponding nullFlags[] element if it needs to tell the difference between a regular value match and a null match. On success, *recheck should be set to true if the heap tuple needs to be rechecked against the query operator, or false if the index test is exact. That is, a false return value guarantees that the heap tuple does not match the query; a true return value with *recheck set to false guarantees that the heap tuple does match the query; and a true return value with *recheck set to true means that the heap tuple might match the query, so it needs to be fetched and rechecked by evaluating the query operator directly against the originally indexed item. GinTernaryValue triConsistent(GinTernaryValue check[], StrategyNumber n, Datum query, int32 nkeys, Pointer extra_data[], Datum queryKeys[], bool nullFlags[]) triConsistent is similar to consistent , but instead of Booleans

2. `chunk-5c63a333d40088a14ca6709c010ce14c12cf0dab3bff8c8534084edad09188e5` — pg-15; score=22.414722, dense=0.000000, sparse=22.414722, rerank=None

> case the consistent method needs to consult it, and so are the queryKeys[] and nullFlags[] arrays previously returned by extractQuery . extra_data is the extra-data array returned by extractQuery , or NULL if none. When extractQuery returns a null key in queryKeys[] , the corresponding check[] element is true if the indexed item contains a null key; that is, the semantics of check[] are like IS NOT DISTINCT FROM . The consistent function can examine the corresponding nullFlags[] element if it needs to tell the difference between a regular value match and a null match. On success, *recheck should be set to true if the heap tuple needs to be rechecked against the query operator, or false if the index test is exact. That is, a false return value guarantees that the heap tuple does not match the query; a true return value with *recheck set to false guarantees that the heap tuple does match the query; and a true return value with *recheck set to true means that the heap tuple might match the query, so it needs to be fetched and rechecked by evaluating the query operator directly against the originally indexed item. GinTernaryValue triConsistent(GinTernaryValue check[], StrategyNumber n, Datum query, int32 nkeys, Pointer extra_data[], Datum queryKeys[], bool nullFlags[]) triConsistent is similar to consistent , but instead of Booleans

3. `chunk-67174b31b3e23d376d837339461b502acf87af06ee2da6cea6f9e8b2c2a81e88` — pg-16; score=22.414722, dense=0.000000, sparse=22.414722, rerank=None

> case the consistent method needs to consult it, and so are the queryKeys[] and nullFlags[] arrays previously returned by extractQuery . extra_data is the extra-data array returned by extractQuery , or NULL if none. When extractQuery returns a null key in queryKeys[] , the corresponding check[] element is true if the indexed item contains a null key; that is, the semantics of check[] are like IS NOT DISTINCT FROM . The consistent function can examine the corresponding nullFlags[] element if it needs to tell the difference between a regular value match and a null match. On success, *recheck should be set to true if the heap tuple needs to be rechecked against the query operator, or false if the index test is exact. That is, a false return value guarantees that the heap tuple does not match the query; a true return value with *recheck set to false guarantees that the heap tuple does match the query; and a true return value with *recheck set to true means that the heap tuple might match the query, so it needs to be fetched and rechecked by evaluating the query operator directly against the originally indexed item. GinTernaryValue triConsistent(GinTernaryValue check[], StrategyNumber n, Datum query, int32 nkeys, Pointer extra_data[], Datum queryKeys[], bool nullFlags[]) triConsistent is similar to consistent , but instead of Booleans

## draft-d1b8f6b5aa7eddfa

When does bool_and return true in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bool_and ( boolean ) boolean Returns true if all non-null input values are true, otherwise false.
- (pg-16) bool_and ( boolean ) boolean Returns true if all non-null input values are true, otherwise false.

### Top three retrieved
1. `chunk-21922f71b59fcc01b283df8cd279ec8a254f46a9b98300887f6489cf5e3fb2ab` — pg-17; score=20.937605, dense=0.000000, sparse=20.937605, rerank=None

> case the consistent method needs to consult it, and so are the queryKeys[] and nullFlags[] arrays previously returned by extractQuery . extra_data is the extra-data array returned by extractQuery , or NULL if none. When extractQuery returns a null key in queryKeys[] , the corresponding check[] element is true if the indexed item contains a null key; that is, the semantics of check[] are like IS NOT DISTINCT FROM . The consistent function can examine the corresponding nullFlags[] element if it needs to tell the difference between a regular value match and a null match. On success, *recheck should be set to true if the heap tuple needs to be rechecked against the query operator, or false if the index test is exact. That is, a false return value guarantees that the heap tuple does not match the query; a true return value with *recheck set to false guarantees that the heap tuple does match the query; and a true return value with *recheck set to true means that the heap tuple might match the query, so it needs to be fetched and rechecked by evaluating the query operator directly against the originally indexed item. GinTernaryValue triConsistent(GinTernaryValue check[], StrategyNumber n, Datum query, int32 nkeys, Pointer extra_data[], Datum queryKeys[], bool nullFlags[]) triConsistent is similar to consistent , but instead of Booleans

2. `chunk-5c63a333d40088a14ca6709c010ce14c12cf0dab3bff8c8534084edad09188e5` — pg-15; score=20.937605, dense=0.000000, sparse=20.937605, rerank=None

> case the consistent method needs to consult it, and so are the queryKeys[] and nullFlags[] arrays previously returned by extractQuery . extra_data is the extra-data array returned by extractQuery , or NULL if none. When extractQuery returns a null key in queryKeys[] , the corresponding check[] element is true if the indexed item contains a null key; that is, the semantics of check[] are like IS NOT DISTINCT FROM . The consistent function can examine the corresponding nullFlags[] element if it needs to tell the difference between a regular value match and a null match. On success, *recheck should be set to true if the heap tuple needs to be rechecked against the query operator, or false if the index test is exact. That is, a false return value guarantees that the heap tuple does not match the query; a true return value with *recheck set to false guarantees that the heap tuple does match the query; and a true return value with *recheck set to true means that the heap tuple might match the query, so it needs to be fetched and rechecked by evaluating the query operator directly against the originally indexed item. GinTernaryValue triConsistent(GinTernaryValue check[], StrategyNumber n, Datum query, int32 nkeys, Pointer extra_data[], Datum queryKeys[], bool nullFlags[]) triConsistent is similar to consistent , but instead of Booleans

3. `chunk-67174b31b3e23d376d837339461b502acf87af06ee2da6cea6f9e8b2c2a81e88` — pg-16; score=20.937605, dense=0.000000, sparse=20.937605, rerank=None

> case the consistent method needs to consult it, and so are the queryKeys[] and nullFlags[] arrays previously returned by extractQuery . extra_data is the extra-data array returned by extractQuery , or NULL if none. When extractQuery returns a null key in queryKeys[] , the corresponding check[] element is true if the indexed item contains a null key; that is, the semantics of check[] are like IS NOT DISTINCT FROM . The consistent function can examine the corresponding nullFlags[] element if it needs to tell the difference between a regular value match and a null match. On success, *recheck should be set to true if the heap tuple needs to be rechecked against the query operator, or false if the index test is exact. That is, a false return value guarantees that the heap tuple does not match the query; a true return value with *recheck set to false guarantees that the heap tuple does match the query; and a true return value with *recheck set to true means that the heap tuple might match the query, so it needs to be fetched and rechecked by evaluating the query operator directly against the originally indexed item. GinTernaryValue triConsistent(GinTernaryValue check[], StrategyNumber n, Datum query, int32 nkeys, Pointer extra_data[], Datum queryKeys[], bool nullFlags[]) triConsistent is similar to consistent , but instead of Booleans

## draft-dadefc52fd565605

What OpenSSL curve name is the default for ssl_ecdh_curve?

**Category:** text gap. **Reason:** No authorized, version-valid chunk contains a whole evidence quote.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 .

### Top three retrieved
1. `chunk-1516438718b7513bfd977d04dd2afed0941fe3834c835381deba48e8a702508a` — pg-17; score=50.220235, dense=0.000000, sparse=50.220235, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

2. `chunk-5eb8f088a27537161214049d6e1af3cbf51e833d78773287d7864d13cae3def4` — pg-16; score=50.220235, dense=0.000000, sparse=50.220235, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

3. `chunk-7db320984913426c010575bf8fd4f79e99b38a5a603cdc29ae591524251088c6` — pg-15; score=50.220235, dense=0.000000, sparse=50.220235, rerank=None

> is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers. !aNULL Disables anonymous cipher suites that do no authentication. Such cipher suites are vulnerable to MITM attacks and therefore should not be used. Available cipher suite details will vary across OpenSSL versions. Use the command openssl ciphers -v 'HIGH:MEDIUM:+3DES:!aNULL' to see actual details for the currently installed OpenSSL version. Note that this list is filtered at run time based on the server key type. ssl_prefer_server_ciphers ( boolean ) Specifies whether to use the server's SSL cipher preferences, rather than the client's. This parameter can only be set in the postgresql.conf file or on the server command line. The default is on . PostgreSQL versions before 9.4 do not have this setting and always use the client's preferences. This setting is mainly for backward compatibility with those versions. Using the server's preferences is usually better because it is more likely that the server is appropriately configured. ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic

## draft-dee2728be3a4e6aa

What is the return type of count(*) in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) count ( * ) bigint Computes the number of input rows.
- (pg-16) count ( * ) bigint Computes the number of input rows.

### Top three retrieved
1. `chunk-19ce536d81f9f2e4a0840b38cc4575ce1259723c2933c6d0b72fc83b8b82c146` — pg-16; score=22.470789, dense=0.000000, sparse=22.470789, rerank=None

> 1, 2, 9, 11, and 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, 15, and 16 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2023. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2023. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2023 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if

2. `chunk-bdbed1a0703466d4547441f4e516b6d9c3d433275fee2c9c2469525489adba7d` — pg-17; score=22.470789, dense=0.000000, sparse=22.470789, rerank=None

> 1, 2, 9, 11, and 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, 15, and 16 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2023. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2023. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2023 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if

3. `chunk-23e0a51180b1e0761f149e3e1a396a11c6a85bf4c8edb7a6db8fc334bd44ddc7` — pg-16; score=20.963544, dense=0.000000, sparse=20.963544, rerank=None

> Return Value The function returns the row(s) produced by the query. Since dblink can be used with any query, it is declared to return record , rather than specifying any particular set of columns. This means that you must specify the expected set of columns in the calling query — otherwise PostgreSQL would not know what to expect. Here is an example: The alias part of the FROM clause must specify the column names and types that the function will return. (Specifying column names in an alias is actually standard SQL syntax, but specifying column types is a PostgreSQL extension.) This allows the system to understand what * should expand to, and what proname in the WHERE clause refers to, in advance of trying to execute the function. At run time, an error will be thrown if the actual query result from the remote database does not have the same number of columns shown in the FROM clause. The column names need not match, however, and dblink does not insist on exact type matches either. It will succeed so long as the returned data strings are valid input for the column type declared in the FROM clause.

## draft-df61a1a2e6822bb7

What does cardinality return for an empty array in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) cardinality ( anyarray ) integer Returns the total number of elements in the array, or 0 if the array is empty.
- (pg-16) cardinality ( anyarray ) integer Returns the total number of elements in the array, or 0 if the array is empty.

### Top three retrieved
1. `chunk-19ce536d81f9f2e4a0840b38cc4575ce1259723c2933c6d0b72fc83b8b82c146` — pg-16; score=24.714966, dense=0.000000, sparse=24.714966, rerank=None

> 1, 2, 9, 11, and 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, 15, and 16 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2023. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2023. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2023 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if

2. `chunk-bdbed1a0703466d4547441f4e516b6d9c3d433275fee2c9c2469525489adba7d` — pg-17; score=24.714966, dense=0.000000, sparse=24.714966, rerank=None

> 1, 2, 9, 11, and 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, 15, and 16 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2023. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2023. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2023 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if

3. `chunk-a3e07d25a5d71bae222e989dc4683c83dc5d480d53e7ed8cfccc2b65d6c4f77f` — pg-17; score=24.250108, dense=0.000000, sparse=24.250108, rerank=None

> the array bounds, then it is silently reduced to just the overlapping region instead of returning null. The current dimensions of any array value can be retrieved with the array_dims function: array_dims produces a text result, which is convenient for people to read but perhaps inconvenient for programs. Dimensions can also be retrieved with array_upper and array_lower , which return the upper and lower bound of a specified array dimension, respectively: array_length will return the length of a specified array dimension: cardinality returns the total number of elements in an array across all dimensions. It is effectively the number of rows a call to unnest would yield:

## draft-3abee3e4240c30d3

What is the default work_mem in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes. The default value is four megabytes ( 4MB ).
- (pg-16) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes. The default value is four megabytes ( 4MB ).

### Top three retrieved
1. `chunk-14fc775ccd038e3a4d93ce4758b505a6d520b0e76509a788a386ae6e9e2415bf` — pg-17; score=33.024913, dense=0.000000, sparse=33.024913, rerank=None

> Sort operations are used for ORDER BY , DISTINCT , and merge joins. Hash tables are used in hash joins, hash-based aggregation, memoize nodes and hash-based processing of IN subqueries. Hash-based operations are generally more sensitive to memory availability than equivalent sort-based operations. The memory limit for a hash table is computed by multiplying work_mem by hash_mem_multiplier . This makes it possible for hash-based operations to use an amount of memory that exceeds the usual work_mem base amount. hash_mem_multiplier ( floating point ) Used to compute the maximum amount of memory that hash-based operations can use. The final limit is determined by multiplying work_mem by hash_mem_multiplier . The default value is 2.0, which makes hash-based operations use twice the usual work_mem base amount. Consider increasing hash_mem_multiplier in environments where spilling by query operations is a regular occurrence, especially when simply increasing work_mem results in memory pressure (memory pressure typically takes the form of intermittent out of memory errors). The default setting of 2.0 is often effective with mixed workloads. Higher settings in the range of 2.0 - 8.0 or more may be effective in environments where work_mem has already been increased to 40MB or more. maintenance_work_mem ( integer ) Specifies the maximum amount of memory to be used by maintenance operations, such as VACUUM , CREATE INDEX , and ALTER

2. `chunk-964c190580d0d6b8dab6d0844ecc7edaa4d9f97e17e90ce941fed4ffc5319e9f` — pg-15; score=32.914883, dense=0.000000, sparse=32.914883, rerank=None

> tables are used in hash joins, hash-based aggregation, memoize nodes and hash-based processing of IN subqueries. Hash-based operations are generally more sensitive to memory availability than equivalent sort-based operations. The memory limit for a hash table is computed by multiplying work_mem by hash_mem_multiplier . This makes it possible for hash-based operations to use an amount of memory that exceeds the usual work_mem base amount. hash_mem_multiplier ( floating point ) Used to compute the maximum amount of memory that hash-based operations can use. The final limit is determined by multiplying work_mem by hash_mem_multiplier . The default value is 2.0, which makes hash-based operations use twice the usual work_mem base amount. Consider increasing hash_mem_multiplier in environments where spilling by query operations is a regular occurrence, especially when simply increasing work_mem results in memory pressure (memory pressure typically takes the form of intermittent out of memory errors). The default setting of 2.0 is often effective with mixed workloads. Higher settings in the range of 2.0 - 8.0 or more may be effective in environments where work_mem has already been increased to 40MB or more. maintenance_work_mem ( integer ) Specifies the maximum amount of memory to be used by maintenance operations, such as VACUUM , CREATE INDEX , and ALTER TABLE ADD FOREIGN KEY . If this value is specified without units, it is

3. `chunk-d8a03bf3620f8541fad82825d1968b8337a2284afb10b513c18ccaba90684b6b` — pg-16; score=32.914883, dense=0.000000, sparse=32.914883, rerank=None

> tables are used in hash joins, hash-based aggregation, memoize nodes and hash-based processing of IN subqueries. Hash-based operations are generally more sensitive to memory availability than equivalent sort-based operations. The memory limit for a hash table is computed by multiplying work_mem by hash_mem_multiplier . This makes it possible for hash-based operations to use an amount of memory that exceeds the usual work_mem base amount. hash_mem_multiplier ( floating point ) Used to compute the maximum amount of memory that hash-based operations can use. The final limit is determined by multiplying work_mem by hash_mem_multiplier . The default value is 2.0, which makes hash-based operations use twice the usual work_mem base amount. Consider increasing hash_mem_multiplier in environments where spilling by query operations is a regular occurrence, especially when simply increasing work_mem results in memory pressure (memory pressure typically takes the form of intermittent out of memory errors). The default setting of 2.0 is often effective with mixed workloads. Higher settings in the range of 2.0 - 8.0 or more may be effective in environments where work_mem has already been increased to 40MB or more. maintenance_work_mem ( integer ) Specifies the maximum amount of memory to be used by maintenance operations, such as VACUUM , CREATE INDEX , and ALTER TABLE ADD FOREIGN KEY . If this value is specified without units, it is

## draft-1a061285c851d1c0

Does array_agg support Partial Mode in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) | Function Description | Partial Mode | | --- | --- | | any_value ( anyelement ) same as input type Returns an arbitrary value from the non-null input values. | Yes | | array_agg ( anynonarray ) anyarray Collects all the input values, including nulls, into an array. | Yes |

### Top three retrieved
1. `chunk-8b016650fef8bd099dbcd9cfd1de8beb5d2bbf2fad2c975133bc5c32d6b548c8` — pg-16; score=36.327001, dense=0.000000, sparse=36.327001, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully

2. `chunk-fbdb452bf605fa53bcb5eac6a958f13013980ea8a0786838d269f3bb9cafabdc` — pg-15; score=35.042914, dense=0.000000, sparse=35.042914, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_object_agg , jsonb_object_agg , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by

3. `chunk-2759f0822a788033d79c3140f537e1c3fc78d00f0d4b2a2ae38f7b1d3f05e262` — pg-17; score=34.668157, dense=0.000000, sparse=34.668157, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. While all aggregates below accept an optional ORDER BY clause (as outlined in Aggregate Expressions ), the clause has only been added to aggregates whose output is affected by ordering. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict ,

## draft-7aba123f3dd8b9f6

What does defaclnamespace = 0 indicate in pg_default_acl?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-16) defaclnamespace oid (references pg_namespace.oid) The OID of the namespace associated with this entry, or zero if none

### Top three retrieved
1. `chunk-497263c216e671ac118ca27f6da0d32df665113296215fb4de41e8142573ae60` — pg-15; score=45.129827, dense=0.000000, sparse=45.129827, rerank=None

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

2. `chunk-da6d3c3daae1d20227cac5402abe455ddc35b88b4b474f42af8724ea34dec1f5` — pg-16; score=45.129827, dense=0.000000, sparse=45.129827, rerank=None

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

3. `chunk-ecb07ce2d8f7a6ba484992fa9abb51168effa59591154263b56051dcd2828dc7` — pg-17; score=45.129827, dense=0.000000, sparse=45.129827, rerank=None

> pg_default_acl The catalog pg_default_acl stores initial privileges to be assigned to newly created objects. A pg_default_acl entry shows the initial privileges to be assigned to an object belonging to the indicated user. There are currently two types of entry: global entries with defaclnamespace = zero, and per-schema entries that reference a particular schema. If a global entry is present then it overrides the normal hard-wired default privileges for the object type. A per-schema entry, if present, represents privileges to be added to the global or hard-wired default privileges. Note that when an ACL entry in another catalog is null, it is taken to represent the hard-wired default privileges for its object, not whatever might be in pg_default_acl at the moment. pg_default_acl is only consulted during object creation.

## draft-51a8ac7c7fbf24a6

What does amtype = i mean in pg_am?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) amtype char t = table (including materialized views), i = index.

### Top three retrieved
1. `chunk-8dd0cf44fc728e489fc78a6d13522cb4bb9700285a5ff49501d85eb23f441ac8` — pg-16; score=26.015794, dense=0.000000, sparse=26.015794, rerank=None

> test=# SELECT bt_index_check(index => c.oid, heapallindexed => i.indisunique), c.relname, c.relpages FROM pg_index i JOIN pg_opclass op ON i.indclass[0] = op.oid JOIN pg_am am ON op.opcmethod = am.oid JOIN pg_class c ON i.indexrelid = c.oid JOIN pg_namespace n ON c.relnamespace = n.oid WHERE am.amname = 'btree' AND n.nspname = 'pg_catalog' -- Don't check temp tables, which may be from another session: AND c.relpersistence != 't' -- Function may throw an error when this is omitted: AND c.relkind = 'i' AND i.indisready AND i.indisvalid ORDER BY c.relpages DESC LIMIT 10; bt_index_check | relname | relpages ----------------+---------------------------------+---------- | pg_depend_reference_index | 43 | pg_depend_depender_index | 40 | pg_proc_proname_args_nsp_index | 31 | pg_description_o_c_o_index | 21 | pg_attribute_relid_attnam_index | 14 | pg_proc_oid_index | 10 | pg_attribute_relid_attnum_index | 9 | pg_amproc_fam_proc_index | 5 | pg_amop_opr_fam_index | 5 | pg_amop_fam_strat_index | 5 (10 rows)

2. `chunk-c8440fc9175b26c5420ba3724818356cb4a32b4e57f4dd6ade22149b5d62c066` — pg-15; score=26.015794, dense=0.000000, sparse=26.015794, rerank=None

> test=# SELECT bt_index_check(index => c.oid, heapallindexed => i.indisunique), c.relname, c.relpages FROM pg_index i JOIN pg_opclass op ON i.indclass[0] = op.oid JOIN pg_am am ON op.opcmethod = am.oid JOIN pg_class c ON i.indexrelid = c.oid JOIN pg_namespace n ON c.relnamespace = n.oid WHERE am.amname = 'btree' AND n.nspname = 'pg_catalog' -- Don't check temp tables, which may be from another session: AND c.relpersistence != 't' -- Function may throw an error when this is omitted: AND c.relkind = 'i' AND i.indisready AND i.indisvalid ORDER BY c.relpages DESC LIMIT 10; bt_index_check | relname | relpages ----------------+---------------------------------+---------- | pg_depend_reference_index | 43 | pg_depend_depender_index | 40 | pg_proc_proname_args_nsp_index | 31 | pg_description_o_c_o_index | 21 | pg_attribute_relid_attnam_index | 14 | pg_proc_oid_index | 10 | pg_attribute_relid_attnum_index | 9 | pg_amproc_fam_proc_index | 5 | pg_amop_opr_fam_index | 5 | pg_amop_fam_strat_index | 5 (10 rows)

3. `chunk-debfb6b4a40e89ad68218377fe374aebd7543cf2b31cf31166945e6a7526ff89` — pg-17; score=26.015794, dense=0.000000, sparse=26.015794, rerank=None

> test=# SELECT bt_index_check(index => c.oid, heapallindexed => i.indisunique), c.relname, c.relpages FROM pg_index i JOIN pg_opclass op ON i.indclass[0] = op.oid JOIN pg_am am ON op.opcmethod = am.oid JOIN pg_class c ON i.indexrelid = c.oid JOIN pg_namespace n ON c.relnamespace = n.oid WHERE am.amname = 'btree' AND n.nspname = 'pg_catalog' -- Don't check temp tables, which may be from another session: AND c.relpersistence != 't' -- Function may throw an error when this is omitted: AND c.relkind = 'i' AND i.indisready AND i.indisvalid ORDER BY c.relpages DESC LIMIT 10; bt_index_check | relname | relpages ----------------+---------------------------------+---------- | pg_depend_reference_index | 43 | pg_depend_depender_index | 40 | pg_proc_proname_args_nsp_index | 31 | pg_description_o_c_o_index | 21 | pg_attribute_relid_attnam_index | 14 | pg_proc_oid_index | 10 | pg_attribute_relid_attnum_index | 9 | pg_amproc_fam_proc_index | 5 | pg_amop_opr_fam_index | 5 | pg_amop_fam_strat_index | 5 (10 rows)

## draft-e5b5f0b94a5943be

Which setting names the server's certificate-authority file?

**Category:** identifier not matched. **Reason:** The expected identifier is absent from the top three.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ca_file ( string ) Specifies the name of the file containing the SSL server certificate authority (CA).

### Top three retrieved
1. `chunk-213c11e5e6fc846bfb78c1aded96935cccbc6d02a511afd117605291f31d3f46` — pg-17; score=34.022822, dense=0.000000, sparse=34.022822, rerank=None

> the current database encoding. It is assumed that if you use non-ASCII characters in the certificate names, your database is able to represent these characters, too. If your database uses the SQL_ASCII encoding, non-ASCII characters in the name will be represented as UTF-8 sequences. The result looks like /CN=Somebody /C=Some country/O=Some organization . ssl_issuer_dn() returns text Returns the full issuer name of the current client certificate, converting character data into the current database encoding. Encoding conversions are handled the same as for ssl_client_dn . The combination of the return value of this function with the certificate serial number uniquely identifies the certificate. This function is really useful only if you have more than one trusted CA certificate in your server's certificate authority file, or if this CA has issued some intermediate certificate authority certificates. ssl_client_dn_field(fieldname text) returns text This function returns the value of the specified field in the certificate subject, or NULL if the field is not present. Field names are string constants that are converted into ASN1 object identifiers using the OpenSSL object database. The following values are acceptable: All of these fields are optional, except commonName . It depends entirely on your CA's policy which of them would be included and which wouldn't. The meaning of these fields, however, is strictly defined by the X.500 and X.509

2. `chunk-2431453273861869ebf510427fa8fd07ee0423e84accd718572e44e444b36f31` — pg-16; score=34.022822, dense=0.000000, sparse=34.022822, rerank=None

> the current database encoding. It is assumed that if you use non-ASCII characters in the certificate names, your database is able to represent these characters, too. If your database uses the SQL_ASCII encoding, non-ASCII characters in the name will be represented as UTF-8 sequences. The result looks like /CN=Somebody /C=Some country/O=Some organization . ssl_issuer_dn() returns text Returns the full issuer name of the current client certificate, converting character data into the current database encoding. Encoding conversions are handled the same as for ssl_client_dn . The combination of the return value of this function with the certificate serial number uniquely identifies the certificate. This function is really useful only if you have more than one trusted CA certificate in your server's certificate authority file, or if this CA has issued some intermediate certificate authority certificates. ssl_client_dn_field(fieldname text) returns text This function returns the value of the specified field in the certificate subject, or NULL if the field is not present. Field names are string constants that are converted into ASN1 object identifiers using the OpenSSL object database. The following values are acceptable: All of these fields are optional, except commonName . It depends entirely on your CA's policy which of them would be included and which wouldn't. The meaning of these fields, however, is strictly defined by the X.500 and X.509

3. `chunk-8a36d3486ba002cf63c2864f9b13288a77a90962a04ae4e5821c98d86f0fb70a` — pg-15; score=34.022822, dense=0.000000, sparse=34.022822, rerank=None

> the current database encoding. It is assumed that if you use non-ASCII characters in the certificate names, your database is able to represent these characters, too. If your database uses the SQL_ASCII encoding, non-ASCII characters in the name will be represented as UTF-8 sequences. The result looks like /CN=Somebody /C=Some country/O=Some organization . ssl_issuer_dn() returns text Returns the full issuer name of the current client certificate, converting character data into the current database encoding. Encoding conversions are handled the same as for ssl_client_dn . The combination of the return value of this function with the certificate serial number uniquely identifies the certificate. This function is really useful only if you have more than one trusted CA certificate in your server's certificate authority file, or if this CA has issued some intermediate certificate authority certificates. ssl_client_dn_field(fieldname text) returns text This function returns the value of the specified field in the certificate subject, or NULL if the field is not present. Field names are string constants that are converted into ASN1 object identifiers using the OpenSSL object database. The following values are acceptable: All of these fields are optional, except commonName . It depends entirely on your CA's policy which of them would be included and which wouldn't. The meaning of these fields, however, is strictly defined by the X.500 and X.509

## draft-529a81ca28099b25

Is Partial Mode supported by string_agg in PostgreSQL 16?

**Category:** wrong version. **Reason:** A same-lineage wrong version outranks the first correct evidence.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) string_agg ( value text, delimiter text ) text string_agg ( value bytea, delimiter bytea ) bytea Concatenates the non-null input values into a string. Each value after the first is preceded by the corresponding delimiter (if it's not null). | Yes

### Top three retrieved
1. `chunk-fbdb452bf605fa53bcb5eac6a958f13013980ea8a0786838d269f3bb9cafabdc` — pg-15; score=28.282705, dense=0.000000, sparse=28.282705, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_object_agg , jsonb_object_agg , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by

2. `chunk-8b016650fef8bd099dbcd9cfd1de8beb5d2bbf2fad2c975133bc5c32d6b548c8` — pg-16; score=27.752054, dense=0.000000, sparse=27.752054, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully

3. `chunk-557d8850f5bad9e6709ba512b164f320b2a43f45f44442e64530ba7f20a3d484` — pg-16; score=27.200639, dense=0.000000, sparse=27.200639, rerank=None

> SELECT string_agg(a, ',' ORDER BY a) FROM table;

## draft-fbf86c0d558416ce

Does array_agg support Partial Mode in PostgreSQL 15?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) | Function Description | Partial Mode | | --- | --- | | array_agg ( anynonarray ) anyarray Collects all the input values, including nulls, into an array. | No |

### Top three retrieved
1. `chunk-8b016650fef8bd099dbcd9cfd1de8beb5d2bbf2fad2c975133bc5c32d6b548c8` — pg-16; score=36.327001, dense=0.000000, sparse=36.327001, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully

2. `chunk-fbdb452bf605fa53bcb5eac6a958f13013980ea8a0786838d269f3bb9cafabdc` — pg-15; score=35.042914, dense=0.000000, sparse=35.042914, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_object_agg , jsonb_object_agg , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by

3. `chunk-2759f0822a788033d79c3140f537e1c3fc78d00f0d4b2a2ae38f7b1d3f05e262` — pg-17; score=34.668157, dense=0.000000, sparse=34.668157, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. While all aggregates below accept an optional ORDER BY clause (as outlined in Aggregate Expressions ), the clause has only been added to aggregates whose output is affected by ordering. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict ,

## draft-519d2a3d29e1d233

Does array_agg retain null scalar inputs in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) array_agg ( anynonarray ) anyarray Collects all the input values, including nulls, into an array.
- (pg-16) array_agg ( anynonarray ) anyarray Collects all the input values, including nulls, into an array.

### Top three retrieved
1. `chunk-8b016650fef8bd099dbcd9cfd1de8beb5d2bbf2fad2c975133bc5c32d6b548c8` — pg-16; score=30.324882, dense=0.000000, sparse=30.324882, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully

2. `chunk-fbdb452bf605fa53bcb5eac6a958f13013980ea8a0786838d269f3bb9cafabdc` — pg-15; score=28.967541, dense=0.000000, sparse=28.967541, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_object_agg , jsonb_object_agg , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by

3. `chunk-0574a70b29396844c30384a5b70b71bdba915e23834994dcbba7c477ac4f903f` — pg-16; score=28.650288, dense=0.000000, sparse=28.650288, rerank=None

> below. Most aggregate functions ignore null inputs, so that rows in which one or more of the expression(s) yield null are discarded. This can be assumed to be true, unless otherwise specified, for all built-in aggregates. For example, count(*) yields the total number of input rows; count(f1) yields the number of input rows in which f1 is non-null, since count ignores nulls; and count(distinct f1) yields the number of distinct non-null values of f1 . Ordinarily, the input rows are fed to the aggregate function in an unspecified order. In many cases this does not matter; for example, min produces the same result no matter what order it receives the inputs in. However, some aggregate functions (such as array_agg and string_agg ) produce results that depend on the ordering of the input rows. When using such an aggregate, the optional order_by_clause can be used to specify the desired ordering. The order_by_clause has the same syntax as for a query-level ORDER BY clause, as described in Sorting Rows (ORDER BY) , except that its expressions are always just expressions and cannot be output-column names or numbers. For example: When dealing with multiple-argument aggregate functions, note that the ORDER BY clause goes after all the aggregate arguments. For example, write this: not this: The latter is syntactically valid, but it represents a

## draft-d6a79ce1778ec9b4

What does array_upper(ARRAY[1,8,3,7], 1) return in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) array_upper ( anyarray, integer ) integer Returns the upper bound of the requested array dimension. array_upper(ARRAY[1,8,3,7], 1) 4
- (pg-16) array_upper ( anyarray, integer ) integer Returns the upper bound of the requested array dimension. array_upper(ARRAY[1,8,3,7], 1) 4

### Top three retrieved
1. `chunk-410255fcbf9b92b62fe0564c658730bd86f4a4a9f7f96ebb3b740181017d4134` — pg-16; score=35.212194, dense=0.000000, sparse=35.212194, rerank=None

> postgres=# SELECT * FROM pg_freespace('foo'); blkno | avail -------+------- 0 | 0 1 | 0 2 | 0 3 | 32 4 | 704 5 | 704 6 | 704 7 | 1216 8 | 704 9 | 704 10 | 704 11 | 704 12 | 704 13 | 704 14 | 704 15 | 704 16 | 704 17 | 704 18 | 704 19 | 3648 (20 rows) postgres=# SELECT * FROM pg_freespace('foo', 7); pg_freespace -------------- 1216 (1 row)

2. `chunk-982e73cee55eb327c7618354722561f2a57581ec8380c284e7f40fa25b0b4819` — pg-17; score=35.212194, dense=0.000000, sparse=35.212194, rerank=None

> postgres=# SELECT * FROM pg_freespace('foo'); blkno | avail -------+------- 0 | 0 1 | 0 2 | 0 3 | 32 4 | 704 5 | 704 6 | 704 7 | 1216 8 | 704 9 | 704 10 | 704 11 | 704 12 | 704 13 | 704 14 | 704 15 | 704 16 | 704 17 | 704 18 | 704 19 | 3648 (20 rows) postgres=# SELECT * FROM pg_freespace('foo', 7); pg_freespace -------------- 1216 (1 row)

3. `chunk-dbd3c9f5171e3a4bb84afeb0c3678226c322e446d1961dac09ed8ff0eccb0cf5` — pg-15; score=35.212194, dense=0.000000, sparse=35.212194, rerank=None

> postgres=# SELECT * FROM pg_freespace('foo'); blkno | avail -------+------- 0 | 0 1 | 0 2 | 0 3 | 32 4 | 704 5 | 704 6 | 704 7 | 1216 8 | 704 9 | 704 10 | 704 11 | 704 12 | 704 13 | 704 14 | 704 15 | 704 16 | 704 17 | 704 18 | 704 19 | 3648 (20 rows) postgres=# SELECT * FROM pg_freespace('foo', 7); pg_freespace -------------- 1216 (1 row)

## draft-32068527036ef646

Which setting selects the configuration file for user-name mapping?

**Category:** identifier not matched. **Reason:** The expected identifier is absent from the top three.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ident_file ( string ) Specifies the configuration file for user name mapping (customarily called pg_ident.conf ).

### Top three retrieved
1. `chunk-8ec7dac3eb31864aaa64f8c5a96c3eb1147abedb281508ab3ece8e27d0669e90` — pg-16; score=28.244490, dense=0.000000, sparse=28.244490, rerank=None

> intends to connect to. The servicename part of the principal is ordinarily postgres , but another value can be selected via libpq 's krbsrvname connection parameter. The hostname part is the fully qualified host name that libpq is told to connect to. The realm name is the preferred realm specified in the Kerberos configuration file(s) accessible to the client. The client will also have a principal name for its own identity (and it must have a valid ticket for this principal). To use GSSAPI for authentication, the client principal must be associated with a PostgreSQL database user name. The pg_ident.conf configuration file can be used to map principals to user names; for example, pgusername@realm could be mapped to just pgusername . Alternatively, you can use the full username@realm principal as the role name in PostgreSQL without any mapping. PostgreSQL also supports mapping client principals to user names by just stripping the realm from the principal. This method is supported for backwards compatibility and is strongly discouraged as it is then impossible to distinguish different users with the same user name but coming from different realms. To enable this, set include_realm to 0. For simple single-realm installations, doing that combined with setting the krb_realm parameter (which checks that the principal's realm matches exactly what is in the krb_realm parameter) is still

2. `chunk-94c672fd4ab5747cc5de3aefc2d7ee23ab56c7649ad9768a9c1244d6d8222369` — pg-15; score=28.244490, dense=0.000000, sparse=28.244490, rerank=None

> intends to connect to. The servicename part of the principal is ordinarily postgres , but another value can be selected via libpq 's krbsrvname connection parameter. The hostname part is the fully qualified host name that libpq is told to connect to. The realm name is the preferred realm specified in the Kerberos configuration file(s) accessible to the client. The client will also have a principal name for its own identity (and it must have a valid ticket for this principal). To use GSSAPI for authentication, the client principal must be associated with a PostgreSQL database user name. The pg_ident.conf configuration file can be used to map principals to user names; for example, pgusername@realm could be mapped to just pgusername . Alternatively, you can use the full username@realm principal as the role name in PostgreSQL without any mapping. PostgreSQL also supports mapping client principals to user names by just stripping the realm from the principal. This method is supported for backwards compatibility and is strongly discouraged as it is then impossible to distinguish different users with the same user name but coming from different realms. To enable this, set include_realm to 0. For simple single-realm installations, doing that combined with setting the krb_realm parameter (which checks that the principal's realm matches exactly what is in the krb_realm parameter) is still

3. `chunk-cbcc04a4ed5bdd7846fa4a6ad932d61737b300a19dcf589fab4cf7e8610a5538` — pg-17; score=28.244490, dense=0.000000, sparse=28.244490, rerank=None

> intends to connect to. The servicename part of the principal is ordinarily postgres , but another value can be selected via libpq 's krbsrvname connection parameter. The hostname part is the fully qualified host name that libpq is told to connect to. The realm name is the preferred realm specified in the Kerberos configuration file(s) accessible to the client. The client will also have a principal name for its own identity (and it must have a valid ticket for this principal). To use GSSAPI for authentication, the client principal must be associated with a PostgreSQL database user name. The pg_ident.conf configuration file can be used to map principals to user names; for example, pgusername@realm could be mapped to just pgusername . Alternatively, you can use the full username@realm principal as the role name in PostgreSQL without any mapping. PostgreSQL also supports mapping client principals to user names by just stripping the realm from the principal. This method is supported for backwards compatibility and is strongly discouraged as it is then impossible to distinguish different users with the same user name but coming from different realms. To enable this, set include_realm to 0. For simple single-realm installations, doing that combined with setting the krb_realm parameter (which checks that the principal's realm matches exactly what is in the krb_realm parameter) is still

## draft-7f9ef8ca7db593fa

What is the customary filename selected by hba_file?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) hba_file ( string ) Specifies the configuration file for host-based authentication (customarily called pg_hba.conf ).

### Top three retrieved
1. `chunk-3d24696d8bf22df17c9d499baa02c736f092adc5f797dfb01435aef4d45d73c5` — pg-17; score=23.997900, dense=0.000000, sparse=23.997900, rerank=None

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The pg_hba.conf file is read on start-up and when the main server process receives a SIGHUP signal. If you edit the file on an active system, you will need to signal the postmaster (using pg_ctl reload , calling the SQL function pg_reload_conf() , or using kill -HUP ) to make it re-read the file. The preceding statement is not true on Microsoft Windows: there, any changes in the pg_hba.conf file are immediately applied by subsequent new connections. The system view pg_hba_file_rules can be helpful for pre-testing changes to the pg_hba.conf file, or for diagnosing problems if loading of the file did not have the desired effects. Rows in the view with non-null error fields indicate problems in the corresponding lines of the file. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the

2. `chunk-67911986d3b2b9cc75a7cb444cd329061fd2defb1e88be726ccdaf3ef765a079` — pg-16; score=22.751975, dense=0.000000, sparse=22.751975, rerank=None

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the next line by ending the line with a backslash. (Backslashes are not special except at the end of a line.) A record is made up of a number of fields which are separated by spaces and/or tabs. Fields can contain white space if the field value is double-quoted. Quoting one of the keywords in a database, user, or address field (e.g., all or replication ) makes the word lose its special meaning, and just match a database, user, or host with that name. Backslash line continuation applies even within quoted text or comments. Each authentication record specifies a connection type, a client IP address range (if relevant for the connection type), a database name, a user name, and the authentication method to be

3. `chunk-b8f76b4a73b8336b8d1f1b8849c85e4a8ab4c21a64f334f6319930eae60ad559` — pg-15; score=22.751975, dense=0.000000, sparse=22.751975, rerank=None

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the next line by ending the line with a backslash. (Backslashes are not special except at the end of a line.) A record is made up of a number of fields which are separated by spaces and/or tabs. Fields can contain white space if the field value is double-quoted. Quoting one of the keywords in a database, user, or address field (e.g., all or replication ) makes the word lose its special meaning, and just match a database, user, or host with that name. Backslash line continuation applies even within quoted text or comments. Each record specifies a connection type, a client IP address range (if relevant for the connection type), a database name, a user name, and the authentication method to be used

## draft-97bcb36324c56d2a

What number identifies the first page of a large object in pg_largeobject?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) pageno int4 Page number of this page within its large object (counting from zero)

### Top three retrieved
1. `chunk-006cbb7bc5add7256d761b85457c7544eeeafa8e73e18e97b992d80c2cba1080` — pg-15; score=51.593954, dense=0.000000, sparse=51.593954, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

2. `chunk-61e357df06adaa29a4cf6da9f325363b17f4d2cc36c5fb14b547aebd4c27856a` — pg-16; score=51.593954, dense=0.000000, sparse=51.593954, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

3. `chunk-7030d3387276a19728f0806066578ef33be22c4946369d8afe8885e40c9fa50a` — pg-17; score=51.593954, dense=0.000000, sparse=51.593954, rerank=None

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

## draft-e0141266fb4b67fd

What filename does ssl_cert_file use by default?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_cert_file ( string ) Specifies the name of the file containing the SSL server certificate. Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file or on the server command line. The default is server.crt .

### Top three retrieved
1. `chunk-7385e8cf22bf0af12a1a47b5d70b5a43df5cbc135d0548af564d37bcfc16b19b` — pg-17; score=35.883077, dense=0.000000, sparse=35.883077, rerank=None

> | File | Contents | Effect | | --- | --- | --- | | ssl_cert_file ($PGDATA/server.crt) | server certificate | sent to client to indicate server's identity | | ssl_key_file ($PGDATA/server.key) | server private key | proves server certificate was sent by the owner; does not indicate certificate owner is trustworthy | | ssl_ca_file | trusted certificate authorities | checks that client certificate is signed by a trusted certificate authority | | ssl_crl_file | certificates revoked by certificate authorities | client certificate must not be on this list |

2. `chunk-b67a28ea116696e7710fe1f28bb6c6d4d384d4b6eb0b1c5ee6722df1a7164b64` — pg-16; score=35.883077, dense=0.000000, sparse=35.883077, rerank=None

> | File | Contents | Effect | | --- | --- | --- | | ssl_cert_file ($PGDATA/server.crt) | server certificate | sent to client to indicate server's identity | | ssl_key_file ($PGDATA/server.key) | server private key | proves server certificate was sent by the owner; does not indicate certificate owner is trustworthy | | ssl_ca_file | trusted certificate authorities | checks that client certificate is signed by a trusted certificate authority | | ssl_crl_file | certificates revoked by certificate authorities | client certificate must not be on this list |

3. `chunk-ed02b66fcb953ea322b20775bf33298bca5247972a2257c0b1b48a93eb0cf60f` — pg-15; score=35.883077, dense=0.000000, sparse=35.883077, rerank=None

> | File | Contents | Effect | | --- | --- | --- | | ssl_cert_file ($PGDATA/server.crt) | server certificate | sent to client to indicate server's identity | | ssl_key_file ($PGDATA/server.key) | server private key | proves server certificate was sent by the owner; does not indicate certificate owner is trustworthy | | ssl_ca_file | trusted certificate authorities | checks that client certificate is signed by a trusted certificate authority | | ssl_crl_file | certificates revoked by certificate authorities | client certificate must not be on this list |

## draft-00d4ad3e896413a3

Is Partial Mode supported by string_agg in PostgreSQL 15?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) string_agg ( value text, delimiter text ) text string_agg ( value bytea, delimiter bytea ) bytea Concatenates the non-null input values into a string. Each value after the first is preceded by the corresponding delimiter (if it's not null). | No

### Top three retrieved
1. `chunk-fbdb452bf605fa53bcb5eac6a958f13013980ea8a0786838d269f3bb9cafabdc` — pg-15; score=28.282705, dense=0.000000, sparse=28.282705, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_object_agg , jsonb_object_agg , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by

2. `chunk-8b016650fef8bd099dbcd9cfd1de8beb5d2bbf2fad2c975133bc5c32d6b548c8` — pg-16; score=27.752054, dense=0.000000, sparse=27.752054, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully

3. `chunk-557d8850f5bad9e6709ba512b164f320b2a43f45f44442e64530ba7f20a3d484` — pg-16; score=27.200639, dense=0.000000, sparse=27.200639, rerank=None

> SELECT string_agg(a, ',' ORDER BY a) FROM table;

## draft-6ea99930a2f5381a

Which units does work_mem assume when none are specified in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes.
- (pg-16) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes.

### Top three retrieved
1. `chunk-964c190580d0d6b8dab6d0844ecc7edaa4d9f97e17e90ce941fed4ffc5319e9f` — pg-15; score=39.797268, dense=0.000000, sparse=39.797268, rerank=None

> tables are used in hash joins, hash-based aggregation, memoize nodes and hash-based processing of IN subqueries. Hash-based operations are generally more sensitive to memory availability than equivalent sort-based operations. The memory limit for a hash table is computed by multiplying work_mem by hash_mem_multiplier . This makes it possible for hash-based operations to use an amount of memory that exceeds the usual work_mem base amount. hash_mem_multiplier ( floating point ) Used to compute the maximum amount of memory that hash-based operations can use. The final limit is determined by multiplying work_mem by hash_mem_multiplier . The default value is 2.0, which makes hash-based operations use twice the usual work_mem base amount. Consider increasing hash_mem_multiplier in environments where spilling by query operations is a regular occurrence, especially when simply increasing work_mem results in memory pressure (memory pressure typically takes the form of intermittent out of memory errors). The default setting of 2.0 is often effective with mixed workloads. Higher settings in the range of 2.0 - 8.0 or more may be effective in environments where work_mem has already been increased to 40MB or more. maintenance_work_mem ( integer ) Specifies the maximum amount of memory to be used by maintenance operations, such as VACUUM , CREATE INDEX , and ALTER TABLE ADD FOREIGN KEY . If this value is specified without units, it is

2. `chunk-d8a03bf3620f8541fad82825d1968b8337a2284afb10b513c18ccaba90684b6b` — pg-16; score=39.797268, dense=0.000000, sparse=39.797268, rerank=None

> tables are used in hash joins, hash-based aggregation, memoize nodes and hash-based processing of IN subqueries. Hash-based operations are generally more sensitive to memory availability than equivalent sort-based operations. The memory limit for a hash table is computed by multiplying work_mem by hash_mem_multiplier . This makes it possible for hash-based operations to use an amount of memory that exceeds the usual work_mem base amount. hash_mem_multiplier ( floating point ) Used to compute the maximum amount of memory that hash-based operations can use. The final limit is determined by multiplying work_mem by hash_mem_multiplier . The default value is 2.0, which makes hash-based operations use twice the usual work_mem base amount. Consider increasing hash_mem_multiplier in environments where spilling by query operations is a regular occurrence, especially when simply increasing work_mem results in memory pressure (memory pressure typically takes the form of intermittent out of memory errors). The default setting of 2.0 is often effective with mixed workloads. Higher settings in the range of 2.0 - 8.0 or more may be effective in environments where work_mem has already been increased to 40MB or more. maintenance_work_mem ( integer ) Specifies the maximum amount of memory to be used by maintenance operations, such as VACUUM , CREATE INDEX , and ALTER TABLE ADD FOREIGN KEY . If this value is specified without units, it is

3. `chunk-7bb0bbd093fbf56955c694cf4c38db5d8dd7ac3aaf606394f28f9ff5a2200ea9` — pg-17; score=36.088287, dense=0.000000, sparse=36.088287, rerank=None

> where work_mem has already been increased to 40MB or more. maintenance_work_mem ( integer ) Specifies the maximum amount of memory to be used by maintenance operations, such as VACUUM , CREATE INDEX , and ALTER TABLE ADD FOREIGN KEY . If this value is specified without units, it is taken as kilobytes. It defaults to 64 megabytes ( 64MB ). Since only one of these operations can be executed at a time by a database session, and an installation normally doesn't have many of them running concurrently, it's safe to set this value significantly larger than work_mem . Larger settings might improve performance for vacuuming and for restoring database dumps. Note that when autovacuum runs, up to autovacuum_max_workers times this memory may be allocated, so be careful not to set the default value too high. It may be useful to control for this by separately setting autovacuum_work_mem . autovacuum_work_mem ( integer ) Specifies the maximum amount of memory to be used by each autovacuum worker process. If this value is specified without units, it is taken as kilobytes. It defaults to -1, indicating that the value of maintenance_work_mem should be used instead. The setting has no effect on the behavior of VACUUM when run in other contexts. This parameter can only be set in the postgresql.conf file or on the

## draft-03c3d795b855d0b7

Which escape produces a literal percent sign in basebackup_to_shell.command?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15']

### Expected evidence
- (pg-15) If %% occurs in the command string, it will be replaced by a single % .

### Top three retrieved
1. `chunk-1f531afff4b62db68899452452222297e08b96ff1e8d2a0f5611be27c1852cf9` — pg-17; score=38.282454, dense=0.000000, sparse=38.282454, rerank=None

> LIKE The LIKE expression returns true if the string matches the supplied pattern . (As expected, the NOT LIKE expression returns false if LIKE returns true, and vice versa. An equivalent expression is NOT ( string LIKE pattern ) .) If pattern does not contain percent signs or underscores, then the pattern only represents the string itself; in that case LIKE acts like the equals operator. An underscore ( _ ) in pattern stands for (matches) any single character; a percent sign ( % ) matches any sequence of zero or more characters. Some examples: LIKE pattern matching always covers the entire string. Therefore, if it's desired to match a sequence anywhere within a string, the pattern must start and end with a percent sign. To match a literal underscore or percent sign without matching other characters, the respective character in pattern must be preceded by the escape character. The default escape character is the backslash but a different one can be selected by using the ESCAPE clause. To match the escape character itself, write two escape characters. If you have standard_conforming_strings turned off, any backslashes you write in literal string constants will need to be doubled. See String Constants for more information. It's also possible to select no escape character by writing ESCAPE '' . This effectively disables the

2. `chunk-6c4716487ffda5d3e3e559d48571637778a078e64efe15150fe16436a5522fdd` — pg-15; score=38.282454, dense=0.000000, sparse=38.282454, rerank=None

> LIKE The LIKE expression returns true if the string matches the supplied pattern . (As expected, the NOT LIKE expression returns false if LIKE returns true, and vice versa. An equivalent expression is NOT ( string LIKE pattern ) .) If pattern does not contain percent signs or underscores, then the pattern only represents the string itself; in that case LIKE acts like the equals operator. An underscore ( _ ) in pattern stands for (matches) any single character; a percent sign ( % ) matches any sequence of zero or more characters. Some examples: LIKE pattern matching always covers the entire string. Therefore, if it's desired to match a sequence anywhere within a string, the pattern must start and end with a percent sign. To match a literal underscore or percent sign without matching other characters, the respective character in pattern must be preceded by the escape character. The default escape character is the backslash but a different one can be selected by using the ESCAPE clause. To match the escape character itself, write two escape characters. If you have standard_conforming_strings turned off, any backslashes you write in literal string constants will need to be doubled. See String Constants for more information. It's also possible to select no escape character by writing ESCAPE '' . This effectively disables the

3. `chunk-e8832ccb6010a6ec788138d4354525d10079124bec779df6f4ca325741624e1a` — pg-16; score=38.282454, dense=0.000000, sparse=38.282454, rerank=None

> LIKE The LIKE expression returns true if the string matches the supplied pattern . (As expected, the NOT LIKE expression returns false if LIKE returns true, and vice versa. An equivalent expression is NOT ( string LIKE pattern ) .) If pattern does not contain percent signs or underscores, then the pattern only represents the string itself; in that case LIKE acts like the equals operator. An underscore ( _ ) in pattern stands for (matches) any single character; a percent sign ( % ) matches any sequence of zero or more characters. Some examples: LIKE pattern matching always covers the entire string. Therefore, if it's desired to match a sequence anywhere within a string, the pattern must start and end with a percent sign. To match a literal underscore or percent sign without matching other characters, the respective character in pattern must be preceded by the escape character. The default escape character is the backslash but a different one can be selected by using the ESCAPE clause. To match the escape character itself, write two escape characters. If you have standard_conforming_strings turned off, any backslashes you write in literal string constants will need to be doubled. See String Constants for more information. It's also possible to select no escape character by writing ESCAPE '' . This effectively disables the

## draft-826bd7733c5466a3

What happens when auto_explain.log_min_duration is zero?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15']

### Expected evidence
- (pg-15) auto_explain.log_min_duration is the minimum statement execution time, in milliseconds, that will cause the statement's plan to be logged. Setting this to 0 logs all plans.

### Top three retrieved
1. `chunk-06e0ee74cb7a506fd20611eee95b48f482132e9b44e56ec03981cda446be8851` — pg-15; score=51.138704, dense=0.000000, sparse=51.138704, rerank=None

> # postgresql.conf session_preload_libraries = 'auto_explain' auto_explain.log_min_duration = '3s'

2. `chunk-5d86f6fa7433e2b0801b51c0635c6fe09b82200ac8eb6f026ec68b2abca99b02` — pg-16; score=51.138704, dense=0.000000, sparse=51.138704, rerank=None

> # postgresql.conf session_preload_libraries = 'auto_explain' auto_explain.log_min_duration = '3s'

3. `chunk-7f9803d3b0bf515057865e4934c9daa0cec6f568107c5cdcb1f96fa6951ced2e` — pg-17; score=51.138704, dense=0.000000, sparse=51.138704, rerank=None

> # postgresql.conf session_preload_libraries = 'auto_explain' auto_explain.log_min_duration = '3s'

## draft-8958779a0216b9a7

Are null inputs included in the array produced by json_agg_strict in PostgreSQL 16?

**Category:** wrong version. **Reason:** A same-lineage wrong version outranks the first correct evidence.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) json_agg_strict ( anyelement ) json jsonb_agg_strict ( anyelement ) jsonb Collects all the input values, skipping nulls, into a JSON array. Values are converted to JSON as per to_json or to_jsonb.

### Top three retrieved
1. `chunk-8b016650fef8bd099dbcd9cfd1de8beb5d2bbf2fad2c975133bc5c32d6b548c8` — pg-16; score=45.982365, dense=0.000000, sparse=45.982365, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully

2. `chunk-679daae5d0d418760b28931d366d44e55adf66c77381fee6f30803c4cdd5e7de` — pg-17; score=45.374323, dense=0.000000, sparse=45.374323, rerank=None

> there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given

3. `chunk-2759f0822a788033d79c3140f537e1c3fc78d00f0d4b2a2ae38f7b1d3f05e262` — pg-17; score=40.685063, dense=0.000000, sparse=40.685063, rerank=None

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. While all aggregates below accept an optional ORDER BY clause (as outlined in Aggregate Expressions ), the clause has only been added to aggregates whose output is affected by ordering. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict ,

## draft-0bd01d40748321be

Which role grants access to the slots reserved by reserved_connections in PostgreSQL 16?

**Category:** wrong version. **Reason:** A same-lineage wrong version outranks the first correct evidence.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) reserved_connections ( integer ) Determines the number of connection slots that are reserved for connections by roles with privileges of the pg_use_reserved_connections role.

### Top three retrieved
1. `chunk-d6edacb790c3e4add8e36a723005729ae943f11c075f69e1df971cf6e8d8086b` — pg-17; score=44.781306, dense=0.000000, sparse=44.781306, rerank=None

> sum of superuser_reserved_connections and reserved_connections , new connections will be accepted only for superusers and roles with privileges of pg_use_reserved_connections . If superuser_reserved_connections or fewer connection slots are available, new connections will be accepted only for superusers. The default value is zero connections. The value must be less than max_connections minus superuser_reserved_connections . This parameter can only be set at server start. superuser_reserved_connections ( integer ) Determines the number of connection slots that are reserved for connections by PostgreSQL superusers. At most max_connections connections can ever be active simultaneously. Whenever the number of active concurrent connections is at least max_connections minus superuser_reserved_connections , new connections will be accepted only for superusers. The connection slots reserved by this parameter are intended as final reserve for emergency use after the slots reserved by reserved_connections have been exhausted. The default value is three connections. The value must be less than max_connections minus reserved_connections . This parameter can only be set at server start. unix_socket_directories ( string ) Specifies the directory of the Unix-domain socket(s) on which the server is to listen for connections from client applications. Multiple sockets can be created by listing multiple directories separated by commas. Whitespace between entries is ignored; surround a directory name with double quotes if you need to include whitespace or commas in the name. An empty

2. `chunk-49edd73b121ff2b2d390c9ed189ff0307b6ea96c49c2d2b92d4f1e5eef8f4494` — pg-16; score=43.434615, dense=0.000000, sparse=43.434615, rerank=None

> connection slots are available, new connections will be accepted only for superusers. The default value is zero connections. The value must be less than max_connections minus superuser_reserved_connections . This parameter can only be set at server start. superuser_reserved_connections ( integer ) Determines the number of connection slots that are reserved for connections by PostgreSQL superusers. At most max_connections connections can ever be active simultaneously. Whenever the number of active concurrent connections is at least max_connections minus superuser_reserved_connections , new connections will be accepted only for superusers. The connection slots reserved by this parameter are intended as final reserve for emergency use after the slots reserved by reserved_connections have been exhausted. The default value is three connections. The value must be less than max_connections minus reserved_connections . This parameter can only be set at server start. unix_socket_directories ( string ) Specifies the directory of the Unix-domain socket(s) on which the server is to listen for connections from client applications. Multiple sockets can be created by listing multiple directories separated by commas. Whitespace between entries is ignored; surround a directory name with double quotes if you need to include whitespace or commas in the name. An empty value specifies not listening on any Unix-domain sockets, in which case only TCP/IP sockets can be used to connect to the server. A value that

3. `chunk-b13c9ef0622ca21f21ed3cff60c520c96b0c414b273b9d1c4317ff92addd299d` — pg-17; score=42.959338, dense=0.000000, sparse=42.959338, rerank=None

> server start. port ( integer ) The TCP port the server listens on; 5432 by default. Note that the same port number is used for all IP addresses the server listens on. This parameter can only be set at server start. max_connections ( integer ) Determines the maximum number of concurrent connections to the database server. The default is typically 100 connections, but might be less if your kernel settings will not support it (as determined during initdb ). This parameter can only be set at server start. PostgreSQL sizes certain resources based directly on the value of max_connections . Increasing its value leads to higher allocation of those resources, including shared memory. When running a standby server, you must set this parameter to the same or higher value than on the primary server. Otherwise, queries will not be allowed in the standby server. reserved_connections ( integer ) Determines the number of connection slots that are reserved for connections by roles with privileges of the pg_use_reserved_connections role. Whenever the number of free connection slots is greater than superuser_reserved_connections but less than or equal to the sum of superuser_reserved_connections and reserved_connections , new connections will be accepted only for superusers and roles with privileges of pg_use_reserved_connections . If superuser_reserved_connections or fewer connection slots are available, new connections will be accepted only

## draft-201911bd3ea7cb06

What is the default max_stack_depth in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) max_stack_depth ( integer ) Specifies the maximum safe depth of the server's execution stack. The ideal setting for this parameter is the actual stack size limit enforced by the kernel (as set by ulimit -s or local equivalent), less a safety margin of a megabyte or so. The safety margin is needed because the stack depth is not checked in every routine in the server, but only in key potentially-recursive routines. If this value is specified without units, it is taken as kilobytes. The default setting is two megabytes ( 2MB ), which is conservatively small and unlikely to risk crashes.
- (pg-16) max_stack_depth ( integer ) Specifies the maximum safe depth of the server's execution stack. The ideal setting for this parameter is the actual stack size limit enforced by the kernel (as set by ulimit -s or local equivalent), less a safety margin of a megabyte or so. The safety margin is needed because the stack depth is not checked in every routine in the server, but only in key potentially-recursive routines. If this value is specified without units, it is taken as kilobytes. The default setting is two megabytes ( 2MB ), which is conservatively small and unlikely to risk crashes.

### Top three retrieved
1. `chunk-15bf55352bcb0fbe5152acdc4314f5e2446d1b2eaed614a9967280af98c44f69` — pg-16; score=48.269282, dense=0.000000, sparse=48.269282, rerank=None

> Insufficient Stack Depth If the errors test results in a server crash at the select infinite_recurse() command, it means that the platform's limit on process stack size is smaller than the max_stack_depth parameter indicates. This can be fixed by running the server under a higher stack size limit (4MB is recommended with the default value of max_stack_depth ). If you are unable to do that, an alternative is to reduce the value of max_stack_depth . On platforms supporting getrlimit() , the server should automatically choose a safe value of max_stack_depth ; so unless you've manually overridden this setting, a failure of this kind is a reportable bug.

2. `chunk-65e88dbe83ca0ba2264359d199988cc8552b3031f2440f93743752525764d3e4` — pg-17; score=48.269282, dense=0.000000, sparse=48.269282, rerank=None

> Insufficient Stack Depth If the errors test results in a server crash at the select infinite_recurse() command, it means that the platform's limit on process stack size is smaller than the max_stack_depth parameter indicates. This can be fixed by running the server under a higher stack size limit (4MB is recommended with the default value of max_stack_depth ). If you are unable to do that, an alternative is to reduce the value of max_stack_depth . On platforms supporting getrlimit() , the server should automatically choose a safe value of max_stack_depth ; so unless you've manually overridden this setting, a failure of this kind is a reportable bug.

3. `chunk-7c1893868418d600b59274b856da9d77736467872d84f403617f081959372389` — pg-15; score=48.269282, dense=0.000000, sparse=48.269282, rerank=None

> Insufficient Stack Depth If the errors test results in a server crash at the select infinite_recurse() command, it means that the platform's limit on process stack size is smaller than the max_stack_depth parameter indicates. This can be fixed by running the server under a higher stack size limit (4MB is recommended with the default value of max_stack_depth ). If you are unable to do that, an alternative is to reduce the value of max_stack_depth . On platforms supporting getrlimit() , the server should automatically choose a safe value of max_stack_depth ; so unless you've manually overridden this setting, a failure of this kind is a reportable bug.

## draft-229c3274e4f0153b

What is the default value of vacuum_buffer_usage_limit in PostgreSQL 16?

**Category:** wrong version. **Reason:** A same-lineage wrong version outranks the first correct evidence.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) vacuum_buffer_usage_limit ( integer ) Specifies the size of the Buffer Access Strategy used by the VACUUM and ANALYZE commands. A setting of 0 will allow the operation to use any number of shared_buffers . Otherwise valid sizes range from 128 kB to 16 GB . If the specified size would exceed 1/8 the size of shared_buffers , the size is silently capped to that value. The default value is 256 kB .

### Top three retrieved
1. `chunk-4082ce958e4bcc6b68df7b2c2604d9b46ad648aaec648ca2d7fece3bb2c77fac` — pg-17; score=42.473817, dense=0.000000, sparse=42.473817, rerank=None

> separately issue VACUUM (ONLY_DATABASE_STATS) afterwards. ONLY_DATABASE_STATS Specifies that VACUUM should do nothing except update the database-wide statistics about oldest unfrozen XIDs. When this option is specified, the table_and_columns list must be empty, and no other option may be enabled except VERBOSE . BUFFER_USAGE_LIMIT Specifies the Buffer Access Strategy ring buffer size for VACUUM . This size is used to calculate the number of shared buffers which will be reused as part of this strategy. 0 disables use of a Buffer Access Strategy . If ANALYZE is also specified, the BUFFER_USAGE_LIMIT value is used for both the vacuum and analyze stages. This option can't be used with the FULL option except if ANALYZE is also specified. When this option is not specified, VACUUM uses the value from vacuum_buffer_usage_limit . Higher settings can allow VACUUM to run more quickly, but having too large a setting may cause too many other useful pages to be evicted from shared buffers. The minimum value is 128 kB and the maximum value is 16 GB . boolean Specifies whether the selected option should be turned on or off. You can write TRUE , ON , or 1 to enable the option, and FALSE , OFF , or 0 to disable it. The boolean value can also be omitted, in which case TRUE is assumed. integer Specifies

2. `chunk-8372197095bd223d626b0d87e4000c8605ada4255c1500710ea4806d978a3c90` — pg-16; score=42.473817, dense=0.000000, sparse=42.473817, rerank=None

> separately issue VACUUM (ONLY_DATABASE_STATS) afterwards. ONLY_DATABASE_STATS Specifies that VACUUM should do nothing except update the database-wide statistics about oldest unfrozen XIDs. When this option is specified, the table_and_columns list must be empty, and no other option may be enabled except VERBOSE . BUFFER_USAGE_LIMIT Specifies the Buffer Access Strategy ring buffer size for VACUUM . This size is used to calculate the number of shared buffers which will be reused as part of this strategy. 0 disables use of a Buffer Access Strategy . If ANALYZE is also specified, the BUFFER_USAGE_LIMIT value is used for both the vacuum and analyze stages. This option can't be used with the FULL option except if ANALYZE is also specified. When this option is not specified, VACUUM uses the value from vacuum_buffer_usage_limit . Higher settings can allow VACUUM to run more quickly, but having too large a setting may cause too many other useful pages to be evicted from shared buffers. The minimum value is 128 kB and the maximum value is 16 GB . boolean Specifies whether the selected option should be turned on or off. You can write TRUE , ON , or 1 to enable the option, and FALSE , OFF , or 0 to disable it. The boolean value can also be omitted, in which case TRUE is assumed. integer Specifies

3. `chunk-b842ce79dc0875c872b49914f59d4437af58cb5503e7ad442c80c3cf0b35e8fc` — pg-17; score=42.375457, dense=0.000000, sparse=42.375457, rerank=None

> value of maintenance_work_mem should be used instead. The setting has no effect on the behavior of VACUUM when run in other contexts. This parameter can only be set in the postgresql.conf file or on the server command line. vacuum_buffer_usage_limit ( integer ) Specifies the size of the Buffer Access Strategy used by the VACUUM and ANALYZE commands. A setting of 0 will allow the operation to use any number of shared_buffers . Otherwise valid sizes range from 128 kB to 16 GB . If the specified size would exceed 1/8 the size of shared_buffers , the size is silently capped to that value. The default value is 2MB . If this value is specified without units, it is taken as kilobytes. This parameter can be set at any time. It can be overridden for VACUUM and ANALYZE when passing the BUFFER_USAGE_LIMIT option. Higher settings can allow VACUUM and ANALYZE to run more quickly, but having too large a setting may cause too many other useful pages to be evicted from shared buffers. logical_decoding_work_mem ( integer ) Specifies the maximum amount of memory to be used by logical decoding, before some of the decoded changes are written to local disk. This limits the amount of memory used by logical streaming replication connections. It defaults to 64 megabytes ( 64MB ). Since

## draft-24083cabffc26972

Does bit_and ignore null inputs in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) Computes the bitwise AND of all non-null input values.
- (pg-16) Computes the bitwise AND of all non-null input values.

### Top three retrieved
1. `chunk-97eec8cb65436e01e1e9468cec070e1fa54a40260344c3eed6ccb5b671a339ba` — pg-15; score=29.765900, dense=0.000000, sparse=29.765900, rerank=None

> File Header The file header consists of 15 bytes of fixed fields, followed by a variable-length header extension area. The fixed fields are: Signature 11-byte sequence PGCOPY\n\377\r\n\0 — note that the zero byte is a required part of the signature. (The signature is designed to allow easy identification of files that have been munged by a non-8-bit-clean transfer. This signature will be changed by end-of-line-translation filters, dropped zero bytes, dropped high bits, or parity changes.) Flags field 32-bit integer bit mask to denote important aspects of the file format. Bits are numbered from 0 ( LSB ) to 31 ( MSB ). Note that this field is stored in network byte order (most significant byte first), as are all the integer fields used in the file format. Bits 16–31 are reserved to denote critical file format issues; a reader should abort if it finds an unexpected bit set in this range. Bits 0–15 are reserved to signal backwards-compatible format issues; a reader should simply ignore any unexpected bits set in this range. Currently only one flag bit is defined, and the rest must be zero: Bit 16 If 1, OIDs are included in the data; if 0, not. Oid system columns are not supported in PostgreSQL anymore, but the format still contains the indicator. Header extension area length 32-bit integer,

2. `chunk-abd596e46d3dfd2903b110c5f7f53bebbfa1a8718e1b232e410e9f6393941bf4` — pg-17; score=29.765900, dense=0.000000, sparse=29.765900, rerank=None

> File Header The file header consists of 15 bytes of fixed fields, followed by a variable-length header extension area. The fixed fields are: Signature 11-byte sequence PGCOPY\n\377\r\n\0 — note that the zero byte is a required part of the signature. (The signature is designed to allow easy identification of files that have been munged by a non-8-bit-clean transfer. This signature will be changed by end-of-line-translation filters, dropped zero bytes, dropped high bits, or parity changes.) Flags field 32-bit integer bit mask to denote important aspects of the file format. Bits are numbered from 0 ( LSB ) to 31 ( MSB ). Note that this field is stored in network byte order (most significant byte first), as are all the integer fields used in the file format. Bits 16–31 are reserved to denote critical file format issues; a reader should abort if it finds an unexpected bit set in this range. Bits 0–15 are reserved to signal backwards-compatible format issues; a reader should simply ignore any unexpected bits set in this range. Currently only one flag bit is defined, and the rest must be zero: Bit 16 If 1, OIDs are included in the data; if 0, not. Oid system columns are not supported in PostgreSQL anymore, but the format still contains the indicator. Header extension area length 32-bit integer,

3. `chunk-f1c55a1888f2a5840cc043d3e95113cfa0d02686ff9dd8cc8717c820e7542a9a` — pg-16; score=29.765900, dense=0.000000, sparse=29.765900, rerank=None

> File Header The file header consists of 15 bytes of fixed fields, followed by a variable-length header extension area. The fixed fields are: Signature 11-byte sequence PGCOPY\n\377\r\n\0 — note that the zero byte is a required part of the signature. (The signature is designed to allow easy identification of files that have been munged by a non-8-bit-clean transfer. This signature will be changed by end-of-line-translation filters, dropped zero bytes, dropped high bits, or parity changes.) Flags field 32-bit integer bit mask to denote important aspects of the file format. Bits are numbered from 0 ( LSB ) to 31 ( MSB ). Note that this field is stored in network byte order (most significant byte first), as are all the integer fields used in the file format. Bits 16–31 are reserved to denote critical file format issues; a reader should abort if it finds an unexpected bit set in this range. Bits 0–15 are reserved to signal backwards-compatible format issues; a reader should simply ignore any unexpected bits set in this range. Currently only one flag bit is defined, and the rest must be zero: Bit 16 If 1, OIDs are included in the data; if 0, not. Oid system columns are not supported in PostgreSQL anymore, but the format still contains the indicator. Header extension area length 32-bit integer,

## draft-4b2f4b62ab512fa7

When automatic plan logging samples nested statements, can it select just some nested statements from a call?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15']

### Expected evidence
- (pg-15) auto_explain.sample_rate causes auto_explain to only explain a fraction of the statements in each session. The default is 1, meaning explain all the queries. In case of nested statements, either all will be explained or none.

### Top three retrieved
1. `chunk-6ddaee7cbf778ca607792f50ab7c3f1a9422f805050989f45eeadecbc44f1d5a` — pg-15; score=30.549664, dense=0.000000, sparse=30.549664, rerank=None

> included when an execution plan is logged. This parameter has no effect unless auto_explain.log_analyze is enabled. This parameter is off by default. Only superusers can change this setting. auto_explain.log_verbose ( boolean ) auto_explain.log_verbose controls whether verbose details are printed when an execution plan is logged; it's equivalent to the VERBOSE option of EXPLAIN . This parameter is off by default. Only superusers can change this setting. auto_explain.log_settings ( boolean ) auto_explain.log_settings controls whether information about modified configuration options is printed when an execution plan is logged. Only options affecting query planning with value different from the built-in default value are included in the output. This parameter is off by default. Only superusers can change this setting. auto_explain.log_format ( enum ) auto_explain.log_format selects the EXPLAIN output format to be used. The allowed values are text , xml , json , and yaml . The default is text. Only superusers can change this setting. auto_explain.log_level ( enum ) auto_explain.log_level selects the log level at which auto_explain will log the query plan. Valid values are DEBUG5 , DEBUG4 , DEBUG3 , DEBUG2 , DEBUG1 , INFO , NOTICE , WARNING , and LOG . The default is LOG . Only superusers can change this setting. auto_explain.log_nested_statements ( boolean ) auto_explain.log_nested_statements causes nested statements (statements executed inside a function) to be considered for logging.

2. `chunk-28b75402e8c5c35be236aa87c9b3138827ab26f6aad28447de81224c0558dc7e` — pg-17; score=29.883238, dense=0.000000, sparse=29.883238, rerank=None

> , json , and yaml . The default is text. Only superusers can change this setting. auto_explain.log_level ( enum ) auto_explain.log_level selects the log level at which auto_explain will log the query plan. Valid values are DEBUG5 , DEBUG4 , DEBUG3 , DEBUG2 , DEBUG1 , INFO , NOTICE , WARNING , and LOG . The default is LOG . Only superusers can change this setting. auto_explain.log_nested_statements ( boolean ) auto_explain.log_nested_statements causes nested statements (statements executed inside a function) to be considered for logging. When it is off, only top-level query plans are logged. This parameter is off by default. Only superusers can change this setting. auto_explain.sample_rate ( real ) auto_explain.sample_rate causes auto_explain to only explain a fraction of the statements in each session. The default is 1, meaning explain all the queries. In case of nested statements, either all will be explained or none. Only superusers can change this setting. In ordinary usage, these parameters are set in postgresql.conf , although superusers can alter them on-the-fly within their own sessions. Typical usage might be:

3. `chunk-e98db9981bf201f66c728351ed56559136fb8ddc0a542444ccd50a528a53e57b` — pg-16; score=29.883238, dense=0.000000, sparse=29.883238, rerank=None

> , json , and yaml . The default is text. Only superusers can change this setting. auto_explain.log_level ( enum ) auto_explain.log_level selects the log level at which auto_explain will log the query plan. Valid values are DEBUG5 , DEBUG4 , DEBUG3 , DEBUG2 , DEBUG1 , INFO , NOTICE , WARNING , and LOG . The default is LOG . Only superusers can change this setting. auto_explain.log_nested_statements ( boolean ) auto_explain.log_nested_statements causes nested statements (statements executed inside a function) to be considered for logging. When it is off, only top-level query plans are logged. This parameter is off by default. Only superusers can change this setting. auto_explain.sample_rate ( real ) auto_explain.sample_rate causes auto_explain to only explain a fraction of the statements in each session. The default is 1, meaning explain all the queries. In case of nested statements, either all will be explained or none. Only superusers can change this setting. In ordinary usage, these parameters are set in postgresql.conf , although superusers can alter them on-the-fly within their own sessions. Typical usage might be:
