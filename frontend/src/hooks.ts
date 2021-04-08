import {
  DocumentNode,
  OperationVariables,
  QueryHookOptions,
  QueryResult,
  useApolloClient,
  useMutation,
  useQuery,
} from "@apollo/client";
import { useCookies } from "react-cookie";

import { LOGOUT_MUTATION } from "./gqlQueries";
import type { LogoutMutationResponseType } from "./types";
import { MutatianStatusEnum } from "./types";

const TOKEN_NAME = "authToken";

type setAuthTokenFuncType = (authToken: string) => void;

const useAuthToken = () => {
  const [cookies, setCookie, removeCookie] = useCookies([TOKEN_NAME]);

  const setAuthToken: setAuthTokenFuncType = (authToken) =>
    setCookie(TOKEN_NAME, authToken);

  const removeAuthToken = () => removeCookie(TOKEN_NAME);

  return [cookies[TOKEN_NAME], setAuthToken, removeAuthToken];
};

const useLogout = () => {
  const [, , removeAuthToken] = useAuthToken();
  const apolloClient = useApolloClient();

  const [mutation] = useMutation(LOGOUT_MUTATION, {
    onCompleted: async (response: LogoutMutationResponseType) => {
      if (
        response.auth.logout.logoutPayload.status ===
        MutatianStatusEnum.success
      ) {
        await apolloClient.clearStore();
        removeAuthToken(); // removes cookie
      } else console.log("Logout failed");
    },
  });

  const logout = () => {
    return mutation();
  };

  return logout;
};

/**
 * @example
 * const callQuery = useImperativeQuery(query, options)
 * const handleClick = async () => {
 *   const{ data, error } = await callQuery()
 * }
 */
function useImperativeQuery<TData = any, TVariables = OperationVariables>(
  query: DocumentNode,
  options: QueryHookOptions<TData, TVariables> = {},
): QueryResult<TData, TVariables>["refetch"] {
  const { refetch } = useQuery<TData, TVariables>(query, {
    ...options,
    skip: true,
  });

  const imperativelyCallQuery = (queryVariables: TVariables) => {
    return refetch(queryVariables);
  };

  return imperativelyCallQuery;
}

export { useAuthToken, useLogout, useImperativeQuery };
