import { ApolloQueryResult } from "@apollo/client";
import { Form, Input, Button, Spin } from "antd";
import { useState } from "react";

import { useImperativeQuery } from "../hooks";
import { PROJECT_TITLE_DUPLICATION_CHECK_QUERY } from "../gqlQueries";

import type { ProjectTitleDuplicationCheckResponseType } from "../types";

type ProjectCreationFormValuesType = {
  title: string;
  description?: string;
};

type ProjectCreationFormPropsType = {
  isLoading: boolean;
  createProject: (input: ProjectCreationFormValuesType) => void;
};

const layout = {
  labelCol: { span: 3, offset: 6 },
  wrapperCol: { span: 8 },
};
const tailLayout = {
  wrapperCol: { offset: 9, span: 6 },
};

const { TextArea } = Input;

const ProjectCreationForm: React.FC<ProjectCreationFormPropsType> = ({
  isLoading,
  createProject,
}: ProjectCreationFormPropsType) => {
  const [titleIsUnique, setTitleIsUnique] = useState<boolean>(false);
  const [titleIsChanged, setTitleIsChanged] = useState<boolean>(false);
  const [titleCheckTimeoutId, setTitleCheckTimeoutId] = useState<number>(0);

  const [form] = Form.useForm();

  const onReset = () => {
    form.resetFields();
  };

  const onFormFinishFailed = (errorInfo: any) => {
    console.log("Form failed:", errorInfo);
  };

  const usernameCheck = useImperativeQuery<ProjectTitleDuplicationCheckResponseType>(
    PROJECT_TITLE_DUPLICATION_CHECK_QUERY,
  );

  const makeTitleCheck = (value: string) => {
    return new Promise((resolve, reject) => {
      setTitleCheckTimeoutId(
        window.setTimeout(async () => {
          usernameCheck({
            title: value,
          })
            .then(
              (response: ApolloQueryResult<ProjectTitleDuplicationCheckResponseType>) => {
                setTitleIsChanged(false);

                if (response.data.projects.duplicationCheck.title) {
                  setTitleIsUnique(false);
                  reject("You already have a project with given title!");
                } else {
                  setTitleIsUnique(true);
                  resolve(true);
                }
              },
            )
            .catch((error: any) => {
              console.log("Error during project title duplication check: ", error);
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
        form={form}
        name="control-hooks"
        onFinishFailed={onFormFinishFailed}
        onFinish={createProject}
      >
        <Form.Item
          required={true}
          name="title"
          label="Title"
          hasFeedback
          rules={[
            {
              min: 4,
              max: 32,
              validator(rule, value) {
                if (!value || !value.length) return Promise.reject("Please input title!");

                if (value.length < rule.min!)
                  return Promise.reject("Title is too short.");

                if (value.length > rule.max!) return Promise.reject("Title is too long.");

                if (titleIsChanged) return makeTitleCheck(value).then();
                else
                  return titleIsUnique
                    ? Promise.resolve()
                    : Promise.reject("You already have a project with given title!");
              },
            },
          ]}
        >
          <Input
            onChange={() => {
              if (!titleIsChanged) setTitleIsChanged(true);
              if (titleCheckTimeoutId) clearTimeout(titleCheckTimeoutId);
            }}
            autoComplete="new-title"
          />
        </Form.Item>
        <Form.Item
          required={false}
          name="description"
          label="Description"
          rules={[{ required: false }, { max: 128, message: "Description is too long." }]}
        >
          <TextArea
            autoComplete="new-description"
            autoSize={{ minRows: 2, maxRows: 5 }}
          />
        </Form.Item>

        <Form.Item {...tailLayout}>
          <Button
            type="primary"
            style={{ marginRight: "10px", marginBottom: "10px" }}
            htmlType="submit"
          >
            Create
          </Button>
          <Button htmlType="button" onClick={onReset}>
            Reset form
          </Button>
        </Form.Item>
      </Form>
    </Spin>
  );
};

export { ProjectCreationForm };
export type { ProjectCreationFormValuesType };
