import { Form, Input, Button, Select, Modal } from "antd";
import { useEffect, useRef, useState } from "react";
import { MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";

import { validateEmail } from "../utils";

import { RoleEnum, RolesCreateionInputType } from "../types";

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
const selectItemLayout = {
  labelCol: {
    xs: { span: 24 },
    sm: { span: 4 },
  },
  wrapperCol: {
    xs: { span: 24 },
    sm: { span: 12 },
  },
};
const formItemLayoutWithOutLabel = {
  wrapperCol: {
    xs: { span: 24, offset: 0 },
    sm: { span: 20, offset: 4 },
  },
};

let maxNumberOfFields = Number(process.env.REACT_APP_MAIL_MAX_LETTERS_NUMBER);
if (!maxNumberOfFields) {
  maxNumberOfFields = 5;
  console.warn(
    "There is no REACT_APP_MAIL_MAX_LETTERS_NUMBER in .env file. Setting it to 5.",
  );
}

const roleList = Object.keys(RoleEnum).map((role) => {
  return { label: role.replaceAll("_", " "), value: role };
});

type RolesCreationFormProps = {
  isVisible: boolean;
  projectId: string;
  setIsVisible: (state: boolean) => void;
  onFormSubmit: (values: RolesCreateionInputType) => Promise<any>;
};

const RolesCreationModal: React.FC<RolesCreationFormProps> = ({
  isVisible,
  setIsVisible,
  onFormSubmit,
  projectId,
}) => {
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [newFieldIsAdded, setNewFieldIsAdded] = useState<boolean>(false);

  const inputRef = useRef(null);

  useEffect(() => {
    if (newFieldIsAdded && inputRef.current) {
      // @ts-ignore
      inputRef.current.focus();
    }
  }, [newFieldIsAdded]);

  const onFormFinishFailed = (errorInfo: any) => {
    console.log("Form failed:", errorInfo);
  };

  const handleSubmit = async (values: RolesCreateionInputType) => {
    values["projectId"] = projectId;

    setConfirmLoading(true);
    await onFormSubmit(values);
    setIsVisible(false);
    setConfirmLoading(false);
  };

  const handleCancel = () => {
    setIsVisible(false);
  };

  return (
    <Modal
      title="Adding new participants"
      maskClosable={false}
      visible={isVisible}
      onCancel={handleCancel}
      footer={[
        <Button type="default" onClick={() => setIsVisible(false)}>
          Cancel
        </Button>,
        <Button
          loading={confirmLoading}
          form="roles_create_form"
          type="primary"
          key="submit"
          htmlType="submit"
        >
          Submit
        </Button>,
      ]}
    >
      <Form
        id="roles_create_form"
        name="dynamic_form_item"
        {...formItemLayoutWithOutLabel}
        onError={onFormFinishFailed}
        onFinish={handleSubmit}
      >
        <Form.List
          name="emailList"
          initialValue={[]}
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
                    key={field.key}
                    validateTrigger={["onChange", "onBlur"]}
                    rules={[
                      ({ getFieldValue }) => ({
                        async validator(_, value) {
                          if (!value)
                            return Promise.reject("Please input new participant email.");

                          if (!validateEmail(value)) {
                            return Promise.reject("The input is not valid email!");
                          }

                          const valueList = getFieldValue("emailList").filter(
                            (elem: string) => elem === value,
                          );
                          if (valueList.length === 2) {
                            return Promise.reject(new Error("Duplicated email address!"));
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
                {fieldList.length < maxNumberOfFields && (
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
                )}

                <Form.ErrorList errors={errors} />
              </Form.Item>
            </>
          )}
        </Form.List>
        <Form.Item
          {...selectItemLayout}
          label="Role"
          name="role"
          rules={[
            {
              required: true,
              whitespace: true,
              message: "Please input new participants role.",
            },
          ]}
          required={false}
        >
          <Select placeholder="select a role for new participants" options={roleList} />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export { RolesCreationModal };
