import { gql } from "@apollo/client";

const LOGIN_MUTATION = gql`
  mutation LoginMutation($input: LoginInput!) {
    auth {
      login(input: $input) {
        loginPayload {
          status
          recordId
          authToken
          record {
            username
          }
        }
      }
    }
  }
`;

const USERNAME_DUPLICATION_CHECK_QUERY = gql`
  query UsernameDuplicationCheckQuery($username: Username!) {
    auth {
      duplicationCheck {
        username(username: $username)
      }
    }
  }
`;

const EMAIL_DUPLICATION_CHECK_QUERY = gql`
  query EmailDuplicationCheckQuery($email: Email!) {
    auth {
      duplicationCheck {
        email(email: $email)
      }
    }
  }
`;

const REGISTER_MUTATION = gql`
  mutation RegisterMutation($input: RegisterInput!) {
    auth {
      register(input: $input) {
        registerPayload {
          status
        }
      }
    }
  }
`;

const LOGOUT_MUTATION = gql`
  mutation LogoutMutation {
    auth {
      logout {
        logoutPayload {
          status
        }
      }
    }
  }
`;

const PROJECT_LIST_QUERY = gql`
  query GetProjectList($first: Int, $after: String) {
    projects {
      list(first: $first, after: $after) {
        edges {
          node {
            id
            title
            description
            myRole {
              role
            }
            createdBy {
              id
              username
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
`;

const PROJECT_DETAIL_QUERY = gql`
  query projectDetailQuery($projectId: ID!, $roleNumber: Int, $after: String) {
    node(id: $projectId) {
      ... on ProjectType {
        title
        description
        createdAt
        myRole {
          id
          role
        }
        createdBy {
          id
          username
        }
        roleList(first: $roleNumber, after: $after) {
          edges {
            node {
              id
              role
              user {
                id
                username
                email
              }
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
  }
`;

const ROLE_DELETION_MUTATION = gql`
  mutation RoleDeletionMutation($input: RoleDeletionInput!) {
    role {
      roleDeletion(input: $input) {
        roleDeletionPayload {
          status
        }
      }
    }
  }
`;

const EMAIL_CONFIRMATION_MUTATION = gql`
  mutation($input: RegisterEmailConfirmationInput!) {
    auth {
      emailConfirmation(input: $input) {
        registerEmailConfirmationPayload {
          recordId
          authToken
          status
        }
      }
    }
  }
`;

const PROJECT_CREATION_MUTATION = gql`
  mutation projectCreationMutation($input: ProjectCreationInput!) {
    project {
      projectCreation(input: $input) {
        projectCreationPayload {
          record {
            id
            title
            description
          }
          status
        }
      }
    }
  }
`;

const PROJECT_TITLE_DUPLICATION_CHECK_QUERY = gql`
  query ProjectTitleDuplicationCheckQuery($title: Title!) {
    projects {
      duplicationCheck {
        title(title: $title)
      }
    }
  }
`;

const USER_DETAIL_HOME_QUERY = gql`
  query UserDetailHomeQuery {
    users {
      detail {
        record {
          id
          username
          email
          registeredAt
        }
      }
    }
  }
`;

const USER_DETAIL_QUERY = gql`
  query UserDetailQuery($userId: ID!) {
    node(id: $userId) {
      ... on UserType {
        id
        email
        username
        registeredAt
      }
    }
  }
`;

// for apollo 3.4 overwrite writeQuery in ProjectDeatail onRoleDelete mutation
const PROJECT_DETAIL_ROLE_LIST_LOCAL_QUERY = gql`
  query projectDetailRoleListLocalQuery($projectId: ID!) {
    node(id: $projectId) {
      title
      description
      createdAt
      myRole {
        id
        role
      }
      createdBy {
        id
        username
      }
      roleList {
        edges {
          node {
            id
            role
            user {
              id
              username
              email
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
`;

const ROLE_CREATION_MUTATION = gql`
  mutation($input: RoleCreationInput!) {
    role {
      roleCreation(input: $input) {
        roleCreationPayload {
          duplicatedEmailList
          status
          errorList
        }
      }
    }
  }
`;

export {
  EMAIL_CONFIRMATION_MUTATION,
  EMAIL_DUPLICATION_CHECK_QUERY,
  REGISTER_MUTATION,
  LOGIN_MUTATION,
  LOGOUT_MUTATION,
  PROJECT_CREATION_MUTATION,
  PROJECT_DETAIL_QUERY,
  PROJECT_DETAIL_ROLE_LIST_LOCAL_QUERY,
  PROJECT_LIST_QUERY,
  PROJECT_TITLE_DUPLICATION_CHECK_QUERY,
  ROLE_CREATION_MUTATION,
  ROLE_DELETION_MUTATION,
  USER_DETAIL_HOME_QUERY,
  USER_DETAIL_QUERY,
  USERNAME_DUPLICATION_CHECK_QUERY,
};
