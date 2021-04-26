import { Avatar } from "antd";
import { UserOutlined } from "@ant-design/icons";

type UserDetailPropsType = {
  username: string;
  email: string;
  registeredAt: string;
};

const UserDetail: React.FC<UserDetailPropsType> = ({
  username,
  email,
  registeredAt,
}: UserDetailPropsType) => {
  return (
    <>
      <h1>{username}`s profile</h1>
      <Avatar size={128} icon={<UserOutlined />} style={{ margin: "auto" }} />
      <p>{username}</p>
      <p>{email}</p>
      <p>{registeredAt}</p>
    </>
  );
};

export { UserDetail };
