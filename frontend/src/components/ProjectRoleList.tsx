import { List, Avatar, Spin, Button } from "antd";
import { CloseOutlined } from "@ant-design/icons";
import { useState } from "react";
import InfiniteScroll from "react-infinite-scroller";
import { Link } from "react-router-dom";

import { RoleEnum } from "../types";

import type { ProjectDetailResponseType } from "../types";
import type { OnRoleClickFunctionType } from "../containers/ProjectDetail";
import Modal from "antd/lib/modal/Modal";

type ProjectRoleListPropsType = {
  data: ProjectDetailResponseType;
  fetchMore: (params: any) => Promise<any>;
  onRoleDelete: OnRoleClickFunctionType;
};

const ProjectRoleList: React.FC<ProjectRoleListPropsType> = ({
  data,
  fetchMore,
  onRoleDelete,
}: ProjectRoleListPropsType) => {
  const userIsProjectManager = data.node.myRole.role === RoleEnum.project_manager;

  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);

  const [clickedRoleId, setClickedRoleId] = useState<string>("");
  const [roleDeleteModalVisible, setRoleDeleteModalVisible] = useState<boolean>(false);
  const [roleDeleteConfirmLoading, setRoleDeleteConfirmLoading] = useState<boolean>(
    false,
  );
  const [roleDeleteModalText, setRoleDeleteModalText] = useState<string>(
    "Are you shure you want to delete this user from a project?",
  );

  const handleRoleDelete = async (userId: string) => {
    setRoleDeleteModalText("Deleting...");
    setRoleDeleteConfirmLoading(true);

    await onRoleDelete(userId);

    setRoleDeleteModalVisible(false);
    setRoleDeleteConfirmLoading(false);
  };

  const handleRoleDeleteCancel = () => {
    setRoleDeleteModalVisible(false);
    setClickedRoleId("");
  };

  const onRoleDeleteClick = (roleId: string) => {
    setClickedRoleId(roleId);
    setRoleDeleteModalVisible(true);
  };

  const onFetchMore = async () => {
    setIsLoadingMore(true);
    await fetchMore({
      variables: {
        after: data.node.roleList.pageInfo.endCursor,
      },
    });
    setIsLoadingMore(false);
  };

  return (
    <div style={{ height: "100px", overflow: "auto" }}>
      <InfiniteScroll
        initialLoad={false}
        pageStart={0}
        loadMore={onFetchMore}
        hasMore={!isLoadingMore && data.node.roleList.pageInfo.hasNextPage}
        useWindow={false}
        threshold={50}
      >
        <List
          dataSource={data.node.roleList.edges}
          renderItem={(item) => (
            <List.Item key={item.node.user.id}>
              <List.Item.Meta
                avatar={
                  <Avatar src="https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png" />
                }
                title={
                  <Link to={`/users/${item.node.user.id}`}>
                    {item.node.user.username}
                  </Link>
                }
                description={item.node.role}
              />
              {userIsProjectManager &&
                // item.node.id !== data.node.myRole.id &&
                item.node.role !== RoleEnum.project_manager &&
                item.node.user.id !== data.node.createdBy.id && (
                  <Button
                    danger
                    type="default"
                    icon={<CloseOutlined />}
                    onClick={() => onRoleDeleteClick(item.node.id)}
                  />
                )}
            </List.Item>
          )}
        ></List>
        <Modal
          visible={roleDeleteModalVisible}
          onCancel={handleRoleDeleteCancel}
          onOk={() => handleRoleDelete(clickedRoleId)}
          maskClosable={true}
          okType="danger"
          okText="Delete"
          cancelText="Cancel"
          confirmLoading={roleDeleteConfirmLoading}
        >
          <span
            style={{
              textAlign: "center",
              fontSize: "18px",
              marginBottom: "0",
              marginTop: "10px",
            }}
          >
            {roleDeleteModalText}
          </span>
        </Modal>
      </InfiniteScroll>
      {isLoadingMore && <Spin />}
    </div>
  );
};

export { ProjectRoleList };
