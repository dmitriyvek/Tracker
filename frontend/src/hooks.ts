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
import jwt_decode from "jwt-decode";

import { LOGOUT_MUTATION } from "./gqlQueries";
import { MutatianStatusEnum } from "./types";

import type { LogoutMutationResponseType, AuthTokenPayloadType } from "./types";

const TOKEN_NAME = "authToken";

type setAuthTokenFuncType = (authToken: string) => void;
type removeAuthTokenFunctionType = () => void;

const useAuthToken = () => {
  const [cookies, setCookie, removeCookie] = useCookies([TOKEN_NAME]);

  const setAuthToken: setAuthTokenFuncType = (authToken) => {
    const decodedToken = jwt_decode<AuthTokenPayloadType>(authToken);
    const authTokenExpirationDate = new Date(decodedToken.exp * 1000);
    setCookie(TOKEN_NAME, authToken, { expires: authTokenExpirationDate });
  };

  const removeAuthToken: removeAuthTokenFunctionType = () => removeCookie(TOKEN_NAME);

  return [cookies[TOKEN_NAME], setAuthToken, removeAuthToken];
};

const useLogout = () => {
  const [, , removeAuthToken] = useAuthToken();
  const apolloClient = useApolloClient();

  const [mutation] = useMutation(LOGOUT_MUTATION, {
    onCompleted: async (response: LogoutMutationResponseType) => {
      if (response.auth.logout.logoutPayload.status === MutatianStatusEnum.success) {
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
export type { removeAuthTokenFunctionType };
