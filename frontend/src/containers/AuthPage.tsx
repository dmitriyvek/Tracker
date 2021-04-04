import { ApolloError, MutationResult, useMutation } from "@apollo/client";
import React, { useState } from "react";

import { REGISTER_MUTATION, LOGIN_MUTATION } from "../gqlQueries";
import { useAuthToken } from "../hooks";
import { LoginForm } from "../components/LoginForm";
import { RegisterForm } from "../components/RegisterForm";

import type { LoginMutationResponseType, RegisterMutationResponseType } from "../types";
import type { LoginFormItemsType, LoginRequirementsType } from "../components/LoginForm";
import type { RegisterFormItemsType } from "../components/RegisterForm";

type LoginFuncType = (input: LoginRequirementsType) => Promise<any>;
type RegisterFuncType = (input: RegisterFormItemsType) => Promise<any>;

const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

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

  const [authToken, setAuthToken, removeAuthToken] = useAuthToken();

  const [loginMutation, { error: loginError, loading: loginIsLoading }] = useMutation(
    LOGIN_MUTATION,
    {
      onCompleted: (response: LoginMutationResponseType) => {
        setAuthToken(response.auth.login.loginPayload.authToken);
      },
      onError: (error: ApolloError) => {},
    },
  );
  const [registerMutation, { error: registerError, loading: registerIsLoading }] = useMutation(
    REGISTER_MUTATION,
    {
      onCompleted: (response: RegisterMutationResponseType) => {
        setAuthToken(response.auth.register.registerPayload.authToken);
      },
      onError: (error: ApolloError) => {},
    },
  );

  const login: LoginFuncType = (input) => {
    if (authToken) removeAuthToken();
    return loginMutation({
      variables: {
        input,
      },
    });
  };
  const register: RegisterFuncType = (input) => {
    if (authToken) removeAuthToken();
    return registerMutation({
      variables: {
        input,
      },
    });
  };

  const onLoginFormFinish = (values: LoginFormItemsType) => {
    // TODO: add to local storage on remember = true
    login({ username: values.username, password: values.password });
  };

  const onRegisterFormFinish = (values: RegisterFormItemsType) => {
    register(values);
  };

  const onFormFinishFailed = (errorInfo: any) => {
    console.log("Form failed:", errorInfo);
  };

  return (
    <>
      {isLogin ? (
        <LoginForm
          onChangeFormTypeClick={() => setIsLogin(false)}
          isLoading={loginIsLoading}
          onFormFinish={onLoginFormFinish}
          onFormFinishFailed={onFormFinishFailed}
        />
      ) : (
        <RegisterForm
          onChangeFormTypeClick={() => setIsLogin(true)}
          isLoading={registerIsLoading}
          onFormFinish={onRegisterFormFinish}
          onFormFinishFailed={onFormFinishFailed}
        />
      )}
      {loginError && <p>{loginError.message}</p>}
      {registerError && <p>{registerError.message}</p>}
    </>
  );
};

export { AuthPage };
