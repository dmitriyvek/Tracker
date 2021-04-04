import { ApolloError } from "@apollo/client";
import React, { useEffect } from "react";
import { message, Form, Input, Button, Checkbox, Spin } from "antd";

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

type LoginFormPropsType = {
  isLoading: boolean;
  onChangeFormTypeClick: () => void;
  onFormFinish: (values: LoginFormItemsType) => void;
  onFormFinishFailed: (errorInfo: any) => void;
  error: ApolloError | undefined;
};

const LoginForm: React.FC<LoginFormPropsType> = ({
  isLoading,
  onFormFinish,
  onFormFinishFailed,
  onChangeFormTypeClick,
  error,
}: LoginFormPropsType) => {
  useEffect(() => {
    if (error)
      message.error({
        content: error.message,
        duration: 5,
        key: "loginErrorMessage",
      });
  }, [error]);

  return (
    <Spin spinning={isLoading} delay={0} size="small">
      <Form
        {...layout}
        name="basic"
        initialValues={{
          remember: true,
        }}
        onFinish={onFormFinish}
        onFinishFailed={onFormFinishFailed}
      >
        <Form.Item
          required={false}
          label="Username"
          name="username"
          rules={[
            {
              required: true,
              message: "Please input your username!",
            },
            { min: 4, message: "Username is too short." },
          ]}
        >
          <Input />
        </Form.Item>

        <Form.Item
          required={false}
          label="Password"
          name="password"
          rules={[
            {
              required: true,
              message: "Please input your password!",
            },
            { min: 6, message: "Password is too short." },
          ]}
        >
          <Input.Password />
        </Form.Item>

        <Form.Item {...tailLayout} name="remember" valuePropName="checked">
          <Checkbox>Remember me</Checkbox>
        </Form.Item>

        <Form.Item {...tailLayout}>
          <Button type="primary" htmlType="submit">
            Login
          </Button>
        </Form.Item>

        <Form.Item {...tailLayout}>
          <Button type="primary" ghost onClick={onChangeFormTypeClick}>
            Register form
          </Button>
        </Form.Item>
      </Form>
    </Spin>
  );
};

export { LoginForm };
export type { LoginFormItemsType, LoginRequirementsType };
