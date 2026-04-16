import { useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect, useState } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ProviderInfo {
  id: string;
  name: string;
  base_url: string;
  protocol: string;
  group: 'international' | 'china' | 'local' | 'custom' | 'ollama';
  icon: string;
  description: string;
  default_models: string[];
  docs_url?: string;
  // merged from user override:
  has_key: boolean;
  api_key: string;       // "***" when set, "" when not
  enabled: boolean;
  extra_models: string[];
  active_model: string | null;
}

export interface OllamaModel {
  name: string;
  size_gb: number;
  modified_at: string;
  quantization: string;
  parameter_size: string;
  family: string;
}

export interface LocalService {
  id: string;
  name: string;
  description?: string;
  port?: number;
  status?: string;
  user_enabled: boolean;
  [key: string]: unknown;
}

const API_BASE = '/api/user-models';

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Providers
// ---------------------------------------------------------------------------

export function useProviders() {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchProviders = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiFetch<ProviderInfo[]>('/providers');
      setProviders(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { void fetchProviders(); }, [fetchProviders]);
  return { providers, isLoading, error, refetch: fetchProviders };
}

export function useSetProviderAPIKey() {
  const [isLoading, setIsLoading] = useState(false);

  const setAPIKey = useCallback(
    async (providerId: string, apiKey: string, baseUrl?: string) => {
      setIsLoading(true);
      try {
        return await apiFetch('/providers/' + providerId + '/apikey', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ provider_id: providerId, api_key: apiKey, base_url: baseUrl }),
        });
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { setAPIKey, isLoading };
}

export function useRemoveProviderAPIKey() {
  const [isLoading, setIsLoading] = useState(false);

  const removeAPIKey = useCallback(async (providerId: string) => {
    setIsLoading(true);
    try {
      return await apiFetch('/providers/' + providerId + '/apikey', { method: 'DELETE' });
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { removeAPIKey, isLoading };
}

export function useTestConnection() {
  const [isLoading, setIsLoading] = useState(false);

  const testConnection = useCallback(
    async (providerId: string, apiKey?: string, baseUrl?: string) => {
      setIsLoading(true);
      try {
        return await apiFetch<{ ok: boolean; models?: string[]; error?: string }>(
          '/providers/' + providerId + '/test',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider_id: providerId, api_key: apiKey, base_url: baseUrl }),
          }
        );
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { testConnection, isLoading };
}

// ---------------------------------------------------------------------------
// Ollama
// ---------------------------------------------------------------------------

export function useOllamaModels() {
  const [models, setModels] = useState<OllamaModel[]>([]);
  const [running, setRunning] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiFetch<{ ok: boolean; running: boolean; models: OllamaModel[]; error?: string }>(
        '/ollama/models'
      );
      setRunning(data.running);
      setModels(data.models ?? []);
      if (!data.ok && data.error) setError(new Error(data.error));
    } catch (err) {
      setRunning(false);
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);
  return { models, running, isLoading, error, refresh };
}

// ---------------------------------------------------------------------------
// Active model
// ---------------------------------------------------------------------------

export interface ActiveModel {
  active_provider: string | null;
  active_model: string | null;
}

export function useActiveModel() {
  const queryClient = useQueryClient();
  const [active, setActive] = useState<ActiveModel>({ active_provider: null, active_model: null });
  const [isLoading, setIsLoading] = useState(false);

  const fetchActive = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await apiFetch<ActiveModel>('/active');
      setActive(data);
    } catch {
      // ignore
    } finally {
      setIsLoading(false);
    }
  }, []);

  const setActiveModel = useCallback(async (providerId: string, modelId: string) => {
    await apiFetch('/active', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider_id: providerId, model_id: modelId }),
    });
    setActive({ active_provider: providerId, active_model: modelId });
    await queryClient.invalidateQueries({ queryKey: ['models'] });
  }, [queryClient]);

  useEffect(() => { void fetchActive(); }, [fetchActive]);
  return { active, isLoading, setActiveModel, refetch: fetchActive };
}

// ---------------------------------------------------------------------------
// Local services (localhost:9999)
// ---------------------------------------------------------------------------

export function useLocalServices() {
  const [services, setServices] = useState<LocalService[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchServices = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiFetch<{ ok: boolean; services: LocalService[]; error?: string }>(
        '/local-services'
      );
      setServices(data.services ?? []);
      if (!data.ok && data.error) setError(new Error(data.error));
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const toggleService = useCallback(async (serviceId: string, enabled: boolean) => {
    await apiFetch('/local-services/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ service_id: serviceId, enabled }),
    });
    setServices(prev =>
      prev.map(s => (s.id === serviceId ? { ...s, user_enabled: enabled } : s))
    );
  }, []);

  useEffect(() => { void fetchServices(); }, [fetchServices]);
  return { services, isLoading, error, refetch: fetchServices, toggleService };
}

// ---------------------------------------------------------------------------
// Legacy compat exports (keep old imports working)
// ---------------------------------------------------------------------------

export interface APIKeyConfig {
  provider: string;
  enabled: boolean;
}

export interface UserModel {
  name: string;
  display_name: string;
  provider: string;
  model_id: string;
  supports_thinking: boolean;
  supports_vision: boolean;
  enabled: boolean;
}

export interface ModelConfigStatus {
  api_keys_configured: string[];
  models_count: number;
  models: string[];
}

export function useUserModels() {
  const [models, setModels] = useState<Record<string, UserModel>>({});
  const [isLoading, setIsLoading] = useState(false);
  const fetchModels = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await apiFetch<Record<string, UserModel>>('/models');
      setModels(data);
    } catch { /* ignore */ } finally { setIsLoading(false); }
  }, []);
  useEffect(() => { void fetchModels(); }, [fetchModels]);
  return { models, isLoading, error: null, refetch: fetchModels };
}

export function useAPIKeys() {
  const [apiKeys, setAPIKeys] = useState<Record<string, APIKeyConfig>>({});
  const [isLoading, setIsLoading] = useState(false);
  const fetchAPIKeys = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await apiFetch<Record<string, APIKeyConfig>>('/api-keys');
      setAPIKeys(data);
    } catch { /* ignore */ } finally { setIsLoading(false); }
  }, []);
  useEffect(() => { void fetchAPIKeys(); }, [fetchAPIKeys]);
  return { apiKeys, isLoading, error: null, refetch: fetchAPIKeys };
}

export function useSetAPIKey() {
  const [isLoading, setIsLoading] = useState(false);
  const setAPIKey = useCallback(async (provider: string, apiKey: string) => {
    setIsLoading(true);
    try {
      return await apiFetch('/api-keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, api_key: apiKey, enabled: true }),
      });
    } finally { setIsLoading(false); }
  }, []);
  return { setAPIKey, isLoading, error: null };
}

export function useRemoveAPIKey() {
  const [isLoading, setIsLoading] = useState(false);
  const removeAPIKey = useCallback(async (provider: string) => {
    setIsLoading(true);
    try {
      return await apiFetch('/api-keys/' + provider, { method: 'DELETE' });
    } finally { setIsLoading(false); }
  }, []);
  return { removeAPIKey, isLoading, error: null };
}

export function useModelConfigStatus() {
  const [status, setStatus] = useState<ModelConfigStatus | null>(null);
  const fetchStatus = useCallback(async () => {
    try {
      const data = await apiFetch<ModelConfigStatus>('/status');
      setStatus(data);
    } catch { /* ignore */ }
  }, []);
  useEffect(() => { void fetchStatus(); }, [fetchStatus]);
  return { status, isLoading: false, error: null, refetch: fetchStatus };
}

