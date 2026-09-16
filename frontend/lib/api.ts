const API_URL =
  process.env.API_URL ?? "http://localhost:8000/api/v1";

export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_URL}${path}`,
    {
      ...options,
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      `API error: ${response.status}`,
    );
  }

  return response.json();
}