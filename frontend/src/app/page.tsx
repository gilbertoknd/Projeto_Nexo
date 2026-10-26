'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Table,
  Tag,
  Button,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Card,
  Space,
  Modal,
  Typography,
  message,
  Divider,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// --- Tipagens alinhadas com 01-DATA-AND-API.md ---
export interface Pagamento {
  id: number;
  status: 'PENDENTE' | 'CONFIRMADO' | 'FALHOU';
  atualizado_em?: string;
}

export interface Proposta {
  id: number;
  solicitacao: number;
  valor: string;
  validade: string;
  status: 'ENVIADA' | 'ACEITA' | 'EXPIRADA';
  pagamento?: Pagamento | null;
}

export interface Solicitacao {
  id: number;
  empresa: string;
  servico_desejado: string;
  status: 'ABERTA' | 'CONTRATADA' | 'ENCERRADA';
  criado_em: string;
  propostas: Proposta[];
}

export default function ContratacaoPage() {
  const queryClient = useQueryClient();
  const [formSolicitacao] = Form.useForm();
  const [formProposta] = Form.useForm();

  // Controlo do Modal para enviar proposta a uma solicitação específica
  const [solicitacaoSelecionada, setSolicitacaoSelecionada] = useState<number | null>(null);

  // 1. QUERY: Listagem com polling de 3 segundos (refetchInterval)
  const { data: solicitacoes = [], isLoading, isFetching } = useQuery<Solicitacao[]>({
    queryKey: ['solicitacoes'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/solicitacoes/`);
      if (!res.ok) throw new Error('Falha ao carregar solicitações');
      return res.json();
    },
    refetchInterval: 3000, // Atualiza sozinho a cada 3s para refletir o Celery Worker!
  });

  // 2. MUTATION: Criar Solicitação
  const criarSolicitacaoMutation = useMutation({
    mutationFn: async (values: { empresa: string; servico_desejado: string }) => {
      const res = await fetch(`${API_URL}/solicitacoes/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      if (!res.ok) throw new Error('Erro ao criar solicitação');
      return res.json();
    },
    onSuccess: () => {
      message.success('Solicitação criada com sucesso!');
      formSolicitacao.resetFields();
      queryClient.invalidateQueries({ queryKey: ['solicitacoes'] });
    },
    onError: () => message.error('Não foi possível criar a solicitação.'),
  });

  // 3. MUTATION: Enviar Proposta
  const enviarPropostaMutation = useMutation({
    mutationFn: async (values: { solicitacao: number; valor: number; validade: string }) => {
      const res = await fetch(`${API_URL}/propostas/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      if (!res.ok) throw new Error('Erro ao enviar proposta');
      return res.json();
    },
    onSuccess: () => {
      message.success('Proposta enviada!');
      setSolicitacaoSelecionada(null);
      formProposta.resetFields();
      queryClient.invalidateQueries({ queryKey: ['solicitacoes'] });
    },
    onError: () => message.error('Erro ao enviar proposta.'),
  });

  // 4. MUTATION: Aceitar Proposta (dispara o Pagamento e a Task no Celery)
  const aceitarPropostaMutation = useMutation({
    mutationFn: async (propostaId: number) => {
      const res = await fetch(`${API_URL}/propostas/${propostaId}/aceitar/`, {
        method: 'POST',
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Erro ao aceitar proposta');
      }
      return res.json();
    },
    onSuccess: () => {
      message.info('Proposta aceite! Pagamento em processamento na fila (Celery)...');
      queryClient.invalidateQueries({ queryKey: ['solicitacoes'] });
    },
    onError: (err: Error) => message.error(err.message),
  });

  // Auxiliares visuais de cores das Tags
  const renderStatusSolicitacao = (status: Solicitacao['status']) => {
    const cores = { ABERTA: 'processing', CONTRATADA: 'success', ENCERRADA: 'default' };
    return <Tag color={cores[status]}>{status}</Tag>;
  };

  const renderStatusPagamento = (status: Pagamento['status']) => {
    const cores = { PENDENTE: 'warning', CONFIRMADO: 'success', FALHOU: 'error' };
    return <Tag color={cores[status]}>Pagamento: {status}</Tag>;
  };

  // Colunas da Table do Ant Design
  const columns: ColumnsType<Solicitacao> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: 'Empresa',
      dataIndex: 'empresa',
      key: 'empresa',
      render: (texto) => <Text strong>{texto}</Text>,
    },
    {
      title: 'Serviço Desejado',
      dataIndex: 'servico_desejado',
      key: 'servico_desejado',
    },
    {
      title: 'Status da Solicitação',
      dataIndex: 'status',
      key: 'status',
      width: 160,
      render: (status) => renderStatusSolicitacao(status),
    },
    {
      title: 'Propostas e Pagamento',
      key: 'propostas',
      render: (_, record) => (
        <Space vertical style={{ width: '100%' }}>
          {record.propostas.length === 0 ? (
            <Text type="secondary">Nenhuma proposta recebida</Text>
          ) : (
            record.propostas.map((prop) => (
              <Card
                key={prop.id}
                size="small"
                style={{ backgroundColor: '#fafafa', border: '1px solid #e8e8e8' }}
              >
                <Space wrap align="center" style={{ justifyContent: 'space-between', width: '100%' }}>
                  <Space>
                    <Text strong>R$ {prop.valor}</Text>
                    <Text type="secondary">(Validade: {prop.validade})</Text>
                    <Tag>{prop.status}</Tag>
                    {prop.pagamento && renderStatusPagamento(prop.pagamento.status)}
                  </Space>

                  {record.status === 'ABERTA' && prop.status === 'ENVIADA' && (
                    <Button
                      type="primary"
                      size="small"
                      loading={aceitarPropostaMutation.isPending}
                      onClick={() => aceitarPropostaMutation.mutate(prop.id)}
                    >
                      Aceitar Proposta
                    </Button>
                  )}
                </Space>
              </Card>
            ))
          )}

          {record.status === 'ABERTA' && (
            <Button
              type="dashed"
              size="small"
              onClick={() => setSolicitacaoSelecionada(record.id)}
            >
              + Nova Proposta
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ maxWidth: 1100, margin: '32px auto', padding: '0 16px' }}>
      <Space align="center" style={{ justifyContent: 'space-between', width: '100%' }}>
        <Title level={3} style={{ margin: 0 }}>
          Portal de Contratação de Serviços
        </Title>
        <Tag color={isFetching ? 'blue' : 'default'}>
          {isFetching ? 'A sincronizar fila...' : 'Sincronizado (Polling 3s)'}
        </Tag>
      </Space>

      <Divider />

      {/* Formulário para Criar Solicitação */}
      <Card title="Nova Solicitação de Serviço" style={{ marginBottom: 24 }}>
        <Form
          form={formSolicitacao}
          layout="inline"
          onFinish={(values) => criarSolicitacaoMutation.mutate(values)}
          style={{ gap: 12, rowGap: 12 }}
        >
          <Form.Item
            name="empresa"
            rules={[{ required: true, message: 'Informe a empresa' }]}
          >
            <Input placeholder="Nome da Empresa (ex: Acme Corp)" style={{ width: 240 }} />
          </Form.Item>

          <Form.Item
            name="servico_desejado"
            rules={[{ required: true, message: 'Descreva o serviço' }]}
            style={{ flex: 1 }}
          >
            <Input placeholder="Serviço desejado (ex: Migração de Servidor Linux)" />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={criarSolicitacaoMutation.isPending}
            >
              Criar Solicitação
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* Tabela de Solicitações */}
      <Card title="Solicitações Cadastradas">
        <Table
          rowKey="id"
          columns={columns}
          dataSource={solicitacoes}
          loading={isLoading}
          pagination={{ pageSize: 5 }}
        />
      </Card>

      {/* Modal rápido para enviar proposta */}
      <Modal
        title={`Enviar Proposta (Solicitação #${solicitacaoSelecionada})`}
        open={solicitacaoSelecionada !== null}
        onCancel={() => setSolicitacaoSelecionada(null)}
        onOk={() => formProposta.submit()}
        confirmLoading={enviarPropostaMutation.isPending}
        okText="Enviar Proposta"
        cancelText="Cancelar"
      >
        <Form
          form={formProposta}
          layout="vertical"
          onFinish={(values) => {
            if (!solicitacaoSelecionada) return;
            enviarPropostaMutation.mutate({
              solicitacao: solicitacaoSelecionada,
              valor: values.valor,
              validade: values.validade.format('YYYY-MM-DD'),
            });
          }}
        >
          <Form.Item
            label="Valor da Proposta (R$)"
            name="valor"
            rules={[{ required: true, message: 'Informe o valor' }]}
          >
            <InputNumber style={{ width: '100%' }} min={1} precision={2} />
          </Form.Item>

          <Form.Item
            label="Data de Validade"
            name="validade"
            rules={[{ required: true, message: 'Informe a validade' }]}
          >
            <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}