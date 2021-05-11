import { ApolloError, useMutation } from "@apollo/client";
import { Button, Spin } from "antd";
import React, { useEffect, useState } from "react";
import { useHistory, useParams } from "react-router";

import { EMAIL_CONFIRMATION_MUTATION } from "../gqlQueries";
import { useAuthToken } from "../hooks";

import type { RegisterEmailConfirmationResponseType } from "../types";

const EmailConfirmationPage: React.FC = () => {
  const history = useHistory();

  const { token } = useParams<{ token: string }>();

  const [finishEventId, setFinishEventId] = useState<number>(0);

  const [authToken, setAuthToken, removeAuthToken] = useAuthToken();

  const [
    confirmMutation,
    { data, error, loading },
  ] = useMutation<RegisterEmailConfirmationResponseType>(EMAIL_CONFIRMATION_MUTATION, {
    onCompleted: (response: RegisterEmailConfirmationResponseType) => {
      setFinishEventId(
        window.setTimeout(() => {
          if (authToken) removeAuthToken();
          setAuthToken(
            response.auth.emailConfirmation.registerEmailConfirmationPayload.authToken,
          );
          history.push("/projects");
        }, 10000),
      );
    },
    onError: (error: ApolloError) => {
      console.log(error);
    },
  });

  const emailConfirm = () => {
    if (authToken) removeAuthToken();
    return confirmMutation({
      variables: {
        input: {
          token,
        },
      },
    });
  };

  const onGoToMainPageClick = () => {
    if (finishEventId) clearTimeout(finishEventId);
    if (authToken) removeAuthToken();

    setAuthToken(data!.auth.emailConfirmation.registerEmailConfirmationPayload.authToken);
    history.push("/projects");
  };

  useEffect(() => {
    emailConfirm();
  }, []);

  if (error) {
    if (
      error.graphQLErrors.length === 1 &&
      // @ts-ignore: don's know how to extend ApolloError type
      error.graphQLErrors[0].status === "BAD_REQUEST"
    )
      return <span>You are using invalid confirmation token!</span>;
    return <span>Something went wrong. Sorry...</span>;
  }

  return (
    <>
      {loading ? (
        <div style={{ textAlign: "center" }}>
          <h1>Your email confirmation is processing</h1>
          <Spin />
        </div>
      ) : (
        <div style={{ textAlign: "center" }}>
          <h1>Your email confirmation was successed.</h1>
          <span>
            You will be redirected to the main page after few seconds or you can click on
            this.
          </span>
          <Button onClick={onGoToMainPageClick}>Go to main page</Button>
        </div>
      )}
    </>
  );
};

export { EmailConfirmationPage };
