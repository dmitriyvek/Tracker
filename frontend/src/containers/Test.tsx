import { useQuery, gql, NetworkStatus } from "@apollo/client";
import React, { useState } from "react";

export const TestView: React.FC = () => {
  type NodeType = {
    node: {
      id: string;
      title: string;
      description: string;
    };
  };

  const [isLoadingMore, setIsLoadingMore] = useState(false);

  const recordNumber = 2;

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
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
  `;
  const {
    loading,
    error,
    data,
    refetch,
    // startPolling,
    // stopPolling,
    networkStatus,
    fetchMore,
  } = useQuery(GET_PROJECT_LIST, {
    variables: { first: recordNumber },
    notifyOnNetworkStatusChange: true,
    // pollInterval: 1000000, // ms
  });

  if (networkStatus === NetworkStatus.refetch) return <p>'Refetching!'</p>;
  if (loading) return <p>"Loading..."</p>;
  if (error) return <p>`Error! ${error}`</p>;

  console.log(data, "data data data");

  return (
    <>
      {data.projects &&
        // data.projects.list &&
        // data.projects.list.edges &&
        data.projects.list.edges.map(({ node }: NodeType) => (
          <div key={node.id}>
            <p>{node.id}</p>
            <p>{node.title}</p>
            <p>{node.description}</p>
          </div>
        ))}
      <button onClick={() => refetch()}>Refetch!</button>
      {data.projects &&
        data.projects.list.pageInfo.hasNextPage &&
        (isLoadingMore ? (
          <p>Getting moooooore......</p>
        ) : (
          <button
            onClick={async () => {
              setIsLoadingMore(true);
              await fetchMore({
                variables: {
                  first: recordNumber,
                  after: data.projects.list.pageInfo.endCursor,
                },
              });
              setIsLoadingMore(false);
            }}
          >
            Load More
          </button>
        ))}
    </>
  );
};
