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
          }
          isLoading @client
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
`;

export { REGISTER_MUTATION, LOGIN_MUTATION, LOGOUT_MUTATION, PROJECT_LIST_QUERY };
