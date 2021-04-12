import { Menu, Layout, Button, Modal, Row, Col, Dropdown } from "antd";
import { useState } from "react";
import { Link, useHistory } from "react-router-dom";

const { Header } = Layout;

type MainHeaderPropsType = {
  logout: () => Promise<any>;
};

const menuLayout = {
  span: 16,
};

const logoutBtnLayout = {
  span: 2,
  offset: 6,
};

const MainHeader: React.FC<MainHeaderPropsType> = ({ logout }) => {
  const [logoutModalVisible, setLogoutModalVisible] = useState<boolean>(false);
  const [logoutConfirmLoading, setLogoutConfirmLoading] = useState<boolean>(false);
  const [logoutModalText, setLogoutModalText] = useState<string>(
    "Are you sure you want to log out?",
  );

  const history = useHistory();

  const showLogoutModal = () => {
    setLogoutModalVisible(true);
  };

  const handleLogout = () => {
    setLogoutModalText("Loging you out...");
    setLogoutConfirmLoading(true);
    logout().then(() => {
      // setLogoutModalVisible(false);
      // setLogoutConfirmLoading(false);
      history.push("/auth");
    });
  };

  const handleLogoutCancel = () => {
    setLogoutModalVisible(false);
  };

  const projectListMenu = (
    <Menu>
      <Menu.Item key="project-list">
        <Link to="/projects">Project list</Link>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="project-create">
        <Link to="/projects/create">Create new project</Link>
      </Menu.Item>
    </Menu>
  );

  return (
    <Header className="header">
      <Row>
        <Col {...menuLayout}>
          <Menu theme="dark" mode="horizontal" defaultSelectedKeys={["projects-link"]}>
            <Menu.Item key="projects-link">
              <Dropdown
                overlay={projectListMenu}
                placement="bottomRight"
                trigger={["click"]}
              >
                <a className="ant-dropdown-link" onClick={(e) => e.preventDefault()}>
                  Projects
                </a>
              </Dropdown>
            </Menu.Item>
          </Menu>
        </Col>

        <Col {...logoutBtnLayout}>
          <Button
            danger
            onClick={showLogoutModal}
            style={{ float: "right", top: "16px" }}
          >
            Log out
          </Button>
          <Modal
            visible={logoutModalVisible}
            onCancel={handleLogoutCancel}
            onOk={handleLogout}
            maskClosable={true}
            okType="danger"
            okText="Log out"
            cancelText="Cancel"
            confirmLoading={logoutConfirmLoading}
          >
            <p
              style={{
                textAlign: "center",
                fontSize: "18px",
                marginBottom: "0",
                marginTop: "10px",
              }}
            >
              {logoutModalText}
            </p>
          </Modal>
        </Col>
      </Row>
    </Header>
  );
};

export { MainHeader };
