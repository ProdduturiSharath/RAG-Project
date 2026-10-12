# Worst test failures: recommended-cross-encoder

DEV-selected system or fixed DEV-derived combined arm. Showing 30 of 52 failures.
Ranking: all-quotes@10, Recall@10, nDCG@10, MRR ascending; then ID.

## draft-33d8c19a2a6a932d

What is the maximum size of one pg_largeobject.data value?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) data bytea Actual data stored in the large object. This will never be more than LOBLKSIZE bytes and might be less.

### Top three retrieved
1. `chunk-006cbb7bc5add7256d761b85457c7544eeeafa8e73e18e97b992d80c2cba1080` — pg-15; score=3.412874, dense=0.809760, sparse=23.997541, rerank=3.412874221801758

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

2. `chunk-61e357df06adaa29a4cf6da9f325363b17f4d2cc36c5fb14b547aebd4c27856a` — pg-16; score=3.412874, dense=0.809760, sparse=23.997541, rerank=3.412874221801758

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

3. `chunk-7030d3387276a19728f0806066578ef33be22c4946369d8afe8885e40c9fa50a` — pg-17; score=3.412874, dense=0.809760, sparse=23.997541, rerank=3.412874221801758

> pg_largeobject The catalog pg_largeobject holds the data making up large objects . A large object is identified by an OID assigned when it is created. Each large object is broken into segments or pages small enough to be conveniently stored as rows in pg_largeobject . The amount of data per page is defined to be LOBLKSIZE (which is currently BLCKSZ/4 , or typically 2 kB). Prior to PostgreSQL 9.0, there was no permission structure associated with large objects. As a result, pg_largeobject was publicly readable and could be used to obtain the OIDs (and contents) of all large objects in the system. This is no longer the case; use pg_largeobject_metadata to obtain a list of large object OIDs. Each row of pg_largeobject holds data for one page of a large object, beginning at byte offset ( pageno * LOBLKSIZE ) within the object. The implementation allows sparse storage: pages might be missing, and might be shorter than LOBLKSIZE bytes even if they are not the last page of the object. Missing regions within a large object read as zeroes.

## draft-9b1f37bc7842b40e

Must the ECDH exchange curve match the curve of the server's elliptic-curve key?

**Category:** text gap. **Reason:** No authorized, version-valid chunk contains a whole evidence quote.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key.

### Top three retrieved
1. `chunk-44ae8642eeb739124b0e979a05fa3720b46decde1b8dc94b7569fc7afd82a620` — pg-15; score=5.879607, dense=0.792794, sparse=47.882802, rerank=5.879607200622559

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

2. `chunk-7a0f69735558b64a65e491b53e5fec6add8b0f7386beb4e360def027cc853198` — pg-16; score=5.879607, dense=0.792794, sparse=47.882802, rerank=5.879607200622559

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

3. `chunk-d368baa59607597c650cea379d867c65561088b6e137e5cd4280087f49373d7e` — pg-17; score=5.879607, dense=0.792794, sparse=47.882802, rerank=5.879607200622559

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

## draft-a2cf6aa49912f6e7

When does bool_or return true in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bool_or ( boolean ) boolean Returns true if any non-null input value is true, otherwise false.
- (pg-16) bool_or ( boolean ) boolean Returns true if any non-null input value is true, otherwise false.

### Top three retrieved
1. `chunk-2361d4168e2d31e3ee1e448c83269bdb731d4b3a1263c8d1054f0852f5894ae9` — pg-15; score=4.512216, dense=0.756914, sparse=20.916121, rerank=4.512215614318848

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

2. `chunk-d36f151f4a60dbc8dc70ef0b26546747f657353b4e2bb40f420e2be9282008e8` — pg-17; score=4.512216, dense=0.756914, sparse=20.916121, rerank=4.512215614318848

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

3. `chunk-d9c5f9047dba883af7c556147a557304d8e7d9b21bca41af46a2d2caf4975e5b` — pg-16; score=4.512216, dense=0.756914, sparse=20.916121, rerank=4.512215614318848

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

## draft-d1b8f6b5aa7eddfa

When does bool_and return true in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) bool_and ( boolean ) boolean Returns true if all non-null input values are true, otherwise false.
- (pg-16) bool_and ( boolean ) boolean Returns true if all non-null input values are true, otherwise false.

### Top three retrieved
1. `chunk-2361d4168e2d31e3ee1e448c83269bdb731d4b3a1263c8d1054f0852f5894ae9` — pg-15; score=4.434857, dense=0.757129, sparse=20.916121, rerank=4.434857368469238

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

2. `chunk-d36f151f4a60dbc8dc70ef0b26546747f657353b4e2bb40f420e2be9282008e8` — pg-17; score=4.434857, dense=0.757129, sparse=20.916121, rerank=4.434857368469238

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

3. `chunk-d9c5f9047dba883af7c556147a557304d8e7d9b21bca41af46a2d2caf4975e5b` — pg-16; score=4.434857, dense=0.757129, sparse=20.916121, rerank=4.434857368469238

> Data Type Mapping When a PL/Python function is called, its arguments are converted from their PostgreSQL data type to a corresponding Python type: PostgreSQL boolean is converted to Python bool . PostgreSQL smallint , int , bigint and oid are converted to Python int . PostgreSQL real and double are converted to Python float . PostgreSQL numeric is converted to Python Decimal . This type is imported from the cdecimal package if that is available. Otherwise, decimal.Decimal from the standard library will be used. cdecimal is significantly faster than decimal . In Python 3.3 and up, however, cdecimal has been integrated into the standard library under the name decimal , so there is no longer any difference. PostgreSQL bytea is converted to Python bytes . All other data types, including the PostgreSQL character string types, are converted to a Python str (in Unicode like all Python strings). For nonscalar data types, see below. When a PL/Python function returns, its return value is converted to the function's declared PostgreSQL return data type as follows: When the PostgreSQL return type is boolean , the return value will be evaluated for truth according to the Python rules. That is, 0 and empty string are false, but notably 'f' is true. When the PostgreSQL return type is bytea , the return value will be

## draft-dadefc52fd565605

What OpenSSL curve name is the default for ssl_ecdh_curve?

**Category:** text gap. **Reason:** No authorized, version-valid chunk contains a whole evidence quote.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ecdh_curve ( string ) Specifies the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 .

### Top three retrieved
1. `chunk-44ae8642eeb739124b0e979a05fa3720b46decde1b8dc94b7569fc7afd82a620` — pg-15; score=7.971632, dense=0.861828, sparse=44.914184, rerank=7.971632480621338

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

2. `chunk-7a0f69735558b64a65e491b53e5fec6add8b0f7386beb4e360def027cc853198` — pg-16; score=7.971632, dense=0.861828, sparse=44.914184, rerank=7.971632480621338

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

3. `chunk-d368baa59607597c650cea379d867c65561088b6e137e5cd4280087f49373d7e` — pg-17; score=7.971632, dense=0.861828, sparse=44.914184, rerank=7.971632480621338

> the name of the curve to use in ECDH key exchange. It needs to be supported by all clients that connect. It does not need to be the same curve used by the server's Elliptic Curve key. This parameter can only be set in the postgresql.conf file or on the server command line. The default is prime256v1 . OpenSSL names for the most common curves are: prime256v1 (NIST P-256), secp384r1 (NIST P-384), secp521r1 (NIST P-521). The full list of available curves can be shown with the command openssl ecparam -list_curves . Not all of them are usable in TLS though. ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use. Valid values are currently: TLSv1 , TLSv1.1 , TLSv1.2 , TLSv1.3 . Older versions of the OpenSSL library do not support all values; an error will be raised if an unsupported setting is chosen. Protocol versions before TLS 1.0, namely SSL version 2 and 3, are always disabled. The default is TLSv1.2 , which satisfies industry best practices as of this writing. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version.

## draft-dee2728be3a4e6aa

What is the return type of count(*) in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) count ( * ) bigint Computes the number of input rows.
- (pg-16) count ( * ) bigint Computes the number of input rows.

### Top three retrieved
1. `chunk-0d7c683bc660a140e94b2775305df3ece1d6ae7a6498b2d0c1999e3eb62a7a0b` — pg-15; score=1.211857, dense=0.000000, sparse=19.149026, rerank=1.2118569612503052

> LIMIT Clause The LIMIT clause consists of two independent sub-clauses: The parameter count specifies the maximum number of rows to return, while start specifies the number of rows to skip before starting to return rows. When both are specified, start rows are skipped before starting to count the count rows to be returned. If the count expression evaluates to NULL, it is treated as LIMIT ALL , i.e., no limit. If start evaluates to NULL, it is treated the same as OFFSET 0 . SQL:2008 introduced a different syntax to achieve the same result, which PostgreSQL also supports. It is: In this syntax, the start or count value is required by the standard to be a literal constant, a parameter, or a variable name; as a PostgreSQL extension, other expressions are allowed, but will generally need to be enclosed in parentheses to avoid ambiguity. If count is omitted in a FETCH clause, it defaults to 1. The WITH TIES option is used to return any additional rows that tie for the last place in the result set according to the ORDER BY clause; ORDER BY is mandatory in this case, and SKIP LOCKED is not allowed. ROW and ROWS as well as FIRST and NEXT are noise words that don't influence the effects of these clauses. According to the standard,

2. `chunk-6b1dd37fbfe32e9b7eb822358f9c1f1a68696f9557fa12ee82525385f3cdb581` — pg-16; score=1.211857, dense=0.000000, sparse=19.149026, rerank=1.2118569612503052

> LIMIT Clause The LIMIT clause consists of two independent sub-clauses: The parameter count specifies the maximum number of rows to return, while start specifies the number of rows to skip before starting to return rows. When both are specified, start rows are skipped before starting to count the count rows to be returned. If the count expression evaluates to NULL, it is treated as LIMIT ALL , i.e., no limit. If start evaluates to NULL, it is treated the same as OFFSET 0 . SQL:2008 introduced a different syntax to achieve the same result, which PostgreSQL also supports. It is: In this syntax, the start or count value is required by the standard to be a literal constant, a parameter, or a variable name; as a PostgreSQL extension, other expressions are allowed, but will generally need to be enclosed in parentheses to avoid ambiguity. If count is omitted in a FETCH clause, it defaults to 1. The WITH TIES option is used to return any additional rows that tie for the last place in the result set according to the ORDER BY clause; ORDER BY is mandatory in this case, and SKIP LOCKED is not allowed. ROW and ROWS as well as FIRST and NEXT are noise words that don't influence the effects of these clauses. According to the standard,

3. `chunk-f3876bceccd94e6915270add371d8379825df677b611bdb2f493a2ab8101cd54` — pg-17; score=1.211857, dense=0.000000, sparse=19.149026, rerank=1.2118569612503052

> LIMIT Clause The LIMIT clause consists of two independent sub-clauses: The parameter count specifies the maximum number of rows to return, while start specifies the number of rows to skip before starting to return rows. When both are specified, start rows are skipped before starting to count the count rows to be returned. If the count expression evaluates to NULL, it is treated as LIMIT ALL , i.e., no limit. If start evaluates to NULL, it is treated the same as OFFSET 0 . SQL:2008 introduced a different syntax to achieve the same result, which PostgreSQL also supports. It is: In this syntax, the start or count value is required by the standard to be a literal constant, a parameter, or a variable name; as a PostgreSQL extension, other expressions are allowed, but will generally need to be enclosed in parentheses to avoid ambiguity. If count is omitted in a FETCH clause, it defaults to 1. The WITH TIES option is used to return any additional rows that tie for the last place in the result set according to the ORDER BY clause; ORDER BY is mandatory in this case, and SKIP LOCKED is not allowed. ROW and ROWS as well as FIRST and NEXT are noise words that don't influence the effects of these clauses. According to the standard,

