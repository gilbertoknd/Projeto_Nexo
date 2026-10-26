'use client';

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AntdRegistry } from '@ant-design/nextjs-registry';

export default function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  );

  return (
    <AntdRegistry>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </AntdRegistry>
  );
}