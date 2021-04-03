import React from "react";
import { Route } from "react-router-dom";
import { LoginForm } from "./components/LoginForm";
import { ProjectList } from "./containers/ProjectList";

type BaseRouterPropsType = {
  isAuthenticated: boolean;
};

const BaseRouter: React.FC<BaseRouterPropsType> = ({ isAuthenticated }: BaseRouterPropsType) => {
  return (
    <>
      {isAuthenticated ? (
        <Route path="/" component={ProjectList} />
      ) : (
        <Route exact path="/" component={LoginForm} />
      )}
    </>
  );
};

export { BaseRouter };
