
const backendDomain = import.meta.env.VITE_BACKEND_DOMAIN

export async function getClaims(access_token: string) {
  if (!access_token)
    throw new Error('Unauthenticated')

  const response = await fetch(backendDomain + '/claim', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${access_token}`,
    }
  });

  if (!response.ok) {
    throw new Error('Failed to get claims. ' + response.text);
  }
  return response;
}

export async function createClaim(access_token: string, client: string, file: File, tags: string[]) {
  if (!access_token)
    throw new Error('Unauthenticated')
  
  const base64Content = await fileToBase64(file);
  const body = {
    client: client,
    filename: file.name,
    file_base64: base64Content,
    tags: tags,
  };

  const response = await fetch(backendDomain + '/claim', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${access_token}`,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error('Failed to create claim. ' + response.text);
  }
  return response;
}

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      const base64 = result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}