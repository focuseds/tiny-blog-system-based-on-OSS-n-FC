# 基于对象存储和函数计算的微型博客系统

## 关于

本项目前身为个人每日打卡项目，无数据库，数据存储在[阿里云对象存储对象标签](https://help.aliyun.com/document_detail/121939.html)中，托管于云平台函数计算。

每条打卡内容包含四个字段：```标题```、```打卡内容```、```打卡日期```、```打卡时间```和```图片载体```。其中，第一个字段作为图片名存储。后三个字段存储在```载体图片```的```OSS_OBJECT_TAGGING```属性中。对应关系如下。

| 序号  | TAG       | 存储位置 | 备注   |
|-----|-----------|------|------|
| 1   | title     | 文件名  | 打卡标题 |
| 2   | time      | 对象标签 | 打卡日期 |
| 3   | content   | 对象标签 | 打卡内容 |
| 4   | timestamp | 对象标签 | 打卡时间 |

## 功能描述

## 使用

### 部署工具

## 参考链接

1. [阿里云对象存储OSS](https://www.aliyun.com/product/oss)
2. [阿里云对象存储对象标签](https://help.aliyun.com/document_detail/121939.html)
3. [阿里云函数计算FC](https://help.aliyun.com/document_detail/52895.html)