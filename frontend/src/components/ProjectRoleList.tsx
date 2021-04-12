import { List, Avatar, Spin } from "antd";
import { useState } from "react";
import InfiniteScroll from "react-infinite-scroller";

import type { ProjectDetailResponseType } from "../types";

type ProjectRoleListPropsType = {
  data: ProjectDetailResponseType;
  fetchMore: (params: any) => Promise<any>;
};

const ProjectRoleList: React.FC<ProjectRoleListPropsType> = ({
  data,
  fetchMore,
}: ProjectRoleListPropsType) => {
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);

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
      >
        <List
          dataSource={data.node.roleList.edges}
          renderItem={(item) => (
            <List.Item key={`${item.node.userId}:${item.node.role}`}>
              <List.Item.Meta
                avatar={
                  <Avatar src="https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png" />
                }
                title={<a href="https://ant.design">{item.node.userId}</a>}
                description={item.node.role}
              />
            </List.Item>
          )}
        ></List>
      </InfiniteScroll>
      {isLoadingMore && <Spin />}
    </div>
  );
};

export { ProjectRoleList };
