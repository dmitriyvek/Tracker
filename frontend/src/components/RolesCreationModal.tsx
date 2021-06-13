import { Button, Modal } from "antd";
import { useState } from "react";

import { RolesCreationForm } from "./RolesCreationForm";

import type { RolesCreateionInputType } from "../types";

type RolesCreationModalPropsType = {
  isVisible: boolean;
  projectId: string;
  setIsVisible: (state: boolean) => void;
  onFormSubmit: (values: RolesCreateionInputType) => Promise<any>;
};

const RolesCreationModal: React.FC<RolesCreationModalPropsType> = ({
  isVisible,
  setIsVisible,
  onFormSubmit,
  projectId,
}) => {
  const formId = "roles_creation_form";

  const [confirmLoading, setConfirmLoading] = useState(false);

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
        <Button key="cancel" type="default" onClick={() => setIsVisible(false)}>
          Cancel
        </Button>,
        <Button
          loading={confirmLoading}
          form={formId}
          type="primary"
          key="submit"
          htmlType="submit"
        >
          Submit
        </Button>,
      ]}
    >
      <RolesCreationForm formId={formId} handleSubmit={handleSubmit} />
    </Modal>
  );
};

export { RolesCreationModal };
