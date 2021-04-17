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
          authToken
          recordId
          record {
            username
          }
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
          role
        }
        createdBy {
          id
          username
        }
        roleList(first: $roleNumber, after: $after) {
          edges {
            node {
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

export {
  REGISTER_MUTATION,
  LOGIN_MUTATION,
  LOGOUT_MUTATION,
  PROJECT_LIST_QUERY,
  USERNAME_DUPLICATION_CHECK_QUERY,
  EMAIL_DUPLICATION_CHECK_QUERY,
  PROJECT_DETAIL_QUERY,
  PROJECT_CREATION_MUTATION,
  PROJECT_TITLE_DUPLICATION_CHECK_QUERY,
  USER_DETAIL_HOME_QUERY,
  USER_DETAIL_QUERY,
};
