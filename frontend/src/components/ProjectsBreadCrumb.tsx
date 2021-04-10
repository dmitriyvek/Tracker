import { Breadcrumb } from "antd";
import { Link } from "react-router-dom";

const ProjectsBreadCrumb = () => {
  return (
    <Breadcrumb style={{ margin: "16px 0" }}>
      <Breadcrumb.Item>
        <Link to="/projects">Projects</Link>
      </Breadcrumb.Item>
      <Breadcrumb.Item>Current</Breadcrumb.Item>
    </Breadcrumb>
  );
};

export { ProjectsBreadCrumb };
