import { ApolloError, FetchResult, useMutation, useQuery } from "@apollo/client";
import { message, Layout, Spin } from "antd";
import { RouteComponentProps } from "react-router";
import { Link } from "react-router-dom";

import { recordNumber } from "../App";
import { PROJECT_DETAIL_QUERY, ROLE_DELETION_MUTATION } from "../gqlQueries";
import { ProjectsBreadCrumb } from "../components/ProjectsBreadCrumb";
import { ProjectRoleList } from "../components/ProjectRoleList";

import type { ProjectDetailResponseType, RoleDeletionResponseType } from "../types";

type TParam = {
  projectId: string;
};

type ProjectDetailPropsType = RouteComponentProps<TParam>;
type OnRoleClickFunctionType = (
  roleId: string,
) => Promise<
  FetchResult<RoleDeletionResponseType, Record<string, any>, Record<string, any>>
>;

const { Content } = Layout;

const ProjectDetail: React.FC<ProjectDetailPropsType> = ({
  match,
}: ProjectDetailPropsType) => {
  const projectId: string = match.params.projectId;

  message.config({
    top: 60,
    duration: 2,
  });

  const {
    data,
    fetchMore,
    error: projectDetailError,
  } = useQuery<ProjectDetailResponseType>(PROJECT_DETAIL_QUERY, {
    variables: { projectId, roleNumber: recordNumber },
  });

  const [roleDeletionMutation] = useMutation(ROLE_DELETION_MUTATION, {
    onCompleted: () => {
      message.success("The user was successfully deleted from the project.");
    },
    onError: (error: ApolloError) => {
      console.log(error);
      message.error("The was an error in role deletion. (see the console)");
    },
  });

  const onRoleDelete = async (roleId: string) => {
    return roleDeletionMutation({
      variables: {
        input: {
          roleId: roleId,
        },
      },
    });
  };

  if (projectDetailError) {
    console.log("Error in project detail: ", projectDetailError);
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
            <p>{data.node.description}</p>
            <p>{data.node.createdAt}</p>
            <p>My role: {data.node.myRole.role}</p>
            <p>
              Lead:{" "}
              <Link to={`/users/${data.node.createdBy.id}`}>
                {data.node.createdBy.username}
              </Link>
            </p>
            <ProjectRoleList
              onRoleDelete={onRoleDelete}
              fetchMore={fetchMore}
              data={data}
            />
          </Content>
        </Layout>
      )) || <Spin style={{ margin: "auto" }} />}
    </>
  );
};

export { ProjectDetail };
export type { OnRoleClickFunctionType };