## draft-2f27ea088c1b07ce

What happens if json_object_agg_unique receives duplicate keys in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) json_object_agg_unique ( key "any", value "any" ) json jsonb_object_agg_unique ( key "any", value "any" ) jsonb Collects all the key/value pairs into a JSON object. Key arguments are coerced to text; value arguments are converted as per to_json or to_jsonb. Values can be null, but keys cannot. If there is a duplicate key an error is thrown.

### Top three retrieved
1. `chunk-ecc3d9d8222bb76d2b65fc0a87cf875bb75d063824bea57052bf74fe8b4d57cc` — pg-16; score=1.269969, dense=0.000000, sparse=32.068673, rerank=1.2699694633483887

> a significant advantage. Because the json type stores an exact copy of the input text, it will preserve semantically-insignificant white space between tokens, as well as the order of keys within JSON objects. Also, if a JSON object within the value contains the same key more than once, all the key/value pairs are kept. (The processing functions consider the last value as the operative one.) By contrast, jsonb does not preserve white space, does not preserve the order of object keys, and does not keep duplicate object keys. If duplicate keys are specified in the input, only the last value is kept. In general, most applications should prefer to store JSON data as jsonb , unless there are quite specialized needs, such as legacy assumptions about ordering of object keys. RFC 7159 specifies that JSON strings should be encoded in UTF8. It is therefore not possible for the JSON types to conform rigidly to the JSON specification unless the database encoding is UTF8. Attempts to directly include characters that cannot be represented in the database encoding will fail; conversely, characters that can be represented in the database encoding but not in UTF8 will be allowed. RFC 7159 permits JSON strings to contain Unicode escape sequences denoted by \u XXXX . In the input function for the json type, Unicode escapes

2. `chunk-f3dcd73fd52c9578ad710d32adeac0710479ccb02ebf3a004e26d40a346c01f5` — pg-16; score=0.740262, dense=0.722668, sparse=17.912222, rerank=0.7402623891830444

> pg_stat_activity view. Fix casting a composite-type variable to a domain type when returning its value from a PL/pgSQL function (Tom Lane) § If the variable's value is NULL, a cache lookup failed for type 0 error resulted. Fix potential null pointer dereference in contrib/hstore 's binary input function (Michael Paquier) § hstore 's receive function crashed on input containing duplicate keys. hstore values generated by Postgres would never contain duplicate keys, so this mistake has gone unnoticed. The crash could be provoked by malicious or corrupted data.

3. `chunk-c9d0861efc88d31c91bb6cc8693a439ec545f4d77e8849601ffe408cd56fe87f` — pg-16; score=0.588260, dense=0.732448, sparse=20.762616, rerank=0.5882604122161865

> Index Uniqueness Checks PostgreSQL enforces SQL uniqueness constraints using unique indexes , which are indexes that disallow multiple entries with identical keys. An access method that supports this feature sets amcanunique true. (At present, only b-tree supports it.) Columns listed in the INCLUDE clause are not considered when enforcing uniqueness. Because of MVCC, it is always necessary to allow duplicate entries to exist physically in an index: the entries might refer to successive versions of a single logical row. The behavior we actually want to enforce is that no MVCC snapshot could include two rows with equal index keys. This breaks down into the following cases that must be checked when inserting a new row into a unique index: If a conflicting valid row has been deleted by the current transaction, it's okay. (In particular, since an UPDATE always deletes the old row version before inserting the new version, this will allow an UPDATE on a row without changing the key.) If a conflicting row has been inserted by an as-yet-uncommitted transaction, the would-be inserter must wait to see if that transaction commits. If it rolls back then there is no conflict. If it commits without deleting the conflicting row again, there is a uniqueness violation. (In practice we just wait for the other transaction to end and then redo

## draft-832a9b9cbacbceba

Which predefined role lets a user with database CREATE permission issue CREATE SUBSCRIPTION in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) pg_create_subscription | Allow users with CREATE permission on the database to issue CREATE SUBSCRIPTION.

### Top three retrieved
1. `chunk-70c178fe2cfd0ebb0602c6fabcb0ed0de35a7833edd44d6e0c69e8def0c75dbc` — pg-16; score=4.252891, dense=0.784970, sparse=37.936402, rerank=4.252890586853027

> Privileges Add predefined role pg_create_subscription with permission to create subscriptions (Robert Haas) § Allow subscriptions to not require passwords (Robert Haas) § § § This is accomplished with the option password_required=false . Simplify permissions for LOCK TABLE (Jeff Davis) § Previously a user's ability to perform LOCK TABLE at various lock levels was limited to the lock levels required by the commands they had permission to execute on the table. For example, someone with UPDATE permission could perform all lock levels except ACCESS SHARE , even though it was a lesser lock level. Now users can issue lesser lock levels if they already have permission for greater lock levels. Allow ALTER GROUP group_name ADD USER user_name to be performed with ADMIN OPTION (Robert Haas) § Previously CREATEROLE permission was required. Allow GRANT to use WITH ADMIN TRUE / FALSE syntax (Robert Haas) § Previously only the WITH ADMIN OPTION syntax was supported. Allow roles that create other roles to automatically inherit the new role's rights or the ability to SET ROLE to the new role (Robert Haas, Shi Yu) § § This is controlled by server variable createrole_self_grant . Prevent users from changing the default privileges of non-inherited roles (Robert Haas) § This is now only allowed for inherited roles. When granting role membership, require the granted-by role to be

2. `chunk-a7aa45f40fd71eb1e9f356317180d4c0efd6b0b8df4f5155736ab8c09e2c9acd` — pg-16; score=3.962882, dense=0.796061, sparse=24.659204, rerank=3.9628818035125732

> Predefined Roles PostgreSQL provides a set of predefined roles that provide access to certain, commonly needed, privileged capabilities and information. Administrators (including roles that have the CREATEROLE privilege) can GRANT these roles to users and/or other roles in their environment, providing those users with access to the specified capabilities and information. The predefined roles are described in Predefined Roles . Note that the specific permissions for each of the roles may change in the future as additional capabilities are added. Administrators should monitor the release notes for changes. The pg_monitor , pg_read_all_settings , pg_read_all_stats and pg_stat_scan_tables roles are intended to allow administrators to easily configure a role for the purpose of monitoring the database server. They grant a set of common privileges allowing the role to read various useful configuration settings, statistics and other system information normally restricted to superusers. The pg_database_owner role has one implicit, situation-dependent member, namely the owner of the current database. Like any role, it can own objects or receive grants of access privileges. Consequently, once pg_database_owner has rights within a template database, each owner of a database instantiated from that template will exercise those rights. pg_database_owner cannot be a member of any role, and it cannot have non-implicit members. Initially, this role owns the public schema, so each database owner governs local use of the

3. `chunk-e7cbd567c7bd82c77b53407c18414c404b61d3cc0a26abc1ce52319e811ebcf7` — pg-16; score=3.627706, dense=0.815109, sparse=27.270641, rerank=3.6277058124542236

> Description createuser creates a new PostgreSQL user (or more precisely, a role). Only superusers and users with CREATEROLE privilege can create new users, so createuser must be invoked by someone who can connect as a superuser or a user with CREATEROLE privilege. If you wish to create a role with the SUPERUSER , REPLICATION , or BYPASSRLS privilege, you must connect as a superuser, not merely with CREATEROLE privilege. Being a superuser implies the ability to bypass all access permission checks within the database, so superuser access should not be granted lightly. CREATEROLE also conveys very extensive privileges . createuser is a wrapper around the SQL command CREATE ROLE . There is no effective difference between creating users via this utility and via other methods for accessing the server.

## draft-39a8f35fc5f9cb13

What happens to null array entries in array_to_string when null_string is omitted in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) array_to_string ( array anyarray, delimiter text , null_string text ) text Converts each array element to its text representation, and concatenates those separated by the delimiter string. If null_string is given and is not NULL, then NULL array entries are represented by that string; otherwise, they are omitted.
- (pg-16) array_to_string ( array anyarray, delimiter text , null_string text ) text Converts each array element to its text representation, and concatenates those separated by the delimiter string. If null_string is given and is not NULL, then NULL array entries are represented by that string; otherwise, they are omitted.

### Top three retrieved
1. `chunk-6560e13f63abd4e6e3a5451dfa771daf888b2a1912c309a93b2cd975764a7fdf` — pg-15; score=4.931211, dense=0.838063, sparse=23.094645, rerank=4.931210994720459

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

2. `chunk-75d6f7845f32cf5b2105aaa47c1bcfbe416391ba5f4f973d1e0ba3d0e6d6e6ae` — pg-17; score=4.931211, dense=0.838063, sparse=23.094645, rerank=4.931210994720459

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

3. `chunk-e96bdd39a5eea04e1d94cad496fb7a45adc7440d5c0425607a7e9fdaf887060f` — pg-16; score=4.931211, dense=0.838063, sparse=23.094645, rerank=4.931210994720459

> Previous PostgreSQL Versions array_nulls ( boolean ) This controls whether the array input parser recognizes unquoted NULL as specifying a null array element. By default, this is on , allowing array values containing null values to be entered. However, PostgreSQL versions before 8.2 did not support null values in arrays, and therefore would treat NULL as specifying a normal array element with the string value NULL . For backward compatibility with applications that require the old behavior, this variable can be turned off . Note that it is possible to create array values containing null values even when this variable is off . backslash_quote ( enum ) This controls whether a quote mark can be represented by \' in a string literal. The preferred, SQL-standard way to represent a quote mark is by doubling it ( '' ) but PostgreSQL has historically also accepted \' . However, use of \' creates security risks because in some client character set encodings, there are multibyte characters in which the last byte is numerically equivalent to ASCII \ . If client-side code does escaping incorrectly then an SQL-injection attack is possible. This risk can be prevented by making the server reject queries in which a quote mark appears to be escaped by a backslash. The allowed values of backslash_quote are on (allow \'

## draft-df61a1a2e6822bb7

What does cardinality return for an empty array in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) cardinality ( anyarray ) integer Returns the total number of elements in the array, or 0 if the array is empty.
- (pg-16) cardinality ( anyarray ) integer Returns the total number of elements in the array, or 0 if the array is empty.

### Top three retrieved
1. `chunk-a3e07d25a5d71bae222e989dc4683c83dc5d480d53e7ed8cfccc2b65d6c4f77f` — pg-17; score=0.923319, dense=0.000000, sparse=24.250108, rerank=0.9233185052871704

> the array bounds, then it is silently reduced to just the overlapping region instead of returning null. The current dimensions of any array value can be retrieved with the array_dims function: array_dims produces a text result, which is convenient for people to read but perhaps inconvenient for programs. Dimensions can also be retrieved with array_upper and array_lower , which return the upper and lower bound of a specified array dimension, respectively: array_length will return the length of a specified array dimension: cardinality returns the total number of elements in an array across all dimensions. It is effectively the number of rows a call to unnest would yield:

