import trafaret as T


ENV_TRAFARET = T.Dict({
    T.Key('postgres'):
        T.Dict({
            'database': T.String(),
            'user': T.String(),
            'password': T.String(),
            'host': T.String(),
            'port': T.Int(),
        }),
    T.Key('host'): T.IP,
    T.Key('port'): T.Int(),
})
