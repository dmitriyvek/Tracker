import {
  ApolloClient,
  HttpLink,
  ApolloLink,
  NormalizedCacheObject,
} from "@apollo/client";
import { useMemo } from "react";

import { cache } from "./cache";
import { useAuthToken } from "./hooks";

let gqlHost = process.env.REACT_APP_GRAPHQL_HOST;
let gqlPort = process.env.REACT_APP_GRAPHQL_PORT;
let gqlUrlSchema = process.env.REACT_APP_GRAPHQL_SCHEMA;
if (!(gqlHost && gqlPort && gqlUrlSchema))
  console.warn(
    "Some of required .env variables are not specified. Using default values.",
  );
gqlHost = gqlHost || "localhost";
gqlPort = gqlPort || "8000";
gqlUrlSchema = gqlUrlSchema || "http";
const httpLink = new HttpLink({
  uri: `${gqlUrlSchema}://${gqlHost}:${gqlPort}/graphql/`,
});

const authMiddleware = (authToken: string) =>
  new ApolloLink((operation, forward) => {
    if (authToken) {
      operation.setContext({
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
    }

    return forward(operation);
  });

type useAppApolloClientType = () => ApolloClient<NormalizedCacheObject>;

const useAppApolloClient: useAppApolloClientType = () => {
  const [authToken] = useAuthToken();
  // TODO: how to use memo here
  return useMemo(
    () =>
      new ApolloClient({
        link: authMiddleware(authToken).concat(httpLink),
        cache,
      }),
    [authToken],
  );
};

export { useAppApolloClient };
