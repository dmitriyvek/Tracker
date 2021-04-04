import React, { useState, useEffect } from "react";
import { useQuery, gql } from "@apollo/client";
import { List, Avatar, Button, Skeleton } from "antd";

import type { ProjectNodeType } from "../types";
import { useLogout } from "../hooks";

const recordNumber = 2;

type ProjectWithLoadingType = {
  isLoading: boolean;
  node: ProjectNodeType;
};

const ProjectList: React.FC = () => {
  const [initLoad, setInitLoad] = useState<boolean>(false);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
  const [dataList, setDataList] = useState<ProjectWithLoadingType[]>([]);

  const logout = useLogout();

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
    if (!loading) {
      if (data) {
        setDataList(data.projects.list.edges);
        setInitLoad(true);
      } else {
        setDataList([]);
        setInitLoad(false);
      }
    }
  }, [loading, data]);

  // if (loading) return <p>"Loading..."</p>;
  if (error) console.log(error);

  const onFetchMore = async () => {
    setIsLoadingMore(true);
    setDataList((prevState) => [
      ...prevState,
      ...[...new Array(recordNumber)].map(() => ({ isLoading: true, node: {} })),
    ]);

    await fetchMore({
      variables: {
        first: recordNumber,
        after: data.projects.list.pageInfo.endCursor,
      },
    });
    setIsLoadingMore(false);
  };

  const loadMore =
    initLoad && !isLoadingMore && !loading && data.projects.list.pageInfo.hasNextPage ? (
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
    <>
      <Button danger onClick={logout}>
        Log out
      </Button>
      <List
        className="demo-loadmore-list"
        loading={!initLoad}
        itemLayout="horizontal"
        loadMore={loadMore}
        // dataSource={data ? data.projects.list.edges : []}
        dataSource={dataList}
        renderItem={(item: ProjectWithLoadingType) => (
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
    </>
  );
};

export { ProjectList };
