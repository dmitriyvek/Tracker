import { Form, Input, Button, Select } from "antd";
import { useEffect, useRef, useState } from "react";
import { MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";

import { validateEmail } from "../utils";

import { RoleEnum } from "../types";

const formItemLayout = {
  labelCol: {
    xs: { span: 24 },
    sm: { span: 4 },
  },
  wrapperCol: {
    xs: { span: 24 },
    sm: { span: 20 },
  },
};
const formItemLayoutWithOutLabel = {
  wrapperCol: {
    xs: { span: 24, offset: 0 },
    sm: { span: 20, offset: 4 },
  },
};

const RolesCreationForm: React.FC = () => {
  const [newFieldIsAdded, setNewFieldIsAdded] = useState<boolean>(false);

  const inputRef = useRef(null);

  useEffect(() => {
    console.log(inputRef, inputRef.current);

    if (newFieldIsAdded && inputRef.current) {
      // @ts-ignore
      inputRef.current.focus();
    }
  }, [newFieldIsAdded]);

  const onFinish = (values: any) => {
    console.log("Received values of form:", values);
  };

  const onFormFinishFailed = (errorInfo: any) => {
    console.log("Form failed:", errorInfo);
  };

  return (
    <Form
      name="dynamic_form_item"
      {...formItemLayoutWithOutLabel}
      onError={onFormFinishFailed}
      onFinish={onFinish}
    >
      <Form.List
        name="emailList"
        rules={[
          {
            validator: async (_, fieldList) => {
              if (!fieldList || fieldList.length < 1) {
                return Promise.reject(new Error("Add at least 1 email address."));
              }
            },
          },
        ]}
      >
        {(fieldList, { add, remove }, { errors }) => (
          <>
            {fieldList.map((field, index) => (
              <Form.Item
                {...(index === 0 ? formItemLayout : formItemLayoutWithOutLabel)}
                label={index === 0 ? "Emails" : ""}
                required={false}
                key={field.key}
              >
                <Form.Item
                  {...field}
                  validateTrigger={["onChange", "onBlur"]}
                  rules={[
                    {
                      required: true,
                      whitespace: true,
                      message: "Please input new participant email.",
                    },
                    () => ({
                      async validator(_, value) {
                        if (!validateEmail(value)) {
                          return Promise.reject("The input is not valid email!");
                        }
                        return Promise.resolve();
                      },
                    }),
                  ]}
                  noStyle
                >
                  <Input
                    ref={inputRef}
                    placeholder="new participant email"
                    style={{ width: "60%" }}
                    onBlur={() => setNewFieldIsAdded(false)}
                    onPressEnter={() => {
                      add();
                    }}
                  />
                </Form.Item>
                <MinusCircleOutlined
                  className="dynamic-delete-button"
                  onClick={() => remove(field.name)}
                />
              </Form.Item>
            ))}
            <Form.Item>
              <Button
                type="dashed"
                onClick={() => {
                  add();
                  setNewFieldIsAdded(true);
                }}
                style={{ width: "60%" }}
                icon={<PlusOutlined />}
              >
                Add email
              </Button>
              <Form.ErrorList errors={errors} />
            </Form.Item>

            <Form.Item
              rules={[
                {
                  required: true,
                  whitespace: true,
                  message: "Please input new participants role.",
                },
              ]}
              required={false}
              label="Role"
              name="role"
            >
              <Select style={{ width: "60%" }}>
                {/* {Object.keys(RoleEnum).map((role, index) => (
                  <Select.Option key={index} value={role}>
                    {role.replaceAll("_", " ")}
                  </Select.Option>
                ))} */}
                <Select.Option value="demo">Demo</Select.Option>
                <Select.Option value="demo2">Demo2</Select.Option>
                <Select.Option value="demo3">Demo3</Select.Option>
              </Select>
            </Form.Item>
          </>
        )}
      </Form.List>
      <Form.Item>
        <Button type="primary" htmlType="submit">
          Submit
        </Button>
      </Form.Item>
    </Form>
  );
};

export { RolesCreationForm };
