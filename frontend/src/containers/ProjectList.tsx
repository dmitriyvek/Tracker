import { useQuery } from "@apollo/client";
import { Layout, Button, Spin, Col, Empty, Table, Avatar, Space } from "antd";
import { ColumnsType } from "antd/es/table";
import React, { useState } from "react";
import { Link } from "react-router-dom";

import { recordNumber } from "../App";
import { PROJECT_LIST_QUERY } from "../gqlQueries";

import type { ProjectNodeType } from "../types";

const { Content } = Layout;

const layout = {
  span: 16,
  offset: 4,
};

const ProjectList: React.FC = () => {
  const [initLoad, setInitLoad] = useState<boolean>(false);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);

  const { error, data, fetchMore } = useQuery(PROJECT_LIST_QUERY, {
    variables: { first: recordNumber },
    onCompleted: () => {
      setInitLoad(true);
    },
  });

  if (error) console.log("Error in project list", error);

  const onFetchMore = async () => {
    setIsLoadingMore(true);

    await fetchMore({
      variables: {
        first: recordNumber,
        after: data?.projects.list.pageInfo.endCursor,
      },
    });
    setIsLoadingMore(false);
  };

  const loadMore =
    initLoad && data && data.projects.list.pageInfo.hasNextPage ? (
      <div
        style={{
          textAlign: "center",
          // marginTop: 12,
          height: 32,
          lineHeight: "32px",
        }}
      >
        {isLoadingMore && <Spin delay={500} />}
        {data.projects.list.pageInfo.hasNextPage && !isLoadingMore && (
          <Button onClick={onFetchMore}>load more</Button>
        )}
      </div>
    ) : null;

  const emptyList = (
    <Empty
      image={Empty.PRESENTED_IMAGE_SIMPLE}
      imageStyle={{
        height: 60,
      }}
      description={<span>You are not involved in any project yet</span>}
    >
      <Button type="primary">
        <Link to="/projects/create">Create new project</Link>
      </Button>
    </Empty>
  );

  const columns: ColumnsType<ProjectNodeType> = [
    {
      title: "Title",
      // dataIndex: ["node", "title"],
      key: "title",
      render: (_, record: ProjectNodeType) => (
        <Link to={`/projects/${record.node.id}`}>
          <Space size="small" direction="horizontal">
            <Avatar src="https://avatars.githubusercontent.com/u/60567822?s=400&u=dd215e7416a4f20549a1decad084eb54b8a809e4&v=4" />
            {record.node.title}
          </Space>
        </Link>
      ),
    },
    {
      title: "My role",
      dataIndex: ["node", "myRole", "role"],
      key: "myRole",
      render: (role: string) => role.replaceAll("_", " "),
    },
    {
      title: "Lead",
      key: "lead",
      render: (_, record: ProjectNodeType) => (
        <Link to={`/users/${record.node.createdBy.id}`}>
          <Space size="small" direction="horizontal">
            <Avatar src="https://avatars.githubusercontent.com/u/60567822?s=400&u=dd215e7416a4f20549a1decad084eb54b8a809e4&v=4" />
            {record.node.createdBy.username}
          </Space>
        </Link>
      ),
    },
  ];

  return (
    <Content style={{ padding: "24px 24px 24px" }}>
      <Col {...layout}>
        <h1>Projects</h1>
        {/* <List
          className="demo-loadmore-list"
          loading={!initLoad}
          itemLayout="horizontal"
          loadMore={loadMore}
          locale={{ emptyText: emptyList }}
          dataSource={data && data.projects.list.edges}
          renderItem={(item: ProjectNodeType) => <ProjectListItem item={item} />}
        /> */}
        <Table<ProjectNodeType>
          loading={!initLoad}
          footer={() => loadMore}
          pagination={false}
          bordered={false}
          locale={{ emptyText: emptyList }}
          rowKey={(record) => record.node.id}
          dataSource={data && data.projects.list.edges}
          columns={columns}
          expandable={{
            expandedRowRender: (record) => (
              <span style={{ margin: 0 }}>{record.node.description}</span>
            ),
            rowExpandable: (record) => Boolean(record.node.description),
          }}
        />
        {/* {loadMore} */}
      </Col>
    </Content>
  );
};

export { ProjectList };
