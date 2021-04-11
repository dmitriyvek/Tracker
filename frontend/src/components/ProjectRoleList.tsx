import { useLazyQuery } from "@apollo/client";
import { List, Avatar, Spin, Button } from "antd";
import InfiniteScroll from "react-infinite-scroller";

import { recordNumber } from "../App";
import { PROJECT_DETAIL_ROLE_LIST_FETCH_MORE } from "../gqlQueries";

import type {
  ProjectDetailResponseType,
  ProjectDetailRoleListFetchMoreResponseType,
} from "../types";

type ProjectRoleListPropsType = {
  projectId: string;
  data: ProjectDetailResponseType;
};

const ProjectRoleList: React.FC<ProjectRoleListPropsType> = ({
  data,
  projectId,
}: ProjectRoleListPropsType) => {
  const [
    fetchMore,
    { error, loading },
  ] = useLazyQuery<ProjectDetailRoleListFetchMoreResponseType>(
    PROJECT_DETAIL_ROLE_LIST_FETCH_MORE,
    {
      variables: {
        projectId,
        first: recordNumber,
      },
    },
  );

  const onFetchMore = () =>
    fetchMore({
      variables: {
        projectId: projectId,

        after: data.node.roleList.pageInfo.endCursor,
      },
    });

  if (error) console.log("Error in project detail role list", error);
  console.log(projectId);

  return (
    <div style={{ height: "100px", overflow: "auto" }}>
      <InfiniteScroll
        initialLoad={false}
        pageStart={0}
        loadMore={() =>
          fetchMore({
            variables: {
              first: recordNumber,
              after: data.node.roleList.pageInfo.endCursor,
            },
          })
        }
        hasMore={!loading && data.node.roleList.pageInfo.hasNextPage}
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
              <div>Content</div>
            </List.Item>
          )}
        >
          {loading && <Spin />}
        </List>
      </InfiniteScroll>
      <Button onClick={() => onFetchMore()}>Fetch more</Button>
    </div>
  );
};

export { ProjectRoleList };
