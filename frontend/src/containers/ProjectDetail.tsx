import { ApolloError, FetchResult, useMutation, useQuery } from "@apollo/client";
import { message, Layout, Spin, Button } from "antd";
import produce from "immer";
import { useState } from "react";
import { RouteComponentProps } from "react-router";
import { Link } from "react-router-dom";

import { recordNumber } from "../App";
import {
  PROJECT_DETAIL_QUERY,
  ROLE_CREATION_MUTATION,
  ROLE_DELETION_MUTATION,
} from "../gqlQueries";
import { ProjectsBreadCrumb } from "../components/ProjectsBreadCrumb";
import { ProjectRoleList } from "../components/ProjectRoleList";
import { RolesCreationModal } from "../components/RolesCreationModal";

import { RoleEnum } from "../types";
import type {
  ProjectDetailResponseType,
  RoleDeletionResponseType,
  RoleCreationMutaionResponseType,
  RolesCreateionInputType,
} from "../types";

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

  const [isModalVisible, setIsModalVisible] = useState<boolean>(false);

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

  const [rolesCreationMutation] = useMutation(ROLE_CREATION_MUTATION, {
    onCompleted: (response: RoleCreationMutaionResponseType) => {
      response.role.roleCreation.roleCreationPayload.duplicatedEmailList.forEach(
        (duplicatedEmail: string) =>
          message.warning(
            `${duplicatedEmail}: a user with the given email address is already participating in this project .`,
            10,
          ),
      );

      if (!response.role.roleCreation.roleCreationPayload.errorList.length)
        message.success("Letters on given emails are sent successfully.");

      response.role.roleCreation.roleCreationPayload.errorList.forEach((msg: string) =>
        message.error(msg),
      );
    },
    onError: (error: ApolloError) => {
      console.log(error);
      message.error(
        "The was an error in roles creation. (see the console for detail information)",
      );
    },
  });

  const onRolesCreation = async (values: RolesCreateionInputType) => {
    return rolesCreationMutation({
      variables: {
        input: values,
      },
    });
  };

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
      // TODO: fix troubles with deleting the last role -> update pageInfo
      update(cache) {
        cache.modify({
          fields: {
            node: (projectNode) => {
              const newRoleList = projectNode.roleList.edges.filter(
                (role: any) => roleId !== role.node.__ref.split(":")[1],
              );

              return produce(projectNode, (updatedProjectNode: any) => {
                updatedProjectNode.roleList.edges = newRoleList;
              });
              // return {
              //   ...projectNode,
              //   roleList: {
              //     ...projectNode.roleList,
              //     edges: newRoleList,
              //   },
              // };
            },
          },
        });
      },

      // cache.writeQuery({overwrite: true}) from apollo 3.4 should prevent cahce merging
      // https://github.com/apollographql/apollo-client/issues/7491#issuecomment-772115227

      // update: (cache) => {
      //   // retruns null if no all fields data
      //   const projectNode = cache.readQuery<any>({
      //     query: PROJECT_DETAIL_ROLE_LIST_LOCAL_QUERY,
      //     variables: {
      //       projectId,
      //     },
      //   });
      //   if (!projectNode) return;

      //   cache.writeQuery({
      //     // overwrite: true,
      //     query: PROJECT_DETAIL_ROLE_LIST_LOCAL_QUERY,
      //     data: {
      //       node: {
      //         ...projectNode.node,
      //         roleList: {
      //           edges: projectNode.node.roleList.edges.filter(
      //             (roleRef: any) => roleId !== roleRef.node.id,
      //           ),
      //           __typename: "RoleConnection",
      //         },
      //       },
      //     },
      //     variables: {
      //       projectId,
      //     },
      //   });
      // },
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

      {data && data.node.myRole.role === RoleEnum.project_manager && (
        <>
          <RolesCreationModal
            projectId={projectId}
            onFormSubmit={onRolesCreation}
            isVisible={isModalVisible}
            setIsVisible={setIsModalVisible}
          />
          <Button onClick={() => setIsModalVisible(true)} type="primary">
            Add new participants
          </Button>
        </>
      )}
    </>
  );
};

export { ProjectDetail };
export type { OnRoleClickFunctionType };
