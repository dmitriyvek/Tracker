type PageInfoType = {
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  startCursor: string;
  endCursor: string;
  __typename: string;
};

type RoleNodeType = Readonly<{
  role: string;
  userId: number;
  projectId: number;
  assignBy: number;
  assignAt: string;
}>;

type RoleListType = {
  totalCount: number;
  edges: {
    cursor: string;
    node: RoleNodeType;
  }[];
  pageInfo: PageInfoType;
};

type ProjectNodeType = Partial<{
  id: string;
  title: string;
  description: string;
  createdAt: string;
  myRole: RoleNodeType;
  roleList: RoleListType;
}>;

type ProjectListType = {
  totalCount: number;
  edges: {
    cursor: string;
    node: ProjectNodeType;
  }[];
  pageInfo: PageInfoType;
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

type UserLoginType = {
  username: string;
};

type LoginPayloadType = {
  authToken: string;
  recordId: number;
  status: MutatianStatusEnum;
  record: UserLoginType;
};

type LoginMutationResponseType = {
  auth: {
    login: {
      loginPayload: LoginPayloadType;
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

export type { ProjectNodeType, LoginMutationResponseType, LogoutMutationResponseType };

export { MutatianStatusEnum };
