type ProjectListPageInfoType = {
  hasNextPage: boolean;
  endCursor: string;
};

type ProjectNodeType = {
  node: {
    id: string;
    title: string;
    description: string;
  };
};

type ProjectListType = {
  edges: ProjectNodeType[];
  pageInfo: ProjectListPageInfoType;
};

type ProjectListResponseType = {
  projects: {
    list: ProjectListType;
  };
};

enum MutatianStatusEnum {
  Success = "SUCCESS",
  Fail = "FAIL",
}

type UserType = {
  username: string;
};

type LoginAndRegisterPayloadType = {
  authToken: string;
  recordId: number;
  status: MutatianStatusEnum;
  record: UserType;
};

type LoginMutationResponseType = {
  auth: {
    login: {
      loginPayload: LoginAndRegisterPayloadType;
    };
  };
};
type RegisterMutationResponseType = {
  auth: {
    register: {
      registerPayload: LoginAndRegisterPayloadType;
    };
  };
};

type LogoutMutationResponseType = {
  auth: {
    logout: {
      logoutPayload: {
        status: MutatianStatusEnum;
      };
    };
  };
};

export type {
  ProjectNodeType,
  ProjectListResponseType,
  LoginMutationResponseType,
  LogoutMutationResponseType,
  RegisterMutationResponseType,
};

export { MutatianStatusEnum };
