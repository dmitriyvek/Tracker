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
  const [isRegisterComplition, setIsRegisterComplition] = useState(false);

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
      setIsRegisterComplition(true);
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

  const onLoginFormFinish = async (values: LoginFormItemsType) => {
    await login({ username: values.username, password: values.password });
    history.push("/projects");
  };

  const onRegisterFormFinish = async (values: RegisterFormItemsType) => {
    const input = {
      username: values.username,
      email: values.email,
      password: values.password,
    };
    await register(input);
    history.push("/auth");
  };

  if (isRegisterComplition)
    return (
      <>
        <h1 style={{ textAlign: "center" }}>You successfully registered.</h1>
        <span style={{ textAlign: "center" }}>
          Check your email for confirmation letter.
        </span>
      </>
    );

  if (isLogin)
    return (
      <>
        <h1 style={{ textAlign: "center" }}>Login page</h1>
        <LoginForm
          onChangeFormTypeClick={() => setIsLogin(false)}
          isLoading={loginIsLoading}
          onFormFinish={onLoginFormFinish}
          error={loginError}
        />
      </>
    );
  else
    return (
      <>
        <h1 style={{ textAlign: "center" }}>Registration page</h1>
        <RegisterForm
          onChangeFormTypeClick={() => setIsLogin(true)}
          isLoading={registerIsLoading}
          onFormFinish={onRegisterFormFinish}
          error={registerError}
        />
      </>
    );
};

export { AuthPage };
