enum RoleEnum {
  project_manager,
  team_member,
  viewer,
}

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
    myRole: {
      role: RoleEnum;
    };
    createdBy: {
      id: string;
      username: string;
    };
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
      __typename: string;
    };
  };
};

type UsernameDuplicationCheckResponse = {
  auth: {
    duplicationCheck: {
      username: boolean;
      __typename: string;
    };
  };
};

type RoleNodeType = {
  node: {
    role: RoleEnum;
    user: {
      id: string;
      username: string;
      email: string;
    };
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
    createdBy: {
      id: string;
      username: string;
    };
    myRole: {
      role: RoleEnum;
    };
  };
};

enum MutatianStatusEnum {
  success = "SUCCESS",
  fail = "FAIL",
}

type UserType = {
  username: string;
};

type LoginPayloadType = {
  authToken: string;
  recordId: number;
  status: MutatianStatusEnum;
  record: UserType;
};

type LoginMutationResponseType = {
  auth: {
    login: {
      loginPayload: LoginPayloadType;
    };
  };
};
type RegisterMutationResponseType = {
  auth: {
    register: {
      registerPayload: {
        status: MutatianStatusEnum;
      };
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

type ProjectCreationMutationResponseType = {
  project: {
    projectCreation: {
      projectCreationPayload: {
        status: MutatianStatusEnum;
        record: {
          id: string;
          title: string;
          description: string;
        };
      };
    };
  };
};

type ProjectTitleDuplicationCheckResponseType = {
  projects: {
    duplicationCheck: {
      title: boolean;
      __typename: string;
    };
  };
};

type UserRecord = {
  id: string;
  username: string;
  email: string;
  registeredAt: string;
};

type UserDetailHomeResponseType = {
  users: {
    detail: {
      record: UserRecord;
    };
  };
};

type UserDetailResponseType = {
  node: UserRecord;
};

type RegisterEmailConfirmationResponseType = {
  auth: {
    emailConfirmation: {
      registerEmailConfirmationPayload: {
        recordId: number;
        authToken: string;
        status: MutatianStatusEnum;
      };
    };
  };
};

export type {
  AuthTokenPayloadType,
  RegisterEmailConfirmationResponseType,
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
  ProjectCreationMutationResponseType,
  ProjectTitleDuplicationCheckResponseType,
  UserDetailHomeResponseType,
  UserDetailResponseType,
};

export { MutatianStatusEnum };
