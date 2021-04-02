import React from "react";
import "antd/dist/antd.css";

import { MainLayout } from "./containers/Layout";
import { ProjectList } from "./containers/ProjectList";

const App: React.FC = () => {
  return (
    <div className="App">
      <MainLayout>
        <ProjectList />
      </MainLayout>
    </div>
  );
};

export default App;
