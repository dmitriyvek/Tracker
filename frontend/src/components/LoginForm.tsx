import { ApolloError } from "@apollo/client";
import React, { useEffect } from "react";
import { message, Form, Input, Button, Spin } from "antd";

const layout = {
  labelCol: {
    span: 3,
    offset: 6,
  },
  wrapperCol: {
    span: 6,
  },
};
const tailLayout = {
  wrapperCol: {
    offset: 9,
    span: 4,
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
  error: ApolloError | undefined;
};

const LoginForm: React.FC<LoginFormPropsType> = ({
  isLoading,
  onFormFinish,
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

  const onFormFinishFailed = (errorInfo: any) => {
    console.log("Form failed:", errorInfo);
  };

  return (
    <Spin spinning={isLoading} delay={500} size="small">
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
            { max: 32, message: "Username is too long." },
          ]}
        >
          <Input autoComplete="on" />
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
            { min: 8, message: "Password is too short." },
            { max: 32, message: "Password is too long." },
          ]}
        >
          <Input.Password autoComplete="on" />
        </Form.Item>

        {/* <Form.Item {...tailLayout} name="remember" valuePropName="checked">
          <Checkbox>Remember me</Checkbox>
        </Form.Item> */}

        <Form.Item {...tailLayout}>
          <Button type="primary" htmlType="submit">
            Login
          </Button>
        </Form.Item>

        <Form.Item {...tailLayout}>
          <Button type="primary" ghost onClick={onChangeFormTypeClick}>
            Register page
          </Button>
        </Form.Item>
      </Form>
    </Spin>
  );
};

export { LoginForm };
export type { LoginFormItemsType, LoginRequirementsType };
