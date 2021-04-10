import { Layout } from "antd";
import { Route } from "react-router";

import { ProjectDetail } from "./ProjectDetail";
import { ProjectList } from "./ProjectList";

const ProjectsLayout: React.FC = () => {
  return (
    <Layout>
      <Route exact path="/projects/:projectId" component={ProjectDetail} />
      <Route exact path="/projects" component={ProjectList} />
    </Layout>
  );
};

export { ProjectsLayout };
