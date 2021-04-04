import { ApolloProvider } from "@apollo/client";
import React from "react";
import { BrowserRouter as Router } from "react-router-dom";
import "antd/dist/antd.css";

import { useAppApolloClient } from "./apolloClient";
import { MainLayout } from "./containers/Layout";
import { useAuthToken } from "./hooks";
import { BaseRouter } from "./routes";

const App: React.FC = () => {
  const apolloClient = useAppApolloClient();
  const [authToken] = useAuthToken();

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