2. `chunk-cc7063e2d03799bb86a5fcb180ea2b9bbd2cf328c94e3afb24556452eea7649c` — pg-15; score=0.923319, dense=0.000000, sparse=24.250108, rerank=0.9233185052871704

> the array bounds, then it is silently reduced to just the overlapping region instead of returning null. The current dimensions of any array value can be retrieved with the array_dims function: array_dims produces a text result, which is convenient for people to read but perhaps inconvenient for programs. Dimensions can also be retrieved with array_upper and array_lower , which return the upper and lower bound of a specified array dimension, respectively: array_length will return the length of a specified array dimension: cardinality returns the total number of elements in an array across all dimensions. It is effectively the number of rows a call to unnest would yield:

3. `chunk-dd49a405464b25acf2e313e0bb0271e8b7565660c9b78b6d5319206327d964e4` — pg-16; score=0.923319, dense=0.000000, sparse=24.250108, rerank=0.9233185052871704

> the array bounds, then it is silently reduced to just the overlapping region instead of returning null. The current dimensions of any array value can be retrieved with the array_dims function: array_dims produces a text result, which is convenient for people to read but perhaps inconvenient for programs. Dimensions can also be retrieved with array_upper and array_lower , which return the upper and lower bound of a specified array dimension, respectively: array_length will return the length of a specified array dimension: cardinality returns the total number of elements in an array across all dimensions. It is effectively the number of rows a call to unnest would yield:

## draft-00f9bb9ebb902fbc

Which dimension does trim_array shorten in a multidimensional array in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) trim_array ( array anyarray, n integer ) anyarray Trims an array by removing the last n elements. If the array is multidimensional, only the first dimension is trimmed.
- (pg-16) trim_array ( array anyarray, n integer ) anyarray Trims an array by removing the last n elements. If the array is multidimensional, only the first dimension is trimmed.

### Top three retrieved
1. `chunk-694386ae933c4ccbd7df98547a55077dc2bb48f5edadaf19dd5feb4cf3979e3d` — pg-17; score=-0.732748, dense=0.743631, sparse=20.903856, rerank=-0.7327476143836975

> Arrays, Lists SQL array values are passed into PL/Python as a Python list. To return an SQL array value out of a PL/Python function, return a Python list: Multidimensional arrays are passed into PL/Python as nested Python lists. A 2-dimensional array is a list of lists, for example. When returning a multi-dimensional SQL array out of a PL/Python function, the inner lists at each level must all be of the same size. For example: Other Python sequences, like tuples, are also accepted for backwards-compatibility with PostgreSQL versions 9.6 and below, when multi-dimensional arrays were not supported. However, they are always treated as one-dimensional arrays, because they are ambiguous with composite types. For the same reason, when a composite type is used in a multi-dimensional array, it must be represented by a tuple, rather than a list. Note that in Python, strings are sequences, which can have undesirable effects that might be familiar to Python programmers:

2. `chunk-697d381610187065d96f107de60c639f4b24670ae7e70e7765e173014d67fdc3` — pg-15; score=-0.732748, dense=0.743631, sparse=20.903856, rerank=-0.7327476143836975

> Arrays, Lists SQL array values are passed into PL/Python as a Python list. To return an SQL array value out of a PL/Python function, return a Python list: Multidimensional arrays are passed into PL/Python as nested Python lists. A 2-dimensional array is a list of lists, for example. When returning a multi-dimensional SQL array out of a PL/Python function, the inner lists at each level must all be of the same size. For example: Other Python sequences, like tuples, are also accepted for backwards-compatibility with PostgreSQL versions 9.6 and below, when multi-dimensional arrays were not supported. However, they are always treated as one-dimensional arrays, because they are ambiguous with composite types. For the same reason, when a composite type is used in a multi-dimensional array, it must be represented by a tuple, rather than a list. Note that in Python, strings are sequences, which can have undesirable effects that might be familiar to Python programmers:

3. `chunk-9f9080e0d6cf841feda3646d0428b7c90007b4ad62c978a63eca904dbd46d252` — pg-16; score=-0.732748, dense=0.743631, sparse=20.903856, rerank=-0.7327476143836975

> Arrays, Lists SQL array values are passed into PL/Python as a Python list. To return an SQL array value out of a PL/Python function, return a Python list: Multidimensional arrays are passed into PL/Python as nested Python lists. A 2-dimensional array is a list of lists, for example. When returning a multi-dimensional SQL array out of a PL/Python function, the inner lists at each level must all be of the same size. For example: Other Python sequences, like tuples, are also accepted for backwards-compatibility with PostgreSQL versions 9.6 and below, when multi-dimensional arrays were not supported. However, they are always treated as one-dimensional arrays, because they are ambiguous with composite types. For the same reason, when a composite type is used in a multi-dimensional array, it must be represented by a tuple, rather than a list. Note that in Python, strings are sequences, which can have undesirable effects that might be familiar to Python programmers:

## draft-3abee3e4240c30d3

What is the default work_mem in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes. The default value is four megabytes ( 4MB ).
- (pg-16) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes. The default value is four megabytes ( 4MB ).

### Top three retrieved
1. `chunk-7fd14a36387fc84e861c402fd973fcfbfd2b6be66b06d29e18b86db8fe479883` — pg-17; score=3.210735, dense=0.796697, sparse=23.656050, rerank=3.2107348442077637

> -S work-mem Specifies the base amount of memory to be used by sorts and hash tables before resorting to temporary disk files. See the description of the work_mem configuration parameter in Memory . -V --version Print the postgres version and exit. -- name = value Sets a named run-time parameter; a shorter form of -c . --describe-config This option dumps out the server's internal configuration variables, descriptions, and defaults in tab-delimited COPY format. It is designed primarily for use by administration tools. -? --help Show help about postgres command line arguments, and exit.

2. `chunk-88c8272c1ad2d399b7072d8d7d8886a83425e75b9045962e0047733fc2a80532` — pg-16; score=3.210735, dense=0.796697, sparse=23.656050, rerank=3.2107348442077637

> -S work-mem Specifies the base amount of memory to be used by sorts and hash tables before resorting to temporary disk files. See the description of the work_mem configuration parameter in Memory . -V --version Print the postgres version and exit. -- name = value Sets a named run-time parameter; a shorter form of -c . --describe-config This option dumps out the server's internal configuration variables, descriptions, and defaults in tab-delimited COPY format. It is designed primarily for use by administration tools. -? --help Show help about postgres command line arguments, and exit.

3. `chunk-fdc50dcaf183bb0e851ed735ae8d77b5aa556f5eda191678e6665f20f7a5b7cc` — pg-15; score=3.210735, dense=0.796697, sparse=23.656050, rerank=3.2107348442077637

> -S work-mem Specifies the base amount of memory to be used by sorts and hash tables before resorting to temporary disk files. See the description of the work_mem configuration parameter in Memory . -V --version Print the postgres version and exit. -- name = value Sets a named run-time parameter; a shorter form of -c . --describe-config This option dumps out the server's internal configuration variables, descriptions, and defaults in tab-delimited COPY format. It is designed primarily for use by administration tools. -? --help Show help about postgres command line arguments, and exit.

## draft-8212c39cab5f00aa

Does bit_or include null inputs in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) Computes the bitwise OR of all non-null input values.
- (pg-16) Computes the bitwise OR of all non-null input values.

### Top three retrieved
1. `chunk-88cfdde5cfc6c6c7827ad146f2b5000cca42c549a04a78125595fd93ee997b08` — pg-17; score=1.569492, dense=0.000000, sparse=21.315630, rerank=1.5694921016693115

> — the SQL standard expects sum to behave that way. We can do this simply by omitting the initcond phrase, so that the initial state value is null. Ordinarily this would mean that the sfunc would need to check for a null state-value input. But for sum and some other simple aggregates like max and min , it is sufficient to insert the first nonnull input value into the state variable and then start applying the transition function at the second nonnull input value. PostgreSQL will do that automatically if the initial state value is null and the transition function is marked strict (i.e., not to be called for null inputs). Another bit of default behavior for a strict transition function is that the previous state value is retained unchanged whenever a null input value is encountered. Thus, null values are ignored. If you need some other behavior for null inputs, do not declare your transition function as strict; instead code it to test for null inputs and do whatever is needed. avg (average) is a more complex example of an aggregate. It requires two pieces of running state: the sum of the inputs and the count of the number of inputs. The final result is obtained by dividing these quantities. Average is typically implemented by using an array as

2. `chunk-89665eb32aaa682cf2887821ff32b951cf56ce25a98b119a7f3f45a6bc895769` — pg-15; score=1.569492, dense=0.000000, sparse=21.315630, rerank=1.5694921016693115

> — the SQL standard expects sum to behave that way. We can do this simply by omitting the initcond phrase, so that the initial state value is null. Ordinarily this would mean that the sfunc would need to check for a null state-value input. But for sum and some other simple aggregates like max and min , it is sufficient to insert the first nonnull input value into the state variable and then start applying the transition function at the second nonnull input value. PostgreSQL will do that automatically if the initial state value is null and the transition function is marked strict (i.e., not to be called for null inputs). Another bit of default behavior for a strict transition function is that the previous state value is retained unchanged whenever a null input value is encountered. Thus, null values are ignored. If you need some other behavior for null inputs, do not declare your transition function as strict; instead code it to test for null inputs and do whatever is needed. avg (average) is a more complex example of an aggregate. It requires two pieces of running state: the sum of the inputs and the count of the number of inputs. The final result is obtained by dividing these quantities. Average is typically implemented by using an array as

3. `chunk-ffa4b517288efbcf8a3a9fc59c75f14c749792ae8ada6effd8c03d14335ba61f` — pg-16; score=1.569492, dense=0.000000, sparse=21.315630, rerank=1.5694921016693115

> — the SQL standard expects sum to behave that way. We can do this simply by omitting the initcond phrase, so that the initial state value is null. Ordinarily this would mean that the sfunc would need to check for a null state-value input. But for sum and some other simple aggregates like max and min , it is sufficient to insert the first nonnull input value into the state variable and then start applying the transition function at the second nonnull input value. PostgreSQL will do that automatically if the initial state value is null and the transition function is marked strict (i.e., not to be called for null inputs). Another bit of default behavior for a strict transition function is that the previous state value is retained unchanged whenever a null input value is encountered. Thus, null values are ignored. If you need some other behavior for null inputs, do not declare your transition function as strict; instead code it to test for null inputs and do whatever is needed. avg (average) is a more complex example of an aggregate. It requires two pieces of running state: the sum of the inputs and the count of the number of inputs. The final result is obtained by dividing these quantities. Average is typically implemented by using an array as

## draft-24083cabffc26972

Does bit_and ignore null inputs in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) Computes the bitwise AND of all non-null input values.
- (pg-16) Computes the bitwise AND of all non-null input values.

### Top three retrieved
1. `chunk-88cfdde5cfc6c6c7827ad146f2b5000cca42c549a04a78125595fd93ee997b08` — pg-17; score=2.946849, dense=0.000000, sparse=21.315630, rerank=2.9468488693237305

