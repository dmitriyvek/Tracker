import { Breadcrumb } from "antd";
import { Link } from "react-router-dom";

type ProjectsBreadCrumbPropsType = {
  currentProjectTitle: string;
};

const ProjectsBreadCrumb: React.FC<ProjectsBreadCrumbPropsType> = ({
  currentProjectTitle,
}: ProjectsBreadCrumbPropsType) => {
  return (
    <Breadcrumb style={{ margin: "16px 0" }}>
      <Breadcrumb.Item>
        <Link to="/projects">Projects</Link>
      </Breadcrumb.Item>
      <Breadcrumb.Item>{currentProjectTitle}</Breadcrumb.Item>
    </Breadcrumb>
  );
};

export { ProjectsBreadCrumb };
