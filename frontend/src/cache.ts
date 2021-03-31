import { InMemoryCache, Reference, makeVar } from "@apollo/client";

let first: any;
let after: any;

let pizdec: any = {};
const cache = new InMemoryCache({
  // addTypename: false,
  typePolicies: {
    Query: {
      keyFields: ["id"],
      fields: {
        projects: {
          keyArgs: false,
          merge(existing, incoming, pizdec) {
            console.log(pizdec);
            console.log(first, after);
            if (!existing) {
              console.log(incoming);
              return incoming;
            }
            if (existing && incoming) {
              let result = { ...existing, ...incoming };
              console.log(result, "aaaaaaaaaaa");
              return result;
            }

            console.log(existing, "toooooooop", incoming);
            let nodes: Reference[] = [];
            const a: Record<string, any> = {};
            let result;
            if (existing && existing.list) {
              result = existing.list;
            }
            if (incoming && incoming.list) {
              // nodes = nodes.concat(incoming.list.edges);
              if (!existing) {
                result = incoming['list({"first":2})'];
                console.log(result);
              } else {
                result.list.edges = result.list.edges.concat(incoming.list.edges);
              }
            } else {
              result = {
                ...incoming,
                nodes,
              };
            }
            console.log(result, "result");
            const { __typename, ...list } = result;
            console.log(list, "result2");
            return result;
          },
        },
      },
    },

    ProjectType: {
      fields: {
        title: {
          read(title: string = "UNKNOWN NAME") {
            return "AZAZA";
          },
          // merge(existing = [], incoming: any[]) {
          //   console.log(existing, "title adfklajdflkadjflkj", incoming);
          //   return [...existing, ...incoming];
          // },
        },
      },
    },
    // ProjectsQuery: {
    //   fields: {
    //     ProjectConnection: {
    //       merge(existing = [], incoming: any[]) {
    //         console.log(existing, "tatatatatatatatatatat", incoming);
    //         return [...existing, ...incoming];
    //       },
    //     },
    //   },
    // },
    // ProjectConnection: {
    //   fields: {
    //     edges: {
    //       keyArgs: false,
    //       merge(existing = [], incoming) {
    //         console.log(existing, "dodododododo", incoming);
    //         let result;
    //         if (existing) {
    //           console.log(1111);
    //         }
    //         if (!existing.length) {
    //           console.log("adssjdmnfgFSGHASGDF");
    //           return incoming;
    //         }
    //         if (incoming) {
    //           console.log(2222);
    //         }
    //         result = [...existing, ...incoming];
    //         console.log(result, "result");

    //         return result;
    //       },
    //     },
    //   },
    // },
  },
});

export { cache };