> — the SQL standard expects sum to behave that way. We can do this simply by omitting the initcond phrase, so that the initial state value is null. Ordinarily this would mean that the sfunc would need to check for a null state-value input. But for sum and some other simple aggregates like max and min , it is sufficient to insert the first nonnull input value into the state variable and then start applying the transition function at the second nonnull input value. PostgreSQL will do that automatically if the initial state value is null and the transition function is marked strict (i.e., not to be called for null inputs). Another bit of default behavior for a strict transition function is that the previous state value is retained unchanged whenever a null input value is encountered. Thus, null values are ignored. If you need some other behavior for null inputs, do not declare your transition function as strict; instead code it to test for null inputs and do whatever is needed. avg (average) is a more complex example of an aggregate. It requires two pieces of running state: the sum of the inputs and the count of the number of inputs. The final result is obtained by dividing these quantities. Average is typically implemented by using an array as

2. `chunk-89665eb32aaa682cf2887821ff32b951cf56ce25a98b119a7f3f45a6bc895769` — pg-15; score=2.946849, dense=0.000000, sparse=21.315630, rerank=2.9468488693237305

> — the SQL standard expects sum to behave that way. We can do this simply by omitting the initcond phrase, so that the initial state value is null. Ordinarily this would mean that the sfunc would need to check for a null state-value input. But for sum and some other simple aggregates like max and min , it is sufficient to insert the first nonnull input value into the state variable and then start applying the transition function at the second nonnull input value. PostgreSQL will do that automatically if the initial state value is null and the transition function is marked strict (i.e., not to be called for null inputs). Another bit of default behavior for a strict transition function is that the previous state value is retained unchanged whenever a null input value is encountered. Thus, null values are ignored. If you need some other behavior for null inputs, do not declare your transition function as strict; instead code it to test for null inputs and do whatever is needed. avg (average) is a more complex example of an aggregate. It requires two pieces of running state: the sum of the inputs and the count of the number of inputs. The final result is obtained by dividing these quantities. Average is typically implemented by using an array as

3. `chunk-ffa4b517288efbcf8a3a9fc59c75f14c749792ae8ada6effd8c03d14335ba61f` — pg-16; score=2.946849, dense=0.000000, sparse=21.315630, rerank=2.9468488693237305

> — the SQL standard expects sum to behave that way. We can do this simply by omitting the initcond phrase, so that the initial state value is null. Ordinarily this would mean that the sfunc would need to check for a null state-value input. But for sum and some other simple aggregates like max and min , it is sufficient to insert the first nonnull input value into the state variable and then start applying the transition function at the second nonnull input value. PostgreSQL will do that automatically if the initial state value is null and the transition function is marked strict (i.e., not to be called for null inputs). Another bit of default behavior for a strict transition function is that the previous state value is retained unchanged whenever a null input value is encountered. Thus, null values are ignored. If you need some other behavior for null inputs, do not declare your transition function as strict; instead code it to test for null inputs and do whatever is needed. avg (average) is a more complex example of an aggregate. It requires two pieces of running state: the sum of the inputs and the count of the number of inputs. The final result is obtained by dividing these quantities. Average is typically implemented by using an array as

## draft-de8d404798f688a2

What limits the number of items requested by array_sample in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) array_sample ( array anyarray, n integer ) anyarray Returns an array of n items randomly selected from array. n may not exceed the length of array's first dimension.

### Top three retrieved
1. `chunk-189f79cd43bf3b9200a68762f0f093df1889cc3a10666ff2fde9798ada2cc723` — pg-16; score=1.347900, dense=0.730296, sparse=18.397452, rerank=1.347900152206421

> Limitations The current limitations of PostgreSQL 's text search features are: The length of each lexeme must be less than 2 kilobytes The length of a tsvector (lexemes + positions) must be less than 1 megabyte The number of lexemes must be less than 2 64 Position values in tsvector must be greater than 0 and no more than 16,383 The match distance in a < N > (FOLLOWED BY) tsquery operator cannot be more than 16,384 No more than 256 positions per lexeme The number of nodes (lexemes + operators) in a tsquery must be less than 32,768 For comparison, the PostgreSQL 8.1 documentation contained 10,441 unique words, a total of 335,420 words, and the most frequent word postgresql was mentioned 6,127 times in 655 documents. Another example — the PostgreSQL mailing list archives contained 910,989 unique words with 57,491,343 lexemes in 461,020 messages.

2. `chunk-a727a5260dcc23fb3587ec005f1d6fd8b161e16febc9b04095019c887214deeb` — pg-16; score=0.456269, dense=0.735971, sparse=17.604320, rerank=0.45626914501190186

> PostgreSQL Limits PostgreSQL Limitations describes various hard limits of PostgreSQL . However, practical limits, such as performance limitations or available disk space may apply before absolute hard limits are reached. The maximum number of columns for a table is further reduced as the tuple being stored must fit in a single 8192-byte heap page. For example, excluding the tuple header, a tuple made up of 1,600 int columns would consume 6400 bytes and could be stored in a heap page, but a tuple of 1,600 bigint columns would consume 12800 bytes and would therefore not fit inside a heap page. Variable-length fields of types such as text , varchar , and char can have their values stored out of line in the table's TOAST table when the values are large enough to require it. Only an 18-byte pointer must remain inside the tuple in the table's heap. For shorter length variable-length fields, either a 4-byte or 1-byte field header is used and the value is stored inside the heap tuple. Columns that have been dropped from the table also contribute to the maximum column limit. Moreover, although the dropped column values for newly created tuples are internally marked as null in the tuple's null bitmap, the null bitmap also occupies space. Each table can store a theoretical maximum of 2^32

3. `chunk-6e8940c69849e783a33f283f2731564a3d5ca2782cb95c6552415e23bef0a9e3` — pg-16; score=-0.752611, dense=0.000000, sparse=23.506324, rerank=-0.7526113986968994

> Resource Limits Unix-like operating systems enforce various kinds of resource limits that might interfere with the operation of your PostgreSQL server. Of particular importance are limits on the number of processes per user, the number of open files per process, and the amount of memory available to each process. Each of these have a hard and a soft limit. The soft limit is what actually counts but it can be changed by the user up to the hard limit. The hard limit can only be changed by the root user. The system call setrlimit is responsible for setting these parameters. The shell's built-in command ulimit (Bourne shells) or limit ( csh ) is used to control the resource limits from the command line. On BSD-derived systems the file /etc/login.conf controls the various resource limits set during login. See the operating system documentation for details. The relevant parameters are maxproc , openfiles , and datasize . For example: ( -cur is the soft limit. Append -max to set the hard limit.) Kernels can also have system-wide limits on some resources. On Linux the kernel parameter fs.file-max determines the maximum number of open files that the kernel will support. It can be changed with sysctl -w fs.file-max= N . To make the setting persist across reboots, add an assignment in /etc/sysctl.conf .

## draft-5ca5682d5aa33579

Does json_object_agg_unique_strict keep entries whose values are null in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) json_object_agg_unique_strict ( key "any", value "any" ) json jsonb_object_agg_unique_strict ( key "any", value "any" ) jsonb Collects all the key/value pairs into a JSON object. Key arguments are coerced to text; value arguments are converted as per to_json or to_jsonb. The key can not be null. If the value is null then the entry is skipped. If there is a duplicate key an error is thrown.

### Top three retrieved
1. `chunk-8908fa26e794467b20d3f73e1de7a855254a1873b19a1936a59b028a09daaf9e` — pg-16; score=4.602391, dense=0.842301, sparse=47.474701, rerank=4.602390766143799

> , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given to these aggregates. Users accustomed to working with other SQL database management systems might be disappointed by the performance of the count aggregate when it is applied to the entire

2. `chunk-8b016650fef8bd099dbcd9cfd1de8beb5d2bbf2fad2c975133bc5c32d6b548c8` — pg-16; score=2.978392, dense=0.000000, sparse=52.284985, rerank=2.978391647338867

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully

3. `chunk-f8602155705b609fc9b9c88f9493b38898e35e605f9f70c59c4ffa26603d2238` — pg-16; score=1.109163, dense=0.000000, sparse=25.950931, rerank=1.1091632843017578

> number of rows containing any single one of the three index items. A disadvantage of the jsonb_path_ops approach is that it produces no index entries for JSON structures not containing any values, such as {"a": {}} . If a search for documents containing such a structure is requested, it will require a full-index scan, which is quite slow. jsonb_path_ops is therefore ill-suited for applications that often perform such searches. jsonb also supports btree and hash indexes. These are usually useful only if it's important to check equality of complete JSON documents. The btree ordering for jsonb datums is seldom of great interest, but for completeness it is: with the exception that (for historical reasons) an empty top level array sorts less than null . Objects with equal numbers of pairs are compared in the order: Note that object keys are compared in their storage order; in particular, since shorter keys are stored before longer keys, this can lead to results that might be unintuitive, such as: Similarly, arrays with equal numbers of elements are compared in the order: Primitive JSON values are compared using the same comparison rules as for the underlying PostgreSQL data type. Strings are compared using the default database collation.

## draft-32068527036ef646

Which setting selects the configuration file for user-name mapping?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ident_file ( string ) Specifies the configuration file for user name mapping (customarily called pg_ident.conf ).

### Top three retrieved
1. `chunk-101d8e38062d0c3c40582d76874e52a55dfa475ae6395dc9eda24e9d022d7b79` — pg-15; score=4.328329, dense=0.000000, sparse=23.585141, rerank=4.328329086303711

> pg_ident_file_mappings The view pg_ident_file_mappings provides a summary of the contents of the client user name mapping configuration file, pg_ident.conf . A row appears in this view for each non-empty, non-comment line in the file, with annotations indicating whether the map could be applied successfully. This view can be helpful for checking whether planned changes in the authentication configuration file will work, or for diagnosing a previous failure. Note that this view reports on the current contents of the file, not on what was last loaded by the server. By default, the pg_ident_file_mappings view can be read only by superusers. Usually, a row reflecting an incorrect entry will have values for only the line_number and error fields. See Client Authentication for more information about client authentication configuration.

2. `chunk-73acaff7cbb3c5eda2f111108ebb48245758e62927fd7264e16cf30188c272ce` — pg-16; score=4.328329, dense=0.000000, sparse=23.585141, rerank=4.328329086303711

> pg_ident_file_mappings The view pg_ident_file_mappings provides a summary of the contents of the client user name mapping configuration file, pg_ident.conf . A row appears in this view for each non-empty, non-comment line in the file, with annotations indicating whether the map could be applied successfully. This view can be helpful for checking whether planned changes in the authentication configuration file will work, or for diagnosing a previous failure. Note that this view reports on the current contents of the file, not on what was last loaded by the server. By default, the pg_ident_file_mappings view can be read only by superusers. Usually, a row reflecting an incorrect entry will have values for only the line_number and error fields. See Client Authentication for more information about client authentication configuration.

3. `chunk-e3b49007e5f0354761327be71a0c09659297fe2136c28697a92d5521c739a02d` — pg-17; score=4.328329, dense=0.000000, sparse=23.585141, rerank=4.328329086303711

> pg_ident_file_mappings The view pg_ident_file_mappings provides a summary of the contents of the client user name mapping configuration file, pg_ident.conf . A row appears in this view for each non-empty, non-comment line in the file, with annotations indicating whether the map could be applied successfully. This view can be helpful for checking whether planned changes in the authentication configuration file will work, or for diagnosing a previous failure. Note that this view reports on the current contents of the file, not on what was last loaded by the server. By default, the pg_ident_file_mappings view can be read only by superusers. Usually, a row reflecting an incorrect entry will have values for only the line_number and error fields. See Client Authentication for more information about client authentication configuration.

## draft-05e120c03871ce0e

When can notify_buffers be set in PostgreSQL 17?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: []

