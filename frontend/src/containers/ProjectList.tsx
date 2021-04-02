import React, { useState, useEffect } from "react";
import { useQuery, gql } from "@apollo/client";
import { List, Avatar, Button, Skeleton } from "antd";

import type { ProjectListType, ProjectListResponseType } from "../types";

const recordNumber = 2;

type ProjectNodeType = Readonly<{
  id: string;
  title: string;
  description: string;
  createdAt: string;
}>;

type ProjectNodeWithLoadingType = {
  loading: boolean;
  node: ProjectNodeType;
};

type StateType = {
  initLoad: boolean;
  loading: boolean;
  list: ProjectNodeWithLoadingType[];
};

const ProjectList = () => {
  const [initLoad, setInitLoad] = useState<boolean>(false);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
  const [dataList, setDataList] = useState<ProjectNodeWithLoadingType[]>([]);

  const GET_PROJECT_LIST = gql`
    query GetProjectList($first: Int, $after: String) {
      projects {
        list(first: $first, after: $after) {
          edges {
            node {
              id
              title
              description
            }
            isLoading @client
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
  `;
  const { loading, error, data, fetchMore } = useQuery(GET_PROJECT_LIST, {
    variables: { first: recordNumber },
    notifyOnNetworkStatusChange: true,
  });

  useEffect(() => {
    if (!loading && data) setInitLoad(true);
  }, [loading, data]);

  // useEffect(() => {
  //   if (data) data.projects.list.edges.map((item) => ({ ...item, loading: false }));
  // }, [data]);

  console.log(data);

  // if (loading) return <p>"Loading..."</p>;
  if (error) console.log(error);

  const onFetchMore = async () => {
    setIsLoadingMore(true);
    await fetchMore({
      variables: {
        first: recordNumber,
        after: data.projects.list.pageInfo.endCursor,
      },
    });
    setIsLoadingMore(false);
  };

  const loadMore =
    initLoad && !loading && data.projects.list.pageInfo.hasNextPage ? (
      <div
        style={{
          textAlign: "center",
          marginTop: 12,
          height: 32,
          lineHeight: "32px",
        }}
      >
        <Button onClick={onFetchMore}>loading more</Button>
      </div>
    ) : null;

  return (
    <List
      className="demo-loadmore-list"
      loading={!initLoad}
      itemLayout="horizontal"
      loadMore={loadMore}
      dataSource={data ? data.projects.list.edges : []}
      renderItem={(item: any) => (
        <List.Item
          actions={[<a key="list-loadmore-edit">edit</a>, <a key="list-loadmore-more">more</a>]}
        >
          <Skeleton avatar title={false} loading={item.isLoading} active>
            <List.Item.Meta
              avatar={
                <Avatar src="https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png" />
              }
              title={<a href="https://ant.design">{item.node.title}</a>}
              description={item.node.description}
            />
            {/* <div>content</div> */}
          </Skeleton>
        </List.Item>
      )}
    />
  );
};

export { ProjectList };
