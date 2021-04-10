import { Layout } from "antd";
import { Route } from "react-router";

import { ProjectsBreadCrumb } from "../components/ProjectsBreadCrumb";
import { ProjectsSideBar } from "../components/ProjectsSideBar";
import { ProjectList } from "./ProjectList";

const { Content } = Layout;

const ProjectsLayout: React.FC = () => {
  return (
    <Layout>
      <ProjectsSideBar />
      <Layout style={{ padding: "0 24px 24px" }}>
        <ProjectsBreadCrumb />

        <Content
          className="site-layout-background"
          style={{
            padding: 24,
            margin: 0,
            minHeight: 280,
          }}
        >
          <Route exact path="/projects" component={ProjectList} />
        </Content>
      </Layout>
    </Layout>
  );
};

export { ProjectsLayout };
