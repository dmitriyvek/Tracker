// TODO: think on how to make it a pure component
import { ApolloError, ApolloQueryResult } from "@apollo/client";
import React, { useEffect, useState } from "react";
import { message, Form, Input, Button, Spin } from "antd";

import {
  EMAIL_DUPLICATION_CHECK_QUERY,
  USERNAME_DUPLICATION_CHECK_QUERY,
} from "../gqlQueries";
import { useImperativeQuery } from "../hooks";
import { validateEmail } from "../utils";

import type {
  EmailDuplicationCheckResponse,
  UsernameDuplicationCheckResponse,
} from "../types";

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

type RegisterFormItemsType = {
  username: string;
  email: string;
  password: string;
  confirm: string;
};

type RegisterFormPropsType = {
  isLoading: boolean;
  onChangeFormTypeClick: () => void;
  onFormFinish: (values: RegisterFormItemsType) => void;
  onFormFinishFailed: (errorInfo: any) => void;
  error: ApolloError | undefined;
};

const RegisterForm: React.FC<RegisterFormPropsType> = ({
  isLoading,
  onFormFinish,
  onFormFinishFailed,
  onChangeFormTypeClick,
  error,
}: RegisterFormPropsType) => {
  useEffect(() => {
    if (error)
      message.error({
        content: error.message,
        duration: 5,
        key: "registerErrorMessage",
      });
  }, [error]);

  const [usernameIsChanged, setUsernameIsChanged] = useState<boolean>(false);
  const [usernameIsUnique, setUsernameIsUnique] = useState<boolean>(false);
  const [usernameCheckTimeoutId, setUsernameCheckTimeoutId] = useState<number>(0);

  const [emailIsChanged, setEmailIsChanged] = useState<boolean>(false);
  const [emailIsUnique, setEmailIsUnique] = useState<boolean>(false);
  const [emailCheckTimeoutId, setEmailCheckTimeoutId] = useState<number>(0);

  const usernameCheck = useImperativeQuery(USERNAME_DUPLICATION_CHECK_QUERY);
  const emailCheck = useImperativeQuery(EMAIL_DUPLICATION_CHECK_QUERY);

  const makeUsernameCheck = (value: string) => {
    return new Promise((resolve, reject) => {
      setUsernameCheckTimeoutId(
        window.setTimeout(async () => {
          usernameCheck({
            username: value,
          })
            .then((response: ApolloQueryResult<UsernameDuplicationCheckResponse>) => {
              setUsernameIsChanged(false);

              if (response.data.auth.duplicationCheck.username) {
                setUsernameIsUnique(false);
                reject("User with given username is already exists!");
              } else {
                setUsernameIsUnique(true);
                resolve(true);
              }
            })
            .catch((error: any) => {
              console.log("Error during username duplication check: ", error);
              resolve(true);
            });
        }, 3000),
      );
    });
  };

  const makeEmailCheck = (value: string) => {
    return new Promise((resolve, reject) => {
      setEmailCheckTimeoutId(
        window.setTimeout(async () => {
          emailCheck({
            email: value,
          })
            .then((response: ApolloQueryResult<EmailDuplicationCheckResponse>) => {
              setEmailIsChanged(false);

              if (response.data.auth.duplicationCheck.email) {
                setEmailIsUnique(false);
                reject("User with given email is already exists!");
              } else {
                setEmailIsUnique(true);
                resolve(true);
              }
            })
            .catch((error: any) => {
              console.log("Error during email duplication check: ", error);
              resolve(true);
            });
        }, 3000),
      );
    });
  };

  return (
    <Spin spinning={isLoading} delay={500} size="small">
      <Form
        {...layout}
        name="basic"
        onFinish={onFormFinish}
        onFinishFailed={onFormFinishFailed}
      >
        <Form.Item
          required={false}
          label="Username"
          name="username"
          tooltip="Username used to log into the application"
          hasFeedback
          rules={[
            {
              min: 4,
              validator(rule, value) {
                if (usernameCheckTimeoutId) clearTimeout(usernameCheckTimeoutId);

                if (!value || !value.length)
                  return Promise.reject("Please input your username!");

                if (value.length >= rule.min!)
                  if (usernameIsChanged) return makeUsernameCheck(value).then();
                  else
                    return usernameIsUnique
                      ? Promise.resolve()
                      : Promise.reject("User with given username is already exists!");
                return Promise.reject("Username is too short.");
              },
            },
          ]}
        >
          <Input
            onChange={() => {
              if (!usernameIsChanged) setUsernameIsChanged(true);
            }}
            autoComplete="new-username"
          />
        </Form.Item>

        <Form.Item
          required={false}
          label="Email"
          name="email"
          tooltip="Email used for account confirmation"
          hasFeedback
          rules={[
            () => ({
              validator(_, value) {
                if (emailCheckTimeoutId) clearTimeout(emailCheckTimeoutId);

                if (!value || !value.length) {
                  return Promise.reject("Please input your email!");
                }

                if (!validateEmail(value)) {
                  return Promise.reject("The input is not valid email!");
                }

                if (emailIsChanged) return makeEmailCheck(value).then();
                else
                  return emailIsUnique
                    ? Promise.resolve()
                    : Promise.reject("User with given email is already exists!");
              },
            }),
          ]}
        >
          <Input
            onChange={() => {
              if (!emailIsChanged) setEmailIsChanged(true);
            }}
            autoComplete="new-email"
          />
        </Form.Item>

        <Form.Item
          required={false}
          label="Password"
          name="password"
          hasFeedback
          rules={[
            {
              required: true,
              message: "Please input your password!",
            },
            { min: 6, message: "Password is too short." },
          ]}
        >
          <Input.Password autoComplete="new-password" />
        </Form.Item>

        <Form.Item
          required={false}
          name="confirm"
          label="Confirm Password"
          dependencies={["password"]}
          hasFeedback
          rules={[
            {
              required: true,
              message: "Please confirm your password!",
            },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue("password") === value) {
                  return Promise.resolve();
                }
                return Promise.reject(
                  new Error("The two passwords that you entered do not match!"),
                );
              },
            }),
          ]}
        >
          <Input.Password />
        </Form.Item>

        <Form.Item {...tailLayout} name="submit-button">
          <Button type="primary" htmlType="submit" disabled={false}>
            Register
          </Button>
        </Form.Item>

        <Form.Item {...tailLayout}>
          <Button type="primary" ghost onClick={onChangeFormTypeClick}>
            Login form
          </Button>
        </Form.Item>
      </Form>
    </Spin>
  );
};

export { RegisterForm };
export type { RegisterFormItemsType };
