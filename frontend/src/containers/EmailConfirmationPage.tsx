import { ApolloError, useMutation } from "@apollo/client";
import { Button, Spin } from "antd";
import React, { useEffect, useState } from "react";
import { useHistory, useParams } from "react-router";

import { EMAIL_CONFIRMATION_MUTATION } from "../gqlQueries";
import { useAuthToken } from "../hooks";

import type { EmailConfirmationResponseType } from "../types";

const EmailConfirmationPage: React.FC = () => {
  const history = useHistory();

  const { token } = useParams<{ token: string }>();

  const [finishEventId, setFinishEventId] = useState<number>(0);

  const [authToken, setAuthToken, removeAuthToken] = useAuthToken();

  const [
    confirmMutation,
    { data, error, loading },
  ] = useMutation<EmailConfirmationResponseType>(EMAIL_CONFIRMATION_MUTATION, {
    onCompleted: (response: EmailConfirmationResponseType) => {
      setFinishEventId(
        window.setTimeout(() => {
          if (authToken) removeAuthToken();
          setAuthToken(
            response.auth.emailConfirmation.emailConfirmationPayload.authToken,
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

    setAuthToken(data!.auth.emailConfirmation.emailConfirmationPayload.authToken);
    history.push("/projects");
  };

  useEffect(() => {
    emailConfirm();
  }, []);

  if (error) {
    if (
      error.graphQLErrors.length === 1 &&
      // @ts-ignore: don's know how extend ApolloError type
      error.graphQLErrors[0].status === "BAD_REQUEST"
    )
      return <p>You are using invalid confirmation token!</p>;
    return <p>Something went wrong. Sorry...</p>;
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
          <p>
            You will be redirected to the main page after few seconds or you can click on
            this.
          </p>
          <Button onClick={onGoToMainPageClick}>Go to main page</Button>
        </div>
      )}
    </>
  );
};

export { EmailConfirmationPage };
