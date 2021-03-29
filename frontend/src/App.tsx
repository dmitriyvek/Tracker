import { useQuery, gql } from '@apollo/client';
import React from 'react';
import 'antd/dist/antd.css';

import { MainLayout } from './containers/Layout';
import { ProjectList } from './containers/ProjectList';

const count = 3;
const PROJECT_LIST = gql`
  query GetProjectList {
    projects {
      list(first: ${count}) {
        edges {
          node {
            id
            title
            createdAt
            description
          }
        }
      }
    }
  }
`;
type ProjectNodeType = {
  node: {
    id: string;
    title: string;
    description: string;
    createdAt: string;
  };
};

function Test() {
  const { loading, error, data } = useQuery(PROJECT_LIST);

  if (loading) return <p>Loading...</p>;
  if (error) {
    console.log(error);
    return <p>Error :(</p>;
  }

  return data.projects.list.edges.map(({ node }: ProjectNodeType) => (
    <div key={node.id}>
      <p>{node.title}</p>
      <p>{node.description}</p>
      <p>{node.createdAt}</p>
    </div>
  ));
}

const App: React.FC = () => {
  return (
    <div className="App">
      <MainLayout>
        <Test />
        {/* <ProjectList /> */}
      </MainLayout>
    </div>
  );
};

export default App;
