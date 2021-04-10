import React, { useState } from "react";
import { useQuery } from "@apollo/client";
import { List, Button, Spin } from "antd";

import { PROJECT_LIST_QUERY } from "../gqlQueries";
import type { ProjectNodeType, ProjectListResponseType } from "../types";
import { ProjectListItem } from "../components/ProjectListItem";

const recordNumber = 2;

const ProjectList: React.FC = () => {
  const [initLoad, setInitLoad] = useState<boolean>(false);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);

  const { error, data, fetchMore } = useQuery(PROJECT_LIST_QUERY, {
    variables: { first: recordNumber },
    notifyOnNetworkStatusChange: true,
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
    <List
      className="demo-loadmore-list"
      loading={!initLoad}
      itemLayout="horizontal"
      loadMore={loadMore}
      dataSource={data && data.projects.list.edges}
      renderItem={(item: ProjectNodeType) => <ProjectListItem item={item} />}
    />
  );
};

export { ProjectList };
