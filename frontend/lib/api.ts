const API_URL =
  typeof window === "undefined"
    ? process.env.INTERNAL_API_URL
    : process.env.NEXT_PUBLIC_API_URL;


if (!API_URL) {
  throw new Error(
    "API URL is not configured",
  );
}


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


  if (
    response.status === 204
  ) {
    return undefined as T;
  }


  return response.json();

}