### Expected evidence
- (pg-17) notify_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_notify (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 16 . This parameter can only be set at server start.

### Top three retrieved
1. `chunk-b842ce79dc0875c872b49914f59d4437af58cb5503e7ad442c80c3cf0b35e8fc` — pg-17; score=2.126385, dense=0.000000, sparse=17.054152, rerank=2.126384735107422

> value of maintenance_work_mem should be used instead. The setting has no effect on the behavior of VACUUM when run in other contexts. This parameter can only be set in the postgresql.conf file or on the server command line. vacuum_buffer_usage_limit ( integer ) Specifies the size of the Buffer Access Strategy used by the VACUUM and ANALYZE commands. A setting of 0 will allow the operation to use any number of shared_buffers . Otherwise valid sizes range from 128 kB to 16 GB . If the specified size would exceed 1/8 the size of shared_buffers , the size is silently capped to that value. The default value is 2MB . If this value is specified without units, it is taken as kilobytes. This parameter can be set at any time. It can be overridden for VACUUM and ANALYZE when passing the BUFFER_USAGE_LIMIT option. Higher settings can allow VACUUM and ANALYZE to run more quickly, but having too large a setting may cause too many other useful pages to be evicted from shared buffers. logical_decoding_work_mem ( integer ) Specifies the maximum amount of memory to be used by logical decoding, before some of the decoded changes are written to local disk. This limits the amount of memory used by logical streaming replication connections. It defaults to 64 megabytes ( 64MB ). Since

2. `chunk-f98fa9a1b35aee4676c55f1d07ee3619a7b07c1523f115b0fea59bc6a08128f4` — pg-17; score=1.660201, dense=0.736035, sparse=17.808658, rerank=1.660200595855713

> during recent rounds. The average recent need is multiplied by bgwriter_lru_multiplier to arrive at an estimate of the number of buffers that will be needed during the next round. Dirty buffers are written until there are that many clean, reusable buffers available. (However, no more than bgwriter_lru_maxpages buffers will be written per round.) Thus, a setting of 1.0 represents a just in time policy of writing exactly the number of buffers predicted to be needed. Larger values provide some cushion against spikes in demand, while smaller values intentionally leave writes to be done by server processes. The default is 2.0. This parameter can only be set in the postgresql.conf file or on the server command line. bgwriter_flush_after ( integer ) Whenever more than this amount of data has been written by the background writer, attempt to force the OS to issue these writes to the underlying storage. Doing so will limit the amount of dirty data in the kernel's page cache, reducing the likelihood of stalls when an fsync is issued at the end of a checkpoint, or when the OS writes data back in larger batches in the background. Often that will result in greatly reduced transaction latency, but there also are some cases, especially with workloads that are bigger than shared_buffers , but smaller than the OS's page

3. `chunk-6658b547b563f4b4317ba25cb15a865f6e6dffbcc6839719c9b6e71f4ba16920` — pg-17; score=0.678105, dense=0.000000, sparse=16.149596, rerank=0.6781051158905029

> General Purpose -B nbuffers Sets the number of shared buffers for use by the server processes. The default value of this parameter is chosen automatically by initdb . Specifying this option is equivalent to setting the shared_buffers configuration parameter. -c name = value Sets a named run-time parameter. The configuration parameters supported by PostgreSQL are described in Server Configuration . Most of the other command line options are in fact short forms of such a parameter assignment. -c can appear multiple times to set multiple parameters. -C name Prints the value of the named run-time parameter, and exits. (See the -c option above for details.) This returns values from postgresql.conf , modified by any parameters supplied in this invocation. It does not reflect parameters supplied when the cluster was started. This can be used on a running server for most parameters. However, the server must be shut down for some runtime-computed parameters (e.g., shared_memory_size , shared_memory_size_in_huge_pages , and wal_segment_size ). This option is meant for other programs that interact with a server instance, such as pg_ctl , to query configuration parameter values. User-facing applications should instead use SHOW or the pg_settings view. -d debug-level Sets the debug level. The higher this value is set, the more debugging output is written to the server log. Values are from 1 to 5.

## draft-6ea99930a2f5381a

Which units does work_mem assume when none are specified in PostgreSQL 15 and PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes.
- (pg-16) work_mem ( integer ) Sets the base maximum amount of memory to be used by a query operation (such as a sort or hash table) before writing to temporary disk files. If this value is specified without units, it is taken as kilobytes.

### Top three retrieved
1. `chunk-7bb0bbd093fbf56955c694cf4c38db5d8dd7ac3aaf606394f28f9ff5a2200ea9` — pg-17; score=3.204711, dense=0.749455, sparse=36.088287, rerank=3.204711437225342

> where work_mem has already been increased to 40MB or more. maintenance_work_mem ( integer ) Specifies the maximum amount of memory to be used by maintenance operations, such as VACUUM , CREATE INDEX , and ALTER TABLE ADD FOREIGN KEY . If this value is specified without units, it is taken as kilobytes. It defaults to 64 megabytes ( 64MB ). Since only one of these operations can be executed at a time by a database session, and an installation normally doesn't have many of them running concurrently, it's safe to set this value significantly larger than work_mem . Larger settings might improve performance for vacuuming and for restoring database dumps. Note that when autovacuum runs, up to autovacuum_max_workers times this memory may be allocated, so be careful not to set the default value too high. It may be useful to control for this by separately setting autovacuum_work_mem . autovacuum_work_mem ( integer ) Specifies the maximum amount of memory to be used by each autovacuum worker process. If this value is specified without units, it is taken as kilobytes. It defaults to -1, indicating that the value of maintenance_work_mem should be used instead. The setting has no effect on the behavior of VACUUM when run in other contexts. This parameter can only be set in the postgresql.conf file or on the

2. `chunk-b842ce79dc0875c872b49914f59d4437af58cb5503e7ad442c80c3cf0b35e8fc` — pg-17; score=2.317413, dense=0.728906, sparse=28.555284, rerank=2.317412853240967

> value of maintenance_work_mem should be used instead. The setting has no effect on the behavior of VACUUM when run in other contexts. This parameter can only be set in the postgresql.conf file or on the server command line. vacuum_buffer_usage_limit ( integer ) Specifies the size of the Buffer Access Strategy used by the VACUUM and ANALYZE commands. A setting of 0 will allow the operation to use any number of shared_buffers . Otherwise valid sizes range from 128 kB to 16 GB . If the specified size would exceed 1/8 the size of shared_buffers , the size is silently capped to that value. The default value is 2MB . If this value is specified without units, it is taken as kilobytes. This parameter can be set at any time. It can be overridden for VACUUM and ANALYZE when passing the BUFFER_USAGE_LIMIT option. Higher settings can allow VACUUM and ANALYZE to run more quickly, but having too large a setting may cause too many other useful pages to be evicted from shared buffers. logical_decoding_work_mem ( integer ) Specifies the maximum amount of memory to be used by logical decoding, before some of the decoded changes are written to local disk. This limits the amount of memory used by logical streaming replication connections. It defaults to 64 megabytes ( 64MB ). Since

3. `chunk-19ce536d81f9f2e4a0840b38cc4575ce1259723c2933c6d0b72fc83b8b82c146` — pg-16; score=1.939020, dense=0.711339, sparse=25.523787, rerank=1.9390196800231934

> 1, 2, 9, 11, and 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, 15, and 16 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2023. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2023. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2023 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if

## draft-4a08f22879a56114

Which dimension of a multidimensional array does array_shuffle randomize in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) array_shuffle ( anyarray ) anyarray Randomly shuffles the first dimension of the array.

### Top three retrieved
1. `chunk-f0d18a2b666b31ccd937d65f9ff9229dd15bc0af1c6faf527853cec44adce24f` — pg-16; score=1.235363, dense=0.706140, sparse=17.122200, rerank=1.235363483428955

> Arrays PostgreSQL allows columns of a table to be defined as variable-length multidimensional arrays. Arrays of any built-in or user-defined base type, enum type, composite type, range type, or domain can be created.

2. `chunk-9f9080e0d6cf841feda3646d0428b7c90007b4ad62c978a63eca904dbd46d252` — pg-16; score=0.992864, dense=0.674628, sparse=21.145939, rerank=0.9928640127182007

> Arrays, Lists SQL array values are passed into PL/Python as a Python list. To return an SQL array value out of a PL/Python function, return a Python list: Multidimensional arrays are passed into PL/Python as nested Python lists. A 2-dimensional array is a list of lists, for example. When returning a multi-dimensional SQL array out of a PL/Python function, the inner lists at each level must all be of the same size. For example: Other Python sequences, like tuples, are also accepted for backwards-compatibility with PostgreSQL versions 9.6 and below, when multi-dimensional arrays were not supported. However, they are always treated as one-dimensional arrays, because they are ambiguous with composite types. For the same reason, when a composite type is used in a multi-dimensional array, it must be represented by a tuple, rather than a list. Note that in Python, strings are sequences, which can have undesirable effects that might be familiar to Python programmers:

3. `chunk-1775902b72efe7372794034a40a2e428a0a2b5f283975cb77334e5fa4019eb84` — pg-16; score=0.378210, dense=0.000000, sparse=26.755393, rerank=0.37821048498153687

> Array Input and Output Syntax The external text representation of an array value consists of items that are interpreted according to the I/O conversion rules for the array's element type, plus decoration that indicates the array structure. The decoration consists of curly braces ( { and } ) around the array value plus delimiter characters between adjacent items. The delimiter character is usually a comma ( , ) but can be something else: it is determined by the typdelim setting for the array's element type. Among the standard data types provided in the PostgreSQL distribution, all use a comma, except for type box , which uses a semicolon ( ; ). In a multidimensional array, each dimension (row, plane, cube, etc.) gets its own level of curly braces, and delimiters must be written between adjacent curly-braced entities of the same level. The array output routine will put double quotes around element values if they are empty strings, contain curly braces, delimiter characters, double quotes, backslashes, or white space, or match the word NULL . Double quotes and backslashes embedded in element values will be backslash-escaped. For numeric data types it is safe to assume that double quotes will never appear, but for textual data types one should be prepared to cope with either the presence or absence of quotes. By

## draft-e5b5f0b94a5943be

Which setting names the server's certificate-authority file?

**Category:** identifier not matched. **Reason:** The expected identifier is absent from the top three.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_ca_file ( string ) Specifies the name of the file containing the SSL server certificate authority (CA).

### Top three retrieved
1. `chunk-061bf406debb26d0a691c41347bf86ab0162105d2828024b22ed367fbf6f48aa` — pg-17; score=3.490977, dense=0.756542, sparse=25.792646, rerank=3.4909768104553223

> and any weaker setting will result in an error. In most cases it is trivial for anyone to obtain a certificate trusted by the system for a hostname they control, rendering verify-ca and all weaker modes useless. The magic system value will take precedence over a local certificate file with the same name. If for some reason you find yourself in this situation, use an alternative path like sslrootcert=./system instead. sslcrl This parameter specifies the file name of the SSL server certificate revocation list (CRL). Certificates listed in this file, if it exists, will be rejected while attempting to authenticate the server's certificate. If neither sslcrl nor sslcrldir is set, this setting is taken as ~/.postgresql/root.crl . sslcrldir This parameter specifies the directory name of the SSL server certificate revocation list (CRL). Certificates listed in the files in this directory, if it exists, will be rejected while attempting to authenticate the server's certificate. The directory needs to be prepared with the OpenSSL command openssl rehash or c_rehash . See its documentation for details. Both sslcrl and sslcrldir can be specified together. sslsni If set to 1 (default), libpq sets the TLS extension Server Name Indication ( SNI ) on SSL-enabled connections. By setting this parameter to 0, this is turned off. The Server Name Indication can be used by SSL-aware

