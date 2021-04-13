import { ApolloError, FetchResult, useMutation } from "@apollo/client";
import { useHistory } from "react-router";

import { PROJECT_CREATION_MUTATION } from "../gqlQueries";
import { ProjectCreationForm } from "../components/ProjectCreationForm";

import type { ProjectCreationFormValuesType } from "../components/ProjectCreationForm";
import type { ProjectCreationMutationResponseType } from "../types";

const ProjectCreationPage = () => {
  const history = useHistory();

  const [
    projectCreationMutation,
    { loading },
  ] = useMutation<ProjectCreationMutationResponseType>(PROJECT_CREATION_MUTATION, {
    onError: (error: ApolloError) => {
      console.log("Error during project creation mutation: ", error);
    },
  });

  const createProject = async (input: ProjectCreationFormValuesType) => {
    const response = await projectCreationMutation({
      variables: {
        input,
      },
    });
    const projectId =
      response.data?.project.projectCreation.projectCreationPayload.record.id;
    history.push(`/projects/${projectId}`);
  };

  return (
    <>
      <h1 style={{ textAlign: "center" }}>Project creation page</h1>
      <ProjectCreationForm isLoading={loading} createProject={createProject} />
    </>
  );
};

export { ProjectCreationPage };
