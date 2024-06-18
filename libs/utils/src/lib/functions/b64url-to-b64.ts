export function b64urlToB64(base64url: string) {
  return base64url.replace(/_/g, '/').replace(/-/g, '+');
}
