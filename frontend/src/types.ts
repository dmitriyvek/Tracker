type AuthTokenPayloadType = {
  exp: number;
  iat: number;
  sub: number;
};

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

type EmailDuplicationCheckResponse = {
  auth: {
    duplicationCheck: {
      email: boolean;
    };
  };
};

type UsernameDuplicationCheckResponse = {
  auth: {
    duplicationCheck: {
      username: boolean;
    };
  };
};

type RoleNodeType = {
  node: {
    userId: number;
    role: string;
  };
};

type RoleListType = {
  edges: RoleNodeType[];
  pageInfo: {
    hasNextPage: boolean;
    endCursor: string;
  };
};

type ProjectDetailResponseType = {
  node: {
    title: string;
    description: string;
    createdAt: string;
    roleList: RoleListType;
  };
};

type ProjectDetailRoleListFetchMoreResponseType = {
  node: {
    roleList: RoleListType;
  };
};

enum MutatianStatusEnum {
  success = "SUCCESS",
  fail = "FAIL",
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

type LoginMutationRequiredVarsType = {
  username: string;
  password: string;
};

type RegistrationMutationRequiredVarsType = {
  username: string;
  email: string;
  password: string;
};

export type {
  AuthTokenPayloadType,
  ProjectNodeType,
  ProjectListResponseType,
  EmailDuplicationCheckResponse,
  UsernameDuplicationCheckResponse,
  LoginMutationResponseType,
  LogoutMutationResponseType,
  RegisterMutationResponseType,
  LoginMutationRequiredVarsType,
  RegistrationMutationRequiredVarsType,
  ProjectDetailResponseType,
  ProjectDetailRoleListFetchMoreResponseType,
};

export { MutatianStatusEnum };
