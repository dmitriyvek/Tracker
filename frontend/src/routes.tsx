import React from "react";
import { Route } from "react-router-dom";

import { AuthPage } from "./containers/AuthPage";
import { MainLayout } from "./containers/MainLayout";
import { ProjectList } from "./containers/ProjectList";

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
          <Route exact path="/projects" component={ProjectList} />
        </MainLayout>
      ) : (
        <Route path="/" component={AuthPage} />
      )}
    </>
  );
};

export { BaseRouter };
