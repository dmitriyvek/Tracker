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

    ProjectType: {
      fields: {
        title: {
          read(title: string = "TITLE") {
            return title;
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
