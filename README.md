# Example text

## There is an issue with asyncpg lib

to solve it you must remove 2 lines from asyncpg/connection.py
in fetch function (line 588)

```
return await self._execute(
    query,
    args,
    0,
    timeout,
    record_class=record_class, # <-- delete this line
)
```

in fetchrow function (line 645)

```
return await self._execute(
    query,
    args,
    0,
    timeout,
    record_class=record_class, # <-- delete this line
)
```

save the file and restart a server
