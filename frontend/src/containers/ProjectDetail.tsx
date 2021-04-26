import { useQuery } from "@apollo/client";
import { Layout, Spin } from "antd";
import { RouteComponentProps } from "react-router";
import { Link } from "react-router-dom";

import { recordNumber } from "../App";
import { PROJECT_DETAIL_QUERY } from "../gqlQueries";
import { ProjectsBreadCrumb } from "../components/ProjectsBreadCrumb";
import { ProjectsSideBar } from "../components/ProjectsSideBar";
import { ProjectRoleList } from "../components/ProjectRoleList";

import type { ProjectDetailResponseType } from "../types";

type TParam = {
  projectId: string;
};

type ProjectDetailPropsType = {} & RouteComponentProps<TParam>;

const { Content } = Layout;

const ProjectDetail: React.FC<ProjectDetailPropsType> = ({
  match,
}: ProjectDetailPropsType) => {
  const projectId: string = match.params.projectId;

  const { error, data, fetchMore } = useQuery<ProjectDetailResponseType>(
    PROJECT_DETAIL_QUERY,
    {
      variables: { projectId, roleNumber: recordNumber },
    },
  );

  if (error) {
    console.log("Error in project detail: ", error);
    return <span>Something went wrong. Sorry...</span>;
  }

  return (
    <>
      {/* <ProjectsSideBar /> */}
      {(data && (
        <Layout style={{ padding: "0 24px 24px" }}>
          <ProjectsBreadCrumb currentProjectTitle={data.node.title} />

          <Content
            className="site-layout-background"
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
            }}
          >
            <h1>{data.node.title}</h1>
            <span>{data.node.description}</span>
            <span>{data.node.createdAt}</span>
            <span>My role: {data.node.myRole.role}</span>
            <span>
              Lead:{" "}
              <Link to={`/users/${data.node.createdBy.id}`}>
                {data.node.createdBy.username}
              </Link>
            </span>
            <ProjectRoleList fetchMore={fetchMore} data={data} />
          </Content>
        </Layout>
      )) || <Spin style={{ margin: "auto" }} />}
    </>
  );
};

export { ProjectDetail };
