import { ApolloError, useLazyQuery } from "@apollo/client";
import React, { useEffect, useState } from "react";
import { message, Form, Input, Button, Spin } from "antd";

import {
  EMAIL_DUPLICATION_CHECK_QUERY,
  USERNAME_DUPLICATION_CHECK_QUERY,
} from "../gqlQueries";
import { useImperativeQuery } from "../hooks";

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
};

type RegisterFormPropsType = {
  isLoading: boolean;
  onChangeFormTypeClick: () => void;
  onFormFinish: (values: RegisterFormItemsType) => void;
  onFormFinishFailed: (errorInfo: any) => void;
  error: ApolloError | undefined;
};

enum DuplicationCheckStatusEnum {
  initial = "",
  success = "success",
  error = "error",
  processing = "validating",
}

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

  const [form] = Form.useForm();

  const [usernameCheckStatus, setUsernameCheckStatus] = useState<any>(
    DuplicationCheckStatusEnum.initial,
  );
  const [emailCheckStatus, setEmailCheckStatus] = useState<any>(
    DuplicationCheckStatusEnum.initial,
  );
  const [usernameCheckTimeoutId, setUsernameCheckTimeoutId] = useState<number>(
    0,
  );
  const [emailCheckTimeoutId, setEmailCheckTimeoutId] = useState<number>(0);

  const [emailCheck] = useLazyQuery(EMAIL_DUPLICATION_CHECK_QUERY, {
    onCompleted: (response: EmailDuplicationCheckResponse) => {
      response.auth.duplicationCheck.email
        ? setEmailCheckStatus(DuplicationCheckStatusEnum.error)
        : setEmailCheckStatus(DuplicationCheckStatusEnum.success);
    },
  });
  const [usernameCheck] = useLazyQuery(USERNAME_DUPLICATION_CHECK_QUERY, {
    onCompleted: (response: UsernameDuplicationCheckResponse) => {
      response.auth.duplicationCheck.username
        ? setUsernameCheckStatus(DuplicationCheckStatusEnum.error)
        : setUsernameCheckStatus(DuplicationCheckStatusEnum.success);
    },
  });

  const usernameCheck2 = useImperativeQuery(USERNAME_DUPLICATION_CHECK_QUERY);

  const onEmailChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (emailCheckTimeoutId) clearTimeout(emailCheckTimeoutId);
    setEmailCheckStatus(DuplicationCheckStatusEnum.processing);
    setEmailCheckTimeoutId(
      window.setTimeout(() => {
        emailCheck({ variables: { email: event.target.value } });
      }, 3000),
    );
  };
  const onUsernameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.value.length < 4) return;

    if (usernameCheckTimeoutId) clearTimeout(usernameCheckTimeoutId);
    setUsernameCheckStatus(DuplicationCheckStatusEnum.processing);
    setUsernameCheckTimeoutId(
      window.setTimeout(() => {
        usernameCheck({ variables: { username: event.target.value } });
      }, 3000),
    );
  };
  const onUsernameChange2 = (value: string) => {
    if (usernameCheckTimeoutId) clearTimeout(usernameCheckTimeoutId);
    return new Promise((resolve, reject) => {
      setUsernameCheckTimeoutId(
        window.setTimeout(async () => {
          await usernameCheck2({
            username: value,
          }).then((response) => {
            if (response.data.auth.duplicationCheck.username) {
              reject("User with given username is already exists!");
            } else resolve(true);
          });
        }, 3000),
      );
    });
    // setUsernameCheckTimeoutId(
    //   window.setTimeout(() => {
    //     usernameCheck({ variables: { username: value } });
    //     if (false) return Promise.resolve();
    //     else
    //       return Promise.reject(
    //         new Error("User with given username is already exists!"),
    //       );
    //   }, 3000),
    // );
  };
  // console.log(usernameCheckStatus);
  // console.log(emailCheckStatus);

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
          // validateStatus={usernameCheckStatus}
          tooltip="Username used to log into the application"
          // hasFeedback={
          //   !(usernameCheckStatus == DuplicationCheckStatusEnum.initial)
          // }
          hasFeedback
          rules={[
            {
              required: true,
              message: "Please input your username!",
            },
            { min: 4, message: "Username is too short." },
            () => ({
              validator(_, value) {
                // if (!value.length)
                //   return Promise.reject(
                //     new Error("Please input your username!"),
                //   );

                // if (value.length < 4)
                // return Promise.reject(new Error("Username is too short."));

                if (value.length >= 4) return onUsernameChange2(value).then();
                return Promise.resolve();

                // if (a) {
                //   return Promise.reject(new Error("Pizdec"));
                // } else return Promise.resolve();

                // if (
                //   usernameCheckStatus == DuplicationCheckStatusEnum.success
                // ) {
                //   return Promise.resolve();
                // } else if (
                //   usernameCheckStatus == DuplicationCheckStatusEnum.error
                // )
                //   return Promise.reject(
                //     new Error("User with given username is already exists!"),
                //   );
              },
            }),
          ]}
        >
          {/* <Input onChange={onUsernameChange} autoComplete="new-username" /> */}
          <Input autoComplete="new-username" />
        </Form.Item>

        <Form.Item
          required={false}
          label="Email"
          name="email"
          tooltip="Email used for account confirmation"
          hasFeedback={
            !(emailCheckStatus == DuplicationCheckStatusEnum.initial)
          }
          rules={[
            {
              required: true,
              message: "Please input your email!",
            },
            { type: "email", message: "The input is not valid email!" },
          ]}
        >
          <Input onChange={onEmailChange} autoComplete="new-email" />
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
            { min: 6, message: "Password is too short." },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue("password") === value) {
                  return Promise.resolve();
                }
                return Promise.reject(
                  new Error(
                    "The two passwords that you entered do not match!",
                  ),
                );
              },
            }),
          ]}
        >
          <Input.Password />
        </Form.Item>

        <Form.Item shouldUpdate {...tailLayout}>
          <Button
            type="primary"
            htmlType="submit"
            // disabled={
            //   !form.isFieldsTouched() ||
            //   form.getFieldsError().filter(({ errors }) => errors.length)
            //     .length > 0
            // }
          >
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
