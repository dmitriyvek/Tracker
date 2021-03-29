import axios, { AxiosResponse } from 'axios';
import React from 'react';
import { List, Avatar, Button, Skeleton } from 'antd';

const count = 3;
const fakeDataUrl = `https://randomuser.me/api/?results=${count}&inc=name,gender,email,nat&noinfo`;

type NameType = {
    type: string,
    first: string,
    last: string
}
type ItemType = {
    loading: boolean,
    gender: string,
    name: NameType,
    email: string,
    nat: string
}
type StateType = {
    initLoading: boolean,
    loading: boolean,
    data: ItemType[],
    list: []
}

type ResponseDataType = {
    results: ItemType[]
}

type CallbackType = (res: ResponseDataType) => void

class ProjectList extends React.Component {
  state: StateType = {
    initLoading: true,
    loading: false,
    data: [],
    list: [],
  };

  componentDidMount() {
    this.getData((res: ResponseDataType) => {
      this.setState({
        initLoading: false,
        data: res.results,
        list: res.results,
      });
    });
  }

  getData = (callback: CallbackType) => {
    axios
    //   .post('localhost:8000/grapiql', {
    //     query: `
    //         {
    //             projects {
    //                 list(first: ${count}) {
    //                     edges {
    //                         node {
    //                             id
    //                             title
    //                             createdAt
    //                             description
    //                         }
    //                     }
    //                 }
    //             }
    //         }
    //     `,
    //   })
      .get<ResponseDataType>(fakeDataUrl)
      .then((response: AxiosResponse) => callback(response.data))
      .catch((err) => {
        console.log(err);
      });
  };

  onLoadMore = () => {

    this.setState({
      loading: true,
      list: this.state.data.concat([...new Array(count)].map(() => ({ loading: true, name: {} } as ItemType))),
    });
    this.getData((res: ResponseDataType) => {
      const data = this.state.data.concat(res.results);
      this.setState(
        {
          data,
          list: data,
          loading: false,
        },
        () => {
          // Resetting window's offsetTop so as to display react-virtualized demo underfloor.
          // In real scene, you can using public method of react-virtualized:
          // https://stackoverflow.com/questions/46700726/how-to-use-public-method-updateposition-of-react-virtualized
          window.dispatchEvent(new Event('resize'));
        },
      );
    });
  };

  render() {
    const { initLoading, loading, list } = this.state;
    const loadMore =
      !initLoading && !loading ? (
        <div
          style={{
            textAlign: 'center',
            marginTop: 12,
            height: 32,
            lineHeight: '32px',
          }}
        >
          <Button onClick={this.onLoadMore}>loading more</Button>
        </div>
      ) : null;

    return (
      <List
        className="demo-loadmore-list"
        loading={initLoading}
        itemLayout="horizontal"
        loadMore={loadMore}
        dataSource={list}
        renderItem={(item: ItemType) => (
          <List.Item actions={[<a key="list-loadmore-edit">edit</a>, <a key="list-loadmore-more">more</a>]}>
            <Skeleton avatar title={false} loading={item.loading} active>
              <List.Item.Meta
                avatar={<Avatar src="https://zos.alipayobjects.com/rmsportal/ODTLcjxAfvqbxHnVXCYX.png" />}
                title={<a href="https://ant.design">{item.name.last}</a>}
                description="Ant Design, a design language for background applications, is refined by Ant UED Team"
              />
              <div>content</div>
            </Skeleton>
          </List.Item>
        )}
      />
    );
  }
}

export { ProjectList };
