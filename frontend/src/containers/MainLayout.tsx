import React, { ReactElement } from "react";
import { Layout } from "antd";

import { useLogout } from "../hooks";
import { MainHeader } from "../components/MainHeader";

type MainLayoutPropsType = {
  children: ReactElement | null;
};

const MainLayout: React.FC<MainLayoutPropsType> = ({ children }: MainLayoutPropsType) => {
  const logout = useLogout();

  return (
    <Layout>
      <MainHeader onLogoutBtnClick={logout} />
      {children}
    </Layout>
  );
};

export { MainLayout };
