import { gql, MutationResult, useMutation } from "@apollo/client";
import React from "react";
import { Form, Input, Button, Checkbox, Spin } from "antd";

import { useAuthToken } from "../hooks";
import { LoginMutationResponseType } from "../types";
import { LoginForm } from "../components/LoginForm";

const layout = {
  labelCol: {
    span: 8,
  },
  wrapperCol: {
    span: 16,
  },
};
const tailLayout = {
  wrapperCol: {
    offset: 8,
    span: 16,
  },
};

type LoginFormItemsType = {
  username: string;
  password: string;
  remember: boolean;
};

type LoginRequirementsType = {
  username: string;
  password: string;
};

type LoginFuncType = (input: LoginRequirementsType) => Promise<any>;

const AuthPage: React.FC = () => {
  const LOGIN_MUTATION = gql`
    mutation LoginMutation($input: LoginInput!) {
      auth {
        login(input: $input) {
          loginPayload {
            status
            recordId
            authToken
            record {
              username
            }
          }
        }
      }
    }
  `;

  const useLoginMutation: () => [LoginFuncType, MutationResult<LoginMutationResponseType>] = () => {
    const [authToken, setAuthToken, removeAuthToken] = useAuthToken();

    const [mutation, mutationResults] = useMutation(LOGIN_MUTATION, {
      onCompleted: (response: LoginMutationResponseType) => {
        setAuthToken(response.auth.login.loginPayload.authToken);
      },
    });

    const login: LoginFuncType = (input) => {
      if (authToken) removeAuthToken();
      return mutation({
        variables: {
          input,
        },
      });
    };
    return [login, mutationResults];
  };

  const [login, loginResult] = useLoginMutation();

  const onFormFinish = (values: LoginFormItemsType) => {
    const input = { username: values.username, password: values.password };
    // TODO: add to local storage on remember = true
    login(input);
  };

  const onFormFinishFailed = (errorInfo: any) => {
    console.log("Login form failed:", errorInfo);
  };

  return (
    <LoginForm
      isLoading={loginResult.loading}
      onFormFinish={onFormFinish}
      onFormFinishFailed={onFormFinishFailed}
    />
  );
};

export { AuthPage };
