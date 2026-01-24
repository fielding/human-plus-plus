/**
 * Human++ TypeScript Sample
 *
 * User service with caching and network fetching.
 * Tests marker detection vs ?? nullish coalescing operator.
 */

type ID = string | number;

interface User {
  id: ID;
  name: string;
  email: string;
  createdAt: Date;
}

interface Result<T> {
  ok: boolean;
  value?: T;
  error?: Error;
}

interface CacheEntry<T> {
  value: T;
  expiresAt: number;
}

const DEFAULT_TTL_MS = 5 * 60 * 1000;
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 100;

// !! Cache has no size limit - monitor memory usage in production
class UserCache {
  private store = new Map<ID, CacheEntry<User>>();

  get(id: ID): User | undefined {
    const entry = this.store.get(id);
    if (!entry) return undefined;
    if (Date.now() > entry.expiresAt) {
      this.store.delete(id);
      return undefined;
    }
    return entry.value;
  }

  set(id: ID, user: User, ttlMs = DEFAULT_TTL_MS): void {
    this.store.set(id, {
      value: user,
      expiresAt: Date.now() + ttlMs,
    });
  }

  invalidate(id: ID): boolean {
    return this.store.delete(id);
  }

  clear(): void {
    this.store.clear();
  }
}

export class UserService {
  private cache = new UserCache();

  constructor(
    private readonly baseUrl: string,
    private readonly apiKey: string
  ) {}

  // ?? Should we add circuit breaker pattern here?
  private async fetchWithRetry(url: string, retries = MAX_RETRIES): Promise<Response> {
    let lastError: Error | undefined;

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) return response;

        if (response.status >= 500) {
          throw new Error(`Server error: ${response.status}`);
        }

        return response;
      } catch (error) {
        lastError = error as Error;
        if (attempt < retries) {
          await this.sleep(RETRY_DELAY_MS * attempt);
        }
      }
    }

    throw lastError ?? new Error('Unknown fetch error');
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async getUser(userId: ID): Promise<Result<User>> {
    const cached = this.cache.get(userId);
    if (cached) {
      return { ok: true, value: cached };
    }

    try {
      const url = `${this.baseUrl}/users/${encodeURIComponent(String(userId))}`;
      const response = await this.fetchWithRetry(url);

      if (!response.ok) {
        return { ok: false, error: new Error(`HTTP ${response.status}`) };
      }

      const data = await response.json();

      // >> Normalize API response - backend returns snake_case
      const user: User = {
        id: data.id,
        name: data.name ?? data.display_name ?? 'Unknown',
        email: data.email ?? '',
        createdAt: new Date(data.created_at),
      };

      this.cache.set(userId, user);
      return { ok: true, value: user };
    } catch (error) {
      return { ok: false, error: error as Error };
    }
  }

  async searchUsers(query: string): Promise<Result<User[]>> {
    if (!query.trim()) {
      return { ok: true, value: [] };
    }

    try {
      const url = `${this.baseUrl}/users/search?q=${encodeURIComponent(query)}`;
      const response = await this.fetchWithRetry(url);

      if (!response.ok) {
        return { ok: false, error: new Error(`HTTP ${response.status}`) };
      }

      const data = await response.json();
      const users: User[] = data.results.map((item: Record<string, unknown>) => ({
        id: item.id,
        name: item.name ?? item.display_name ?? 'Unknown',
        email: item.email ?? '',
        createdAt: new Date(item.created_at as string),
      }));

      return { ok: true, value: users };
    } catch (error) {
      return { ok: false, error: error as Error };
    }
  }
}

// Example usage
async function main() {
  const service = new UserService('https://api.example.com', 'secret-key');

  const result = await service.getUser('user-123');
  if (result.ok) {
    console.log(`Found user: ${result.value?.name}`);
  } else {
    console.error(`Error: ${result.error?.message}`);
  }
}

main().catch(console.error);
