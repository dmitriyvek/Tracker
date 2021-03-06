import { InMemoryCache } from "@apollo/client";

const cache = new InMemoryCache({
  addTypename: true,
  typePolicies: {
    Mutation: {
      fields: {
        auth: {
          keyArgs: false,
          merge(_, incoming) {
            return incoming;
          },
        },
      },
    },

    ProjectsQuery: {
      fields: {
        list: {
          keyArgs: false,
        },
        duplicationCheck: {
          merge(existing, incoming) {
            if (!existing) return incoming;
            return { ...existing, ...incoming };
          },
        },
      },
    },

    ProjectConnection: {
      fields: {
        edges: {
          merge(existing = [], incoming) {
            return [...existing, ...incoming];
          },
        },
      },
    },

    RoleConnection: {
      fields: {
        edges: {
          merge(existing = [], incoming: Array<any>) {
            return [...existing, ...incoming];
          },
        },
        pageInfo: {
          merge(_, incoming) {
            return incoming;
          },
        },
      },
    },

    RoleRootMutation: {
      fields: {
        roleCreation: {
          keyArgs: false,
          merge(_, incoming) {
            return incoming;
          },
        },
      },
    },

    ProjectType: {
      fields: {
        roleList: {
          keyArgs: false,
        },
        title: {
          merge(existing, incoming) {
            if (!existing) return incoming;
            return existing;
          },
        },
        description: {
          merge(existing, incoming) {
            if (!existing) return incoming;
            return existing;
          },
        },
        createdAt: {
          merge(existing, incoming) {
            if (!existing) return incoming;
            return existing;
          },
        },
      },
    },

    AuthQuery: {
      fields: {
        duplicationCheck: {
          merge(existing, incoming) {
            if (!existing) return incoming;
            return { ...existing, ...incoming };
          },
        },
      },
    },

    UserDuplicationChecksType: {
      fields: {
        email: {
          keyArgs: false,
          merge(_, incoming) {
            return incoming;
          },
        },
        username: {
          keyArgs: false,
          merge(_, incoming) {
            return incoming;
          },
        },
      },
    },

    ProjectDuplicationChecksType: {
      fields: {
        title: {
          keyArgs: false,
          merge(_, incoming) {
            return incoming;
          },
        },
      },
    },
  },
});

export { cache };
