import { ApolloClient, HttpLink, ApolloLink, NormalizedCacheObject } from "@apollo/client";

import { cache } from "./cache";
import { useAuthToken } from "./hooks";

const httpLink = new HttpLink({ uri: "http://localhost:8000/graphql" });

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
  return new ApolloClient({
    link: authMiddleware(authToken).concat(httpLink),
    cache,
  });
};

export { useAppApolloClient };
