import React from "react";
import { Form, Input, Button, Checkbox, Spin } from "antd";

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
};

const RegisterForm: React.FC<RegisterFormPropsType> = ({
  isLoading,
  onFormFinish,
  onFormFinishFailed,
  onChangeFormTypeClick,
}: RegisterFormPropsType) => {
  return (
    <Spin spinning={isLoading} delay={0} size="small">
      <Form {...layout} name="basic" onFinish={onFormFinish} onFinishFailed={onFormFinishFailed}>
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
          label="Email"
          name="email"
          rules={[
            {
              required: true,
              message: "Please input your email!",
            },
            { type: "email", message: "The input is not valid email!" },
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

        <Form.Item {...tailLayout}>
          <Button type="primary" htmlType="submit">
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
