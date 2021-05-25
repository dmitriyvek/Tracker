import { Layout } from "antd";
import React from "react";
import { Route, Switch } from "react-router";

import { useLogout } from "../hooks";
import { MainHeader } from "../components/MainHeader";
import { UsersLayout } from "./UsersLayout";
import { ProjectsLayout } from "./ProjectsLayout";

const MainLayout: React.FC = () => {
  const logout = useLogout();

  return (
    <Layout>
      <MainHeader logout={logout} />
      <Switch>
        <Route path="/users" component={UsersLayout} />
        <Route path="/" component={ProjectsLayout} />
      </Switch>
    </Layout>
  );
};

export { MainLayout };
