import { Layout } from "antd";
import { Route, Switch } from "react-router";

import { ProjectDetail } from "./ProjectDetail";
import { ProjectList } from "./ProjectList";
import { ProjectCreationPage } from "./ProjectCreationPage";

const ProjectsLayout: React.FC = () => {
  return (
    <Layout>
      <Switch>
        <Route exact path="/projects/create" component={ProjectCreationPage} />
        <Route exact path="/projects/:projectId" component={ProjectDetail} />
        <Route exact path="/projects" component={ProjectList} />
      </Switch>
    </Layout>
  );
};

export { ProjectsLayout };
