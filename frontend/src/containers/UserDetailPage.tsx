import { useQuery } from "@apollo/client";
import { Spin } from "antd";
import { useParams } from "react-router";

import { USER_DETAIL_QUERY } from "../gqlQueries";
import { UserDetail } from "../components/UserDetail";

import type { UserDetailResponseType } from "../types";

const UserDetailPage: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();

  const { error, data, loading } = useQuery<UserDetailResponseType>(USER_DETAIL_QUERY, {
    variables: {
      userId,
    },
  });

  if (error) {
    console.log("Error in user detail: ", error);
    return <span>Something went wrong. Sorry...</span>;
  }

  if (!loading && data)
    return (
      <UserDetail
        username={data.node.username}
        email={data.node.email}
        registeredAt={data.node.registeredAt}
      />
    );
  else return <Spin style={{ margin: "auto" }} />;
};

export { UserDetailPage };
