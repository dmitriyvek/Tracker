import { List, Avatar } from "antd";

import type { ProjectNodeType } from "../types";

type ProjectListItemPropsType = {
  item: ProjectNodeType;
};

const ProjectListItem: React.FC<ProjectListItemPropsType> = ({
  item,
}: ProjectListItemPropsType) => {
  return (
    <List.Item
      actions={[
        <a key="list-loadmore-edit">edit</a>,
        <a key="list-loadmore-more">more</a>,
      ]}
    >
      <List.Item.Meta
        avatar={
          <Avatar src="https://avatars.githubusercontent.com/u/60567822?s=400&u=dd215e7416a4f20549a1decad084eb54b8a809e4&v=4" />
        }
        title={<a href="https://ant.design">{item.node.title}</a>}
        description={item.node.description}
      />
      {/* <div>content</div> */}
    </List.Item>
  );
};

export { ProjectListItem };
