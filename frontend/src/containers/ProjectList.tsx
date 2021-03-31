import axios, { AxiosResponse } from "axios";
import React, { useState, useEffect } from "react";
import { useQuery, gql } from "@apollo/client";
import { List, Avatar, Button, Skeleton } from "antd";

import type { ProjectListType, ProjectListResponseType } from "../types";

const recordNumber = 3;

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

type getProjectListType = () => ProjectNodeWithLoadingType[];

const ProjectList = () => {
  const [initLoad, setInitLoad] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [list, setList] = useState<ProjectNodeWithLoadingType[]>([]);

  const getProjectList: getProjectListType = () => {
    const GET_PROJECT_LIST = gql`
      query GetProjectList_2($first: Int) {
        projects {
          list(first: $first) {
            edges {
              node {
                id
                title
                description
              }
            }
          }
        }
      }
    `;
    const { loading, error, data } = useQuery(GET_PROJECT_LIST, {
      variables: { first: recordNumber },
    });

    if (loading) {
      setLoading(true);
    }
    if (error) {
      console.log(error);
      return null;
    }

    setLoading(false);

    if (!data) {
      return null;
    }

    return data.projects.list.edges;

    // axios
    //   .post("localhost:8000/grapiql", {
    //     query: `
    //         {
    //             projects {
    //                 list(first: ${recordNumber}) {
    //                     edges {
    //                         node {
    //                             id
    //                             title
    //                             createdAt
    //                             description
    //                         }
    //                     }
    //                 }
    //             }
    //         }
    //     `,
    //   })
    //   .then((response: AxiosResponse) => {
    //     console.log(response.data.projects.list);
    //     return response.data.projects.list;
    //   })
    //   .catch((err) => {
    //     console.log(err);
    //   });
  };

  useEffect(() => {
    setList(getProjectList());
    setInitLoad(true);
  });

  const onLoadMore = () => {
    setLoading(true);
    setList(
      list.concat(
        [...new Array(recordNumber)].map(
          () =>
            ({
              loading: true,
              node: {
                id: "",
                title: "",
                description: "",
              },
            } as ProjectNodeWithLoadingType),
        ),
      ),
    );
    setList(getProjectList());
  };

  const loadMore =
    initLoad && !loading ? (
      <div
        style={{
          textAlign: "center",
          marginTop: 12,
          height: 32,
          lineHeight: "32px",
        }}
      >
        <Button onClick={onLoadMore}>loading more</Button>
      </div>
    ) : null;

  return (
    <List
      className="demo-loadmore-list"
      loading={!initLoad}
      itemLayout="horizontal"
      loadMore={loadMore}
      dataSource={list}
      renderItem={(item: ProjectNodeWithLoadingType) => (
        <List.Item
          actions={[<a key="list-loadmore-edit">edit</a>, <a key="list-loadmore-more">more</a>]}
        >
          <Skeleton avatar title={false} loading={item.loading} active>
            <List.Item.Meta
              avatar={
                <Avatar src="https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png" />
              }
              title={<a href="https://ant.design">{item.node.title}</a>}
              description={item.node.description}
            />
            <div>content</div>
          </Skeleton>
        </List.Item>
      )}
    />
  );
};

export { ProjectList };
