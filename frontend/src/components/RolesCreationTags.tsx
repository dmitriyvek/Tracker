import { Tag, Input, Tooltip } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { useEffect, useRef, useState } from "react";

const RolesCreationForm: React.FC = () => {
  const [tagList, setTagList] = useState<string[]>([]);
  const [isInputVisible, setIsInputVisible] = useState<boolean>(false);
  const [inputValue, setInputValue] = useState<string>("");
  const [editInputIndex, setEditInputIndex] = useState<number>(-1);
  const [editInputValue, setEditInputValue] = useState<string>("");

  const inputRef = useRef(null);
  const editInputRef = useRef(null);

  useEffect(() => {
    if (isInputVisible && inputRef.current) {
      // @ts-ignore
      inputRef.current.focus();
    }
  }, [isInputVisible]);

  useEffect(() => {
    if (editInputIndex >= 0 && editInputRef.current) {
      // @ts-ignore
      editInputRef.current.focus();
    }
  }, [editInputIndex]);

  const handleTagClose = (removedTag: string) => {
    const tags = tagList.filter((tag) => tag !== removedTag);
    setTagList(tags);
  };

  const showTagInput = () => {
    setIsInputVisible(true);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleInputConfirm = () => {
    let tags = tagList;
    if (inputValue && tagList.indexOf(inputValue) === -1) {
      tags = [...tagList, inputValue];
    }
    console.log(tags);
    setIsInputVisible(false);
    setTagList(tags);
    setInputValue("");
  };

  const handleEditInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEditInputValue(e.target.value);
  };

  const handleEditInputConfirm = () => {
    const newTags = [...tagList];
    newTags[editInputIndex] = editInputValue;

    setTagList(newTags);
    setEditInputIndex(-1);
    setEditInputValue("");
  };

  return (
    <>
      {tagList.map((tag, index) => {
        if (editInputIndex === index) {
          return (
            <Input
              ref={editInputRef}
              key={tag}
              size="small"
              className="tag-input"
              value={editInputValue}
              onChange={handleEditInputChange}
              onBlur={handleEditInputConfirm}
              onPressEnter={handleEditInputConfirm}
            />
          );
        }

        const isLongTag = tag.length > 20;

        const tagElem = (
          <Tag
            className="edit-tag"
            key={tag}
            closable={true}
            onClose={() => handleTagClose(tag)}
          >
            <span
              onDoubleClick={(e) => {
                setEditInputIndex(index);
                setEditInputValue(tag);
                e.preventDefault();
              }}
            >
              {isLongTag ? `${tag.slice(0, 20)}...` : tag}
            </span>
          </Tag>
        );
        return isLongTag ? (
          <Tooltip title={tag} key={tag}>
            {tagElem}
          </Tooltip>
        ) : (
          tagElem
        );
      })}
      {isInputVisible && (
        <Input
          ref={inputRef}
          type="text"
          size="small"
          className="tag-input"
          value={inputValue}
          onChange={handleInputChange}
          onBlur={handleInputConfirm}
          onPressEnter={handleInputConfirm}
        />
      )}
      {!isInputVisible && (
        <Tag className="site-tag-plus" onClick={showTagInput}>
          <PlusOutlined /> Add email
        </Tag>
      )}
    </>
  );
};

export { RolesCreationForm };
