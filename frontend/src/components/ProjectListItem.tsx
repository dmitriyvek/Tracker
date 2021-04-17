import { List, Avatar } from "antd";
import { Link } from "react-router-dom";

import type { ProjectNodeType } from "../types";

type ProjectListItemPropsType = {
  item: ProjectNodeType;
};

const ProjectListItem: React.FC<ProjectListItemPropsType> = ({
  item,
}: ProjectListItemPropsType) => {
  return (
    <List.Item
      style={{ borderBottom: "1px solid silver" }}
      actions={[
        <a key="list-loadmore-edit">edit</a>,
        <a key="list-loadmore-more">more</a>,
      ]}
    >
      <List.Item.Meta
        avatar={
          <Avatar src="https://avatars.githubusercontent.com/u/60567822?s=400&u=dd215e7416a4f20549a1decad084eb54b8a809e4&v=4" />
        }
        title={<Link to={`/projects/${item.node.id}`}>{item.node.title}</Link>}
        description={item.node.description}
      />
      My role: {item.node.myRole.role}
    </List.Item>
  );
};

export { ProjectListItem };
