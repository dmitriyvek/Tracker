import { ApolloProvider } from "@apollo/client";
import React, { useEffect, useState } from "react";
import { BrowserRouter as Router } from "react-router-dom";
import jwt_decode from "jwt-decode";
import "antd/dist/antd.css";

import { useAppApolloClient } from "./apolloClient";
import { MainLayout } from "./containers/Layout";
import { useAuthToken } from "./hooks";
import { BaseRouter } from "./routes";

import type { AuthTokenPayloadType } from "./types";
import type { removeAuthTokenFunctionType } from "./hooks";

const App: React.FC = () => {
  const [logoutTimeoutId, setLogoutTimeoutId] = useState<number>(0);

  const apolloClient = useAppApolloClient();
  const [authToken, _, removeAuthToken] = useAuthToken();

  useEffect(() => {
    if (authToken) validateAuthToken(authToken, removeAuthToken);
  }, [authToken]);

  const validateAuthToken = (
    authToken: string,
    removeAuthToken: removeAuthTokenFunctionType,
  ) => {
    const decodedToken = jwt_decode<AuthTokenPayloadType>(authToken);
    const authTokenExpirationDate = new Date(decodedToken.exp * 1000);

    if (authTokenExpirationDate <= new Date()) {
      removeAuthToken();
    } else {
      if (logoutTimeoutId) clearTimeout(logoutTimeoutId);

      const expirationTime = authTokenExpirationDate.getTime() - new Date().getTime();
      setLogoutTimeoutId(
        window.setTimeout(async () => {
          console.log("Your time is out");
          await apolloClient.clearStore();
          removeAuthToken();
        }, expirationTime),
      );
    }
  };

  return (
    <ApolloProvider client={apolloClient}>
      <Router>
        <MainLayout>
          <BaseRouter isAuthenticated={Boolean(authToken)} />
        </MainLayout>
      </Router>
    </ApolloProvider>
  );
};

export default App;
