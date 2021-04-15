import { Layout } from "antd";
import { Route, Switch } from "react-router";

import { UserDetailPage } from "./UserDetailPage";
import { UserHomePage } from "./UserHomePage";

const UsersLayout = () => {
  return (
    <Layout style={{ textAlign: "center" }}>
      <Switch>
        <Route exact path="/users/home" component={UserHomePage} />
        <Route exact path="/users/:userId" component={UserDetailPage} />
      </Switch>
    </Layout>
  );
};

export { UsersLayout };
