import React, { ReactElement } from "react";
import { Layout, Menu, Breadcrumb } from "antd";

import { useLogout } from "../hooks";
import { MainHeader } from "../components/MainHeader";
import { MainSideBar } from "../components/MainSideBar";

const { Content } = Layout;

type MainLayoutPropsType = {
  children: ReactElement | null;
};

const MainLayout: React.FC<MainLayoutPropsType> = ({ children }: MainLayoutPropsType) => {
  const logout = useLogout();

  return (
    <Layout>
      <MainHeader onLogoutBtnClick={logout} />
      <Layout>
        <MainSideBar />
        <Layout style={{ padding: "0 24px 24px" }}>
          <Breadcrumb style={{ margin: "16px 0" }}>
            <Breadcrumb.Item>Home</Breadcrumb.Item>
            <Breadcrumb.Item>List</Breadcrumb.Item>
            <Breadcrumb.Item>App</Breadcrumb.Item>
          </Breadcrumb>

          <Content
            className="site-layout-background"
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
            }}
          >
            {children}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export { MainLayout };
