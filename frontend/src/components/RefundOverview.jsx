import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Input, Button, Table } from 'antd';

export default function RefundOverview(){
  const [overview, setOverview] = useState(null);
  const [phone, setPhone] = useState('');
  const [user, setUser] = useState(null);

  useEffect(()=>{
    fetch('/api/overview').then(r=>r.json()).then(setOverview);
  },[]);

  function onQuery(){
    fetch(`/api/user?phone=${phone}`).then(r=>r.json()).then(setUser).catch(()=>setUser(null));
  }

  const columns = [
    {title:'产品名称', dataIndex:'name'},
    {title:'金额', dataIndex:'amount'},
    {title:'开始', dataIndex:'start'},
    {title:'结束', dataIndex:'end'},
    {title:'每日应返', dataIndex:'daily_return'},
    {title:'状态', dataIndex:'status'},
    {title:'额外', dataIndex:'extra'}
  ];

  return (
    <div>
      <h2>退款查询系统</h2>
      {overview && (
        <Row gutter={16}>
          <Col><Card title="总认购额度">${overview.total_subscribed}</Card></Col>
          <Col><Card title="已返款总额">${overview.total_refunded}</Card></Col>
          <Col><Card title="到期未返款">${overview.due_not_refunded}</Card></Col>
          <Col><Card title="未到期总额">${overview.not_due_total}</Card></Col>
        </Row>
      )}

      <div style={{marginTop:20}}>
        <Input.Search placeholder="手机号" enterButton="查询" onSearch={(v)=>{setPhone(v); fetch(`/api/user?phone=${v}`).then(r=>r.json()).then(setUser).catch(()=>setUser(null))}} />
      </div>

      {user && (
        <div style={{marginTop:20}}>
          <h3>手机号：{user.phone} 地址：{user.address}</h3>
          <Row gutter={16}>
            <Col><Card>产品数量<br/>{user.product_count}</Card></Col>
            <Col><Card>累计认购<br/>${user.total_subscribed}</Card></Col>
            <Col><Card>已返款<br/>${user.total_refunded}</Card></Col>
            <Col><Card>到期未返<br/>${user.due_not_refunded}</Card></Col>
            <Col><Card>未到期<br/>${user.not_due_total}</Card></Col>
          </Row>

          <Table style={{marginTop:20}} dataSource={user.products} columns={columns} rowKey={(r,i)=>i} />
        </div>
      )}
    </div>
  );
}
