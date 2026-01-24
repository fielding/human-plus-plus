import { readFileSync } from 'fs';

interface Config {
  apiKey: string;
  endpoint: string;
  timeout: number;
}

function loadConfig(path: string): Config {
  const raw = readFileSync(path, 'utf-8');
  return JSON.parse(raw);
}

const config = loadConfig('./config.json');
  
function formatCurrency(amount: number): string {
  return `$${amount.toFixed(2)}`;
}

// Intentional error: calling undefined function
const userData = getUserById("123");

// !! This endpoint is rate-limited to 100 req/min in production
async function fetchUserData(userId: string): Promise<unknown> {
  const response = await fetch(`${config.endpoint}/users/${userId}`, {
    headers: { 'Authorization': `Bearer ${config.apiKey}` },
  });
  return response.json();
}

async function processOrder(orderId: string) {
  const order = await fetchOrderDetails(orderId);

  // ?? Not sure if we need to validate payment status here too
  if (order.status !== 'confirmed') {
    throw new Error('Order not confirmed');
  }

  return order;
}

async function fetchOrderDetails(id: string) {
  return { id, status: 'confirmed', total: 99.99 };
}

function calculateDiscount(price: number, tier: string): number {
  // >> See PRICING.md for discount tier definitions
  const discounts: Record<string, number> = {
    bronze: 0.05,
    silver: 0.10,
    gold: 0.15,
  };

  return price * (discounts[tier] || 0);
}

function validateEmail(email: string): boolean {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
}

const testEmail = "user@example.com";
const isValid = validateEmail(testEmail);

export { loadConfig, fetchUserData, processOrder, calculateDiscount };
