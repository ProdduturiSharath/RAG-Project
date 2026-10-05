# Evidence changes requiring re-review

These are the only 16 candidates with changed quote text. IDs, questions,
answers, and evidence lineage keys are unchanged. `reviewed.jsonl` was not
edited. Two existing accepted reviews need evidence reconfirmation:
`draft-257b83c46f868ef6` and `draft-2698580abdaeb4fb`; their factual answers
remain correct. All old/new quote pairs are printed in full below.

The review tool skips an ID already present in its chosen output file; it
does not replace or re-prompt it. To reconfirm just those two, use a fresh
output file, preserving the original six decisions:

```bash
PYTHONPATH=src .venv/bin/python scripts/label_dataset.py review --ids draft-257b83c46f868ef6,draft-2698580abdaeb4fb --output data/eval/parser-reconfirmations.jsonl
```

Choose `a` after checking each repaired quote, or `e`/`r` as appropriate.
Acceptance appends a human row with the same candidate ID,
`review_status=accepted` and `validated=true` to that separate file. The
original reviewed file is untouched. If this new output already contains
those IDs, it will skip them too; choose another fresh filename to re-prompt.
The two `pg_subscription` reviews still have unchanged bool/char quotes and
answers; their corrected headings now identify `pg_subscription`, with the
table caption stored separately.

## draft-257b83c46f868ef6

pg-17 / `pg-section:runtime-config-resource-memory`

**Old quote**
```text
multixact_member_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_multixact/members (see ).
```

**New quote**
```text
multixact_member_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_multixact/members (see Contents of PGDATA ).
```

## draft-2698580abdaeb4fb

pg-17 / `pg-section:runtime-config-resource-memory`

**Old quote**
```text
multixact_offset_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_multixact/offsets (see ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 16 .
```

**New quote**
```text
multixact_offset_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_multixact/offsets (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 16 .
```

## draft-05e120c03871ce0e

pg-17 / `pg-section:runtime-config-resource-memory`

**Old quote**
```text
notify_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_notify (see ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 16 . This parameter can only be set at server start.
```

**New quote**
```text
notify_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_notify (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 16 . This parameter can only be set at server start.
```

## draft-59e8d98dc1e8267d

pg-17 / `pg-section:runtime-config-resource-memory`

**Old quote**
```text
serializable_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_serial (see ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 32 .
```

**New quote**
```text
serializable_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_serial (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 32 .
```

## draft-9087662e522341da

pg-17 / `pg-section:runtime-config-resource-memory`

**Old quote**
```text
subtransaction_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_subtrans (see ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 0 , which requests shared_buffers /512 up to 1024 blocks, but not fewer than 16 blocks.
```

**New quote**
```text
subtransaction_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_subtrans (see Contents of PGDATA ). If this value is specified without units, it is taken as blocks, that is BLCKSZ bytes, typically 8kB. The default value is 0 , which requests shared_buffers /512 up to 1024 blocks, but not fewer than 16 blocks.
```

## draft-aa8fc2079022d8f2

pg-17 / `pg-section:runtime-config-resource-memory`

**Old quote**
```text
transaction_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_xact (see ).
```

**New quote**
```text
transaction_buffers ( integer ) Specifies the amount of shared memory to use to cache the contents of pg_xact (see Contents of PGDATA ).
```

## draft-14d3ffdd0bfc1fc6

pg-17 / `pg-section:catalog-pg-event-trigger#table0`

**Old quote**
```text
evtenabled char Controls in which modes the event trigger fires. O = trigger fires in origin and local modes, D = trigger is disabled, R = trigger fires in replica mode, A = trigger fires always.
```

**New quote**
```text
evtenabled char Controls in which session_replication_role modes the event trigger fires. O = trigger fires in origin and local modes, D = trigger is disabled, R = trigger fires in replica mode, A = trigger fires always.
```

## draft-29bf0d3d09985e6f

pg-15 / `pg-section:config-setting-sql-command-interaction`

**Old quote**
```text
The SHOW command allows inspection of the current value of any parameter. The corresponding SQL function is current_setting(setting_name text) (see ).
```

**New quote**
```text
The SHOW command allows inspection of the current value of any parameter. The corresponding SQL function is current_setting(setting_name text) (see Configuration Settings Functions ).
```

## draft-434bc40422c18e75

