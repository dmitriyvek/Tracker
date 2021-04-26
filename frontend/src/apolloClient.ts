import {
  ApolloClient,
  HttpLink,
  ApolloLink,
  NormalizedCacheObject,
} from "@apollo/client";
import { useMemo } from "react";

import { cache } from "./cache";
import { useAuthToken } from "./hooks";

const gqlHost = process.env.REACT_APP_GRAPHQL_HOST;
const gqlPort = process.env.REACT_APP_GRAPHQL_PORT;
if (!(gqlHost && gqlPort))
  throw new ReferenceError("Some of .env variables are not specified!");
const httpLink = new HttpLink({ uri: `http://${gqlHost}:${gqlPort}/graphql` });

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
