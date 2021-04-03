import { useApolloClient } from "@apollo/client";
import { useCookies } from "react-cookie";

const TOKEN_NAME = "authToken";

type setAuthTokenFuncType = (authToken: string) => void;

const useAuthToken = () => {
  const [cookies, setCookie, removeCookie] = useCookies([TOKEN_NAME]);

  const setAuthToken: setAuthTokenFuncType = (authToken) => setCookie(TOKEN_NAME, authToken);

  const removeAuthToken = () => removeCookie(TOKEN_NAME);

  return [cookies[TOKEN_NAME], setAuthToken, removeAuthToken];
};

const useLogout = () => {
  const [, , removeAuthToken] = useAuthToken();
  const apolloClient = useApolloClient();

  const logout = async () => {
    await apolloClient.clearStore();
    removeAuthToken(); // removes cookie
  };
  return logout;
};

export { useAuthToken, useLogout };
