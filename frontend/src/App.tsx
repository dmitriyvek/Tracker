import React from "react";
import "antd/dist/antd.css";

import { MainLayout } from "./containers/Layout";
// import { ProjectList } from "./containers/ProjectList";
import { TestView } from "./containers/Test";

const App: React.FC = () => {
  return (
    <div className="App">
      <MainLayout>
        {/* <ProjectList /> */}
        <TestView />
      </MainLayout>
    </div>
  );
};

export default App;
