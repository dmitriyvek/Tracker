import { InMemoryCache, Reference, makeVar } from "@apollo/client";

const cache = new InMemoryCache({
  addTypename: true,
  typePolicies: {
    ProjectsQuery: {
      fields: {
        list: {
          keyArgs: false,
          merge(existing = [], incoming) {
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

    ProjectEdge: {
      fields: {
        isLoading: {
          read(_) {
            return false;
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
  },
});

export { cache };
