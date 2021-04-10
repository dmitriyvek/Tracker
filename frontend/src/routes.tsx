import React from "react";
import { Route } from "react-router-dom";

import { AuthPage } from "./containers/AuthPage";
import { MainLayout } from "./containers/MainLayout";
import { ProjectsLayout } from "./containers/ProjectsLayout";

type BaseRouterPropsType = {
  isAuthenticated: boolean;
};

const BaseRouter: React.FC<BaseRouterPropsType> = ({
  isAuthenticated,
}: BaseRouterPropsType) => {
  return (
    <>
      {isAuthenticated ? (
        <MainLayout>
          <Route path="/projects" component={ProjectsLayout} />
        </MainLayout>
      ) : (
        <Route path="/" component={AuthPage} />
      )}
    </>
  );
};

export { BaseRouter };