2. `chunk-843b3d4e73d70c55857d31399b2ba53a42780b048416743aacc1b0ff6c3e0cc5` — pg-17; score=2.731020, dense=0.734708, sparse=32.718960, rerank=2.731020450592041

> server requests one and the client has one to send. require The server must request a certificate. The connection will fail if the client does not send a certificate and the server successfully authenticates the client anyway. sslcertmode=require doesn't add any additional security, since there is no guarantee that the server is validating the certificate correctly; PostgreSQL servers generally request TLS certificates from clients whether they validate them or not. The option may be useful when troubleshooting more complicated TLS setups. sslrootcert This parameter specifies the name of a file containing SSL certificate authority ( CA ) certificate(s). If the file exists, the server's certificate will be verified to be signed by one of these authorities. The default is ~/.postgresql/root.crt . The special value system may be specified instead, in which case the trusted CA roots from the SSL implementation will be loaded. The exact locations of these root certificates differ by SSL implementation and platform. For OpenSSL in particular, the locations may be further modified by the SSL_CERT_DIR and SSL_CERT_FILE environment variables. When using sslrootcert=system , the default sslmode is changed to verify-full , and any weaker setting will result in an error. In most cases it is trivial for anyone to obtain a certificate trusted by the system for a hostname they control, rendering verify-ca and all weaker

3. `chunk-6c1fae01327b112894a5467d761bb80d42809ce6878626400c2da9b6561c4baf` — pg-15; score=1.928226, dense=0.727045, sparse=31.996437, rerank=1.9282255172729492

> Enter PEM pass phrase: prompt that OpenSSL will emit by default when an encrypted client certificate key is provided to libpq . If the key is not encrypted this parameter is ignored. The parameter has no effect on keys specified by OpenSSL engines unless the engine uses the OpenSSL password callback mechanism for prompts. There is no environment variable equivalent to this option, and no facility for looking it up in .pgpass . It can be used in a service file connection definition. Users with more sophisticated uses should consider using OpenSSL engines and tools like PKCS#11 or USB crypto offload devices. sslrootcert This parameter specifies the name of a file containing SSL certificate authority ( CA ) certificate(s). If the file exists, the server's certificate will be verified to be signed by one of these authorities. The default is ~/.postgresql/root.crt . sslcrl This parameter specifies the file name of the SSL server certificate revocation list (CRL). Certificates listed in this file, if it exists, will be rejected while attempting to authenticate the server's certificate. If neither sslcrl nor sslcrldir is set, this setting is taken as ~/.postgresql/root.crl . sslcrldir This parameter specifies the directory name of the SSL server certificate revocation list (CRL). Certificates listed in the files in this directory, if it exists, will be rejected while attempting

## draft-59e8d98dc1e8267d

How many blocks does serializable_buffers allocate by default in PostgreSQL 17?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: []

