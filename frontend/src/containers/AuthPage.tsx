import { ApolloError, useMutation } from "@apollo/client";
import React, { useState } from "react";
import { useHistory } from "react-router";

import { REGISTER_MUTATION, LOGIN_MUTATION } from "../gqlQueries";
import { useAuthToken } from "../hooks";
import { LoginForm } from "../components/LoginForm";
import { RegisterForm } from "../components/RegisterForm";

import type {
  LoginMutationResponseType,
  RegisterMutationResponseType,
  LoginMutationRequiredVarsType,
  RegistrationMutationRequiredVarsType,
} from "../types";
import type { LoginFormItemsType } from "../components/LoginForm";
import type { RegisterFormItemsType } from "../components/RegisterForm";

type LoginFuncType = (input: LoginMutationRequiredVarsType) => Promise<any>;
type RegisterFuncType = (input: RegistrationMutationRequiredVarsType) => Promise<any>;

const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

  const history = useHistory();

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
  const [
    registerMutation,
    { error: registerError, loading: registerIsLoading },
  ] = useMutation(REGISTER_MUTATION, {
    onCompleted: (response: RegisterMutationResponseType) => {
      setAuthToken(response.auth.register.registerPayload.authToken);
    },
    onError: (error: ApolloError) => {},
  });

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
    login({ username: values.username, password: values.password }).then(() =>
      history.push("/projects"),
    );
  };

  const onRegisterFormFinish = (values: RegisterFormItemsType) => {
    const input = {
      username: values.username,
      email: values.email,
      password: values.password,
    };
    register(input).then(() => history.push("/projects"));
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
          error={loginError}
        />
      ) : (
        <RegisterForm
          onChangeFormTypeClick={() => setIsLogin(true)}
          isLoading={registerIsLoading}
          onFormFinish={onRegisterFormFinish}
          onFormFinishFailed={onFormFinishFailed}
          error={registerError}
        />
      )}
    </>
  );
};

export { AuthPage };
