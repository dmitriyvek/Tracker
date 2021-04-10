import { Menu, Layout, Button } from "antd";
import { Link } from "react-router-dom";

const { Header } = Layout;

type MainHeaderPropsType = {
  onLogoutBtnClick: () => void;
};

const MainHeader: React.FC<MainHeaderPropsType> = ({ onLogoutBtnClick }) => {
  return (
    <Header className="header">
      <Menu theme="dark" mode="horizontal" defaultSelectedKeys={["projects-link"]}>
        <Menu.Item key="projects-link">
          <Link to="/projects">Projects</Link>
        </Menu.Item>
        <Menu.Item key="logout-btn">
          <Button danger onClick={onLogoutBtnClick}>
            Log out
          </Button>
        </Menu.Item>
      </Menu>
    </Header>
  );
};

export { MainHeader };
