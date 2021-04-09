import React, { useState } from "react";
import { useQuery } from "@apollo/client";
import { List, Avatar, Button, Spin } from "antd";

import { PROJECT_LIST_QUERY } from "../gqlQueries";
import type { ProjectNodeType, ProjectListResponseType } from "../types";
import { useLogout } from "../hooks";

const recordNumber = 2;

const ProjectList: React.FC = () => {
  const [initLoad, setInitLoad] = useState<boolean>(false);
  const [skipQuery, setSkipQuery] = useState<boolean>(false);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);

  const logout = useLogout();
  const onLogoutClick = () => {
    setSkipQuery(true);
    logout();
    setInitLoad(false);
  };

  const { loading, error, data, fetchMore } = useQuery(PROJECT_LIST_QUERY, {
    variables: { first: recordNumber },
    notifyOnNetworkStatusChange: true,
    skip: skipQuery,
    onCompleted: (response: ProjectListResponseType) => {
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
          marginTop: 12,
          height: 32,
          lineHeight: "32px",
        }}
      >
        {isLoadingMore && <Spin delay={500} />}
        {data.projects.list.pageInfo.hasNextPage && !isLoadingMore && (
          <Button onClick={onFetchMore}>loading more</Button>
        )}
      </div>
    ) : null;

  return (
    <>
      <Button danger onClick={onLogoutClick}>
        Log out
      </Button>
      <List
        className="demo-loadmore-list"
        loading={!initLoad}
        itemLayout="horizontal"
        loadMore={loadMore}
        dataSource={data && data.projects.list.edges}
        renderItem={({ node }: ProjectNodeType) => (
          <List.Item
            actions={[
              <a key="list-loadmore-edit">edit</a>,
              <a key="list-loadmore-more">more</a>,
            ]}
          >
            <List.Item.Meta
              avatar={
                <Avatar src="https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png" />
              }
              title={<a href="https://ant.design">{node.title}</a>}
              description={node.description}
            />
            {/* <div>content</div> */}
          </List.Item>
        )}
      />
    </>
  );
};

export { ProjectList };