pg-17 / `pg-section:runtime-config-query-constants`

**Old quote**
```text
jit_above_cost ( floating point ) Sets the query cost above which JIT compilation is activated, if enabled (see ). Performing JIT costs planning time but can accelerate query execution. Setting this to -1 disables JIT compilation.
```

**New quote**
```text
jit_above_cost ( floating point ) Sets the query cost above which JIT compilation is activated, if enabled (see Just-in-Time Compilation (JIT) ). Performing JIT costs planning time but can accelerate query execution. Setting this to -1 disables JIT compilation.
```

## draft-6a52c545b09efc02

pg-17 / `pg-section:runtime-config-connection-ssl`

**Old quote**
```text
ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for , with addition of an empty string, which allows any protocol version. The default is to allow any version.
```

**New quote**
```text
ssl_max_protocol_version ( enum ) Sets the maximum SSL/TLS protocol version to use. Valid values are as for ssl_min_protocol_version , with addition of an empty string, which allows any protocol version. The default is to allow any version.
```

## draft-c606806c6ba4b0ef

pg-16 / `pg-section:catalog-pg-authid#table0`

**Old quote**
```text
rolbypassrls bool Role bypasses every row-level security policy, see for more information.
```

**New quote**
```text
rolbypassrls bool Role bypasses every row-level security policy, see Row Security Policies for more information.
```

## draft-580cf5be88985635

pg-16 / `pg-section:jit-decision`

**Old quote**
```text
These cost-based decisions will be made at plan time, not execution time. This means that when prepared statements are in use, and a generic plan is used (see ), the values of the configuration parameters in effect at prepare time control the decisions, not the settings at execution time.
```

**New quote**
```text
These cost-based decisions will be made at plan time, not execution time. This means that when prepared statements are in use, and a generic plan is used (see PREPARE ), the values of the configuration parameters in effect at prepare time control the decisions, not the settings at execution time.
```

## draft-9c2802b2b594163e

pg-17 / `pg-section:jit-decision`

**Old quote**
```text
These cost-based decisions will be made at plan time, not execution time. This means that when prepared statements are in use, and a generic plan is used (see ), the values of the configuration parameters in effect at prepare time control the decisions, not the settings at execution time.
```

**New quote**
```text
These cost-based decisions will be made at plan time, not execution time. This means that when prepared statements are in use, and a generic plan is used (see PREPARE ), the values of the configuration parameters in effect at prepare time control the decisions, not the settings at execution time.
```

## draft-54999895baea7983

pg-16 / `pg-section:runtime-config-query-constants`

**Old quote**
```text
jit_above_cost ( floating point ) Sets the query cost above which JIT compilation is activated, if enabled (see ). Performing JIT costs planning time but can accelerate query execution.
```

**New quote**
```text
jit_above_cost ( floating point ) Sets the query cost above which JIT compilation is activated, if enabled (see Just-in-Time Compilation (JIT) ). Performing JIT costs planning time but can accelerate query execution.
```

## draft-54f1be3754a7cee9

pg-16 / `pg-section:functions-datetime#table1`

**Old quote**
```text
date_add ( timestamp with time zone, interval , text ) timestamp with time zone Add an interval to a timestamp with time zone, computing times of day and daylight-savings adjustments according to the time zone named by the third argument, or the current setting if that is omitted.
```

**New quote**
```text
date_add ( timestamp with time zone, interval , text ) timestamp with time zone Add an interval to a timestamp with time zone, computing times of day and daylight-savings adjustments according to the time zone named by the third argument, or the current TimeZone setting if that is omitted.
```

## draft-917b1268426c767d

pg-16 / `pg-section:functions-datetime#table1`

**Old quote**
```text
date_subtract ( timestamp with time zone, interval , text ) timestamp with time zone Subtract an interval from a timestamp with time zone, computing times of day and daylight-savings adjustments according to the time zone named by the third argument, or the current setting if that is omitted. The form with two arguments is equivalent to the timestamp with time zone - interval operator.
```

**New quote**
```text
date_subtract ( timestamp with time zone, interval , text ) timestamp with time zone Subtract an interval from a timestamp with time zone, computing times of day and daylight-savings adjustments according to the time zone named by the third argument, or the current TimeZone setting if that is omitted. The form with two arguments is equivalent to the timestamp with time zone - interval operator.
```
