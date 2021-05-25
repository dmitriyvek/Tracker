import { useQuery } from "@apollo/client";
import { Spin } from "antd";

import { USER_DETAIL_HOME_QUERY } from "../gqlQueries";
import { UserDetail } from "../components/UserDetail";

import type { UserDetailHomeResponseType } from "../types";

const UserHomePage: React.FC = () => {
  const { error, data, loading } = useQuery<UserDetailHomeResponseType>(
    USER_DETAIL_HOME_QUERY,
  );

  if (error) {
    console.log("Error in user home detail: ", error);
    return <span>Something went wrong. Sorry...</span>;
  }

  if (!loading && data)
    return (
      <UserDetail
        username={data.users.detail.record.username}
        email={data.users.detail.record.email}
        registeredAt={data.users.detail.record.registeredAt}
      />
    );
  else return <Spin style={{ margin: "auto" }} />;
};

export { UserHomePage };
