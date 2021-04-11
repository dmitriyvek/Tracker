import { InMemoryCache } from "@apollo/client";

const cache = new InMemoryCache({
  addTypename: true,
  typePolicies: {
    Mutation: {
      fields: {
        auth: {
          keyArgs: false,
          merge(existing, incoming) {
            return incoming;
          },
        },
      },
    },

    ProjectsQuery: {
      fields: {
        list: {
          keyArgs: false,
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
          merge(existing = [], incoming) {
            console.log(existing, "2222", incoming);
            return [...existing, ...incoming];
          },
        },
      },
    },

    ProjectType: {
      fields: {
        roleList: {
          keyArgs: false,
          merge(existing, incoming) {
            console.log(existing, "1111", incoming);

            if (!existing) return incoming;
            return { ...existing, ...incoming };
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

    DuplicationChecksType: {
      fields: {
        email: {
          keyArgs: false,
          merge(existing, incoming) {
            return incoming;
          },
        },
        username: {
          keyArgs: false,
          merge(existing, incoming) {
            return incoming;
          },
        },
      },
    },
  },
});

export { cache };
