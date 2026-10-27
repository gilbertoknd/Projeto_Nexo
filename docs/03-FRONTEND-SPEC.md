# 03. Especificação do Frontend (Next.js + Ant Design + React Query)

## 1. Gerenciamento de Estado (`@tanstack/react-query`)
- **Configuração de Ambiente**:
  - `NEXT_PUBLIC_API_URL`: URL base da API Django (default: `http://localhost:8000/api`).
- **Listagem (`useQuery`)**:
  - `queryKey: ['solicitacoes']`
  - `queryFn`: `GET ${NEXT_PUBLIC_API_URL}/solicitacoes/`
  - `refetchInterval: 3000` (obrigatório para observar a transição assíncrona `PENDENTE` -> `CONFIRMADO`/`FALHOU` e `ABERTA` -> `CONTRATADA` em tempo real).
- **Mutações (`useMutation`)**:
  - Criar solicitação (`POST /api/solicitacoes/`)
  - Criar proposta (`POST /api/propostas/`)
  - Aceitar proposta (`POST /api/propostas/{id}/aceitar/`)
  - Todas as mutações devem chamar `queryClient.invalidateQueries({ queryKey: ['solicitacoes'] })` no `onSuccess`.

## 2. Componentes Ant Design (`antd`)
- **`Table`**: Exibir empresa, serviço desejado, tag colorida de status da solicitação, lista de propostas recebidas, status do pagamento e o `Button` "Aceitar Proposta" (habilitado apenas quando a solicitação estiver `ABERTA` e a proposta `ENVIADA`).
- **`Form` + `Modal` (ou Card)**: Campos `empresa` e `servico_desejado` para nova solicitação, além de opção rápida para enviar proposta para uma solicitação aberta.