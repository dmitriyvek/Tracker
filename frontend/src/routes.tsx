import React from "react";
import { Route, Switch } from "react-router-dom";

import { AuthPage } from "./containers/AuthPage";
import { EmailConfirmationPage } from "./containers/EmailConfirmationPage";
import { MainLayout } from "./containers/MainLayout";

type BaseRouterPropsType = {
  isAuthenticated: boolean;
};

const BaseRouter: React.FC<BaseRouterPropsType> = ({
  isAuthenticated,
}: BaseRouterPropsType) => {
  return (
    <Switch>
      <Route exact path="/auth/confirmation/:token" component={EmailConfirmationPage} />
      {isAuthenticated ? <MainLayout /> : <Route path="/" component={AuthPage} />}
    </Switch>
  );
};

export { BaseRouter };
