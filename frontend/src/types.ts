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

type ProjectNodeType = Readonly<{
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
  data: {
    projects: {
      list: ProjectListType;
    };
  };
};

export type { ProjectNodeType, ProjectListType, ProjectListResponseType };