### Expected evidence
- (pg-17) serializable_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_serial (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 32 .

### Top three retrieved
1. `chunk-8a2237587bc1a83e94feb138913e39b20c6d2431d92dfd000b7fba113993ad13` — pg-17; score=1.233621, dense=0.761585, sparse=20.609557, rerank=1.23362135887146

> set at server start. subtransaction_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_subtrans (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 0 , which requests shared_buffers /512 up to 1024 blocks, but not fewer than 16 blocks. This parameter can only be set at server start. transaction_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_xact (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 0 , which requests shared_buffers /512 up to 1024 blocks, but not fewer than 16 blocks. This parameter can only be set at server start. max_stack_depth ( integer ) Specifies the maximum safe depth of the server's execution stack. The ideal setting for this parameter is the actual stack size limit enforced by the kernel (as set by ulimit -s or local equivalent), less a safety margin of a megabyte or so. The safety margin is needed because the stack depth is not checked in every routine in the server, but only in key potentially-recursive routines. If this value is specified

2. `chunk-e4966549ff1bee68b8f62742ee81ac1e23658454bf733af3f0f83da716a40e89` — pg-17; score=-0.356618, dense=0.776129, sparse=22.458689, rerank=-0.35661762952804565

> by logical decoding, before some of the decoded changes are written to local disk. This limits the amount of memory used by logical streaming replication connections. It defaults to 64 megabytes ( 64MB ). Since each replication connection only uses a single buffer of this size, and an installation normally doesn't have many such connections concurrently (as limited by max_wal_senders ), it's safe to set this value significantly higher than work_mem , reducing the amount of decoded changes written to disk. commit_timestamp_buffers ( integer ) Specifies the amount of memory to use to cache the contents of pg_commit_ts (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 0 , which requests shared_buffers /512 up to 1024 blocks, but not fewer than 16 blocks. This parameter can only be set at server start. multixact_member_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_multixact/members (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 32 . This parameter can only be set at server start. multixact_offset_buffers ( integer ) Specifies the amount of shared memory to use to cache

3. `chunk-be19a2575eae2e55120e2ce097e5d5e7c02792f0cd16a1738e8ff5ffc9423234` — pg-17; score=-0.597044, dense=0.000000, sparse=20.032008, rerank=-0.5970436334609985

> in the buffer pool, though, it goes into a longer sleep regardless of bgwriter_delay . If this value is specified without units, it is taken as milliseconds. The default value is 200 milliseconds ( 200ms ). Note that on some systems, the effective resolution of sleep delays is 10 milliseconds; setting bgwriter_delay to a value that is not a multiple of 10 might have the same results as setting it to the next higher multiple of 10. This parameter can only be set in the postgresql.conf file or on the server command line. bgwriter_lru_maxpages ( integer ) In each round, no more than this many buffers will be written by the background writer. Setting this to zero disables background writing. (Note that checkpoints, which are managed by a separate, dedicated auxiliary process, are unaffected.) The default value is 100 buffers. This parameter can only be set in the postgresql.conf file or on the server command line. bgwriter_lru_multiplier ( floating point ) The number of dirty buffers written in each round is based on the number of new buffers that have been needed by server processes during recent rounds. The average recent need is multiplied by bgwriter_lru_multiplier to arrive at an estimate of the number of buffers that will be needed during the next round. Dirty buffers are written until there

## draft-00d4ad3e896413a3

Is Partial Mode supported by string_agg in PostgreSQL 15?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: []

### Expected evidence
- (pg-15) string_agg ( value text, delimiter text ) text string_agg ( value bytea, delimiter bytea ) bytea Concatenates the non-null input values into a string. Each value after the first is preceded by the corresponding delimiter (if it's not null). | No

### Top three retrieved
1. `chunk-d2b5ab77bf6aa0b44652a22dfb976c65f01d9781e8c1084dee6e613c400f590e` — pg-15; score=1.540200, dense=0.000000, sparse=17.814753, rerank=1.5402002334594727

> Parallel Aggregation PostgreSQL supports parallel aggregation by aggregating in two stages. First, each process participating in the parallel portion of the query performs an aggregation step, producing a partial result for each group of which that process is aware. This is reflected in the plan as a Partial Aggregate node. Second, the partial results are transferred to the leader via Gather or Gather Merge . Finally, the leader re-aggregates the results across all workers in order to produce the final result. This is reflected in the plan as a Finalize Aggregate node. Because the Finalize Aggregate node runs on the leader process, queries that produce a relatively large number of groups in comparison to the number of input rows will appear less favorable to the query planner. For example, in the worst-case scenario the number of groups seen by the Finalize Aggregate node could be as many as the number of input rows that were seen by all worker processes in the Partial Aggregate stage. For such cases, there is clearly going to be no performance benefit to using parallel aggregation. The query planner takes this into account during the planning process and is unlikely to choose parallel aggregate in this scenario. Parallel aggregation is not supported in all situations. Each aggregate must be safe for parallelism and must have

2. `chunk-3e7596d096f6d72115a5bc69777f909456547468ffede91368ab27c4cc28b03b` — pg-15; score=0.577905, dense=0.737895, sparse=18.238456, rerank=0.5779049396514893

> 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, and 15 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2016. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2016. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2016 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if some other subfeatures are supported.

3. `chunk-0a2bc8bc20369b3ac4b40204c954bb758e0c94bb79066a8aec365a860ac60780` — pg-15; score=0.167372, dense=0.749565, sparse=20.814154, rerank=0.1673719435930252

> , json_object_agg , jsonb_object_agg , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully different result values depending on the order of the input values. This ordering is unspecified by default, but can be controlled by writing an ORDER BY clause within the aggregate call, as shown in Aggregate Expressions . Alternatively, supplying the input values from a sorted subquery will usually work. For example: Beware that this approach can fail if the outer query level contains additional processing, such as a join, because that might cause the subquery's output to be reordered before the aggregate is computed. The boolean aggregates bool_and and bool_or correspond to the standard SQL aggregates every and any or some . PostgreSQL supports every , but not any or some , because there is an ambiguity built into the standard syntax: Here ANY can be considered either as introducing a subquery, or as being an aggregate function, if the subquery returns one row with a Boolean value. Thus the standard name cannot be given to these aggregates. Users accustomed to working with other SQL database management systems might be disappointed by the performance of the count aggregate when it is applied to the entire table. A query like: will require effort proportional to the size of the table: PostgreSQL will

## draft-0bd01d40748321be

Which role grants access to the slots reserved by reserved_connections in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) reserved_connections ( integer ) Determines the number of connection slots that are reserved for connections by roles with privileges of the pg_use_reserved_connections role.

### Top three retrieved
1. `chunk-49edd73b121ff2b2d390c9ed189ff0307b6ea96c49c2d2b92d4f1e5eef8f4494` — pg-16; score=2.891462, dense=0.763951, sparse=42.888641, rerank=2.8914623260498047

> connection slots are available, new connections will be accepted only for superusers. The default value is zero connections. The value must be less than max_connections minus superuser_reserved_connections . This parameter can only be set at server start. superuser_reserved_connections ( integer ) Determines the number of connection slots that are reserved for connections by PostgreSQL superusers. At most max_connections connections can ever be active simultaneously. Whenever the number of active concurrent connections is at least max_connections minus superuser_reserved_connections , new connections will be accepted only for superusers. The connection slots reserved by this parameter are intended as final reserve for emergency use after the slots reserved by reserved_connections have been exhausted. The default value is three connections. The value must be less than max_connections minus reserved_connections . This parameter can only be set at server start. unix_socket_directories ( string ) Specifies the directory of the Unix-domain socket(s) on which the server is to listen for connections from client applications. Multiple sockets can be created by listing multiple directories separated by commas. Whitespace between entries is ignored; surround a directory name with double quotes if you need to include whitespace or commas in the name. An empty value specifies not listening on any Unix-domain sockets, in which case only TCP/IP sockets can be used to connect to the server. A value that

2. `chunk-2d785059557ba8e60cde58c2d81822dd99c4227288d7f455214cacb480f93b05` — pg-16; score=1.545969, dense=0.000000, sparse=21.352267, rerank=1.545968770980835

> it controls the inheritance status of memberships added with this command using the IN ROLE clause, and in later commands using the ROLE clause. It is also used as the default inheritance status when adding this role as a member using the GRANT command. If not specified, INHERIT is the default. In PostgreSQL versions before 16, inheritance was a role-level attribute that controlled all runtime membership checks for that role. LOGIN NOLOGIN These clauses determine whether a role is allowed to log in; that is, whether the role can be given as the initial session authorization name during client connection. A role having the LOGIN attribute can be thought of as a user. Roles without this attribute are useful for managing database privileges, but are not users in the usual sense of the word. If not specified, NOLOGIN is the default, except when CREATE ROLE is invoked through its alternative spelling CREATE USER . REPLICATION NOREPLICATION These clauses determine whether a role is a replication role. A role must have this attribute (or be a superuser) in order to be able to connect to the server in replication mode (physical or logical replication) and in order to be able to create or drop replication slots. A role having the REPLICATION attribute is a very highly privileged role, and should only

3. `chunk-a7aa45f40fd71eb1e9f356317180d4c0efd6b0b8df4f5155736ab8c09e2c9acd` — pg-16; score=1.314646, dense=0.782987, sparse=21.549127, rerank=1.3146462440490723

> Predefined Roles PostgreSQL provides a set of predefined roles that provide access to certain, commonly needed, privileged capabilities and information. Administrators (including roles that have the CREATEROLE privilege) can GRANT these roles to users and/or other roles in their environment, providing those users with access to the specified capabilities and information. The predefined roles are described in Predefined Roles . Note that the specific permissions for each of the roles may change in the future as additional capabilities are added. Administrators should monitor the release notes for changes. The pg_monitor , pg_read_all_settings , pg_read_all_stats and pg_stat_scan_tables roles are intended to allow administrators to easily configure a role for the purpose of monitoring the database server. They grant a set of common privileges allowing the role to read various useful configuration settings, statistics and other system information normally restricted to superusers. The pg_database_owner role has one implicit, situation-dependent member, namely the owner of the current database. Like any role, it can own objects or receive grants of access privileges. Consequently, once pg_database_owner has rights within a template database, each owner of a database instantiated from that template will exercise those rights. pg_database_owner cannot be a member of any role, and it cannot have non-implicit members. Initially, this role owns the public schema, so each database owner governs local use of the

## draft-3797673671fc1771

Relative to which directory is the server's TLS certificate path resolved?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_cert_file ( string ) Specifies the name of the file containing the SSL server certificate. Relative paths are relative to the data directory.

### Top three retrieved
1. `chunk-055dae61efb2bffb709921891a2e0e4079098a6c1a0f08af7cd3be92edefeb08` — pg-16; score=3.697173, dense=0.736124, sparse=31.692721, rerank=3.6971726417541504

> Specifies the name of the file containing the SSL client certificate revocation list (CRL). Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file or on the server command line. The default is empty, meaning no CRL file is loaded (unless ssl_crl_dir is set). ssl_crl_dir ( string ) Specifies the name of the directory containing the SSL client certificate revocation list (CRL). Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file or on the server command line. The default is empty, meaning no CRLs are used (unless ssl_crl_file is set). The directory needs to be prepared with the OpenSSL command openssl rehash or c_rehash . See its documentation for details. When using this setting, CRLs in the specified directory are loaded on-demand at connection time. New CRLs can be added to the directory and will be used immediately. This is unlike ssl_crl_file , which causes the CRL in the file to be loaded at server start time or when the configuration is reloaded. Both settings can be used together. ssl_key_file ( string ) Specifies the name of the file containing the SSL server private key. Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file

2. `chunk-88fecc8c420190423a987987e08f610499cd0f66242ecac490ef5c8f1aae7984` — pg-15; score=3.697173, dense=0.736124, sparse=31.692721, rerank=3.6971726417541504

> Specifies the name of the file containing the SSL client certificate revocation list (CRL). Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file or on the server command line. The default is empty, meaning no CRL file is loaded (unless ssl_crl_dir is set). ssl_crl_dir ( string ) Specifies the name of the directory containing the SSL client certificate revocation list (CRL). Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file or on the server command line. The default is empty, meaning no CRLs are used (unless ssl_crl_file is set). The directory needs to be prepared with the OpenSSL command openssl rehash or c_rehash . See its documentation for details. When using this setting, CRLs in the specified directory are loaded on-demand at connection time. New CRLs can be added to the directory and will be used immediately. This is unlike ssl_crl_file , which causes the CRL in the file to be loaded at server start time or when the configuration is reloaded. Both settings can be used together. ssl_key_file ( string ) Specifies the name of the file containing the SSL server private key. Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file

3. `chunk-f167c69074cef593b955fb716bfa392e0348ac33f70f91bd3e0f0323f79dd61e` — pg-17; score=3.697173, dense=0.736124, sparse=31.692721, rerank=3.6971726417541504

> Specifies the name of the file containing the SSL client certificate revocation list (CRL). Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file or on the server command line. The default is empty, meaning no CRL file is loaded (unless ssl_crl_dir is set). ssl_crl_dir ( string ) Specifies the name of the directory containing the SSL client certificate revocation list (CRL). Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file or on the server command line. The default is empty, meaning no CRLs are used (unless ssl_crl_file is set). The directory needs to be prepared with the OpenSSL command openssl rehash or c_rehash . See its documentation for details. When using this setting, CRLs in the specified directory are loaded on-demand at connection time. New CRLs can be added to the directory and will be used immediately. This is unlike ssl_crl_file , which causes the CRL in the file to be loaded at server start time or when the configuration is reloaded. Both settings can be used together. ssl_key_file ( string ) Specifies the name of the file containing the SSL server private key. Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file

## draft-51a8ac7c7fbf24a6

What does amtype = i mean in pg_am?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-15; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-15) amtype char t = table (including materialized views), i = index.

### Top three retrieved
1. `chunk-28519f7eb362bcdbaa90205b0118b69183eb7361f4eacfdd2f2e733686e4fc46` — pg-17; score=3.652203, dense=0.715740, sparse=24.602397, rerank=3.65220308303833

> SELECT am.amname AS index_method, opc.opcname AS opclass_name, opc.opcintype::regtype AS indexed_type, opc.opcdefault AS is_default FROM pg_am am, pg_opclass opc WHERE opc.opcmethod = am.oid ORDER BY index_method, opclass_name;

2. `chunk-e146379eff239c4647bc09f7f2fb4d6f5a5451bf4e032a39a53f2658a3578540` — pg-15; score=3.652203, dense=0.715740, sparse=24.602397, rerank=3.65220308303833

> SELECT am.amname AS index_method, opc.opcname AS opclass_name, opc.opcintype::regtype AS indexed_type, opc.opcdefault AS is_default FROM pg_am am, pg_opclass opc WHERE opc.opcmethod = am.oid ORDER BY index_method, opclass_name;

3. `chunk-ed041b3ff31c812ceac3ac1ded17578f3d15d1dd83ce51b6224f1e0ac0e18f99` — pg-16; score=3.652203, dense=0.715740, sparse=24.602397, rerank=3.65220308303833

> SELECT am.amname AS index_method, opc.opcname AS opclass_name, opc.opcintype::regtype AS indexed_type, opc.opcdefault AS is_default FROM pg_am am, pg_opclass opc WHERE opc.opcmethod = am.oid ORDER BY index_method, opclass_name;

## draft-529a81ca28099b25

Is Partial Mode supported by string_agg in PostgreSQL 16?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-16; gold versions: []

### Expected evidence
- (pg-16) string_agg ( value text, delimiter text ) text string_agg ( value bytea, delimiter bytea ) bytea Concatenates the non-null input values into a string. Each value after the first is preceded by the corresponding delimiter (if it's not null). | Yes

### Top three retrieved
1. `chunk-3c04aa7200f400eb6279cd8895b029f79cd9a079f0fb64c6744724a19e61b237` — pg-16; score=1.526296, dense=0.000000, sparse=17.841336, rerank=1.5262961387634277

> Parallel Aggregation PostgreSQL supports parallel aggregation by aggregating in two stages. First, each process participating in the parallel portion of the query performs an aggregation step, producing a partial result for each group of which that process is aware. This is reflected in the plan as a Partial Aggregate node. Second, the partial results are transferred to the leader via Gather or Gather Merge . Finally, the leader re-aggregates the results across all workers in order to produce the final result. This is reflected in the plan as a Finalize Aggregate node. Because the Finalize Aggregate node runs on the leader process, queries that produce a relatively large number of groups in comparison to the number of input rows will appear less favorable to the query planner. For example, in the worst-case scenario the number of groups seen by the Finalize Aggregate node could be as many as the number of input rows that were seen by all worker processes in the Partial Aggregate stage. For such cases, there is clearly going to be no performance benefit to using parallel aggregation. The query planner takes this into account during the planning process and is unlikely to choose parallel aggregate in this scenario. Parallel aggregation is not supported in all situations. Each aggregate must be safe for parallelism and must have

2. `chunk-19ce536d81f9f2e4a0840b38cc4575ce1259723c2933c6d0b72fc83b8b82c146` — pg-16; score=0.232016, dense=0.731581, sparse=17.636402, rerank=0.23201590776443481

> 1, 2, 9, 11, and 14. Part 3 is covered by the ODBC driver, and part 13 is covered by the PL/Java plug-in, but exact conformance is currently not being verified for these components. There are currently no implementations of parts 4, 10, 15, and 16 for PostgreSQL . PostgreSQL supports most of the major features of SQL:2023. Out of 177 mandatory features required for full Core conformance, PostgreSQL conforms to at least 170. In addition, there is a long list of supported optional features. It might be worth noting that at the time of writing, no current version of any database management system claims full conformance to Core SQL:2023. In the following two sections, we provide a list of those features that PostgreSQL supports, followed by a list of the features defined in SQL:2023 which are not yet supported in PostgreSQL . Both of these lists are approximate: There might be minor details that are nonconforming for a feature that is listed as supported, and large parts of an unsupported feature might in fact be implemented. The main body of the documentation always contains the most accurate information about what does and does not work. Feature codes containing a hyphen are subfeatures. Therefore, if a particular subfeature is not supported, the main feature is listed as unsupported even if

3. `chunk-8b016650fef8bd099dbcd9cfd1de8beb5d2bbf2fad2c975133bc5c32d6b548c8` — pg-16; score=0.101258, dense=0.000000, sparse=27.604061, rerank=0.10125759989023209

> Aggregate Functions Aggregate functions compute a single result from a set of input values. The built-in general-purpose aggregate functions are listed in General-Purpose Aggregate Functions while statistical aggregates are in Aggregate Functions for Statistics . The built-in within-group ordered-set aggregate functions are listed in Ordered-Set Aggregate Functions while the built-in within-group hypothetical-set ones are in Hypothetical-Set Aggregate Functions . Grouping operations, which are closely related to aggregate functions, are listed in Grouping Operations . The special syntax considerations for aggregate functions are explained in Aggregate Expressions . Consult Aggregate Functions for additional introductory information. Aggregate functions that support Partial Mode are eligible to participate in various optimizations, such as parallel aggregation. It should be noted that except for count , these functions return a null value when no rows are selected. In particular, sum of no rows returns null, not zero as one might expect, and array_agg returns null rather than an empty array when there are no input rows. The coalesce function can be used to substitute zero or an empty array for null when necessary. The aggregate functions array_agg , json_agg , jsonb_agg , json_agg_strict , jsonb_agg_strict , json_object_agg , jsonb_object_agg , json_object_agg_strict , jsonb_object_agg_strict , json_object_agg_unique , jsonb_object_agg_unique , json_object_agg_unique_strict , jsonb_object_agg_unique_strict , string_agg , and xmlagg , as well as similar user-defined aggregate functions, produce meaningfully

## draft-7f9ef8ca7db593fa

What is the customary filename selected by hba_file?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) hba_file ( string ) Specifies the configuration file for host-based authentication (customarily called pg_hba.conf ).

### Top three retrieved
1. `chunk-67911986d3b2b9cc75a7cb444cd329061fd2defb1e88be726ccdaf3ef765a079` — pg-16; score=0.019379, dense=0.745920, sparse=22.751975, rerank=0.019378721714019775

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the next line by ending the line with a backslash. (Backslashes are not special except at the end of a line.) A record is made up of a number of fields which are separated by spaces and/or tabs. Fields can contain white space if the field value is double-quoted. Quoting one of the keywords in a database, user, or address field (e.g., all or replication ) makes the word lose its special meaning, and just match a database, user, or host with that name. Backslash line continuation applies even within quoted text or comments. Each authentication record specifies a connection type, a client IP address range (if relevant for the connection type), a database name, a user name, and the authentication method to be

2. `chunk-b8f76b4a73b8336b8d1f1b8849c85e4a8ab4c21a64f334f6319930eae60ad559` — pg-15; score=-0.079415, dense=0.753416, sparse=22.751975, rerank=-0.07941485941410065

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the next line by ending the line with a backslash. (Backslashes are not special except at the end of a line.) A record is made up of a number of fields which are separated by spaces and/or tabs. Fields can contain white space if the field value is double-quoted. Quoting one of the keywords in a database, user, or address field (e.g., all or replication ) makes the word lose its special meaning, and just match a database, user, or host with that name. Backslash line continuation applies even within quoted text or comments. Each record specifies a connection type, a client IP address range (if relevant for the connection type), a database name, a user name, and the authentication method to be used

3. `chunk-3d24696d8bf22df17c9d499baa02c736f092adc5f797dfb01435aef4d45d73c5` — pg-17; score=-0.774002, dense=0.733305, sparse=23.997900, rerank=-0.7740020751953125

> Example pg_hba.conf Entries Client authentication is controlled by a configuration file, which traditionally is named pg_hba.conf and is stored in the database cluster's data directory. ( HBA stands for host-based authentication.) A default pg_hba.conf file is installed when the data directory is initialized by initdb . It is possible to place the authentication configuration file elsewhere, however; see the hba_file configuration parameter. The pg_hba.conf file is read on start-up and when the main server process receives a SIGHUP signal. If you edit the file on an active system, you will need to signal the postmaster (using pg_ctl reload , calling the SQL function pg_reload_conf() , or using kill -HUP ) to make it re-read the file. The preceding statement is not true on Microsoft Windows: there, any changes in the pg_hba.conf file are immediately applied by subsequent new connections. The system view pg_hba_file_rules can be helpful for pre-testing changes to the pg_hba.conf file, or for diagnosing problems if loading of the file did not have the desired effects. Rows in the view with non-null error fields indicate problems in the corresponding lines of the file. The general format of the pg_hba.conf file is a set of records, one per line. Blank lines are ignored, as is any text after the # comment character. A record can be continued onto the

## draft-e0141266fb4b67fd

What filename does ssl_cert_file use by default?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_cert_file ( string ) Specifies the name of the file containing the SSL server certificate. Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file or on the server command line. The default is server.crt .

### Top three retrieved
1. `chunk-36832490f110b5b252a0f5ced829914bba4e957b218b768c688b9074419d5a02` — pg-15; score=5.011071, dense=0.780624, sparse=19.608633, rerank=5.01107120513916

> together. ssl_key_file ( string ) Specifies the name of the file containing the SSL server private key. Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file or on the server command line. The default is server.key . ssl_ciphers ( string ) Specifies a list of SSL cipher suites that are allowed to be used by SSL connections. See the ciphers manual page in the OpenSSL package for the syntax of this setting and a list of supported values. Only connections using TLS version 1.2 and lower are affected. There is currently no setting that controls the cipher choices used by TLS version 1.3 connections. The default value is HIGH:MEDIUM:+3DES:!aNULL . The default is usually a reasonable choice unless you have specific security requirements. This parameter can only be set in the postgresql.conf file or on the server command line. Explanation of the default value: HIGH Cipher suites that use ciphers from HIGH group (e.g., AES, Camellia, 3DES) MEDIUM Cipher suites that use ciphers from MEDIUM group (e.g., RC4, SEED) +3DES The OpenSSL default order for HIGH is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers.

2. `chunk-c988e3bf9ad619104bb6a41782ff0150c2bec73f5c6a0389df8b5b96aa8d6531` — pg-17; score=5.011071, dense=0.780624, sparse=19.608633, rerank=5.01107120513916

> together. ssl_key_file ( string ) Specifies the name of the file containing the SSL server private key. Relative paths are relative to the data directory. This parameter can only be set in the postgresql.conf file or on the server command line. The default is server.key . ssl_ciphers ( string ) Specifies a list of SSL cipher suites that are allowed to be used by SSL connections. See the ciphers manual page in the OpenSSL package for the syntax of this setting and a list of supported values. Only connections using TLS version 1.2 and lower are affected. There is currently no setting that controls the cipher choices used by TLS version 1.3 connections. The default value is HIGH:MEDIUM:+3DES:!aNULL . The default is usually a reasonable choice unless you have specific security requirements. This parameter can only be set in the postgresql.conf file or on the server command line. Explanation of the default value: HIGH Cipher suites that use ciphers from HIGH group (e.g., AES, Camellia, 3DES) MEDIUM Cipher suites that use ciphers from MEDIUM group (e.g., RC4, SEED) +3DES The OpenSSL default order for HIGH is problematic because it orders 3DES higher than AES128. This is wrong because 3DES offers less security than AES128, and it is also much slower. +3DES reorders it after all other HIGH and MEDIUM ciphers.

3. `chunk-dc214c6df93bff6b271d6c0d2c2a5429f34134ee19a14ecbf8725e3493d39e80` — pg-16; score=4.712675, dense=0.772768, sparse=30.204077, rerank=4.712674617767334

> will be loaded. The exact locations of these root certificates differ by SSL implementation and platform. For OpenSSL in particular, the locations may be further modified by the SSL_CERT_DIR and SSL_CERT_FILE environment variables. When using sslrootcert=system , the default sslmode is changed to verify-full , and any weaker setting will result in an error. In most cases it is trivial for anyone to obtain a certificate trusted by the system for a hostname they control, rendering verify-ca and all weaker modes useless. The magic system value will take precedence over a local certificate file with the same name. If for some reason you find yourself in this situation, use an alternative path like sslrootcert=./system instead. sslcrl This parameter specifies the file name of the SSL server certificate revocation list (CRL). Certificates listed in this file, if it exists, will be rejected while attempting to authenticate the server's certificate. If neither sslcrl nor sslcrldir is set, this setting is taken as ~/.postgresql/root.crl . sslcrldir This parameter specifies the directory name of the SSL server certificate revocation list (CRL). Certificates listed in the files in this directory, if it exists, will be rejected while attempting to authenticate the server's certificate. The directory needs to be prepared with the OpenSSL command openssl rehash or c_rehash . See its documentation for details. Both sslcrl

## draft-16dbda44b7eb794d

Which setting establishes the minimum accepted TLS protocol version?

**Category:** other. **Reason:** Evidence exists but ranking/scoping does not place it early enough.

Target: pg-17; gold versions: ['pg-15', 'pg-16', 'pg-17']

### Expected evidence
- (pg-17) ssl_min_protocol_version ( enum ) Sets the minimum SSL/TLS protocol version to use.

### Top three retrieved
1. `chunk-f5c6b8802364dee02ef39d05e66fa1ff7701c41932833e7e1a8bc8216f619284` — pg-17; score=4.331719, dense=0.850275, sparse=32.310872, rerank=4.331718921661377

> there. Use this parameter to ensure that you are connected to a server run by a trusted user.) This option is only supported on platforms for which the peer authentication method is implemented; see Peer Authentication . ssl_min_protocol_version This parameter specifies the minimum SSL/TLS protocol version to allow for the connection. Valid values are TLSv1 , TLSv1.1 , TLSv1.2 and TLSv1.3 . The supported protocols depend on the version of OpenSSL used, older versions not supporting the most modern protocol versions. If not specified, the default is TLSv1.2 , which satisfies industry best practices as of this writing. ssl_max_protocol_version This parameter specifies the maximum SSL/TLS protocol version to allow for the connection. Valid values are TLSv1 , TLSv1.1 , TLSv1.2 and TLSv1.3 . The supported protocols depend on the version of OpenSSL used, older versions not supporting the most modern protocol versions. If not set, this parameter is ignored and the connection will use the maximum bound defined by the backend, if set. Setting the maximum protocol version is mainly useful for testing or if some component has issues working with a newer protocol. krbsrvname Kerberos service name to use when authenticating with GSSAPI. This must match the service name specified in the server configuration for Kerberos authentication to succeed. (See also GSSAPI Authentication .) The default value is normally

2. `chunk-2cc5912576ce56b9ab9f39b91d92f993dd4a430c5251b20d52b8e952402cd640` — pg-16; score=3.819631, dense=0.769641, sparse=24.615196, rerank=3.8196310997009277

> on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version. The default is to allow any version. Setting the maximum protocol version is mainly useful for testing or if some component has issues working with a newer protocol. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_dh_params_file ( string ) Specifies the name of the file containing Diffie-Hellman parameters used for so-called ephemeral DH family of SSL ciphers. The default is empty, in which case compiled-in default DH parameters used. Using custom DH parameters reduces the exposure if an attacker manages to crack the well-known compiled-in DH parameters. You can create your own DH parameters file with the command openssl dhparam -out dhparams.pem 2048 . This parameter can only be set in the postgresql.conf file or on the server command line. ssl_passphrase_command ( string ) Sets an external command to be invoked when a passphrase for decrypting an SSL file such as a private key needs to be obtained. By default, this parameter is empty, which means the built-in prompting mechanism is used. The command must print the passphrase to the standard output and exit with code

3. `chunk-65f32e227546ad5f091a163dffee6ce77b2da8b695a2cf5d8e63599a1097728a` — pg-15; score=3.819631, dense=0.769641, sparse=24.615196, rerank=3.8196310997009277

> on the server command line. ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version. The default is to allow any version. Setting the maximum protocol version is mainly useful for testing or if some component has issues working with a newer protocol. This parameter can only be set in the postgresql.conf file or on the server command line. ssl_dh_params_file ( string ) Specifies the name of the file containing Diffie-Hellman parameters used for so-called ephemeral DH family of SSL ciphers. The default is empty, in which case compiled-in default DH parameters used. Using custom DH parameters reduces the exposure if an attacker manages to crack the well-known compiled-in DH parameters. You can create your own DH parameters file with the command openssl dhparam -out dhparams.pem 2048 . This parameter can only be set in the postgresql.conf file or on the server command line. ssl_passphrase_command ( string ) Sets an external command to be invoked when a passphrase for decrypting an SSL file such as a private key needs to be obtained. By default, this parameter is empty, which means the built-in prompting mechanism is used. The command must print the passphrase to the standard output and exit with code
